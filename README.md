# FastAPI Intranet Demo

A production-ready, full-stack intranet web application demonstrating enterprise features including authentication (username/password + LDAP), user management, personal access tokens, and CRUD operations.

## 🚀 Features

- **Backend**: FastAPI (Python) with SQLModel/SQLAlchemy
- **Frontend**: React + TypeScript + Vite
- **Database**: SQLite (development) → SQL Server (production)
- **Authentication**: JWT tokens, LDAP/Active Directory, future SAML/OIDC SSO
- **Docker**: Full containerization with Docker Compose
- **Testing**: PyTest (backend), Vitest + Playwright (frontend)

## 📋 Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Docker and Docker Compose (optional, for containerized deployment)
- Git

## 🛠️ Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fastapi-demo
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and set your SECRET_KEY (generate with: openssl rand -hex 32)

# Run the backend
python -m uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000  
API Documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Run the frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

### 4. Docker Setup (Alternative)

```bash
# Development mode with hot-reloading
docker-compose -f docker-compose.dev.yml up

# Production mode
docker-compose up
```

## 📁 Project Structure

```
fastapi-demo/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Configuration, security
│   │   ├── models/      # Database models
│   │   ├── crud/        # Database operations
│   │   └── tests/       # Tests
│   ├── alembic/         # Database migrations
│   └── requirements.txt
├── frontend/            # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API client
│   │   └── types/       # TypeScript types
│   └── package.json
├── docs/                # Documentation
├── docker-compose.yml   # Production Docker config
├── docker-compose.dev.yml  # Development Docker config
└── README.md
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📚 Documentation

- **Project Context**: See [CONTEXT.md](CONTEXT.md)
- **Implementation Plan**: See [plan-001-implementation.md](plan-001-implementation.md)
- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **Copilot Instructions**: See [.github/copilot-instructions.md](.github/copilot-instructions.md)

## 🔐 Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- HTTPS/TLS required in production
- Environment variables for secrets (never commit .env files)
- SQL injection prevention via SQLModel
- XSS prevention via React
- CSRF protection

## 🚢 Deployment

The application is designed for deployment on Azure Government Cloud (GCC High) using Docker Compose on a Linux server.

See the [Implementation Plan](plan-001-implementation.md) Phase 8 for detailed deployment instructions.

## 📖 Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes with tests
3. Run tests: `pytest` and `npm test`
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature/your-feature`
6. Create a Pull Request

## 🤝 Contributing

See [CONTEXT.md](CONTEXT.md) for coding conventions and contribution guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

**Backend won't start**
- Check Python version (3.10+ required)
- Verify dependencies installed: `pip install -r requirements.txt`
- Check `.env` file configuration

**Frontend won't start**
- Check Node.js version (18+ recommended)
- Clear and reinstall: `rm -rf node_modules && npm install`
- Check `.env` file configuration

**Docker issues**
- Ensure Docker Desktop is running
- Check port conflicts (8000, 3000)
- Clear cache: `docker system prune -a`

## 📞 Support

For questions or issues:
1. Check [CONTEXT.md](CONTEXT.md)
2. Review [plan-001-implementation.md](plan-001-implementation.md)
3. Check documentation in `docs/`
4. Contact project maintainers

---

**Status**: Phase 1 - Foundation Complete ✅  
**Version**: 1.0.0  
**Last Updated**: 2025-10-30
