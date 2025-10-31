"""Authentication API endpoints."""
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.core.security import create_access_token, validate_password_strength
from app.core.deps import get_current_user
from app.crud import user as crud_user
from app.models.user import User, UserCreate, UserInDB
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    session: Session = Depends(get_session)
):
    """
    Register a new user.
    
    - **email**: Valid email address (must be unique)
    - **full_name**: User's full name
    - **password**: Strong password (min 8 chars, uppercase, lowercase, number)
    - **is_active**: Whether user is active (default: true)
    - **is_admin**: Whether user is admin (default: false)
    """
    # Check if user already exists
    existing_user = crud_user.get_user_by_email(session, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    is_valid, error_message = validate_password_strength(user_create.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Create user
    user = crud_user.create_user(session, user_create)
    
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    """
    Login with email and password to get an access token.
    
    - **username**: User's email address
    - **password**: User's password
    
    Returns JWT access token for authentication.
    """
    # Authenticate user (username field contains email)
    user = crud_user.authenticate_user(session, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "is_admin": user.is_admin},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user.
    
    Note: With JWT tokens, logout is typically handled client-side
    by removing the token. This endpoint is provided for API completeness.
    """
    return {
        "message": "Successfully logged out",
        "user": current_user.email
    }


@router.get("/me", response_model=UserInDB)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Requires: Valid JWT token
    """
    return current_user


@router.post("/test-token", response_model=UserInDB)
async def test_token(current_user: User = Depends(get_current_user)):
    """
    Test if the access token is valid.
    
    Returns current user if token is valid.
    """
    return current_user
