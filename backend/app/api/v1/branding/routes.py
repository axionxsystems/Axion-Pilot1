import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth.org_dependencies import require_org_admin, require_org_member
from app.database import get_db
from app.models.branding import OrgBranding
from app.schemas.branding import BrandingResponse, BrandingUpdate

router = APIRouter(prefix="/{org_id}/branding")


def _get_branding(db: Session, org_id: str) -> Optional[OrgBranding]:
    return db.query(OrgBranding).filter(OrgBranding.org_id == org_id).first()


def _build_logo_url(request: Request, org_id: str) -> Optional[str]:
    return request.url_for("get_branding_logo", org_id=org_id)


@router.get("", response_model=BrandingResponse)
def get_branding(
    org_id: str,
    request: Request,
    _ctx=Depends(require_org_member),
    db: Session = Depends(get_db),
):
    branding = _get_branding(db, org_id)
    if not branding:
        return BrandingResponse(
            brand_name=None,
            primary_color=None,
            secondary_color=None,
            accent_color=None,
            support_email=None,
            logo_filename=None,
            logo_url=None,
        )

    return BrandingResponse(
        brand_name=branding.brand_name,
        primary_color=branding.primary_color,
        secondary_color=branding.secondary_color,
        accent_color=branding.accent_color,
        support_email=branding.support_email,
        logo_filename=branding.logo_filename,
        logo_url=_build_logo_url(request, org_id) if branding.logo_data else None,
    )


@router.patch("", response_model=BrandingResponse)
def update_branding(
    org_id: str,
    updates: BrandingUpdate,
    request: Request,
    db: Session = Depends(get_db),
    _ctx=Depends(require_org_admin),
):
    branding = _get_branding(db, org_id)
    if not branding:
        branding = OrgBranding(org_id=org_id)
        db.add(branding)

    if updates.brand_name is not None:
        branding.brand_name = updates.brand_name.strip() if updates.brand_name else None
    if updates.primary_color is not None:
        branding.primary_color = updates.primary_color
    if updates.secondary_color is not None:
        branding.secondary_color = updates.secondary_color
    if updates.accent_color is not None:
        branding.accent_color = updates.accent_color
    if updates.support_email is not None:
        branding.support_email = updates.support_email

    db.commit()
    db.refresh(branding)

    return BrandingResponse(
        brand_name=branding.brand_name,
        primary_color=branding.primary_color,
        secondary_color=branding.secondary_color,
        accent_color=branding.accent_color,
        support_email=branding.support_email,
        logo_filename=branding.logo_filename,
        logo_url=_build_logo_url(request, org_id) if branding.logo_data else None,
    )


@router.post("/logo", response_model=BrandingResponse)
async def upload_branding_logo(
    org_id: str,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _ctx=Depends(require_org_admin),
):
    accepted_types = ["image/png", "image/jpeg", "image/webp", "image/svg+xml"]
    if file.content_type not in accepted_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Logo must be PNG, JPEG, WEBP, or SVG.",
        )

    data = await file.read()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded logo is empty.")

    branding = _get_branding(db, org_id)
    if not branding:
        branding = OrgBranding(org_id=org_id)
        db.add(branding)

    branding.logo_filename = file.filename
    branding.logo_content_type = file.content_type
    branding.logo_data = data

    db.commit()
    db.refresh(branding)

    return BrandingResponse(
        brand_name=branding.brand_name,
        primary_color=branding.primary_color,
        secondary_color=branding.secondary_color,
        accent_color=branding.accent_color,
        support_email=branding.support_email,
        logo_filename=branding.logo_filename,
        logo_url=_build_logo_url(request, org_id) if branding.logo_data else None,
    )


@router.delete("/logo")
def delete_branding_logo(
    org_id: str,
    _ctx=Depends(require_org_admin),
    db: Session = Depends(get_db),
):
    branding = _get_branding(db, org_id)
    if not branding or not branding.logo_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No logo uploaded for this organization.")

    branding.logo_filename = None
    branding.logo_content_type = None
    branding.logo_data = None
    db.commit()
    return {"message": "Logo deleted successfully."}


@router.get("/logo", name="get_branding_logo")
def get_branding_logo(
    org_id: str,
    _ctx=Depends(require_org_member),
    db: Session = Depends(get_db),
):
    branding = _get_branding(db, org_id)
    if not branding or not branding.logo_data or not branding.logo_content_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branding logo not found.")

    return StreamingResponse(
        io.BytesIO(branding.logo_data),
        media_type=branding.logo_content_type,
        headers={"Content-Disposition": f"inline; filename=\"{branding.logo_filename or 'logo'}\""},
    )
