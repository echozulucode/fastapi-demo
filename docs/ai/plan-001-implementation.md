# Implementation Plan: Full-Stack FastAPI Intranet Application

## Project Vision
Build a production-ready, full-stack intranet web application using FastAPI (Python) backend and React+Vite frontend, showcasing enterprise features including authentication (username/password + LDAP), user management, personal access tokens, and CRUD operations. Deploy using Docker Compose on Azure GCC High infrastructure.

## Technology Stack Summary
- **Backend**: FastAPI (Python 3.10+), SQLModel/SQLAlchemy, Pydantic
- **Frontend**: React + TypeScript + Vite, Tailwind CSS or Chakra UI
- **Database**: SQLite (demo) → SQL Server (production)
- **Auth**: JWT, LDAP (Active Directory), future SAML/OIDC SSO
- **Deployment**: Docker Compose, Linux server, Azure GCC High
- **Testing**: PyTest (backend), Vitest/Playwright (frontend)
- **CI/CD**: GitHub Actions or Jenkins

---

## Phase 1: Foundation & Project Setup (Week 1-2)

### 1.1 Development Environment Setup
**Priority**: Critical | **Effort**: 2-3 days

- [ ] Set up Python 3.10+ development environment
- [ ] Install Node.js (LTS) and npm/yarn for React development
- [ ] Install Docker Desktop and Docker Compose
- [ ] Set up Git repository with proper `.gitignore`
- [ ] Create `.env.example` template (12-factor app approach)
- [ ] Set up IDE/editor with Python and TypeScript support

**Deliverables**:
- Working development environment
- Repository structure with proper configuration
- Documentation for local setup

### 1.2 Project Scaffolding
**Priority**: Critical | **Effort**: 3-4 days

- [ ] Fork/reference FastAPI full-stack template as starting point
- [ ] Initialize FastAPI backend with proper project structure
  ```
  backend/
  ├── app/
  │   ├── main.py
  │   ├── api/
  │   ├── core/          # config, security
  │   ├── models/        # SQLModel schemas
  │   ├── crud/          # database operations
  │   └── tests/
  ├── alembic/           # migrations
  ├── requirements.txt
  └── Dockerfile
  ```
- [ ] Initialize React+Vite frontend with TypeScript
  ```
  frontend/
  ├── src/
  │   ├── components/
  │   ├── pages/
  │   ├── hooks/
  │   ├── services/      # API calls
  │   └── types/
  ├── package.json
  └── Dockerfile
  ```
- [ ] Set up Docker Compose configuration for local development
- [ ] Configure hot-reloading for both frontend and backend

**Deliverables**:
- Basic "Hello World" running on both backend and frontend
- Docker Compose successfully orchestrating services
- Development workflow documentation

### 1.3 Database & Configuration
**Priority**: Critical | **Effort**: 2-3 days

- [ ] Set up SQLite database for development
- [ ] Configure SQLModel with SQLAlchemy
- [ ] Initialize Alembic for database migrations
- [ ] Implement Pydantic BaseSettings for environment configuration
- [ ] Create initial database schema (users table basic structure)
- [ ] Test database connection and first migration

**Deliverables**:
- Working database with migration system
- Configuration management via environment variables
- Database schema documentation

---

## Phase 2: Authentication & Security (Week 3-4)

### 2.1 Basic Authentication System
**Priority**: Critical | **Effort**: 4-5 days

- [ ] Implement user model with password hashing (bcrypt/argon2)
- [ ] Create user registration endpoint (POST /api/users)
- [ ] Implement login endpoint with JWT token generation
- [ ] Set up FastAPI OAuth2 password bearer scheme
- [ ] Implement JWT token validation middleware
- [ ] Create logout mechanism (token invalidation/blacklist if needed)
- [ ] Add password strength validation

**Deliverables**:
- Working username/password authentication
- Secure password storage (hashed)
- JWT-based session management
- API endpoints: `/api/auth/login`, `/api/auth/register`, `/api/auth/logout`

### 2.2 Frontend Authentication UI
**Priority**: Critical | **Effort**: 3-4 days

