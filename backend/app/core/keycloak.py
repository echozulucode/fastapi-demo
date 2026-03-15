"""Keycloak JWT validation via JWKS (RS256)."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx
import jwt

from app.core.config import settings

logger = logging.getLogger(__name__)


class KeycloakJWTValidator:
    """
    Validates Keycloak-issued RS256 JWTs by fetching and caching JWKS.

    Key cache is refreshed every hour, or immediately on an unknown `kid`.
    """

    def __init__(self) -> None:
        self.issuer = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}"
        self.jwks_uri = f"{self.issuer}/protocol/openid-connect/certs"
        self._jwks_cache: Optional[Dict] = None
        self._jwks_fetched_at: Optional[datetime] = None
        self._jwks_ttl = timedelta(hours=1)

    # ------------------------------------------------------------------
    # JWKS cache management
    # ------------------------------------------------------------------

    def _cache_valid(self) -> bool:
        return (
            self._jwks_cache is not None
            and self._jwks_fetched_at is not None
            and datetime.utcnow() - self._jwks_fetched_at < self._jwks_ttl
        )

    def _fetch_jwks(self) -> Dict:
        try:
            response = httpx.get(self.jwks_uri, timeout=10)
            response.raise_for_status()
            self._jwks_cache = response.json()
            self._jwks_fetched_at = datetime.utcnow()
            logger.info("Keycloak JWKS refreshed from %s", self.jwks_uri)
            return self._jwks_cache
        except Exception as exc:
            logger.error("Failed to fetch Keycloak JWKS: %s", exc)
            raise

    def _get_jwks(self) -> Dict:
        if not self._cache_valid():
            return self._fetch_jwks()
        return self._jwks_cache  # type: ignore[return-value]

    def _get_public_key(self, kid: Optional[str], *, force_refresh: bool = False):
        """Return the RSA public key matching `kid`, refreshing cache if needed."""
        jwks = self._fetch_jwks() if force_refresh else self._get_jwks()
        for k in jwks.get("keys", []):
            if k.get("kid") == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(k)
        return None

    # ------------------------------------------------------------------
    # Token validation
    # ------------------------------------------------------------------

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a Keycloak-issued JWT.

        Returns the decoded claims dict on success, or None on failure.
        """
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")

            key = self._get_public_key(kid)
            if key is None:
                # kid not found – try a single forced refresh
                key = self._get_public_key(kid, force_refresh=True)
            if key is None:
                logger.warning("No JWKS key found for kid=%s", kid)
                return None

            payload: Dict[str, Any] = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )

            if payload.get("iss") != self.issuer:
                logger.warning(
                    "JWT issuer mismatch: got %s, expected %s",
                    payload.get("iss"),
                    self.issuer,
                )
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.debug("Keycloak JWT expired")
            return None
        except jwt.PyJWTError as exc:
            logger.debug("Keycloak JWT validation failed: %s", exc)
            return None
        except Exception as exc:
            logger.error("Unexpected error validating Keycloak JWT: %s", exc)
            return None

    def warm_cache(self) -> bool:
        """Pre-fetch JWKS at application startup. Returns True on success."""
        try:
            self._fetch_jwks()
            return True
        except Exception:
            return False


# Singleton validator – instantiated once, reused across requests.
keycloak_validator = KeycloakJWTValidator()
