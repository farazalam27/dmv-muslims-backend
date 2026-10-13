from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from db.models import User
from config import settings
import jwt
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Permissions matrix
PERMISSIONS = {
    "user": [
        "view_public_data",
        "save_favorites",
        "submit_listing",
        "rsvp_event",
    ],
    "business_owner": [
        "submit_listing",
        "claim_business",
        "edit_own_business",
        "update_hours",
    ],
    "event_organizer": [
        "create_event",
        "edit_own_event",
        "delete_own_event",
    ],
    "masjid_rep": [
        "update_prayer_times",
        "post_announcement",
        "manage_masjid_events",
    ],
    "admin": [
        "approve_submissions",
        "reject_submissions",
        "feature_content",
        "ban_users",
        "trigger_scrapers",
        "view_analytics",
    ],
}

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get the current user from the JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Get user from database
    user = await db.query(User).filter(User.supabase_id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

async def require_permission(required: str):
    """Dependency for protecting endpoints with specific permissions"""
    async def check(user: User = Depends(get_current_user)):
        if required not in PERMISSIONS.get(user.role, []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        return user
    return check