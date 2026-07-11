from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


class BrandingUpdate(BaseModel):
    brand_name: Optional[str] = Field(None, max_length=120)
    primary_color: Optional[str] = Field(None, min_length=7, max_length=7)
    secondary_color: Optional[str] = Field(None, min_length=7, max_length=7)
    accent_color: Optional[str] = Field(None, min_length=7, max_length=7)
    support_email: Optional[EmailStr] = None

    @field_validator("primary_color", "secondary_color", "accent_color")
    @classmethod
    def validate_color(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not _COLOR_RE.match(value):
            raise ValueError("Color must be a valid hex code like #1A2B3C")
        return value


class BrandingResponse(BaseModel):
    brand_name: Optional[str]
    primary_color: Optional[str]
    secondary_color: Optional[str]
    accent_color: Optional[str]
    support_email: Optional[str]
    logo_filename: Optional[str]
    logo_url: Optional[str]

    class Config:
        from_attributes = True
