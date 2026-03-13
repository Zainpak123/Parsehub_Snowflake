# Infrastructure & Deployment Guide

## Directory Structure

```
infrastructure/
├── kubernetes/              # Kubernetes manifests
│   ├── README.md
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── backend-hpa.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── configmap.yaml
│   └── secrets.yaml
├── docker/                  # Docker configurations
│   ├── Dockerfile-backend
│   ├── Dockerfile-frontend
│   └── .dockerignore
└── scripts/                 # Deployment scripts
    ├── deploy.sh
    ├── rollback.sh
    └── health-check.sh
```

## Docker

### Build Images

**Backend:**
```bash
docker build -f infrastructure/docker/Dockerfile-backend \
  -t parsehub-backend:latest \
  -t parsehub-backend:v1.0.0 .
```

**Frontend:**
```bash
docker build -f infrastructure/docker/Dockerfile-frontend \
  -t parsehub-frontend:latest \
  -t parsehub-frontend:v1.0.0 .
```

### Local Testing

```bash
# Start both services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

### Push to Registry

```bash
# Docker Hub
docker tag parsehub-backend:latest yourregistry/parsehub-backend:latest
docker push yourregistry/parsehub-backend:latest

# AWS ECR
aws ecr get-login-password --region us-west-2 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-west-2.amazonaws.com
docker tag parsehub-backend:latest 123456789.dkr.ecr.us-west-2.amazonaws.com/parsehub-backend:latest
docker push 123456789.dkr.ecr.us-west-2.amazonaws.com/parsehub-backend:latest
```

## Kubernetes

### Prerequisite

- Kubernetes cluster running (v1.24+)
- `kubectl` configured
- Container registry access
- Secrets configured

### Deploy Application

```bash
# 1. Create namespace
kubectl create namespace parsehub

# 2. Create secrets
kubectl create secret generic snowflake-credentials \
  --from-literal=account=YOUR_ACCOUNT \
  --from-literal=user=YOUR_USER \
  --from-literal=password=YOUR_PASSWORD \
  -n parsehub

# 3. Apply manifests
kubectl apply -f infrastructure/kubernetes/
kubectl apply -f infrastructure/kubernetes/backend-deployment.yaml
kubectl apply -f infrastructure/kubernetes/frontend-deployment.yaml

# 4. Verify deployment
kubectl get pods -n parsehub
kubectl get svc -n parsehub
```

### Check Status

```bash
# Watch pods start
kubectl get pods -n parsehub -w

# View pod logs
kubectl logs -f -n parsehub deployment/parsehub-backend

# Exec into pod
kubectl exec -it -n parsehub pod/parsehub-backend-xxx bash

# Port forward
kubectl port-forward -n parsehub svc/parsehub-backend 5000:5000
```

### Configuration

#### ConfigMap

Update `configmap.yaml`:
```yaml
data:
  FLASK_ENV: production
  LOG_LEVEL: INFO
  PORT: "5000"
```

#### Secrets

Create secret for sensitive data:
```bash
kubectl create secret generic parsehub-secrets \
  --from-literal=parsehub-api-key=YOUR_KEY \
  --from-literal=snowflake-password=YOUR_PASSWORD \
  -n parsehub
```

### Scaling

#### Manual Scaling

```bash
# Scale backend to 5 replicas
kubectl scale deployment parsehub-backend --replicas=5 -n parsehub

# View HPA status
kubectl get hpa -n parsehub
```

#### Auto-Scaling (HPA)

Configured in `backend-hpa.yaml`:
- Min replicas: 2
- Max replicas: 10
- CPU threshold: 70%
- Memory threshold: 80%

### Monitoring & Logs

```bash
# View pod metrics
kubectl top nodes
kubectl top pods -n parsehub

# Stream logs
kubectl logs -f -n parsehub deployment/parsehub-backend

# Get pod events
kubectl describe pod <pod-name> -n parsehub
```

### Updating Deployment

```bash
# Update image
kubectl set image deployment/parsehub-backend \
  parsehub-backend=yourregistry/parsehub-backend:v1.1.0 \
  -n parsehub

# View rollout status
kubectl rollout status deployment/parsehub-backend -n parsehub

# Rollback if needed
kubectl rollout undo deployment/parsehub-backend -n parsehub
```

## Continuous Deployment

### CI/CD Pipeline

See `.github/workflows/` for full configuration.

**Pipeline Steps:**
1. Test - Unit & integration tests
2. Build - Docker image creation
3. Push - Push to registry
4. Deploy - Update K8s cluster

### GitHub Actions

Trigger on:
- Push to `main` branch
- Manual trigger
- Version tags (v*)

## Environment Setup

### Development
```bash
docker-compose up -d

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

### Staging
```bash
# Deploy to staging K8s cluster
kubectl apply -f infrastructure/kubernetes/ -n staging
```

### Production
```bash
# Deploy with blue/green strategy
./infrastructure/scripts/deploy.sh production
```

## Backup & Recovery

### Database Backups

```bash
# Snowflake automatic backups (1-35 days retention)
# Configure in Snowflake web console

# Manual export
SELECT * FROM PARSEHUB_DB.PARSEHUB_DB.products 
LIMIT 10000 TO @~/products.csv;
```

### Disaster Recovery

**Recreate from scratch:**
```bash
# Delete deployment
kubectl delete namespace parsehub

# Redeploy
kubectl create namespace parsehub
kubectl apply -f infrastructure/kubernetes/
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n parsehub

# Common issues:
# - Image not found: update image registry
# - CrashLoopBackOff: check logs
# - Pending: check resource requests
```

### Service Not Accessible

```bash
# Check service exists
kubectl get svc -n parsehub

# Test internal connectivity
kubectl run debug --image=busybox --stdin -it -- sh
# curl http://parsehub-backend:5000/health
```

### Database Connection

```bash
# Verify secrets
kubectl get secret snowflake-credentials -n parsehub -o yaml

# Check pod env vars
kubectl exec -it <pod-name> -n parsehub -- env | grep SNOW
```

## Health Checks

### Liveness Probe
Checks if container is alive:
```bash
curl http://localhost:5000/health
```

### Readiness Probe
Checks if container is ready for traffic:
```bash
curl http://localhost:5000/health/detailed
```

## Cost Optimization

1. **Resource Requests/Limits**
   - Set appropriate CPU/memory limits
   - Use HPA for scaling

2. **Pod Disruption Budgets**
   - Enable graceful degradation
   - Minimize disruption during updates

3. **Node Affinity**
   - Schedule pods on cheaper nodes
   - Use spot instances

## Security

### Network Policies
```yaml
kind: NetworkPolicy
metadata:
  name: parsehub-network-policy
spec:
  podSelector:
    matchLabels:
      app: parsehub-backend
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: parsehub
```

### RBAC

```bash
# View RBAC
kubectl get roles -n parsehub
kubectl get rolebindings -n parsehub
```

### Secrets Encryption

Enable encryption at rest:
```bash
# Configure in K8s cluster
etcdctl --cacert=... --cert=... --key=... \
  set /registry/secrets/parsehub/... <encrypted-data>
```

---

**Last Updated:** March 8, 2026
