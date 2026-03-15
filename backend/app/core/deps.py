"""FastAPI dependencies for authentication and database."""
import secrets
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_session
from app.core.security import decode_access_token, get_password_hash
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Primary auth dependency
# ---------------------------------------------------------------------------

def get_current_user(
    jwt_token: Optional[str] = Depends(oauth2_scheme),
    bearer_credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    session: Session = Depends(get_session),
) -> User:
    """
    Resolve the current user from one of three auth methods (in priority order):
      1. Personal Access Token  (Bearer prefix: ``pat_``)
      2. Keycloak RS256 JWT     (when AUTH_MODE=keycloak)
      3. Local HS256 JWT        (when AUTH_MODE=local)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    raw_token = (
        bearer_credentials.credentials if bearer_credentials else jwt_token
    )

    # 1. PAT
    if raw_token and raw_token.startswith("pat_"):
        user = _authenticate_with_pat(raw_token, session)
        if user:
            return user

    # 2. Keycloak JWT
    if raw_token and settings.AUTH_MODE == "keycloak":
        user = _authenticate_with_keycloak_jwt(raw_token, session)
        if user:
            return user

    # 3. Local JWT (always available as fallback / primary in local mode)
    if jwt_token:
        user = _authenticate_with_local_jwt(jwt_token, session)
        if user:
            return user

    raise credentials_exception


# ---------------------------------------------------------------------------
# Role guards
# ---------------------------------------------------------------------------

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _authenticate_with_local_jwt(token: str, session: Session) -> Optional[User]:
    payload = decode_access_token(token)
    if payload is None:
        return None
    user_id = payload.get("sub")
    if user_id is None:
        return None
    user = session.get(User, int(user_id))
    if user is None or not user.is_active:
        return None
    return user


def _authenticate_with_keycloak_jwt(token: str, session: Session) -> Optional[User]:
    from app.core.keycloak import keycloak_validator

    claims = keycloak_validator.validate_token(token)
    if claims is None:
        return None

    email: Optional[str] = claims.get("email") or claims.get("preferred_username")
    if not email:
        return None

    user = session.execute(select(User).where(User.email == email)).scalars().first()

    realm_roles: list[str] = claims.get("realm_access", {}).get("roles", [])
    is_admin = "admin" in realm_roles

    if user is None:
        # Auto-provision on first Keycloak login
        user = User(
            email=email,
            full_name=claims.get("name") or claims.get("preferred_username", email),
            hashed_password=get_password_hash(secrets.token_hex(32)),
            is_active=True,
            is_admin=is_admin,
            is_ldap_user=False,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    elif user.is_admin != is_admin:
        # Keep admin role in sync with Keycloak realm roles
        user.is_admin = is_admin
        session.add(user)
        session.commit()
        session.refresh(user)

    if not user.is_active:
        return None

    return user


def _authenticate_with_pat(token: str, session: Session) -> Optional[User]:
    from app.core.token_security import hash_token, is_token_expired
    from app.models.token import PersonalAccessToken

    token_hash = hash_token(token)
    db_token = session.execute(
        select(PersonalAccessToken).where(PersonalAccessToken.token_hash == token_hash)
    ).scalars().first()

    if not db_token or not db_token.is_active:
        return None
    if is_token_expired(db_token.expires_at):
        return None

    db_token.last_used_at = datetime.utcnow()
    session.add(db_token)
    session.commit()

    user = session.get(User, db_token.user_id)
    if user is None or not user.is_active:
        return None
    return user
