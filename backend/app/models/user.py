"""User model and schemas."""
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Base user model with shared attributes."""
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str = Field(max_length=255)
    is_active: bool = True
    is_admin: bool = False


class User(UserBase, table=True):
    """User database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(min_length=8, max_length=100)


class UserUpdate(SQLModel):
    """Schema for updating a user."""
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=100)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserInDB(UserBase):
    """User model as stored in database (for responses)."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
