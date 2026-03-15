# Stack Upgrade Plan

Migrate the fastapi-demo intranet application to the recommended enterprise baseline stack.

**Target stack:** Next.js + TypeScript + Bootstrap 5.3 + FastAPI + SQLAlchemy 2.x + pyodbc + SQL Server + Keycloak + pytest + Vitest + Playwright + Docker Compose

---

## Current vs Target Stack

| Layer | Current | Target |
|---|---|---|
| Frontend framework | React 18 SPA + Vite | Next.js 15 (App Router) |
| UI styling | Custom CSS | Bootstrap 5.3 |
| Auth (frontend) | localStorage JWT | Auth.js v5 + Keycloak OIDC |
| ORM | SQLModel (SQLAlchemy wrapper) | SQLAlchemy 2.x (direct) |
| Database | SQLite (file) | SQL Server 2022 |
| DB driver | (built-in) | pyodbc |
| Auth (backend) | Custom HS256 JWT + ldap3 | Keycloak RS256 JWT via JWKS |
| E2E testing | Puppeteer (Node.js) | Playwright |
| Frontend serving | nginx static | Next.js standalone server |

**Kept as-is:** Personal Access Tokens (PAT), Alembic, pytest, Vitest, passlib/Argon2, Docker Compose topology.

---

## Key Design Decisions

### Next.js App Router
Use the App Router (not Pages Router). It is the current standard — Pages Router is in maintenance mode. Route Groups map cleanly to this app's structure: `(auth)` for login/register, `(dashboard)` for protected pages. Server Components reduce client-side JavaScript for data-heavy admin tables.

### Keycloak Integration Pattern
- **Frontend:** Auth.js v5 (`next-auth`) handles the OIDC Authorization Code + PKCE flow. Sessions stored in HTTP-only cookies (no more `localStorage`).
- **Backend:** FastAPI fetches Keycloak JWKS at startup, caches public keys, and validates RS256 tokens. User roles come from `realm_access.roles` claims in the JWT.
- **Auto-provisioning:** On first Keycloak login, a local DB record is created (same pattern as the existing LDAP provisioning in `auth.py`).
- **PATs kept:** Personal Access Tokens serve API automation use cases that SSO does not cover. The `get_current_user` dependency gains a third auth path: PAT → Keycloak JWT → 401.

### SQLAlchemy 2.x Migration
SQLModel is replaced by pure SQLAlchemy 2.x. ORM models use `DeclarativeBase` with `Mapped[T]` / `mapped_column()`. Pydantic schemas remain separate with `model_config = ConfigDict(from_attributes=True)`. CRUD changes are mechanical: `session.exec(stmt).all()` → `session.execute(stmt).scalars().all()`.

### pyodbc + SQL Server
pyodbc is synchronous. FastAPI runs sync endpoint handlers in a threadpool automatically. No async SQL Server driver is mature enough for production. Connection string format: `mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes`. SQLite remains a fallback for quick local runs without Docker.

### Bootstrap 5.3
Plain Bootstrap CSS classes — no `react-bootstrap`. React-Bootstrap requires `"use client"` everywhere and adds an unnecessary dependency layer. Bootstrap 5 is JavaScript-minimal. Import strategy: install `bootstrap` npm package, add `custom.scss` that overrides Bootstrap SCSS variables then `@import "bootstrap/scss/bootstrap"`, import in root `layout.tsx`.

### Playwright
Playwright replaces all 9 Puppeteer scripts. A `global-setup.ts` logs into Keycloak once and saves `storageState` — all tests reuse the browser cookie session, avoiding OIDC redirect flakiness in most tests. Test files mirror the 23 Gherkin feature file domains.

---

## Phase 1 — Infrastructure (Weeks 1–2)

**Goal:** Docker Compose runs all 4 services (backend, frontend, SQL Server, Keycloak) and they can communicate. No application code changes.

### Tasks

#### 1.1 Add SQL Server to Docker Compose

Add `sqlserver` service to `docker-compose.yml` and `docker-compose.dev.yml`:

