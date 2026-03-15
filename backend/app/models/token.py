"""Personal Access Token ORM model and Pydantic schemas."""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


# ---------------------------------------------------------------------------
# ORM model
# ---------------------------------------------------------------------------

class PersonalAccessToken(Base):
    """Personal Access Token database table."""
    __tablename__ = "personal_access_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    scopes: Mapped[str] = mapped_column(String(255), default="read", nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped[Optional["User"]] = relationship(back_populates="tokens")


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class TokenCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    scopes: str = "read"
    expires_in_days: Optional[int] = None


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    token: str
    scopes: str
    expires_at: Optional[datetime]
    created_at: datetime


class TokenInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    scopes: str
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    created_at: datetime
    is_active: bool
