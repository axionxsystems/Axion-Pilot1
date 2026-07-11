import hashlib
import logging
import os
import secrets
import string
import unicodedata
from datetime import datetime, timedelta

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.auth.mailer import mailer

from app.auth.jwt_handler import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.utils import get_password_hash, verify_password
from app.auth.saml import SAMLAuth
from app.auth.saml_settings import get_saml_settings
from app.database import get_db
from app.models.activity import Activity
from app.models.organization import AuditLog
from app.models.sso import SSOConfig, SSOSession
from app.models.user import ForgotPasswordVerification, LoginVerification, SignupVerification, User
from app.schemas.user import (
    ForgotPasswordRequest,
    ForgotPasswordReset,
    LoginOTPVerify,
    LoginPending,
    SignupVerify,
    Token,
    UserCreate,
    UserResponse,
)
from app.limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Config ────────────────────────────────────────────────────────────────────
SUPER_ADMIN_EMAIL = os.environ.get("SUPER_ADMIN_EMAIL", "").strip().lower()
OTP_MAX_ATTEMPTS = 5
OTP_EXPIRY_MINUTES = 10   # increased to 10 min so it doesn't expire too fast
OTP_RESEND_COOLDOWN_SECONDS = 60


def _normalize_email(email: str) -> str:
    """NFKC-normalize to block Unicode homoglyph attacks."""
    return unicodedata.normalize("NFKC", email.strip().lower())

def _hash_otp(otp: str) -> str:
    """SHA-256 hash of the OTP — never store plaintext."""
    return hashlib.sha256(otp.encode()).hexdigest()

def _generate_otp(length: int = 6) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(length))

def _is_gmail(email: str) -> bool:
    return _normalize_email(email).endswith("@gmail.com")


# ── Signup ────────────────────────────────────────────────────────────────────

@router.post("/signup")
@limiter.limit("5/minute")
def signup_request(request: Request, background_tasks: BackgroundTasks, user: UserCreate, db: Session = Depends(get_db)):
    """Initiate signup — sends email OTP for verification."""
    email = _normalize_email(user.email)
    if not _is_gmail(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only Gmail accounts are allowed.")

    # [Privacy] Generic response to prevent user enumeration
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        return {"message": "If this email is not yet registered, an OTP has been sent."}

    # Resend cooldown logic
    pending = db.query(SignupVerification).filter(SignupVerification.email == email).first()
    if pending:
        elapsed = (datetime.utcnow() - pending.created_at).total_seconds()
        if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
            wait = int(OTP_RESEND_COOLDOWN_SECONDS - elapsed)
            raise HTTPException(status_code=429, detail=f"Wait {wait}s before requesting a new OTP.")

    email_otp = _generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    hashed_password = get_password_hash(user.password)

    if pending:
        pending.name = user.full_name
        pending.mobile = user.mobile
        pending.hashed_password = hashed_password
        pending.email_otp_hash = _hash_otp(email_otp)
        pending.mobile_otp_hash = "bypass"  # no longer used
        pending.expires_at = expires_at
        pending.created_at = datetime.utcnow()
        pending.attempt_count = 0
    else:
        pending = SignupVerification(
            email=email,
            mobile=user.mobile or "",
            name=user.full_name,
            hashed_password=hashed_password,
            email_otp_hash=_hash_otp(email_otp),
            mobile_otp_hash="bypass",  # no longer used
            expires_at=expires_at,
        )
        db.add(pending)

    db.commit()
    logger.info(f"[SIGNUP] Registration pending for {email}")
    
    # Send email OTP in background
    background_tasks.add_task(mailer.send_otp, email, email_otp, "Signup Verification")
    
    msg = "Registration pending. Please verify your email to complete signup."
    return {"message": msg}


@router.post("/verify-signup", response_model=UserResponse)
@limiter.limit("10/minute")
def verify_signup(request: Request, data: SignupVerify, db: Session = Depends(get_db)):
    """Finish signup — creates User in DB after OTP verification."""
    email = _normalize_email(data.email)
    pending = db.query(SignupVerification).filter(SignupVerification.email == email).first()

    if not pending:
        raise HTTPException(status_code=400, detail="Registration session not found. Please sign up again.")

    # Verify OTP hasn't expired
    if datetime.utcnow() > pending.expires_at:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=400, detail="Registration session expired. Please sign up again.")

    # Check attempt limit
    if pending.attempt_count >= OTP_MAX_ATTEMPTS:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=429, detail="Too many failed attempts. Please restart signup.")

    # Verify email OTP
    if pending.email_otp_hash != _hash_otp(data.email_otp):
        pending.attempt_count += 1
        db.commit()
        remaining = OTP_MAX_ATTEMPTS - pending.attempt_count
        raise HTTPException(status_code=400, detail=f"Incorrect OTP. {remaining} attempts remaining.")

    # Is super-admin check (normalized)
    is_admin = bool(SUPER_ADMIN_EMAIL and email == SUPER_ADMIN_EMAIL)
    new_user = User(
        email=email,
        name=pending.name,
        mobile=pending.mobile if pending.mobile else None,
        hashed_password=pending.hashed_password,
        is_admin=is_admin,
    )
    db.add(new_user)
    db.delete(pending)
    db.flush()
    db.add(Activity(user_id=new_user.id, action_type="USER_REG", description=f"Registered: {email}"))
    db.commit()
    logger.info(f"[SIGNUP] New user created: {email}")
    return new_user