```yaml
sqlserver:
  image: mcr.microsoft.com/mssql/server:2022-latest
  environment:
    ACCEPT_EULA: "Y"
    MSSQL_SA_PASSWORD: "YourStrong@Passw0rd"
    MSSQL_PID: Developer
  ports:
    - "1433:1433"
  volumes:
    - sqlserver-data:/var/opt/mssql
  healthcheck:
    test: /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$$MSSQL_SA_PASSWORD" -Q "SELECT 1" -C
    interval: 10s
    timeout: 5s
    retries: 5
  networks:
    - app-network
```

Create `infrastructure/sql/init.sql`:
```sql
CREATE DATABASE fastapi_demo;
```

#### 1.2 Add Keycloak to Docker Compose

Create `infrastructure/keycloak/realm-export.json` containing:
- Realm: `fastapi-demo`
- OIDC client: `fastapi-frontend` (public, redirect URIs for `localhost:3000` and `localhost:3001`)
- Bearer-only client: `fastapi-backend`
- Realm roles: `user`, `admin`
- Test users: `admin@example.com` (admin role), `user@example.com` (user role)

Add `keycloak` service to both Compose files:

```yaml
keycloak:
  image: quay.io/keycloak/keycloak:26.0
  command: start-dev --import-realm
  environment:
    KC_BOOTSTRAP_ADMIN_USERNAME: admin
    KC_BOOTSTRAP_ADMIN_PASSWORD: admin
    KC_HTTP_PORT: 8080
    KC_HOSTNAME_URL: http://localhost:8080
  ports:
    - "8080:8080"
  volumes:
    - ./infrastructure/keycloak/realm-export.json:/opt/keycloak/data/import/realm-export.json
  depends_on:
    sqlserver:
      condition: service_healthy
  networks:
    - app-network
```

#### 1.3 Update Backend Dockerfile for ODBC Driver

Add to `backend/Dockerfile` builder stage:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc curl gnupg2 unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/12/prod.list \
       > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*
```

#### 1.4 Stub the Next.js Frontend Project

```bash
npx create-next-app@latest frontend-next \
  --typescript --app --src-dir --no-tailwind \
  --import-alias "@/*"
```

Add `frontend-next` service to Compose on port 3001 (runs alongside `frontend/` during migration).

#### 1.5 Update Environment Configuration

Add to `backend/.env.example`:
```
DATABASE_URL=mssql+pyodbc://sa:YourStrong@Passw0rd@sqlserver:1433/fastapi_demo?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=fastapi-demo
KEYCLOAK_CLIENT_ID=fastapi-backend
AUTH_MODE=keycloak
```

Create `frontend-next/.env.local.example`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=<generate with: openssl rand -base64 32>
KEYCLOAK_CLIENT_ID=fastapi-frontend
KEYCLOAK_CLIENT_SECRET=
KEYCLOAK_ISSUER=http://localhost:8080/realms/fastapi-demo
```

### Risks

| Risk | Mitigation |
|---|---|
| SQL Server Docker image is ~1.5 GB and x86_64 only (no ARM/M-series Mac) | Document Windows/Linux x86_64 requirement. Provide Azure SQL fallback connection string. |
| Keycloak realm import fails silently | Add a smoke-test script `infrastructure/scripts/test-keycloak.sh` |

---

## Phase 2 — Backend Migration (Weeks 3–5)

**Goal:** FastAPI runs on SQLAlchemy 2.x + SQL Server with Keycloak JWT validation. All existing pytest tests pass.

### Tasks

#### 2.1 Migrate from SQLModel to SQLAlchemy 2.x

**Files to create:**
- `backend/app/models/base.py` — shared `Base = DeclarativeBase()` and metadata

**Files to modify:**
- `backend/requirements.txt` — replace `sqlmodel==0.0.14` with `sqlalchemy==2.0.36`, add `pyodbc==5.2.0`
- `backend/app/models/user.py` — convert to `DeclarativeBase` + separate Pydantic schemas
- `backend/app/models/item.py` — same conversion
- `backend/app/models/token.py` — same conversion
- `backend/app/core/database.py` — rewrite using `sqlalchemy.orm.Session` and `create_engine`