- [ ] Design and implement login page
- [ ] Design and implement registration page
- [ ] Implement JWT token storage (secure cookie or httpOnly)
- [ ] Create authentication context/state management
- [ ] Implement protected route wrapper
- [ ] Add authentication error handling and user feedback
- [ ] Create "Forgot Password" UI placeholder

**Deliverables**:
- Functional login/registration forms
- Authentication state management
- Protected routes functionality
- Responsive, accessible UI design

### 2.3 LDAP Integration
**Priority**: High | **Effort**: 3-4 days

- [ ] Install and configure ldap3 library
- [ ] Implement LDAP connection configuration (via env vars)
- [ ] Create LDAP authentication endpoint
- [ ] Add fallback logic (LDAP first, then local DB)
- [ ] Implement user provisioning from LDAP (create local record on first login)
- [ ] Add LDAP connection health check
- [ ] Test against Active Directory test environment

**Deliverables**:
- Working LDAP authentication
- Dual authentication support (LDAP + local)
- LDAP configuration documentation
- API endpoint: `/api/auth/ldap-login`

### 2.4 Role-Based Access Control (RBAC)
**Priority**: High | **Effort**: 2-3 days

- [ ] Add roles to user model (admin, user, etc.)
- [ ] Implement role checking dependency injection
- [ ] Create admin-only endpoint protections
- [ ] Add role information to JWT claims
- [ ] Implement permission checking utilities
- [ ] Write unit tests for RBAC

**Deliverables**:
- Working RBAC system
- Admin-protected endpoints
- Role management in database

---

## Phase 3: User Management (Week 5-6)

### 3.1 User Profile Management
**Priority**: High | **Effort**: 3-4 days

- [ ] Create user profile endpoints (GET/PUT /api/users/me)
- [ ] Implement profile update functionality (name, email, etc.)
- [ ] Add password change endpoint with current password verification
- [ ] Create profile page UI component
- [ ] Implement form validation (frontend and backend)
- [ ] Add user avatar upload (optional)

**Deliverables**:
- User profile management API
- Profile settings page
- Password change functionality
- API endpoints: `/api/users/me`, `/api/users/me/password`

### 3.2 Admin User Management Dashboard
**Priority**: High | **Effort**: 4-5 days

- [ ] Create admin endpoints for user CRUD operations
  - GET /api/admin/users (list with pagination)
  - POST /api/admin/users (create)
  - PUT /api/admin/users/{id} (update)
  - DELETE /api/admin/users/{id} (soft delete/disable)
- [ ] Implement user search and filtering
- [ ] Add user status management (active/disabled)
- [ ] Create admin dashboard UI with user table
- [ ] Implement user creation modal/form
- [ ] Add user edit modal/form
- [ ] Implement user deletion confirmation

**Deliverables**:
- Complete admin user management API
- Admin dashboard with user table
- User CRUD operations
- Search and filter capabilities

### 3.3 Email & Password Reset
**Priority**: Medium | **Effort**: 3-4 days

- [ ] Implement password reset token generation
- [ ] Create password reset request endpoint
- [ ] Set up email service integration (SMTP configuration)
- [ ] Create password reset confirmation endpoint
- [ ] Design password reset request UI
- [ ] Design password reset form UI
- [ ] Add email templates for password reset
- [ ] Implement token expiration (e.g., 24 hours)

**Deliverables**:
- Working password reset flow
- Email notification system
- Reset password UI pages
- API endpoints: `/api/auth/reset-password`, `/api/auth/reset-password/confirm`

---

## Phase 4: Personal Access Tokens (Week 7)

### 4.1 PAT Backend Implementation
**Priority**: High | **Effort**: 3-4 days

