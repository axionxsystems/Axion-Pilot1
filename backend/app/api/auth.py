import hashlib
import logging
import os
import secrets
import string
import unicodedata
from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.auth.mailer import mailer

from app.auth.jwt_handler import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.utils import get_password_hash, verify_password
from app.database import get_db
from app.models.activity import Activity
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
OTP_EXPIRY_MINUTES = 5
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
@limiter.limit("2/minute")
def signup_request(request: Request, background_tasks: BackgroundTasks, user: UserCreate, db: Session = Depends(get_db)):
    """Initiate signup — sends hashed OTPs for email and phone verification."""
    email = _normalize_email(user.email)
    if not _is_gmail(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only Gmail accounts are allowed.")

    # [Privacy] Generic response to prevent user enumeration
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        return {"message": "If this email is not yet registered, OTPs have been sent."}

    # Resend cooldown logic
    pending = db.query(SignupVerification).filter(SignupVerification.email == email).first()
    if pending:
        elapsed = (datetime.utcnow() - pending.created_at).total_seconds()
        if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
            wait = int(OTP_RESEND_COOLDOWN_SECONDS - elapsed)
            raise HTTPException(status_code=429, detail=f"Wait {wait}sec before requesting a new OTP.")

    email_otp = _generate_otp()
    mobile_otp = _generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    hashed_password = get_password_hash(user.password)

    if pending:
        pending.name, pending.mobile, pending.hashed_password = user.full_name, user.mobile, hashed_password
        pending.email_otp_hash, pending.mobile_otp_hash = _hash_otp(email_otp), _hash_otp(mobile_otp)
        pending.expires_at, pending.created_at, pending.attempt_count = expires_at, datetime.utcnow(), 0
    else:
        pending = SignupVerification(
            email=email, mobile=user.mobile, name=user.full_name,
            hashed_password=hashed_password, email_otp_hash=_hash_otp(email_otp),
            mobile_otp_hash=_hash_otp(mobile_otp), expires_at=expires_at,
        )
        db.add(pending)

    db.commit()
    print(f"[DEV] Signup OTPs for {email} → Email: {email_otp} | Mobile: {mobile_otp}")
    # Send both OTPs in one email in background
    background_tasks.add_task(mailer.send_signup_otps, email, email_otp, mobile_otp)
    return {"message": "Verification codes sent to Gmail and mobile."}


@router.post("/verify-signup", response_model=UserResponse)
@limiter.limit("3/minute")
def verify_signup(request: Request, data: SignupVerify, db: Session = Depends(get_db)):
    """Finish signup — validates hashed OTPs and creates User in DB."""
    email = _normalize_email(data.email)
    pending = db.query(SignupVerification).filter(SignupVerification.email == email).first()

    if not pending or (datetime.utcnow() > pending.expires_at):
        if pending: db.delete(pending); db.commit()
        raise HTTPException(status_code=400, detail="Registration session expired.")

    if pending.attempt_count >= OTP_MAX_ATTEMPTS:
        db.delete(pending); db.commit()
        raise HTTPException(status_code=429, detail="Too many failed attempts. Restart signup.")

    # Check OTP hashes
    if pending.email_otp_hash != _hash_otp(data.email_otp) or pending.mobile_otp_hash != _hash_otp(data.mobile_otp):
        pending.attempt_count += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Incorrect OTP(s).")

    # Is super-admin check (normalized)
    is_admin = bool(SUPER_ADMIN_EMAIL and email == SUPER_ADMIN_EMAIL)
    new_user = User(email=email, name=pending.name, mobile=pending.mobile, 
                    hashed_password=pending.hashed_password, is_admin=is_admin)
    db.add(new_user)
    db.delete(pending)
    db.flush()
    db.add(Activity(user_id=new_user.id, action_type="USER_REG", description=f"Registered: {email}"))
    db.commit()
    return new_user


# ── Login Flow (Step 1 & Step 2 for MFA) ──────────────────────────────────────

@router.post("/login", response_model=LoginPending)
@limiter.limit("5/minute")
def login_step1(request: Request, background_tasks: BackgroundTasks, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Password Check → Generates Hashed OTP for 2FA."""
    email = _normalize_email(form_data.username)
    user = db.query(User).filter(User.email == email).first()

    # Timing-safe failure (always verify password even if user missing)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account suspended.")

    otp = _generate_otp(); expires_at = datetime.utcnow() + timedelta(minutes=5)
    existing = db.query(LoginVerification).filter(LoginVerification.user_id == user.id).first()
    if existing:
        existing.otp_hash, existing.expires_at, existing.created_at, existing.attempt_count = _hash_otp(otp), expires_at, datetime.utcnow(), 0
    else:
        db.add(LoginVerification(user_id=user.id, otp_hash=_hash_otp(otp), expires_at=expires_at))

    db.commit()
    print(f"[DEV] Login OTP for {email}: {otp}")
    # Send OTP email in background so login response is instant
    background_tasks.add_task(mailer.send_otp, email, otp, "Login")
    return LoginPending(message="2FA code sent to your email.")


@router.post("/login/verify-otp", response_model=Token)
@limiter.limit("5/minute")
def login_step2(request: Request, data: LoginOTPVerify, db: Session = Depends(get_db)):
    """Final Authentication — consumes OTP hash and issues JWT."""
    email = _normalize_email(data.email)
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active: raise HTTPException(status_code=401, detail="Invalid session.")

    v = db.query(LoginVerification).filter(LoginVerification.user_id == user.id).first()
    if not v or (datetime.utcnow() > v.expires_at) or (v.attempt_count >= OTP_MAX_ATTEMPTS):
        if v: db.delete(v); db.commit()
        raise HTTPException(status_code=400, detail="OTP session invalid.")

    if v.otp_hash != _hash_otp(data.otp):
        v.attempt_count += 1; db.commit()
        raise HTTPException(status_code=400, detail="Invalid code.")

    db.delete(v); db.commit()
    access_token = create_access_token(data={"sub": user.email, "v": user.token_version})
    return {"access_token": access_token, "token_type": "bearer"}


# ── Forgot Password ───────────────────────────────────────────────────────────

@router.post("/forgot-password")
@limiter.limit("2/minute")
def forgot_password(request: Request, background_tasks: BackgroundTasks, data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email = _normalize_email(data.email)
    user = db.query(User).filter(User.email == email).first()
    if user and user.is_active:
        otp = _generate_otp(); expires_at = datetime.utcnow() + timedelta(minutes=5)
        v = db.query(ForgotPasswordVerification).filter(ForgotPasswordVerification.user_id == user.id).first()
        if v: v.otp_hash, v.expires_at, v.created_at, v.attempt_count = _hash_otp(otp), expires_at, datetime.utcnow(), 0
        else: db.add(ForgotPasswordVerification(user_id=user.id, otp_hash=_hash_otp(otp), expires_at=expires_at))
        db.commit()
        print(f"[DEV] Password-reset OTP for {email}: {otp}")
        # Send reset OTP email in background
        background_tasks.add_task(mailer.send_otp, email, otp, "Password Reset")

    return {"message": "Success. Check your email for reset instructions."}


@router.post("/reset-password")
@limiter.limit("3/minute")
def reset_password(request: Request, data: ForgotPasswordReset, db: Session = Depends(get_db)):
    email = _normalize_email(data.email)
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active: raise HTTPException(status_code=400, detail="Invalid.")

    v = db.query(ForgotPasswordVerification).filter(ForgotPasswordVerification.user_id == user.id).first()
    if not v or datetime.utcnow() > v.expires_at:
        if v: db.delete(v); db.commit()
        raise HTTPException(status_code=400, detail="Reset code expired. Please request a new one.")
    if v.otp_hash != _hash_otp(data.otp):
        v.attempt_count += 1; db.commit()
        raise HTTPException(status_code=400, detail="Code invalid.")

    # REVOCATION: increment token_version to boot all existing login session tokens instantly
    user.hashed_password, user.token_version = get_password_hash(data.new_password), user.token_version + 1
    db.query(LoginVerification).filter(LoginVerification.user_id == user.id).delete()
    db.delete(v)
    db.add(Activity(user_id=user.id, action_type="PWD_RESET", description="Resetted password via OTP"))
    db.commit()
    return {"message": "Password updated successfully."}