Conversion pattern:

```python
# Before (SQLModel)
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

# After (SQLAlchemy 2.x ORM model)
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

# After (Pydantic schema)
class UserInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
```

#### 2.2 Update CRUD Layer

Mechanical find/replace across `backend/app/crud/user.py`, `crud/item.py`, and `api/tokens.py`:

| Before | After |
|---|---|
| `session.exec(stmt).first()` | `session.execute(stmt).scalars().first()` |
| `session.exec(stmt).all()` | `session.execute(stmt).scalars().all()` |
| `session.exec(stmt).one()` | `session.execute(stmt).scalars().one()` |

#### 2.3 Update Database Configuration for SQL Server

Modify `backend/app/core/config.py`:
- Remove SQLite-specific `check_same_thread` workaround
- Add `KEYCLOAK_URL`, `KEYCLOAK_REALM`, `KEYCLOAK_CLIENT_ID`, `AUTH_MODE` settings

Modify `backend/app/core/database.py`:
- Remove SQLite `connect_args`
- Add SQL Server connection pool settings: `pool_size=5`, `max_overflow=10`, `pool_pre_ping=True`, `pool_recycle=3600`
- Detect `sqlite` prefix in `DATABASE_URL` to maintain local dev without Docker

#### 2.4 Integrate Keycloak JWT Validation

**Files to create:** `backend/app/core/keycloak.py`

```python
class KeycloakJWTValidator:
    """Fetches JWKS from Keycloak, caches public keys, validates RS256 tokens."""

    async def startup(self):
        # Fetch /.well-known/openid-configuration → get jwks_uri
        # Fetch JWKS, cache public keys with TTL

    def validate_token(self, token: str) -> dict:
        # Decode header to get kid
        # Look up key from cache (refresh if missing)
        # Validate RS256 signature, iss, aud, exp
        # Return claims dict: sub, email, preferred_username, realm_access.roles
```

**Files to modify:** `backend/app/core/deps.py`

```python
def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    # 1. PAT check: if token starts with "pat_"
    # 2. Keycloak JWT: if AUTH_MODE == "keycloak"
    #    → validate via KeycloakJWTValidator
    #    → auto-provision user if not in local DB
    # 3. Local JWT: if AUTH_MODE == "local" (backward compat)
    # 4. Raise 401
```

#### 2.5 User Auto-Provisioning from Keycloak

When a Keycloak JWT is valid but the user's email does not exist in the database, create a new local user record. Mirrors the existing LDAP provisioning pattern in `auth.py`. Map `realm_access.roles` → `is_admin` flag.

#### 2.6 Retire LDAP Service

- Wrap `backend/app/core/ldap_service.py` with deprecation notice
- Make LDAP login endpoints (`/api/auth/ldap/*`) return 410 Gone when `AUTH_MODE=keycloak`
- Keycloak handles AD/LDAP federation natively — no application-level LDAP code needed

#### 2.7 Update Alembic for SQL Server

- Update `backend/alembic.ini`: `sqlalchemy.url` reads from env var
- Update `backend/alembic/env.py`: import new `Base.metadata`, configure for `mssql` dialect
- Generate initial migration: `alembic revision --autogenerate -m "initial schema sqlalchemy 2x"`

#### 2.8 Update Backend Tests

**Files to modify:**
- `backend/app/tests/conftest.py` — replace `SQLModel.metadata` with `Base.metadata`, replace `sqlmodel.Session` with `sqlalchemy.orm.Session`
- All 6 test files — update imports, fix any inline `session.exec()` calls

**Files to create:**
- `backend/app/tests/test_keycloak.py` — test JWT validation with mocked JWKS (pre-generated RS256 test keys)

### Package Versions

