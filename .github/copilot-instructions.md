# GitHub Copilot Instructions for FastAPI Intranet Demo

## Project Overview

This is a full-stack intranet web application demonstrating enterprise features including authentication, user management, personal access tokens, and CRUD operations. The application is designed for deployment on Azure Government Cloud (GCC High) infrastructure.

**Purpose**: Showcase a production-ready intranet application with modern authentication methods (username/password, LDAP, future SSO) and common enterprise features.

**Target Deployment**: Docker Compose on Linux server in Azure GCC High private datacenter.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Data Models**: SQLModel (built on SQLAlchemy) with Pydantic validation
- **Database**: SQLite (development/demo) → SQL Server (production)
- **Authentication**: JWT tokens, OAuth2 password bearer, LDAP (ldap3), future SAML/OIDC
- **Password Hashing**: bcrypt or argon2
- **Testing**: PyTest with pytest-asyncio
- **Migrations**: Alembic

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Routing**: React Router v6
- **State Management**: React Context API or TanStack Query
- **UI Library**: Tailwind CSS or Chakra UI (to be decided)
- **HTTP Client**: Axios or fetch
- **Testing**: Vitest (unit tests) + Playwright (E2E tests)

### DevOps
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions or Jenkins
- **Base Images**: Official python:slim for backend, node:alpine for frontend builds

## Code Style & Conventions

### Python (Backend)
- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Use async/await for async operations (FastAPI endpoints)
- Dependency injection via FastAPI dependencies
- Structure: Separate concerns into `api/`, `core/`, `models/`, `crud/`, `tests/`
- Config: Use Pydantic BaseSettings for environment configuration
- Error handling: Use FastAPI HTTPException with appropriate status codes
- Testing: Write unit tests for business logic, integration tests for endpoints

**Example patterns**:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.deps import get_current_user, get_session
from app.models.user import User, UserUpdate
from app.crud import user as crud_user

router = APIRouter()

@router.get("/users/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user profile."""
    return current_user

@router.put("/users/me", response_model=User)
async def update_user_me(
    user_in: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> User:
    """Update current user profile."""
    user = crud_user.update(session, db_obj=current_user, obj_in=user_in)
    return user
```

### TypeScript/React (Frontend)
- Use functional components with hooks (no class components)
- Prefer TypeScript strict mode
- Use proper type definitions (avoid `any`)
- Component file naming: PascalCase (e.g., `LoginForm.tsx`)
- Utility file naming: camelCase (e.g., `apiClient.ts`)
- Use async/await for API calls
- Error boundaries for error handling
- Responsive design (mobile-first approach)

**Example patterns**:
```typescript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/auth';

interface LoginFormProps {
  onSuccess?: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      onSuccess?.();
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
    </form>
  );
};
```

## Security Best Practices

### Authentication & Authorization
- **Never** store passwords in plain text (always hash with bcrypt/argon2)
- JWTs should include expiration (`exp` claim)
- Store JWTs in httpOnly cookies when possible (XSS protection)
- Implement RBAC (role-based access control) using FastAPI dependencies
- Personal Access Tokens (PATs) must be hashed like passwords
- Enforce token expiration and scope validation

### Data Protection
- All sensitive data in environment variables (never commit secrets)
- Use `.env.example` for documentation (not actual `.env` files)
- HTTPS/TLS required in production (even for internal apps)
- SQL injection protection via SQLModel parameterized queries
- XSS protection via React's automatic escaping + CSP headers
- CSRF tokens for state-changing operations

### Configuration
- Follow 12-factor app methodology
- Environment-based configuration (dev, staging, prod)
- Secrets management: Never hardcode, use env vars or secret managers
- Validate all environment variables at startup

## Database Guidelines

### Schema Design
- Use SQLModel for type-safe models (works with both SQLite and SQL Server)
- All tables should have: `id` (primary key), `created_at`, `updated_at`
- Use soft deletes where appropriate (add `is_deleted` boolean)
- Foreign keys for relationships
- Indexes on frequently queried columns

### Migrations
- Use Alembic for all schema changes
- Never modify migrations after they've been applied to production
- Test migrations with both SQLite (dev) and SQL Server (prod)
- Always provide both `upgrade()` and `downgrade()` functions
- Run migrations atomically (one instance only)

**Example model**:
```python
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
```

## API Design Principles

### RESTful Conventions
- Use proper HTTP methods: GET (read), POST (create), PUT/PATCH (update), DELETE (remove)
- Use plural nouns for resources: `/api/users`, `/api/items`
- Nest related resources: `/api/users/me/tokens`
- Version APIs if needed: `/api/v1/...`
- Return appropriate status codes: 200, 201, 204, 400, 401, 403, 404, 500

### Request/Response Format
- Accept and return JSON
- Use Pydantic models for request validation and response serialization
- Include pagination for list endpoints: `?skip=0&limit=100`
- Support filtering and sorting where appropriate
- Return meaningful error messages with details

### Documentation
- Use FastAPI's automatic OpenAPI/Swagger documentation
- Add docstrings to all endpoints
- Include examples in Pydantic models using `schema_extra`
- Keep docs up-to-date with implementation

## Testing Strategy

### Backend Tests (PyTest)
- Unit tests for business logic (CRUD operations, utilities)
- Integration tests for API endpoints (use TestClient)
- Test database operations with test database/fixtures
- Test authentication and authorization flows
- Mock external services (LDAP, email)
- Aim for >80% code coverage

### Frontend Tests
- Unit tests for components (Vitest)
- E2E tests for critical user flows (Playwright)
- Test authentication flows thoroughly
- Test form validation
- Test error handling and loading states

### Test Organization
```
backend/app/tests/
├── __init__.py
├── conftest.py          # PyTest fixtures
├── test_auth.py
├── test_users.py
├── test_tokens.py
└── test_items.py

frontend/src/__tests__/
├── components/
├── pages/
└── e2e/
    └── auth.spec.ts
```

## Docker Best Practices

### Dockerfile Patterns
- Use multi-stage builds to minimize image size
- Use official base images (`python:3.11-slim`, `node:18-alpine`)
- Don't run containers as root (create non-root user)
- Copy only necessary files (use `.dockerignore`)
- Leverage layer caching (copy `requirements.txt` before code)
- Set explicit versions for base images (not `latest`)

### Docker Compose
- Separate development and production configs
- Use environment variables for configuration
- Implement health checks for all services
- Set resource limits (CPU, memory)
- Use volumes for persistent data (database)
- Use networks for service isolation

## Development Workflow

### Git Workflow
- Use feature branches: `feature/user-authentication`, `bugfix/login-error`
- Write descriptive commit messages
- Keep commits focused and atomic
- Rebase before merging to keep history clean
- Squash commits if needed for cleaner history

### Code Review Checklist
- [ ] Code follows project conventions
- [ ] Tests added/updated and passing
- [ ] No hardcoded secrets or sensitive data
- [ ] Error handling implemented
- [ ] Documentation updated if needed
- [ ] No console.logs or debug code
- [ ] Type safety maintained (TypeScript)
- [ ] Security considerations addressed

### Local Development
- Use Docker Compose for local development
- Hot-reloading enabled for both frontend and backend
- Use `.env` files for local configuration
- Test against SQLite locally, SQL Server in staging/prod
- Run linters before committing (pylint, eslint)

## Common Patterns

### Authentication Flow
1. User submits credentials (POST `/api/auth/login`)
2. Backend validates credentials (check DB or LDAP)
3. Backend generates JWT with user info and roles
4. Frontend stores JWT (httpOnly cookie or localStorage)
5. Frontend includes JWT in Authorization header for protected routes
6. Backend validates JWT on each protected endpoint

### RBAC Pattern
```python
from app.core.deps import get_current_user
from app.models.user import User
from fastapi import Depends, HTTPException, status

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin)
):
    # Only admins can access this endpoint
    pass
