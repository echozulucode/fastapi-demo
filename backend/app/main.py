"""
FastAPI Intranet Demo - Main Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.api import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Create database tables
    create_db_and_tables()
    
    # Create initial admin user if it doesn't exist
    from app.core.database import get_session
    from app.crud import user as crud_user
    from app.models.user import UserCreate
    
    session = next(get_session())
    admin = crud_user.get_user_by_email(session, settings.FIRST_SUPERUSER_EMAIL)
    if not admin:
        admin_create = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Admin User",
            is_admin=True,
            is_active=True
        )
        crud_user.create_user(session, admin_create)
        print(f"✅ Created admin user: {settings.FIRST_SUPERUSER_EMAIL}")
    
    yield
    
    # Shutdown: cleanup if needed


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A full-stack intranet application with FastAPI backend and React frontend",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "Welcome to FastAPI Intranet Demo",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "authentication": "enabled"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