```
# backend/requirements.txt (revised)
fastapi==0.115.6
uvicorn[standard]==0.32.1
python-multipart==0.0.18
pydantic==2.10.4
pydantic-settings==2.7.1

# Database
sqlalchemy==2.0.36
alembic==1.14.1
pyodbc==5.2.0

# Security
PyJWT[crypto]==2.9.0
cryptography==43.0.3
passlib[argon2]==1.7.4
argon2-cffi==23.1.0

# HTTP (JWKS fetching + tests)
httpx==0.28.1

# LDAP (deprecated, kept for backward compat)
ldap3==2.9.1

# Environment
python-dotenv==1.0.1

# Testing
pytest==8.3.4
pytest-asyncio==0.24.0

# Code quality (replaces pylint + black)
ruff==0.8.6
```

### Risks

| Risk | Mitigation |
|---|---|
| SQLModel → SQLAlchemy breaks existing tests | Convert one model at a time (start with `Item`, simplest). Run full pytest after each. |
| Keycloak JWT claim differences vs current HS256 tokens | Build `KeycloakJWTValidator` with comprehensive unit tests using pre-generated test JWTs before wiring into `deps.py`. |
| pyodbc connection pool behaviour differs from SQLite | Add `pool_pre_ping=True` to detect stale connections. Configure `pool_recycle=3600`. |

---

## Phase 3 — Frontend Migration (Weeks 5–8)

*Overlaps with Phase 2 — frontend can use the existing FastAPI backend (local JWT auth) during initial development, then switch to Keycloak in the second half of this phase.*

**Goal:** Next.js 15 + Bootstrap 5.3 frontend with Keycloak login replaces the React SPA. All pages functional.

### Tasks

#### 3.1 Initialize Next.js Project

```bash
npx create-next-app@latest frontend-next \
  --typescript --app --src-dir --no-tailwind \
  --import-alias "@/*"
```

Configure `frontend-next/next.config.ts`:
```typescript
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [{ source: '/api/:path*', destination: 'http://backend:8000/api/:path*' }]
  },
}
```

#### 3.2 Set Up Bootstrap 5.3

Install: `npm install bootstrap sass`

Create `frontend-next/src/styles/custom.scss`:
```scss
// Override Bootstrap variables before importing
$primary: #0d6efd;
$font-family-base: 'Segoe UI', system-ui, sans-serif;

@import "bootstrap/scss/bootstrap";
```

Import in `frontend-next/src/app/layout.tsx`:
```typescript
import '@/styles/custom.scss'
```

#### 3.3 Set Up Auth.js v5 with Keycloak

**Files to create:**

`frontend-next/src/auth.ts`:
```typescript
import NextAuth from 'next-auth'
import Keycloak from 'next-auth/providers/keycloak'

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Keycloak({
      clientId: process.env.KEYCLOAK_CLIENT_ID!,
      clientSecret: process.env.KEYCLOAK_CLIENT_SECRET!,
      issuer: process.env.KEYCLOAK_ISSUER!,
    }),
  ],
  callbacks: {
    async jwt({ token, account }) {
      if (account) token.accessToken = account.access_token
      return token
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string
      return session
    },
  },
})
```

`frontend-next/src/middleware.ts`:
```typescript
export { auth as middleware } from '@/auth'
export const config = {
  matcher: ['/((?!login|api/auth|_next|favicon.ico).*)'],
}
```

`frontend-next/src/app/api/auth/[...nextauth]/route.ts`:
```typescript
import { handlers } from '@/auth'
export const { GET, POST } = handlers
```

#### 3.4 Route Structure

```
frontend-next/src/app/
  layout.tsx                          ← root layout, Bootstrap CSS import
  (auth)/
    layout.tsx                        ← centered card layout (no nav)
    login/page.tsx                    ← Keycloak redirect button
    register/page.tsx                 ← optional local registration form
  (dashboard)/
    layout.tsx                        ← TopBar + main content wrapper
    page.tsx                          ← Dashboard (Server Component)
    profile/page.tsx                  ← Client Component (form)
    admin/users/page.tsx              ← Server Component list + Client modal
    items/page.tsx                    ← Server Component list + Client modal
    tokens/page.tsx                   ← Client Component (PAT create form)
```

