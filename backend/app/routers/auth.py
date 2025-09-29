from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta

from ..database import get_session
from ..models import User
from ..auth import (
    verify_password, 
    create_access_token, 
    get_current_active_user,
    get_password_hash
)
from ..services import UserService
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    referrer_id: Optional[int] = None
    is_active: bool = True


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    referrer_id: Optional[int] = None
    package_tier: Optional[str] = None
    purchased_at: Optional[str] = None
    created_at: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class ReferralLinkResponse(BaseModel):
    referral_link: str
    referral_code: str


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """Register a new user"""
    try:
        user = UserService.create_user(
            session=session,
            email=user_data.email,
            full_name=user_data.full_name,
            password=user_data.password,
            referrer_id=user_data.referrer_id
        )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            referrer_id=user.referrer_id,
            package_tier=user.package_tier,
            purchased_at=user.purchased_at.isoformat() if user.purchased_at else None,
            created_at=user.created_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """Login user and return access token"""
    # Get user by email (OAuth2PasswordRequestForm uses 'username' field for email)
    user = UserService.get_user_by_email(session, form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        referrer_id=user.referrer_id,
        package_tier=user.package_tier,
        purchased_at=user.purchased_at.isoformat() if user.purchased_at else None,
        created_at=user.created_at.isoformat()
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        referrer_id=current_user.referrer_id,
        package_tier=current_user.package_tier,
        purchased_at=current_user.purchased_at.isoformat() if current_user.purchased_at else None,
        created_at=current_user.created_at.isoformat()
    )


@router.get("/referral-link", response_model=ReferralLinkResponse)
async def get_referral_link(
    current_user: User = Depends(get_current_active_user)
):
    """Get user's referral link"""
    base_url = "http://localhost:5173"  # This should come from config
    referral_link = f"{base_url}/signup?ref={current_user.id}"
    
    return ReferralLinkResponse(
        referral_link=referral_link,
        referral_code=str(current_user.id)
    )