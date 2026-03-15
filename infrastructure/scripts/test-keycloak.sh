#!/usr/bin/env bash
# Smoke-test: verify Keycloak has started and the realm was imported successfully.
# Usage: ./infrastructure/scripts/test-keycloak.sh [keycloak-base-url]
# Default URL: http://localhost:8080

set -euo pipefail

BASE_URL="${1:-http://localhost:8080}"
REALM="fastapi-demo"
WELL_KNOWN="${BASE_URL}/realms/${REALM}/.well-known/openid-configuration"

echo "Testing Keycloak at ${BASE_URL} ..."

# Wait up to 60s for Keycloak to become ready
for i in $(seq 1 12); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${WELL_KNOWN}" || true)
  if [ "${STATUS}" = "200" ]; then
    break
  fi
  echo "  Attempt ${i}/12 — HTTP ${STATUS}, retrying in 5s ..."
  sleep 5
done

if [ "${STATUS}" != "200" ]; then
  echo "FAIL: Keycloak did not become ready within 60s (last HTTP status: ${STATUS})"
  exit 1
fi

# Verify key fields in the OIDC discovery document
ISSUER=$(curl -s "${WELL_KNOWN}" | grep -o '"issuer":"[^"]*"' | cut -d'"' -f4)
EXPECTED_ISSUER="${BASE_URL}/realms/${REALM}"

if [ "${ISSUER}" = "${EXPECTED_ISSUER}" ]; then
  echo "PASS: Keycloak realm '${REALM}' is healthy (issuer: ${ISSUER})"
else
  echo "FAIL: Unexpected issuer '${ISSUER}' (expected '${EXPECTED_ISSUER}')"
  exit 1
fi
