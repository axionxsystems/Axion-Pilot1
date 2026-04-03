from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.settings import PlatformSettings
from app.models.user import User
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/admin/infrastructure", tags=["admin-infrastructure"])

# --- Models ---
class ServiceStatus(BaseModel):
    id: str
    name: str
    status: str # "active", "inactive", "error"
    last_updated: str
    usage_metrics: Optional[Dict[str, Any]] = None
    config_schema: List[Dict[str, Any]] # For frontend UI building

class ConfigUpdate(BaseModel):
    service_id: str
    config: Dict[str, Any]

class RotateKeyRequest(BaseModel):
    service_id: str

# --- Middleware check for Admin ---
async def get_current_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have admin privileges"
        )
    return current_user

# --- Routes ---

@router.get("/status", response_model=List[ServiceStatus])
async def get_infrastructure_status(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Get the status of all external services.
    Important: Secrets are NEVER returned here.
    """
    services = [
        {"id": "ai_openai", "name": "OpenAI / Claude AI", "key": "AI_CONFIG"},
        {"id": "email_service", "name": "SendGrid / SMTP Email", "key": "EMAIL_CONFIG"},
        {"id": "sms_service", "name": "Twilio SMS", "key": "SMS_CONFIG"},
        {"id": "storage_service", "name": "AWS S3 / Supabase Storage", "key": "STORAGE_CONFIG"},
    ]

    results = []
    for s in services:
        setting = db.query(PlatformSettings).filter(PlatformSettings.setting_key == s["key"]).first()
        
        status_val = "inactive"
        last_updated = "Never"
        metrics = {}
        
        if setting:
            status_val = "active" if setting.setting_value.get("is_enabled") else "inactive"
            last_updated = setting.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            metrics = setting.setting_value.get("metrics", {})

        # Define schema for the UI to know what fields to show (without values)
        schema = []
        if s["id"] == "ai_openai":
            schema = [
                {"field": "api_key", "label": "API Key", "type": "password", "placeholder": "sk-..."},
                {"field": "default_model", "label": "Default Model", "type": "text", "placeholder": "gpt-4-turbo"},
                {"field": "is_enabled", "label": "Service Enabled", "type": "boolean"}
            ]
        elif s["id"] == "email_service":
            schema = [
                {"field": "smtp_server", "label": "SMTP Server", "type": "text"},
                {"field": "smtp_user", "label": "User", "type": "text"},
                {"field": "smtp_pass", "label": "Password/Key", "type": "password"},
                {"field": "is_enabled", "label": "Service Enabled", "type": "boolean"}
            ]
        elif s["id"] == "sms_service":
            schema = [
                {"field": "account_sid", "label": "Twilio SID", "type": "text"},
                {"field": "auth_token", "label": "Auth Token", "type": "password"},
                {"field": "is_enabled", "label": "Service Enabled", "type": "boolean"}
            ]
        elif s["id"] == "storage_service":
            schema = [
                {"field": "access_key", "label": "Access Key ID", "type": "text"},
                {"field": "secret_key", "label": "Secret Access Key", "type": "password"},
                {"field": "bucket_name", "label": "Bucket Name", "type": "text"},
                {"field": "is_enabled", "label": "Service Enabled", "type": "boolean"}
            ]

        results.append({
            "id": s["id"],
            "name": s["name"],
            "status": status_val,
            "last_updated": last_updated,
            "usage_metrics": metrics,
            "config_schema": schema
        })

    return results

@router.put("/config")
async def update_infrastructure_config(
    update: ConfigUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Update configuration for a service.
    """
    key_map = {
        "ai_openai": "AI_CONFIG",
        "email_service": "EMAIL_CONFIG",
        "sms_service": "SMS_CONFIG",
        "storage_service": "STORAGE_CONFIG"
    }
    
    setting_key = key_map.get(update.service_id)
    if not setting_key:
        raise HTTPException(status_code=400, detail="Invalid service ID")
    
    setting = db.query(PlatformSettings).filter(PlatformSettings.setting_key == setting_key).first()
    
    if not setting:
        setting = PlatformSettings(setting_key=setting_key, setting_value={})
        db.add(setting)
    
    # Merge existing value to preserve metrics or other non-secret metadata
    current_value = setting.setting_value or {}
    new_value = {**current_value, **update.config}
    
    setting.setting_value = new_value
    setting.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": f"Successfully updated {update.service_id} configuration"}

@router.post("/rotate")
async def rotate_service_keys(
    request: RotateKeyRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Rotate API keys logic. (Simulated workflow)
    """
    # Logic to invalidate old keys and generate new ones if the external provider supports it.
    # For many external APIs, this involves notifying the admin or triggering an automated rotation flow.
    
    return {"message": f"Key rotation sequence initiated for {request.service_id}"}