# ── Login Flow (Step 1 & Step 2 for MFA) ──────────────────────────────────────

@router.post("/login")
@limiter.limit("10/minute")
def login_step1(request: Request, background_tasks: BackgroundTasks, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Password Check → Sends OTP via email (2FA enabled)."""
    email = _normalize_email(form_data.username)
    user = db.query(User).filter(User.email == email).first()

    # Timing-safe failure
    if not user or not user.hashed_password or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account suspended. Contact support.")

    # Generate OTP for 2FA
    otp = _generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    existing = db.query(LoginVerification).filter(LoginVerification.user_id == user.id).first()
    if existing:
        existing.otp_hash = _hash_otp(otp)
        existing.expires_at = expires_at
        existing.created_at = datetime.utcnow()
        existing.attempt_count = 0
    else:
        db.add(LoginVerification(user_id=user.id, otp_hash=_hash_otp(otp), expires_at=expires_at))

    db.commit()


    # Send OTP email in background so login response is instant
    background_tasks.add_task(mailer.send_otp, email, otp, "Login Verification")
    return LoginPending(message="2FA code sent to your email. Check your inbox.")



@router.post("/login/verify-otp", response_model=Token)
@limiter.limit("10/minute")
def login_step2(request: Request, data: LoginOTPVerify, db: Session = Depends(get_db)):
    """Final Authentication — consumes OTP hash and issues JWT."""
    email = _normalize_email(data.email)
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid session.")

    v = db.query(LoginVerification).filter(LoginVerification.user_id == user.id).first()
    if not v or (datetime.utcnow() > v.expires_at):
        if v:
            db.delete(v)
            db.commit()
        raise HTTPException(status_code=400, detail="OTP expired. Please log in again to get a new code.")

    if v.attempt_count >= OTP_MAX_ATTEMPTS:
        db.delete(v)
        db.commit()
        raise HTTPException(status_code=429, detail="Too many failed attempts. Please log in again.")

    if v.otp_hash != _hash_otp(data.otp):
        v.attempt_count += 1
        db.commit()
        remaining = OTP_MAX_ATTEMPTS - v.attempt_count
        raise HTTPException(status_code=400, detail=f"Invalid code. {remaining} attempts remaining.")

    db.delete(v)

    # Auto-elevate super-admin in case the flag was ever unset
    if SUPER_ADMIN_EMAIL and email == SUPER_ADMIN_EMAIL and not user.is_admin:
        user.is_admin = True
    
    # Update last login
    user.last_login = datetime.utcnow()

    db.commit()
    access_token = create_access_token(
        data={"sub": user.email, "v": user.token_version},
        org_id=user.org_id,   # ← multi-tenancy: embed org claim in JWT
    )
    logger.info(f"[LOGIN] Successful login for {email}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/saml/login")
async def saml_login(org_id: str, db: Session = Depends(get_db)):
    """Initiate SAML login flow for an organization."""
    sso_config = db.query(SSOConfig).filter(SSOConfig.org_id == org_id).first()
    if not sso_config or sso_config.sso_method != "saml":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SAML not configured")

    saml_auth = SAMLAuth(get_saml_settings(org_id))
    request_id, login_url = saml_auth.get_login_url()

    session = SSOSession(
        org_id=org_id,
        sso_method="saml",
        state=request_id or secrets.token_urlsafe(32),
        nonce=secrets.token_urlsafe(32),
        expires_at=datetime.utcnow() + timedelta(minutes=15),
    )
    db.add(session)
    db.commit()

    return {"redirect_url": login_url}


@router.post("/saml/callback")
async def saml_callback(org_id: str, request: Request, db: Session = Depends(get_db)):
    """Handle SAML assertion from Auth0."""
    form = await request.form()
    saml_response = form.get("SAMLResponse")
    relay_state = form.get("RelayState")

    if not saml_response:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing SAMLResponse")

    session = (
        db.query(SSOSession)
        .filter(SSOSession.state == relay_state, SSOSession.org_id == org_id)
        .first()
    )
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired SAML state")

    sso_config = db.query(SSOConfig).filter(SSOConfig.org_id == org_id).first()
    if not sso_config or sso_config.sso_method != "saml":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SAML not configured")

    saml_auth = SAMLAuth(get_saml_settings(org_id))
    try:
        user_data = saml_auth.process_response(saml_response, relay_state)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    if sso_config.allowed_domains:
        email_domain = user_data["email"].split("@", 1)[-1].lower()
        allowed = [d.lower() for d in sso_config.allowed_domains or []]
        if email_domain not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email domain not allowed")

    user = db.query(User).filter(User.email == user_data["email"]).first()
    if not user:
        if not sso_config.auto_provision:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not exist")

        user = User(
            org_id=org_id,
            email=user_data["email"],
            name=f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            first_name=user_data.get("first_name", ""),
            last_name=user_data.get("last_name", ""),
            auth_method="saml",
            hashed_password=None,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(
        data={"sub": user.email, "v": user.token_version, "method": "saml"},
        org_id=org_id,
    )

    audit_log = AuditLog(
        org_id=org_id,
        actor_id=user.id,
        action="sso_login",
        resource_type="user",
        resource_id=str(user.id),
        changes={"method": "saml"},
    )
    db.add(audit_log)
    db.commit()

    return {"access_token": access_token, "user_id": str(user.id)}


@router.post("/oauth/callback")
async def oauth_callback(code: str, state: str, org_id: str, db: Session = Depends(get_db)):
    """Handle OAuth2 callback from Auth0."""
    sso_config = db.query(SSOConfig).filter(SSOConfig.org_id == org_id).first()
    if not sso_config or sso_config.sso_method != "oauth2":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth2 not configured")

    session = db.query(SSOSession).filter(SSOSession.state == state, SSOSession.org_id == org_id).first()
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid state")

    token_url = f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token"
    payload = {
        "client_id": os.getenv("AUTH0_CLIENT_ID"),
        "client_secret": os.getenv("AUTH0_CLIENT_SECRET"),
        "code": code,
        "redirect_uri": f"{os.getenv('AUTH0_OAUTH_CALLBACK_URL')}?org_id={org_id}",
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, json=payload, timeout=20.0)
        token_data = resp.json()
        if resp.status_code != 200 or "access_token" not in token_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to exchange OAuth2 code")

        user_info_url = f"https://{os.getenv('AUTH0_DOMAIN')}/userinfo"
        user_resp = await client.get(
            user_info_url,
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
            timeout=20.0,
        )
        user_info = user_resp.json()

    user = db.query(User).filter(User.email == user_info.get("email", "")).first()
    if not user:
        if not sso_config.auto_provision:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not exist")

        user = User(
            org_id=org_id,
            email=user_info.get("email", ""),
            name=f"{user_info.get('given_name', '')} {user_info.get('family_name', '')}".strip(),
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
            auth_method="oauth2",
            hashed_password=None,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    jwt_token = create_access_token(
        data={"sub": user.email, "v": user.token_version, "method": "oauth2"},
        org_id=org_id,
    )

    audit_log = AuditLog(
        org_id=org_id,
        actor_id=user.id,
        action="sso_login",
        resource_type="user",
        resource_id=str(user.id),
        changes={"method": "oauth2"},
    )
    db.add(audit_log)
    db.commit()

    return {"access_token": jwt_token, "user_id": str(user.id)}


# ── Forgot Password ───────────────────────────────────────────────────────────

@router.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password(request: Request, background_tasks: BackgroundTasks, data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Password reset endpoint."""
    email = _normalize_email(data.email)
    logger.info(f"[FORGOT-PWD] Request for: {email}")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        logger.warning(f"[FORGOT-PWD] No account found for: {email}")
    elif not user.is_active:
        logger.warning(f"[FORGOT-PWD] Account inactive: {email}")
    else:
        otp = _generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

        v = db.query(ForgotPasswordVerification).filter(ForgotPasswordVerification.user_id == user.id).first()
        if v:
            v.otp_hash = _hash_otp(otp)
            v.expires_at = expires_at
            v.created_at = datetime.utcnow()
            v.attempt_count = 0
        else:
            db.add(ForgotPasswordVerification(
                user_id=user.id,
                otp_hash=_hash_otp(otp),
                expires_at=expires_at,
            ))

        db.commit()


        # Send reset OTP email in background
        background_tasks.add_task(mailer.send_otp, email, otp, "Password Reset")

    msg = "If an account with that email exists, a reset code has been sent."
    return {"message": msg}


@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(request: Request, data: ForgotPasswordReset, db: Session = Depends(get_db)):
    """Update password after OTP verification."""
    email = _normalize_email(data.email)
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="Invalid request.")

    v = db.query(ForgotPasswordVerification).filter(ForgotPasswordVerification.user_id == user.id).first()
    
    # Verify OTP exists and hasn't expired
    if not v or datetime.utcnow() > v.expires_at:
        if v:
            db.delete(v)
            db.commit()
        raise HTTPException(status_code=400, detail="Reset code expired. Please request a new one.")

    # Check attempt limit
    if v.attempt_count >= OTP_MAX_ATTEMPTS:
        db.delete(v)
        db.commit()
        raise HTTPException(status_code=429, detail="Too many attempts. Please request a new reset code.")

    # Verify OTP
    if v.otp_hash != _hash_otp(data.otp):
        v.attempt_count += 1
        db.commit()
        remaining = OTP_MAX_ATTEMPTS - v.attempt_count
        raise HTTPException(status_code=400, detail=f"Invalid code. {remaining} attempts remaining.")

    # REVOCATION: increment token_version to invalidate all existing sessions instantly
    user.hashed_password = get_password_hash(data.new_password)
    user.token_version = user.token_version + 1
    db.query(LoginVerification).filter(LoginVerification.user_id == user.id).delete()
    # Delete password reset verification record
    if v:
        db.delete(v)
    db.add(Activity(user_id=user.id, action_type="PWD_RESET", description="Password reset"))
    db.commit()
    logger.info(f"[RESET-PWD] Password updated for {email}")
    return {"message": "Password updated successfully. Please log in with your new password."}