- [ ] Create PAT model (token, user_id, name, scopes, expiry, created_at)
- [ ] Implement PAT generation with secure hashing
- [ ] Create PAT CRUD endpoints
  - POST /api/users/me/tokens (create)
  - GET /api/users/me/tokens (list user's tokens)
  - DELETE /api/users/me/tokens/{id} (revoke)
- [ ] Implement PAT authentication middleware
- [ ] Add scope validation logic
- [ ] Implement token expiration checking
- [ ] Write PAT validation tests

**Deliverables**:
- PAT data model and database schema
- PAT management API endpoints
- PAT authentication support
- Scope-based access control

### 4.2 PAT Frontend UI
**Priority**: High | **Effort**: 2-3 days

- [ ] Create PAT management page
- [ ] Implement token creation form (name, scopes, expiry)
- [ ] Display generated token once (copy-to-clipboard)
- [ ] Show list of user's active tokens
- [ ] Add token revocation confirmation
- [ ] Display token metadata (name, created, last used, expiry)
- [ ] Add security warnings about token handling

**Deliverables**:
- PAT management UI page
- Token creation and revocation workflows
- User-friendly token display and management

---

## Phase 5: Sample CRUD Entity (Week 8)

### 5.1 Items/Projects CRUD Backend
**Priority**: Medium | **Effort**: 2-3 days

- [ ] Design sample entity model (e.g., "Items" with title, description, owner_id)
- [ ] Create database migration for items table
- [ ] Implement CRUD endpoints
  - GET /api/items (list, with filtering by owner)
  - POST /api/items (create)
  - GET /api/items/{id} (read)
  - PUT /api/items/{id} (update)
  - DELETE /api/items/{id} (delete)
- [ ] Add ownership validation (users can only edit their items)
- [ ] Implement pagination and sorting
- [ ] Write CRUD tests

**Deliverables**:
- Sample entity data model
- Complete CRUD API
- Ownership-based access control
- API documentation in Swagger

### 5.2 Items/Projects CRUD Frontend
**Priority**: Medium | **Effort**: 3-4 days

- [ ] Create items list page with table/cards view
- [ ] Implement create item form/modal
- [ ] Implement edit item form/modal
- [ ] Add delete confirmation dialog
- [ ] Implement search and filtering UI
- [ ] Add pagination controls
- [ ] Implement sorting functionality
- [ ] Add empty state and loading states

**Deliverables**:
- Items management UI
- Complete CRUD operations in frontend
- Responsive design for all CRUD views

---

## Phase 6: Testing & Quality Assurance (Week 9-10)

### 6.1 Backend Testing
**Priority**: High | **Effort**: 4-5 days

- [ ] Set up PyTest configuration and fixtures
- [ ] Write unit tests for authentication logic
- [ ] Write tests for user management endpoints
- [ ] Write tests for PAT functionality
- [ ] Write tests for CRUD operations
- [ ] Implement integration tests with test database
- [ ] Add test coverage reporting (aim for >80%)
- [ ] Set up test data factories/fixtures

**Deliverables**:
- Comprehensive test suite (PyTest)
- Test coverage report
- CI-ready test configuration

### 6.2 Frontend Testing
**Priority**: High | **Effort**: 4-5 days

- [ ] Set up Vitest configuration
- [ ] Write component unit tests (authentication forms, etc.)
- [ ] Set up Playwright for E2E tests
- [ ] Write E2E tests for authentication flows
- [ ] Write E2E tests for user management
- [ ] Write E2E tests for CRUD operations
- [ ] Add visual regression testing (optional)
- [ ] Generate test coverage reports

**Deliverables**:
- Frontend unit tests (Vitest)
- E2E test suite (Playwright)
- Test documentation

### 6.3 Security Testing & Hardening
**Priority**: Critical | **Effort**: 3-4 days

- [ ] Perform security audit of authentication flows
- [ ] Test SQL injection prevention
- [ ] Test XSS prevention
- [ ] Verify CSRF protection
- [ ] Test rate limiting implementation
- [ ] Audit secret management (no hardcoded secrets)
- [ ] Review HTTPS/TLS configuration
- [ ] Test token expiration and invalidation
- [ ] Perform dependency vulnerability scan

**Deliverables**:
- Security audit report
- Fixed vulnerabilities
- Security testing documentation

---

## Phase 7: UI/UX Polish & Documentation (Week 11)

### 7.1 UI/UX Improvements
**Priority**: Medium | **Effort**: 3-4 days

- [ ] Implement consistent styling with Tailwind CSS/Chakra UI
- [ ] Add loading spinners and skeletons
- [ ] Implement toast notifications for user feedback
- [ ] Add form validation error messages
- [ ] Improve responsive design for mobile
- [ ] Add accessibility features (ARIA labels, keyboard navigation)
- [ ] Implement dark mode support (optional)
- [ ] Create consistent color scheme and branding

**Deliverables**:
- Polished, consistent UI design
- Responsive layouts
- Accessibility improvements
- Style guide documentation

### 7.2 API Documentation
**Priority**: High | **Effort**: 2 days

- [ ] Enhance FastAPI automatic Swagger documentation
- [ ] Add detailed endpoint descriptions
- [ ] Include request/response examples
- [ ] Document authentication requirements
- [ ] Create API usage guide
- [ ] Add code examples for common operations

**Deliverables**:
- Comprehensive API documentation (Swagger/ReDoc)
- API usage guide for developers

### 7.3 User Documentation
**Priority**: Medium | **Effort**: 2-3 days

- [ ] Create user guide for common workflows
- [ ] Document login procedures (local and LDAP)
- [ ] Write PAT management guide
- [ ] Create admin user guide
- [ ] Add troubleshooting section
- [ ] Create video tutorials (optional)

**Deliverables**:
- User documentation
- Admin guide
- FAQ and troubleshooting guide

---

## Phase 8: Deployment & DevOps (Week 12-13)

### 8.1 Docker Production Configuration
**Priority**: Critical | **Effort**: 3-4 days

- [ ] Create production Dockerfiles (multi-stage builds)
- [ ] Optimize Docker images (use slim base images)
- [ ] Configure non-root container users
- [ ] Set up Docker Compose for production
- [ ] Implement health check endpoints
- [ ] Configure proper logging (JSON format)
- [ ] Set up log rotation in Docker
- [ ] Add resource limits to containers

**Deliverables**:
- Production-ready Dockerfiles
- Optimized Docker Compose configuration
- Health check implementation

### 8.2 CI/CD Pipeline
**Priority**: High | **Effort**: 3-4 days

- [ ] Set up GitHub Actions or Jenkins pipeline
- [ ] Configure automated testing on PR/commit
- [ ] Implement linting checks (pylint, eslint)
- [ ] Set up automated Docker image building
- [ ] Configure image tagging strategy (semantic versioning)
- [ ] Implement automated deployment to staging
- [ ] Add deployment approval gates for production
- [ ] Set up rollback procedures

**Deliverables**:
- Working CI/CD pipeline
- Automated testing and deployment
- Pipeline documentation

### 8.3 Production Environment Setup
**Priority**: Critical | **Effort**: 4-5 days

- [ ] Set up Linux server on Azure GCC High
- [ ] Configure TLS/SSL certificates (HTTPS)
- [ ] Set up reverse proxy (nginx) if needed
- [ ] Configure firewall rules and security groups
- [ ] Set up SQL Server instance (if using in production)
- [ ] Configure database backups (coordinate with IT)
- [ ] Implement monitoring and alerting
- [ ] Set up centralized logging (optional: ELK stack)
- [ ] Configure environment variables securely

**Deliverables**:
- Production server configured
- HTTPS enabled
- Database production setup
- Monitoring and logging system

### 8.4 Database Migration Strategy
**Priority**: High | **Effort**: 2 days

- [ ] Document SQLite to SQL Server migration path
- [ ] Create SQL Server connection configuration
- [ ] Test Alembic migrations with SQL Server
- [ ] Create data migration scripts
- [ ] Document backup and restore procedures
- [ ] Test rollback procedures

**Deliverables**:
- Database migration documentation
- SQL Server configuration guide
- Migration scripts

---

## Phase 9: Advanced Features (Week 14-15)

### 9.1 SSO Integration (SAML/OIDC)
**Priority**: Low (Future) | **Effort**: 5-6 days

- [ ] Research Azure AD (EntraID) SAML requirements for GCC High
- [ ] Install and configure PySAML2 or python-saml
- [ ] Implement SAML authentication flow
- [ ] Create SSO login endpoints
- [ ] Add SSO login button to frontend
- [ ] Test with Azure AD test tenant
- [ ] Document SSO configuration steps

**Deliverables**:
- SSO authentication support
- Azure AD integration
- SSO configuration guide

### 9.2 Advanced Admin Features
**Priority**: Low | **Effort**: 3-4 days

- [ ] Implement audit logging (user actions)
- [ ] Create admin analytics dashboard
- [ ] Add bulk user operations (import/export)
- [ ] Implement user session management (view/revoke active sessions)
- [ ] Add system configuration page
- [ ] Create admin activity reports

**Deliverables**:
- Enhanced admin capabilities
- Audit logging system
- Admin reporting features

### 9.3 Performance Optimization
**Priority**: Medium | **Effort**: 3-4 days

- [ ] Implement API response caching (Redis optional)
- [ ] Add database query optimization (indexes)
- [ ] Implement frontend code splitting
- [ ] Add lazy loading for routes
- [ ] Optimize bundle size
- [ ] Implement API rate limiting
- [ ] Add CDN for static assets (optional)

**Deliverables**:
- Performance improvements
- Load testing results
- Optimization documentation

---

## Phase 10: Launch & Maintenance (Week 16+)

### 10.1 Pre-Launch Checklist
**Priority**: Critical | **Effort**: 2-3 days

- [ ] Perform full security audit
- [ ] Complete penetration testing
- [ ] Verify all tests passing
- [ ] Verify GCC High compliance requirements
- [ ] Complete user acceptance testing (UAT)
- [ ] Review and update all documentation
- [ ] Create deployment runbook
- [ ] Train support team
- [ ] Prepare rollback plan
- [ ] Set up incident response procedures

**Deliverables**:
- Security audit report
- UAT sign-off
- Complete documentation
- Deployment runbook

### 10.2 Production Deployment
**Priority**: Critical | **Effort**: 1-2 days

- [ ] Schedule maintenance window
- [ ] Deploy to production environment
- [ ] Run database migrations
- [ ] Verify all services healthy
- [ ] Perform smoke tests
- [ ] Monitor error rates and performance
- [ ] Communicate launch to users

**Deliverables**:
- Live production system
- Deployment report
- Launch announcement

### 10.3 Post-Launch Support
**Priority**: High | **Effort**: Ongoing

- [ ] Monitor application health and errors
- [ ] Respond to user feedback and issues
- [ ] Create bug fix process
- [ ] Plan feature enhancements based on usage
- [ ] Regular dependency updates
- [ ] Security patch management
- [ ] Performance monitoring and optimization
- [ ] Regular backup verification

**Deliverables**:
- Support procedures
- Issue tracking system
- Regular maintenance schedule

---

## Success Criteria

### Technical Requirements
- ✅ All tests passing with >80% code coverage
- ✅ API response time <200ms for 95th percentile
- ✅ Frontend loads in <3 seconds
- ✅ Zero critical security vulnerabilities
- ✅ 99.9% uptime during business hours

### Functional Requirements
- ✅ Users can register, login, and manage profiles
- ✅ LDAP authentication working with Active Directory
- ✅ Admins can manage users (CRUD operations)
- ✅ Users can create and manage personal access tokens
- ✅ Sample CRUD entity fully functional
- ✅ All features accessible via responsive UI

### Compliance Requirements
- ✅ GCC High compliance verified
- ✅ All traffic encrypted (HTTPS/TLS)
- ✅ Secrets properly managed (no hardcoded credentials)
- ✅ Audit logging implemented
- ✅ Data backup strategy in place

---

## Risk Management

### High Priority Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| LDAP integration issues with AD | High | Early testing with AD test environment; fallback to local auth |
| GCC High compliance gaps | Critical | Regular compliance reviews; Azure GCC documentation review |
| Security vulnerabilities | Critical | Regular security audits; automated vulnerability scanning |
| Database migration issues | High | Thorough testing; backup and rollback procedures |
| Performance bottlenecks | Medium | Load testing early; performance monitoring |

### Dependencies & Assumptions
- **Assumption**: Access to Active Directory test environment for LDAP testing
- **Assumption**: IT support for SQL Server setup and backups
- **Assumption**: Azure GCC High tenant access for deployment
- **Dependency**: TLS/SSL certificate provisioning
- **Dependency**: Network configuration and firewall rules

---

## Resource Requirements

### Team
- **Backend Developer**: 1 FTE (Python/FastAPI expertise)
- **Frontend Developer**: 1 FTE (React/TypeScript expertise)
- **DevOps Engineer**: 0.5 FTE (Docker, CI/CD, Azure)
- **QA Engineer**: 0.5 FTE (Testing, security)
- **Project Manager**: 0.25 FTE (coordination, documentation)

### Infrastructure
- **Development**: Local machines + Docker Desktop
- **Staging**: Linux VM on Azure (4 vCPU, 8GB RAM)
- **Production**: Linux VM on Azure GCC High (8 vCPU, 16GB RAM)
- **Database**: SQL Server instance (managed by IT)

### Tools & Licenses
- GitHub/GitLab repository
- Azure subscription (GCC High)
- IDE licenses (VSCode/PyCharm)
- Testing tools (open source)
- Monitoring tools (optional: Datadog, New Relic)

---

## Timeline Summary

| Phase | Duration | Week(s) |
|-------|----------|---------|
| Phase 1: Foundation & Setup | 2 weeks | 1-2 |
| Phase 2: Authentication & Security | 2 weeks | 3-4 |
| Phase 3: User Management | 2 weeks | 5-6 |
| Phase 4: Personal Access Tokens | 1 week | 7 |
| Phase 5: Sample CRUD Entity | 1 week | 8 |
| Phase 6: Testing & QA | 2 weeks | 9-10 |
| Phase 7: UI/UX & Documentation | 1 week | 11 |
| Phase 8: Deployment & DevOps | 2 weeks | 12-13 |
| Phase 9: Advanced Features | 2 weeks | 14-15 |
| Phase 10: Launch & Maintenance | 1+ week | 16+ |
| **Total Initial Development** | **16 weeks** | **~4 months** |

---

## Next Steps

1. **Week 1, Day 1**: Kick-off meeting with stakeholders
2. **Week 1, Day 2**: Set up development environments
3. **Week 1, Day 3**: Initialize project repositories
4. **Week 1, Day 4-5**: Begin Phase 1 implementation
5. **Week 2**: Complete foundation and begin authentication work

---

## References & Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Full-Stack Template](https://github.com/fastapi/full-stack-fastapi-template)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [React + Vite Documentation](https://vitejs.dev/guide/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Azure GCC High Documentation](https://docs.microsoft.com/en-us/azure/azure-government/)
- [LDAP3 Python Library](https://ldap3.readthedocs.io/)
- [12-Factor App Methodology](https://12factor.net/)

---

## Document Control

- **Version**: 1.0
- **Created**: 2025-10-30
- **Last Updated**: 2025-10-30
- **Status**: Draft
- **Owner**: Development Team
- **Approvers**: Project Stakeholders

---

## Appendix A: Folder Structure

```
fastapi-demo/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── admin.py
│   │   │   ├── tokens.py
│   │   │   └── items.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── deps.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── token.py
│   │   │   └── item.py
│   │   ├── crud/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── token.py
│   │   │   └── item.py
│   │   └── tests/
│   ├── alembic/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
├── docker-compose.prod.yml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── docs/
│   ├── api/
│   ├── user-guide/
│   └── admin-guide/
├── LICENSE
├── README.md
└── plan-001-implementation.md
```

## Appendix B: Key Configuration Files

### Backend requirements.txt (sample)
```txt
fastapi[all]==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
ldap3==2.9.1
pytest==7.4.3
pytest-asyncio==0.21.1
```

### Frontend package.json (sample dependencies)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "@tanstack/react-query": "^5.12.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.42",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.2",
    "vite": "^5.0.5",
    "vitest": "^1.0.4",
    "@playwright/test": "^1.40.0"
  }
}
```

---

**End of Implementation Plan**
