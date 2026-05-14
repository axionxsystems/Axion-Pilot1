from pathlib import Path
import os
from dotenv import load_dotenv
# Use absolute path relative to this file to ensure .env is found from any CWD
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import logging
from fastapi import FastAPI, Request, status, Body
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# from app.utils.ollama_generator import generate_code, generate_documentation, generate_viva_questions


from app.database import engine, Base
from app.api import auth, users, projects, project, viva, passkey, admin
from app.api import v1
from app.limiter import limiter
from app.middleware.tenant import TenantMiddleware

# ── Ensure all models are imported so create_all sees them ────────────────────
import app.models.organization  # noqa: F401 — registers Organization, Subscription, AuditLog
import app.models.stripe_billing  # noqa: F401 — registers Stripe billing models
import app.models.api_key  # noqa: F401 — registers APIKey model
import app.models.rate_limit  # noqa: F401 — registers RateLimitLog model

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# ── DB tables ─────────────────────────────────────────────────────────────────
# SQLite: Creates the database file on first run
Base.metadata.create_all(bind=engine)

# ── Environment ───────────────────────────────────────────────────────────────
ENV = os.environ.get("ENV", "development")
IS_PROD = ENV == "production"

# ── Security headers middleware ────────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        # CSP: restrict resource origins for security
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        if IS_PROD:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AxionX API",
    version="1.1.0",
    docs_url="/docs" if not IS_PROD else None,
    redoc_url="/redoc" if not IS_PROD else None,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Restricted Origins: no wildcards in production
# Allow all origins in dev for easier testing from different hosts/IPs
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "")
allowed_origins = (
    [o.strip() for o in _raw_origins.split(",") if o.strip()]
    if IS_PROD and _raw_origins
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # Wildcard origin ("*") cannot be used with allow_credentials=True
    allow_credentials=False if not IS_PROD else True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Middlewares & Handlers ────────────────────────────────────────────────────
# The middlewares listed below are WRAPPED by the CORS middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SecurityHeadersMiddleware)

# TenantMiddleware: extracts org_id from JWT and stores in context var.
# Registered AFTER SecurityHeaders so it runs on the inner side of the stack.
_JWT_SECRET = os.environ.get("SECRET_KEY", "")
app.add_middleware(TenantMiddleware, secret_key=_JWT_SECRET)

# RateLimitMiddleware: enforces rate limits for API keys
from app.middleware.rate_limiting import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(passkey.router, prefix="/api/auth", tags=["Passkey"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(project.router, prefix="/project", tags=["Project Generation"])
app.include_router(viva.router, prefix="/api/viva", tags=["Viva"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(v1.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "ProjectPilot API is running", "env": ENV}


@app.get("/health")
async def health():
    """Health check endpoint for auto-heal platform checks."""
    return {"status": "ok", "env": ENV}


# @app.post("/api/projects/ollama-generate", tags=["Ollama"])
# async def generate_project(
#     project_title: str = Body(...),
#     project_description: str = Body(...),
#     language: str = Body(...),
#     difficulty: str = Body(...)
# ):
#     """
#     Main endpoint to generate complete project
#     
#     What this does:
#     1. Student submits project details via frontend
#     2. This function gets called
#     3. Generates code, docs, and viva questions
#     4. Returns everything as JSON
#     """
#     
#     try:
#         # STEP 1: Create prompt for code generation
#         code_prompt = f"""
#         Generate a complete, production-ready {language} project.
#         
#         Title: {project_title}
#         Description: {project_description}
#         Difficulty: {difficulty}
#         
#         Requirements:
#         - All code must be complete and functional
#         - Include all necessary files (config, dependencies, setup)
#         - Code must run immediately when student downloads it
#         - Include comments on complex parts
#         - Follow best practices for {language}
#         
#         Generate EVERY file needed, not just snippets.
#         """
#         
#         # STEP 2: Call Ollama to generate code
#         print(f"Generating code for {project_title}...")
#         code = generate_code(code_prompt)
#         
#         if code.startswith("Error"):
#             return {"error": code}
#         
#         # STEP 3: Generate documentation
#         print(f"Generating documentation...")
#         documentation = generate_documentation(code, project_title)
#         
#         # STEP 4: Generate viva questions
#         print(f"Generating viva questions...")
#         viva = generate_viva_questions(code, project_description)
#         
#         # STEP 5: Return everything
#         return {
#             "success": True,
#             "project_title": project_title,
#             "code": code,
#             "documentation": documentation,
#             "viva_questions": viva
#         }
#     
#     except Exception as e:
#         return {"error": f"Project generation failed: {str(e)}"}



