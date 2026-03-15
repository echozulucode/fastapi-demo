"""Tests for Keycloak JWT validation (mocked JWKS)."""
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.keycloak import KeycloakJWTValidator


# ---------------------------------------------------------------------------
# Helpers: generate a throw-away RSA key pair for test tokens
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def rsa_key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


@pytest.fixture(scope="module")
def test_validator(rsa_key_pair):
    """A KeycloakJWTValidator pre-loaded with a mock JWKS."""
    _, public_key = rsa_key_pair
    public_pem = public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    jwk_dict = jwt.algorithms.RSAAlgorithm.to_jwk(public_key, as_dict=True)
    jwk_dict["kid"] = "test-key-id"
    jwk_dict["use"] = "sig"
    jwk_dict["alg"] = "RS256"

    validator = KeycloakJWTValidator.__new__(KeycloakJWTValidator)
    validator.issuer = "http://keycloak:8080/realms/fastapi-demo"
    validator.jwks_uri = "http://keycloak:8080/realms/fastapi-demo/protocol/openid-connect/certs"
    validator._jwks_cache = {"keys": [jwk_dict]}
    validator._jwks_fetched_at = datetime.utcnow()
    validator._jwks_ttl = timedelta(hours=1)
    return validator


def _make_token(private_key, payload: dict, kid: str = "test-key-id") -> str:
    return jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
        headers={"kid": kid},
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_valid_token(test_validator, rsa_key_pair):
    private_key, _ = rsa_key_pair
    payload = {
        "sub": "keycloak-user-uuid",
        "email": "user@example.com",
        "preferred_username": "user@example.com",
        "name": "Test User",
        "iss": test_validator.issuer,
        "aud": "fastapi-frontend",
        "exp": int(time.time()) + 1800,
        "iat": int(time.time()),
        "realm_access": {"roles": ["user"]},
    }
    token = _make_token(private_key, payload)
    claims = test_validator.validate_token(token)
    assert claims is not None
    assert claims["email"] == "user@example.com"
    assert "user" in claims["realm_access"]["roles"]


def test_admin_role_in_claims(test_validator, rsa_key_pair):
    private_key, _ = rsa_key_pair
    payload = {
        "sub": "admin-uuid",
        "email": "admin@example.com",
        "iss": test_validator.issuer,
        "exp": int(time.time()) + 1800,
        "iat": int(time.time()),
        "realm_access": {"roles": ["user", "admin"]},
    }
    token = _make_token(private_key, payload)
    claims = test_validator.validate_token(token)
    assert claims is not None
    assert "admin" in claims["realm_access"]["roles"]


def test_expired_token_rejected(test_validator, rsa_key_pair):
    private_key, _ = rsa_key_pair
    payload = {
        "sub": "user-uuid",
        "email": "user@example.com",
        "iss": test_validator.issuer,
        "exp": int(time.time()) - 60,  # already expired
        "iat": int(time.time()) - 120,
    }
    token = _make_token(private_key, payload)
    assert test_validator.validate_token(token) is None


def test_wrong_issuer_rejected(test_validator, rsa_key_pair):
    private_key, _ = rsa_key_pair
    payload = {
        "sub": "user-uuid",
        "email": "user@example.com",
        "iss": "http://malicious-idp.example.com/realms/evil",
        "exp": int(time.time()) + 1800,
        "iat": int(time.time()),
    }
    token = _make_token(private_key, payload)
    assert test_validator.validate_token(token) is None


def test_unknown_kid_triggers_refresh(test_validator, rsa_key_pair):
    private_key, _ = rsa_key_pair
    payload = {
        "sub": "user-uuid",
        "email": "user@example.com",
        "iss": test_validator.issuer,
        "exp": int(time.time()) + 1800,
        "iat": int(time.time()),
    }
    # Sign with an unknown kid – validator should attempt a refresh and then fail
    token = _make_token(private_key, payload, kid="unknown-kid")

    with patch.object(test_validator, "_fetch_jwks", return_value=test_validator._jwks_cache):
        result = test_validator.validate_token(token)
    # Still fails because unknown kid is not in the refreshed JWKS
    assert result is None


def test_invalid_signature_rejected(test_validator):
    # A completely bogus token string
    assert test_validator.validate_token("not.a.jwt") is None


def test_warm_cache_success(monkeypatch):
    validator = KeycloakJWTValidator.__new__(KeycloakJWTValidator)
    validator.issuer = "http://keycloak:8080/realms/fastapi-demo"
    validator.jwks_uri = "http://keycloak:8080/realms/fastapi-demo/protocol/openid-connect/certs"
    validator._jwks_cache = None
    validator._jwks_fetched_at = None
    validator._jwks_ttl = timedelta(hours=1)

    mock_response = MagicMock()
    mock_response.json.return_value = {"keys": []}

    with patch("httpx.get", return_value=mock_response):
        result = validator.warm_cache()

    assert result is True
    assert validator._jwks_cache == {"keys": []}


def test_warm_cache_failure(monkeypatch):
    validator = KeycloakJWTValidator.__new__(KeycloakJWTValidator)
    validator.issuer = "http://keycloak:8080/realms/fastapi-demo"
    validator.jwks_uri = "http://keycloak:8080/realms/fastapi-demo/protocol/openid-connect/certs"
    validator._jwks_cache = None
    validator._jwks_fetched_at = None
    validator._jwks_ttl = timedelta(hours=1)

    with patch("httpx.get", side_effect=Exception("connection refused")):
        result = validator.warm_cache()

    assert result is False
