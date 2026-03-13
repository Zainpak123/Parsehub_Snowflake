# Kubernetes Deployment Guide

## Directory Structure Overview

```
infrastructure/
├── docker/                          # Container images
│   ├── Dockerfile-backend          # Backend Python app
│   └── Dockerfile-frontend         # Frontend Next.js app
│
├── kubernetes/                      # Kubernetes manifests
│   ├── base/                        # Base configurations (all environments)
│   │   ├── namespace.yaml
│   │   ├── secrets.yaml            # ⚠️ WARNING: DON'T commit with real secrets!
│   │   ├── configmaps.yaml
│   │   ├── backend-deployment.yaml
│   │   ├── backend-service.yaml
│   │   ├── frontend-deployment.yaml
│   │   ├── frontend-service.yaml
│   │   ├── ingress.yaml
│   │   ├── hpa.yaml                # Auto-scaling
│   │   └── kustomization.yaml      # Kustomize entry point
│   │
│   ├── overlays/                    # Environment-specific overrides
│   │   ├── local/                  # Kind cluster (local testing)
│   │   │   ├── kustomization.yaml
│   │   │   ├── backend-patch.yaml
│   │   │   └── frontend-patch.yaml
│   │   │
│   │   ├── production/              # AWS/GCP/AKS (production)
│   │   │   ├── kustomization.yaml
│   │   │   ├── backend-patch.yaml
│   │   │   └── frontend-patch.yaml
│   │   │
│   │   └── development/             # Dev environment
│   │       ├── kustomization.yaml
│   │       ├── backend-patch.yaml
│   │       └── frontend-patch.yaml
│   │
│   └── scripts/                     # Helper scripts
│       ├── setup-secrets.sh         # Create K8s secrets
│       ├── deploy.sh                # Deploy to cluster
│       └── cleanup.sh               # Remove deployment

config/                             # Configuration files
├── .env.example                    # Template for env vars
├── .env.local                      # Local config (gitignored)
└── .env.production                 # Production config (gitignored)

docs/deployment/                    # Deployment documentation
├── KUBERNETES_SETUP.md             # K8s setup guide
├── DEPLOYMENT_GUIDE.md             # Step-by-step deployment
└── TROUBLESHOOTING.md              # Troubleshooting tips
```

## Key Concepts

### **Base vs Overlays (Kustomize Pattern)**

**Base** (`base/`):
- Shared manifests for ALL environments
- Generic configuration
- Single source of truth

**Overlays** (`overlays/`):
- Environment-specific patches
- Override replicas, resources, images
- No duplicate code

**Example:**
- Base: Backend with 3 replicas
- Local overlay: Override to 1 replica (saves resources)
- Production overlay: Keep 3 replicas + pod anti-affinity

### **Secrets vs ConfigMaps**

**Secrets** (sensitive):
- Database passwords
- API keys
- Never commit to git
- Created manually at runtime

**ConfigMaps** (non-sensitive):
- Flask environment mode
- Log levels
- Safe to version control

## Quick Start

### 1. Test Locally (Kind)

```bash
# Create local cluster
kind create cluster --name parsehub

# Build images
docker build -f infrastructure/docker/Dockerfile-backend -t parsehub-backend:latest .
docker build -f infrastructure/docker/Dockerfile-frontend -t parsehub-frontend:latest .

# Load into Kind
kind load docker-image parsehub-backend:latest --name parsehub
kind load docker-image parsehub-frontend:latest --name parsehub

# Create secrets
cd infrastructure/kubernetes/scripts
bash setup-secrets.sh

# Deploy
bash deploy.sh local

# Port forward
kubectl port-forward svc/frontend-svc 3000:3000
kubectl port-forward svc/backend-svc 5000:5000

# Visit: http://localhost:3000
```

### 2. Deploy to Production (AWS)

```bash
# Push images to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag parsehub-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/parsehub-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/parsehub-backend:latest

# Update image in production overlay
# vim overlays/production/kustomization.yaml

# Deploy
bash deploy.sh production

# Get Ingress IP
kubectl get ingress -n parsehub
```

## Customization

### 1. Change Domain

Edit: `infrastructure/kubernetes/base/ingress.yaml`
```yaml
- host: app.yourdomain.com
- host: api.yourdomain.com
```

### 2. Change Replicas

Edit: `infrastructure/kubernetes/overlays/*/backend-patch.yaml`
```yaml
spec:
  replicas: 5  # Change this
```

### 3. Change Resources

Edit: `infrastructure/kubernetes/base/backend-deployment.yaml`
```yaml
resources:
  requests:
    memory: "512Mi"   # Change this
    cpu: "500m"       # Change this
```

### 4. Update Image Registry

Edit: `infrastructure/kubernetes/overlays/production/kustomization.yaml`
```yaml
images:
  - name: parsehub-backend
    newName: YOUR_REGISTRY/parsehub-backend
```

## Common Commands

```bash
# View all resources
kubectl get all -n parsehub

# View specific resource
kubectl get deployment -n parsehub
kubectl get pods -n parsehub
kubectl get services -n parsehub

# Describe resource (troubleshooting)
kubectl describe pod POD_NAME -n parsehub
kubectl describe deployment backend -n parsehub

# View logs
kubectl logs deployment/backend -n parsehub
kubectl logs -f deployment/backend -n parsehub  # Follow
kubectl logs deployment/backend --tail=50 -n parsehub

# Execute command in pod
kubectl exec -it POD_NAME -n parsehub -- /bin/bash

# Scale deployment
kubectl scale deployment backend --replicas=5 -n parsehub

# Port forward
kubectl port-forward svc/backend-svc 5000:5000 -n parsehub

# Delete resources
kubectl delete deployment backend -n parsehub
kubectl delete namespace parsehub
```

## Troubleshooting

### Pods not starting?
```bash
kubectl describe pod POD_NAME -n parsehub
kubectl logs POD_NAME -n parsehub
```

### Image pull errors?
```bash
# Check image exists in registry
docker images | grep parsehub

# Check image pull policy
kubectl describe pod POD_NAME -n parsehub | grep Image
```

### Can't connect to backend?
```bash
# Check service exists
kubectl get svc backend-svc -n parsehub

# Test connectivity
kubectl run -it --rm debug --image=alpine --restart=Never -n parsehub -- sh
# Inside pod: wget http://backend-svc:5000/health
```

### Ingress not routing traffic?
```bash
# Check ingress
kubectl get ingress -n parsehub

# Check ingress controller
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx INGRESS_POD_NAME
```

See `TROUBLESHOOTING.md` for more details.
