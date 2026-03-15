"""Authentication API endpoints."""
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_session
from app.core.deps import get_current_user
from app.core.security import (
    create_access_token,
    get_password_hash,
    validate_password_strength,
)
from app.crud import user as crud_user
from app.models.user import User, UserCreate, UserInDB

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    session: Session = Depends(get_session),
):
    """
    Register a new local user account.

    Not available when AUTH_MODE=keycloak (user provisioning is automatic on first login).
    """
    if settings.AUTH_MODE == "keycloak":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Self-registration is disabled; accounts are managed via Keycloak.",
        )

    if crud_user.get_user_by_email(session, user_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    is_valid, error_message = validate_password_strength(user_create.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )

    return crud_user.create_user(session, user_create)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
):
    """
    Login with email + password to receive a local HS256 JWT.

    When AUTH_MODE=keycloak, clients should authenticate via the Keycloak OIDC
    flow instead. This endpoint remains available for backwards-compat PAT flows
    and direct API access in local mode.
    """
    user = None

    # LDAP path (deprecated – only runs when explicitly enabled and AUTH_MODE=local)
    if settings.AUTH_MODE == "local" and settings.LDAP_ENABLED:
        from app.core.ldap_service import ldap_service

        success, ldap_user_info, _ = ldap_service.authenticate(
            form_data.username, form_data.password
        )
        if success and ldap_user_info:
            user = crud_user.get_user_by_email(session, ldap_user_info["email"])
            if not user:
                user_create = UserCreate(
                    email=ldap_user_info["email"],
                    full_name=ldap_user_info["full_name"] or ldap_user_info["username"],
                    password=form_data.password,
                    is_active=True,
                    is_admin=ldap_user_info.get("is_admin", False),
                    is_ldap_user=True,
                )
                user = crud_user.create_user(session, user_create)
            else:
                user.full_name = ldap_user_info["full_name"] or user.full_name
                user.is_admin = ldap_user_info.get("is_admin", user.is_admin)
                user.is_ldap_user = True
                session.add(user)
                session.commit()
                session.refresh(user)

    if not user:
        user = crud_user.authenticate_user(session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "is_admin": user.is_admin},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout current user (client-side token removal)."""
    return {"message": "Successfully logged out", "user": current_user.email}


@router.get("/me", response_model=UserInDB)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return current_user


@router.post("/test-token", response_model=UserInDB)
async def test_token(current_user: User = Depends(get_current_user)):
    """Verify an access token is valid and return the associated user."""
    return current_user


# ---------------------------------------------------------------------------
# LDAP endpoints (deprecated – returns 410 when AUTH_MODE=keycloak)
# ---------------------------------------------------------------------------

@router.get("/ldap/health")
async def ldap_health_check():
    """
    Check LDAP connectivity.

    Deprecated: Keycloak handles LDAP/AD federation natively.
    Returns 410 Gone when AUTH_MODE=keycloak.
    """
    if settings.AUTH_MODE == "keycloak":
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="LDAP health check is deprecated; use Keycloak for directory integration.",
        )
    from app.core.ldap_service import ldap_service

    health = ldap_service.health_check()
    if not health.get("healthy", False):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health)
    return health


@router.get("/ldap/config")
async def ldap_config_info(current_user: User = Depends(get_current_user)):
    """
    Get sanitised LDAP configuration (admin only).

    Deprecated: Returns 410 Gone when AUTH_MODE=keycloak.
    """
    if settings.AUTH_MODE == "keycloak":
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="LDAP config endpoint is deprecated; LDAP is managed inside Keycloak.",
        )
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    from app.core.ldap_service import ldap_service

    config = ldap_service.config
    return {
        "enabled": config.enabled,
        "server": config.server,
        "port": config.port,
        "use_ssl": config.use_ssl,
        "use_ntlm": config.use_ntlm,
        "bind_dn": config.bind_dn,
        "search_base": config.search_base,
        "user_search_filter": config.user_search_filter,
        "admin_groups": config.admin_groups,
        "allowed_groups": config.allowed_groups,
        "timeout": config.timeout,
    }
