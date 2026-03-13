# Docker Build Guide

## Overview

ParseHub Dashboard uses multi-stage Docker builds for optimal image size and security.

## Building Images

### Backend Image

```bash
docker build \
  -f infrastructure/docker/Dockerfile-backend \
  -t parsehub-backend:latest \
  -t parsehub-backend:v1.0.0 \
  .
```

**Image Details:**
- Base: `python:3.12-slim` (small, optimized)
- Security: Non-root user (appuser)
- Health Checks: Built-in
- Ports: 5000 (Flask)

### Frontend Image

```bash
docker build \
  -f infrastructure/docker/Dockerfile-frontend \
  -t parsehub-frontend:latest \
  -t parsehub-frontend:v1.0.0 \
  .
```

**Image Details:**
- Build Stage: `node:20-alpine` (compile Next.js)
- Runtime Stage: `node:20-alpine` (lightweight)
- Security: Non-root user (appuser)
- Health Checks: Built-in
- Ports: 3000 (Next.js)

## Testing Locally

### Run with Docker Compose

```bash
docker-compose up -d

# Check if running
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Test endpoints
curl http://localhost:5000/health
curl http://localhost:3000/health

# Stop
docker-compose down
```

### Run Individual Containers

```bash
# Backend
docker run -d \
  -p 5000:5000 \
  -e SNOWFLAKE_ACCOUNT=your-account \
  -e SNOWFLAKE_USER=your-user \
  -e SNOWFLAKE_PASSWORD=your-password \
  -e SNOWFLAKE_WAREHOUSE=your-warehouse \
  -e SNOWFLAKE_DATABASE=your-db \
  -e SNOWFLAKE_SCHEMA=your-schema \
  --name parsehub-backend \
  parsehub-backend:latest

# Frontend
docker run -d \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:5000 \
  --name parsehub-frontend \
  parsehub-frontend:latest
```

## Pushing to Container Registry

### Docker Hub

```bash
# Tag image
docker tag parsehub-backend:latest docker.io/YOUR_USERNAME/parsehub-backend:latest

# Login
docker login

# Push
docker push docker.io/YOUR_USERNAME/parsehub-backend:latest
```

### AWS ECR

```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag parsehub-backend:latest \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/parsehub-backend:latest

# Push
docker push \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/parsehub-backend:latest
```

### Google Container Registry (GCR)

```bash
# Configure Docker (one time)
gcloud auth configure-docker

# Tag image
docker tag parsehub-backend:latest \
  gcr.io/YOUR_PROJECT_ID/parsehub-backend:latest

# Push
docker push \
  gcr.io/YOUR_PROJECT_ID/parsehub-backend:latest
```

## Best Practices

### Image Optimization

1. **Multi-stage builds** - Reduces final image size
   - Backend: ~300MB (Python deps only, not dev tools)
   - Frontend: ~250MB (Next.js built app, no build tools)

2. **Non-root user** - Security
   - Runs as `appuser:1000` (not root)
   - Prevents privilege escalation exploits

3. **Health checks** - Monitoring
   - `/health` endpoint responds in <5 seconds
   - Container restarts if unhealthy

4. **Layer caching** - Faster builds
   - Dependencies copied first (cached)
   - Source code copied last (changes frequently)

### Build Optimization

```bash
# Build with BuildKit (faster, better caching)
DOCKER_BUILDKIT=1 docker build -f Dockerfile-backend .

# View build layers
docker history parsehub-backend:latest

# Check image size
docker images | grep parsehub
```

## Tagging Strategy

### Semantic Versioning
```bash
docker tag parsehub-backend:latest parsehub-backend:1.0.0
docker tag parsehub-backend:latest parsehub-backend:1.0
docker tag parsehub-backend:latest parsehub-backend:1
```

### Environment Tags
```bash
docker tag parsehub-backend:latest parsehub-backend:prod
docker tag parsehub-backend:latest parsehub-backend:dev
docker tag parsehub-backend:latest parsehub-backend:staging
```

## Dockerfile Structure

### Backend Pattern

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim
COPY --from=builder /app /app
COPY backend/ /app/
USER appuser  # Non-root
EXPOSE 5000
HEALTHCHECK ...
CMD ["gunicorn", ...]
```

### Frontend Pattern

```dockerfile
# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY frontend/package*.json .
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Runtime
FROM node:20-alpine
COPY --from=builder /app/.next ./.next
USER appuser  # Non-root
EXPOSE 3000
HEALTHCHECK ...
CMD ["npm", "start"]
```

## Troubleshooting

### Image too large?
```bash
# Check layer sizes
docker history parsehub-backend:latest --human --no-trunc

# Use alpine base images
# Use --no-cache-dir for pip
# Remove build dependencies in multi-stage build
```

### Image won't start?
```bash
# Check logs
docker logs CONTAINER_ID

# Run bash for debugging
docker run -it parsehub-backend:latest /bin/bash

# Check health
docker inspect CONTAINER_ID | grep Health -A 5
```

### Application fails in container?
```bash
# Environment variables set correctly?
docker inspect CONTAINER_ID | grep Env -B 1 -A 20

# Port exposed?
docker port CONTAINER_ID

# Network connectivity?
docker exec CONTAINER_ID ping snowflake-server
```

## Next Steps

1. Build images locally: `docker build -f infrastructure/docker/Dockerfile-* .`
2. Test with docker-compose: `docker-compose up`
3. Push to registry (Docker Hub, ECR, GCR, etc.)
4. Deploy to Kubernetes: `kubectl apply -k infrastructure/kubernetes/overlays/local`

See **KUBERNETES_DEPLOYMENT_GUIDE.md** for Kubernetes-specific steps.