#### 3.5 Page Migration

| Current file | New file | Component type | Notes |
|---|---|---|---|
| `pages/LoginPage.tsx` + `AuthPages.css` | `(auth)/login/page.tsx` | Server | Keycloak redirect button |
| `pages/RegisterPage.tsx` | `(auth)/register/page.tsx` | Client | Keep if local registration needed |
| `pages/DashboardPage.tsx` + `.css` | `(dashboard)/page.tsx` | Server | Fetches stats server-side |
| `pages/ProfilePage.tsx` + `.css` | `(dashboard)/profile/page.tsx` | Client | Form interaction |
| `pages/AdminUsersPage.tsx` + `.css` | `(dashboard)/admin/users/page.tsx` | Server + Client | List (Server), modals (Client) |
| `pages/ItemsPage.tsx` + `.css` | `(dashboard)/items/page.tsx` | Server + Client | List (Server), CRUD modals (Client) |
| `pages/TokensPage.tsx` + `.css` | `(dashboard)/tokens/page.tsx` | Client | PAT create/revoke |

#### 3.6 Component Migration

| Current component | New location | Bootstrap class mapping |
|---|---|---|
| `TopBar.tsx` | `components/TopBar.tsx` | `navbar navbar-expand-lg navbar-dark bg-dark` |
| `FormField.tsx` | `components/FormField.tsx` | `mb-3`, `form-label`, `form-control`, `invalid-feedback` |
| `Loading.tsx` | `components/Loading.tsx` | `spinner-border` |
| `Toast.tsx` / `ToastContainer.tsx` | `components/Toast.tsx` | `toast`, `toast-container position-fixed` |
| `UserModal.tsx` | `components/UserModal.tsx` | `modal`, `modal-dialog`, `modal-content` |
| `ProtectedRoute.tsx` | **Deleted** | Replaced by `middleware.ts` |

#### 3.7 API Service Layer

Split `frontend/src/services/api.ts` into focused modules. Replace the localStorage interceptor with `next-auth` session reading.

Files to create under `frontend-next/src/lib/api/`:
- `client.ts` — axios instance with session token interceptor
- `auth.ts` — auth API functions
- `users.ts` — user API functions
- `items.ts` — items API functions
- `tokens.ts` — tokens API functions

#### 3.8 Next.js Dockerfile

Multi-stage build using Next.js standalone mode:

