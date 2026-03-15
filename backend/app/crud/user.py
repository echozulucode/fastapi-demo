"""CRUD operations for users."""
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserCreate, UserUpdate


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return session.execute(select(User).where(User.email == email)).scalars().first()


def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


def get_all_users(session: Session) -> list[User]:
    return list(session.execute(select(User)).scalars().all())


def create_user(session: Session, user_create: UserCreate) -> User:
    db_user = User(
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=get_password_hash(user_create.password),
        is_active=user_create.is_active,
        is_admin=user_create.is_admin,
        is_ldap_user=getattr(user_create, "is_ldap_user", False),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(session: Session, user: User, user_update: UserUpdate) -> User:
    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def delete_user(session: Session, user: User) -> None:
    session.delete(user)
    session.commit()
