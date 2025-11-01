# Podman Deployment Testing

## Status: ✅ COMPLETED

Successfully tested deployment using Podman and podman-compose as an alternative to Docker.

## Setup Steps

### 1. Install podman-compose
```bash
pip install podman-compose
```

### 2. Build and Start Services
```bash
# Build images
python -m podman_compose -f docker-compose.yml build

# Start services in detached mode
python -m podman_compose -f docker-compose.yml up -d

# Check status
podman ps
```

### 3. Stop Services
```bash
# Stop all services
python -m podman_compose -f docker-compose.yml down

# Stop and remove volumes
python -m podman_compose -f docker-compose.yml down -v
```

## Test Results

All deployment tests passed successfully:

### ✅ Backend Health Check
- **URL**: http://127.0.0.1:8000/health
- **Status**: 200 OK
- **Response**: 
  ```json
  {
    "status": "healthy",
    "app": "FastAPI Intranet Demo",
    "version": "1.0.0"
  }
  ```

### ✅ Backend API Documentation
- **URL**: http://127.0.0.1:8000/docs
- **Status**: 200 OK
- **Type**: Interactive Swagger UI

### ✅ Frontend Application
- **URL**: http://127.0.0.1:3000
- **Status**: 200 OK
- **Type**: React SPA served by Nginx

### ✅ Authentication API
- **URL**: http://127.0.0.1:8000/api/auth/login
- **Status**: 200 OK
- **Method**: POST (application/x-www-form-urlencoded)
- **Response**: JWT access token with bearer type

## Container Details

### Backend Container
- **Image**: localhost/fastapi-demo_backend:latest
- **Ports**: 8000:8000
- **Base**: Python 3.11-slim
- **Server**: Uvicorn ASGI server
- **Database**: SQLite (volume mounted)
- **Features**:
  - Multi-stage build for optimized size
  - Non-root user (appuser)
  - Automatic database initialization
  - Default admin user creation

### Frontend Container
- **Image**: localhost/fastapi-demo_frontend:latest
- **Ports**: 3000:80
- **Base**: Nginx Alpine
- **Build**: Node.js 18 build stage
- **Features**:
  - Multi-stage build
  - Static file serving
  - SPA routing support
  - Gzip compression
  - Security headers

## Access Information

### URLs
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend App: http://localhost:3000

### Default Credentials
- **Email**: admin@example.com
- **Password**: changethis

⚠️ **Important**: Change the default password in production!

## Testing

Run the automated deployment test:
```bash
node test-podman-deployment.js
```

This test verifies:
1. Backend health endpoint
2. API documentation availability
3. Frontend accessibility
4. Login functionality with JWT token generation

## Notes

### IPv4 vs IPv6
- Podman on Windows may have IPv6 connectivity issues
- Use `127.0.0.1` instead of `localhost` for reliable connections
- The test script explicitly uses IPv4 addresses

### Volume Persistence
- Backend data is stored in a Podman volume: `fastapi-demo_backend-data`
- Database persists across container restarts
- Use `down -v` to remove volumes when cleaning up

### Healthcheck
- Backend healthcheck requires curl in the container
- Current healthcheck may show as unhealthy if curl is missing
- Application is functional despite healthcheck status

## Comparison: Podman vs Docker

Both work identically with the docker-compose.yml file:

**Docker:**
```bash
docker compose up -d
docker compose down
```

**Podman:**
```bash
python -m podman_compose -f docker-compose.yml up -d
python -m podman_compose -f docker-compose.yml down
```

## Next Steps

1. ✅ Podman deployment verified
2. Configure environment variables for production
3. Set up TLS/SSL certificates
4. Configure reverse proxy (Traefik/Nginx)
5. Set up monitoring and logging
6. Implement backup strategy for database

## Troubleshooting

### Containers not starting
```bash
# Check logs
podman logs fastapi-backend
podman logs fastapi-frontend

# Restart services
python -m podman_compose -f docker-compose.yml restart
```

### Port conflicts
```bash
# Check what's using the ports
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

### Build issues
```bash
# Clean rebuild
python -m podman_compose -f docker-compose.yml down
podman system prune -a
python -m podman_compose -f docker-compose.yml build --no-cache
```