```

### Error Handling
```python
# Backend
from fastapi import HTTPException, status

def get_user_by_id(session: Session, user_id: int) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user

# Frontend
try {
  const response = await api.get('/users/me');
  setUser(response.data);
} catch (error) {
  if (error.response?.status === 401) {
    // Redirect to login
    navigate('/login');
  } else {
    setError(error.response?.data?.detail || 'An error occurred');
  }
}
```

## Environment Variables

### Backend (.env)
```bash
# Application
APP_NAME=FastAPI Intranet Demo
APP_VERSION=1.0.0
ENVIRONMENT=development  # development, staging, production

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./app.db  # or SQL Server connection string

# LDAP (optional)
LDAP_SERVER=ldap://dc.example.com
LDAP_BIND_DN=CN=Service Account,OU=Users,DC=example,DC=com
LDAP_BIND_PASSWORD=service-account-password
LDAP_SEARCH_BASE=OU=Users,DC=example,DC=com

# Email (optional)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=smtp-password
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=FastAPI Intranet Demo
```

## Deployment Considerations

### GCC High Compliance
- Use FedRAMP-authorized Azure services
- Ensure all network traffic is encrypted (HTTPS/TLS)
- No external network calls to non-approved services
- Use Azure AD (GCC) for SSO when implemented
- Follow government security compliance requirements
- Document data handling and storage policies

### Production Checklist
- [ ] All secrets in environment variables (not in code)
- [ ] HTTPS/TLS configured with valid certificates
- [ ] Database backups configured and tested
- [ ] Health check endpoints implemented
- [ ] Logging configured (structured JSON logs)
- [ ] Monitoring and alerting set up
- [ ] Rate limiting implemented
- [ ] CORS configured properly
- [ ] Security headers set (CSP, HSTS, etc.)
- [ ] Error messages don't leak sensitive info

## Reference Implementation

This project is based on the official [FastAPI full-stack template](https://github.com/fastapi/full-stack-fastapi-template) which provides:
- FastAPI + React + Vite + Docker setup
- User authentication with JWT
- SQLModel database models
- PyTest and Playwright tests
- GitHub Actions CI/CD
- Best practices for security and testing

## Common Tasks for Copilot

When generating code for this project, please:

1. **API Endpoints**: Always include proper type hints, Pydantic models, authentication dependencies, and docstrings
2. **Database Models**: Use SQLModel with proper relationships and validation
3. **React Components**: Use TypeScript, functional components with hooks, and proper error handling
4. **Tests**: Generate both unit and integration tests for new features
5. **Documentation**: Update API docs and code comments
6. **Security**: Never suggest storing passwords unhashed or secrets in code
7. **Error Handling**: Include comprehensive error handling with user-friendly messages

## Questions to Ask Before Implementing

1. Does this feature require authentication? What role/permission level?
2. Should this be available in the API documentation (Swagger)?
3. What are the validation requirements for input data?
4. How should errors be handled and communicated to users?
5. Are there performance considerations (pagination, caching)?
6. Does this need to work with both SQLite and SQL Server?
7. What tests are needed for this feature?

## Project References

- **Implementation Plan**: See `plan-001-implementation.md` for phased rollout
- **Project Overview**: See `docs/ai/Project Overview.pdf` for full requirements
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **React + Vite**: https://vitejs.dev/guide/
- **LDAP3**: https://ldap3.readthedocs.io/

---

**Last Updated**: 2025-10-30  
**Project Status**: Phase 1 - Foundation & Setup  
**License**: MIT
