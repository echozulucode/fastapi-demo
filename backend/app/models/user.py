"""User ORM model and Pydantic schemas."""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.token import PersonalAccessToken


# ---------------------------------------------------------------------------
# ORM model
# ---------------------------------------------------------------------------

class User(Base):
    """User database table."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_ldap_user: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    tokens: Mapped[List["PersonalAccessToken"]] = relationship(back_populates="user")


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    full_name: str
    is_active: bool = True
    is_admin: bool = False
    is_ldap_user: bool = False


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 100:
            raise ValueError("Password must be 8–100 characters")
        return v


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
