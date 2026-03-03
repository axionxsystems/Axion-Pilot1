from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse
from app.models.user import User
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserPasswordUpdate
from app.auth.utils import verify_password, get_password_hash

@router.put("/me/password")
def update_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    # Update to new password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}