```dockerfile
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

This replaces the current nginx-based static file serving.

### Package Versions

```json
{
  "dependencies": {
    "next": "15.1.4",
    "react": "19.0.0",
    "react-dom": "19.0.0",
    "next-auth": "5.0.0-beta.25",
    "bootstrap": "5.3.3",
    "axios": "1.7.9"
  },
  "devDependencies": {
    "typescript": "5.7.3",
    "@types/node": "22.10.5",
    "@types/react": "19.0.7",
    "@types/react-dom": "19.0.3",
    "sass": "1.83.4",
    "@playwright/test": "1.49.1",
    "vitest": "2.1.8",
    "@vitejs/plugin-react": "4.3.4",
    "@testing-library/react": "16.1.0",
    "@testing-library/jest-dom": "6.6.3",
    "happy-dom": "16.6.0"
  }
}
```

### Risks

| Risk | Mitigation |
|---|---|
| Keycloak localhost vs container hostname conflict | Browser hits `localhost:8080`; container hits `keycloak:8080`. Use `KC_HOSTNAME_URL` in Keycloak and `wellKnown` URL override in Auth.js config. |
| Auth.js v5 beta API instability | Pin to exact version `5.0.0-beta.25`. Auth.js v5 has been in beta since 2023 with minimal breaking changes. |
| Bootstrap CSS conflicts with remaining custom styles | Build fresh with Bootstrap only — do not attempt to merge old CSS. Rebuild each component from scratch. |

---

## Phase 4 — Testing Migration (Weeks 8–10)

**Goal:** Full test coverage with pytest (backend), Vitest (frontend unit), Playwright (E2E). Puppeteer fully removed.

### Tasks

#### 4.1 Vitest for Next.js

Create `frontend-next/vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: './src/test/setup.ts',
    include: ['src/**/*.test.{ts,tsx}'],
  },
  resolve: {
    alias: { '@': new URL('./src', import.meta.url).pathname },
  },
})
```

Create `frontend-next/src/test/setup.ts`:
```typescript
import '@testing-library/jest-dom'
```

#### 4.2 Migrate Frontend Unit Tests

| Current test | New test | Key change |
|---|---|---|
| `__tests__/Login.test.tsx` | `src/__tests__/login.test.tsx` | Mock `next-auth` session instead of localStorage |
| `__tests__/Register.test.tsx` | `src/__tests__/register.test.tsx` | Same auth mock changes |
| `__tests__/ItemsPage.test.tsx` | `src/__tests__/items.test.tsx` | Test data-fetching logic, not Server Component rendering |
| `__tests__/ProfilePage.test.tsx` | `src/__tests__/profile.test.tsx` | Mock session for current user data |
| `__tests__/TokensPage.test.tsx` | `src/__tests__/tokens.test.tsx` | Minimal changes |

Note: Only Client Components are unit-tested with Vitest. Server Components are covered by Playwright E2E tests.

#### 4.3 Set Up Playwright

Create `playwright.config.ts` at project root:
```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3001',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'tests/.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
  webServer: [
    {
      command: 'cd backend && uvicorn app.main:app --port 8000',
      port: 8000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'cd frontend-next && npm run dev -- --port 3001',
      port: 3001,
      reuseExistingServer: !process.env.CI,
    },
  ],
})
```

Create `tests/e2e/auth.setup.ts` (runs once, saves authenticated state):
```typescript
import { test as setup } from '@playwright/test'
import path from 'path'

const authFile = path.join(__dirname, '../.auth/user.json')

setup('authenticate via Keycloak', async ({ page }) => {
  await page.goto('/login')
  await page.getByRole('button', { name: /sign in/i }).click()
  // Fill Keycloak login form
  await page.fill('#username', 'admin@example.com')
  await page.fill('#password', 'admin')
  await page.getByRole('button', { name: /sign in/i }).click()
  await page.waitForURL('/')
  await page.context().storageState({ path: authFile })
})
```

#### 4.4 Write Playwright E2E Tests

Replace all 9 Puppeteer scripts. Map to Gherkin feature file domains:

| Playwright file | Gherkin domain | Replaces Puppeteer file |
|---|---|---|
| `tests/e2e/auth/login.spec.ts` | `authentication/` | `test-ui.js` |
| `tests/e2e/auth/register.spec.ts` | `authentication/` | (new) |
| `tests/e2e/admin/users.spec.ts` | `user-management/`, `system-admin/` | `test-admin-users.js` |
| `tests/e2e/items/items-crud.spec.ts` | `items-management/` | `test-items-ui.js` |
| `tests/e2e/tokens/tokens.spec.ts` | `personal-access-tokens/` | `test-api-keys-flow.js` |
| `tests/e2e/navigation/topbar.spec.ts` | `ui-ux/` | `test-topbar.js`, `test-topbar-simple.js` |
| `tests/e2e/security/headers.spec.ts` | `security/` | `test-deployment.js` |

#### 4.5 Remove Puppeteer

- Delete all `.js` files in `tests/e2e/` and `tests/api/`
- Remove root-level `package.json` (puppeteer + axios dependencies)
- Add root-level `package.json` with only `@playwright/test` for E2E

### Risks

| Risk | Mitigation |
|---|---|
| Playwright + Keycloak OIDC redirect flakiness | `auth.setup.ts` authenticates once and saves `storageState`. Only the setup test performs the OIDC redirect. |
| Server Components cannot be rendered in Vitest | Only test Client Components with Vitest. Cover Server Component behaviour via Playwright. |

---

## Phase 5 — Cutover & Cleanup (Weeks 10–12)

**Goal:** Single stack in production configuration. Legacy frontend removed. Documentation updated.

### Tasks

#### 5.1 Rename and Restructure

```bash
mv frontend/ frontend-legacy/
mv frontend-next/ frontend/
```

Update all Docker Compose files to reference the new `frontend/` directory. Validate, then delete `frontend-legacy/`.

#### 5.2 Final Docker Compose

Services in `docker-compose.yml` with startup order enforced via `depends_on` + healthchecks:

```
sqlserver (healthy) → keycloak (healthy) → backend (healthy) → frontend
```

```yaml
services:
  sqlserver:   # port 1433
  keycloak:    # port 8080, depends_on: sqlserver
  backend:     # port 8000, depends_on: sqlserver + keycloak
  frontend:    # port 3000, depends_on: backend

volumes:
  sqlserver-data:
```

#### 5.3 Data Migration

Create `scripts/migrate_sqlite_to_sqlserver.py` for one-time data migration from SQLite to SQL Server. Argon2 password hashes are portable — no rehashing needed. PAT hashes (SHA-256) are also portable.

#### 5.4 Remove Legacy Code

| Item | Action |
|---|---|
| `frontend-legacy/` | Delete after validation |
| `tests/e2e/*.js` (Puppeteer) | Delete |
| `tests/api/*.js` | Delete |
| Root `package.json` (puppeteer) | Delete (replaced by new root `package.json` with only `@playwright/test`) |
| `backend/app/core/ldap_service.py` | Delete |
| `backend/app/api/auth.py` LDAP endpoints | Remove `/ldap/health`, `/ldap/config` |
| `backend/venv/` | Add to `.gitignore`, delete from repo |

#### 5.5 Update Documentation

| File | Change |
|---|---|
| `README.md` | Update getting started, prerequisites, tech stack |
| `CONTEXT.md` | Update architecture diagram, service list, env setup |
| `docs/LDAP_CONFIGURATION.md` | Add note: Keycloak handles LDAP federation natively |
| `features/authentication/02-user-login.feature` | Update login scenarios to reflect Keycloak redirect |
| `features/authentication/03-ldap-authentication.feature` | Update: LDAP is now handled by Keycloak federation |
| `features/security/02-jwt-security.feature` | Update: JWT is now RS256 issued by Keycloak |

Files to create:
- `docs/KEYCLOAK_SETUP.md` — realm configuration, user management, LDAP federation setup
- `docs/MIGRATION_GUIDE.md` — how to migrate an existing installation from the old stack

---

## Keep vs. Replace Summary

| Component | Decision | Reason |
|---|---|---|
| Personal Access Tokens | **Keep** | API automation use case that SSO does not cover |
| Alembic | **Keep** | Still needed for SQL Server schema migrations |
| passlib / Argon2 | **Keep** | PAT token storage still uses hashing |
| LDAP service (ldap3) | **Remove** | Keycloak natively federates to AD/LDAP |
| Custom JWT issuance (python-jose) | **Remove** | Keycloak issues all tokens; backend only validates |
| Local user registration endpoint | **Optional** | Keep behind `AUTH_MODE=local` flag, or remove if Keycloak manages all users |
| nginx frontend serving | **Remove** | Next.js standalone server replaces it |
| Puppeteer tests | **Remove** | Replaced by Playwright |
| SQLite support | **Keep as dev fallback** | Useful for quick local runs without Docker |

---

## Dependency Version Matrix

| Package | Current | Target | Notes |
|---|---|---|---|
| **Backend** | | | |
| FastAPI | 0.115.0 | 0.115.6 | Minor bump |
| SQLModel | 0.0.14 | removed | Replaced by SQLAlchemy |
| SQLAlchemy | via SQLModel | 2.0.36 | Direct dependency |
| pyodbc | — | 5.2.0 | New: SQL Server ODBC driver |
| python-jose | 3.3.0 | removed | Replaced by PyJWT |
| PyJWT | — | 2.9.0 | New: Keycloak JWT validation |
| cryptography | via jose | 43.0.3 | RS256 key handling |
| passlib | 1.7.4 | 1.7.4 | Unchanged |
| ldap3 | 2.9.1 | deprecated | Kept but inactive |
| Alembic | 1.12.1 | 1.14.1 | Minor bump |
| pytest | 7.4.3 | 8.3.4 | Major bump |
| httpx | 0.25.2 | 0.28.1 | JWKS fetching + tests |
| pylint + black | — | removed | Replaced by ruff 0.8.6 |
| **Frontend** | | | |
| React | 18.3.1 | 19.0.0 | Via Next.js 15 |
| Vite | 7.1.12 | removed | Next.js uses its own bundler |
| Next.js | — | 15.1.4 | New |
| next-auth | — | 5.0.0-beta.25 | New: Keycloak OIDC |
| Bootstrap | — | 5.3.3 | New: replaces custom CSS |
| sass | — | 1.83.4 | New: Bootstrap SCSS compilation |
| react-router-dom | 6.30.1 | removed | Next.js has built-in routing |
| axios | 1.13.1 | 1.7.9 | Kept |
| Vitest | 4.0.6 | 2.1.8 | Compatible version for Next.js |
| **E2E Testing** | | | |
| Puppeteer | 24.27.0 | removed | Replaced by Playwright |
| @playwright/test | — | 1.49.1 | New |
| **Infrastructure** | | | |
| Keycloak | — | 26.0 | New |
| SQL Server | — | 2022-latest | New |
| Node.js (Docker) | 18-alpine | 22-alpine | LTS bump |
| Python (Docker) | 3.11-slim | 3.12-slim | Minor bump |

---

## Risk Register

| # | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| 1 | SQLModel → SQLAlchemy introduces subtle ORM behaviour differences | Medium | High | Convert one model at a time, starting with `Item`. Run full pytest after each. |
| 2 | Keycloak Docker networking issues (browser vs container hostname) | High | Medium | Use `KC_HOSTNAME_URL` in Keycloak config. Document dual-URL pattern. |
| 3 | Auth.js v5 beta API instability | Low | Medium | Pin exact version. Stable in practice since 2023. |
| 4 | SQL Server Docker image not available on ARM64 | Medium | Low | Document x86_64 requirement. Provide Azure SQL connection string alternative. |
| 5 | Bootstrap CSS causes visual regression from current design | Low | Medium | Build fresh with Bootstrap — do not merge old CSS. |
| 6 | Playwright tests flaky with Keycloak OIDC redirects | Medium | Medium | `auth.setup.ts` storageState pattern; only the setup test does the OIDC flow. |
| 7 | SQLite → SQL Server data migration loses type fidelity | Low | High | Write explicit migration script with type mapping. Test with production-like data. |
| 8 | Gherkin scenario coverage gaps after migration | Medium | High | Create traceability matrix mapping each Gherkin scenario to a Playwright test before Phase 4 ends. |
| 9 | Scope creep during migration | High | Medium | Strict scope: migrate only. Feature enhancements go on a separate backlog post-migration. |

---

## Timeline Summary

| Phase | Weeks | Deliverable |
|---|---|---|
| 1 — Infrastructure | 1–2 | Docker Compose with 4 services (backend, frontend, SQL Server, Keycloak) running |
| 2 — Backend | 3–5 | SQLAlchemy 2.x + SQL Server + Keycloak JWT validation; all pytest passing |
| 3 — Frontend | 5–8 | Next.js 15 + Bootstrap 5.3 + Auth.js; all pages functional |
| 4 — Testing | 8–10 | Playwright replaces Puppeteer; full Vitest unit coverage |
| 5 — Cutover | 10–12 | Legacy removed; docs updated; production-ready |

Phases 2 and 3 overlap intentionally (weeks 5–8). The frontend team builds Next.js pages against the existing FastAPI backend with local JWT auth, then switches to Keycloak auth in the second half of Phase 3.
