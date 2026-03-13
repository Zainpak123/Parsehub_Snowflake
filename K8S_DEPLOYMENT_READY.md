# ParseHub - Kubernetes-Ready Directory Structure

## ✅ Organization Complete

Your project is now organized for Kubernetes deployment. Here's the complete structure:

```
ParseHub/
│
├── infrastructure/                          # 🎯 DEPLOYMENT HUB
│   ├── docker/
│   │   ├── Dockerfile-backend              # Backend image definition
│   │   └── Dockerfile-frontend             # Frontend image definition
│   │
│   ├── kubernetes/
│   │   ├── base/                           # Shared manifests
│   │   │   ├── namespace.yaml              # Namespace
│   │   │   ├── secrets.yaml                # Database credentials (⚠️ template)
│   │   │   ├── configmaps.yaml             # Environment config
│   │   │   ├── backend-deployment.yaml     # Backend pods
│   │   │   ├── backend-service.yaml        # Backend service
│   │   │   ├── frontend-deployment.yaml    # Frontend pods
│   │   │   ├── frontend-service.yaml       # Frontend service
│   │   │   ├── ingress.yaml                # External routing
│   │   │   ├── hpa.yaml                    # Auto-scaling
│   │   │   └── kustomization.yaml          # Base config
│   │   │
│   │   ├── overlays/
│   │   │   ├── local/                      # Kind cluster (testing)
│   │   │   │   ├── kustomization.yaml
│   │   │   │   ├── backend-patch.yaml
│   │   │   │   └── frontend-patch.yaml
│   │   │   │
│   │   │   ├── production/                 # Cloud deployment (AWS/GCP/Azure)
│   │   │   │   ├── kustomization.yaml
│   │   │   │   ├── backend-patch.yaml
│   │   │   │   └── frontend-patch.yaml
│   │   │   │
│   │   │   └── development/                # Dev environment
│   │   │       ├── kustomization.yaml
│   │   │       ├── backend-patch.yaml
│   │   │       └── frontend-patch.yaml
│   │   │
│   │   └── scripts/
│   │       ├── setup-secrets.sh            # Create K8s secrets
│   │       ├── deploy.sh                   # Deploy to cluster
│   │       └── cleanup.sh                  # Remove deployment
│   │
│   └── README.md                           # Infrastructure overview
│
├── config/                                  # Configuration files
│   └── .env.example                        # Template for env vars
│
├── docs/deployment/                        # 📚 DOCUMENTATION
│   ├── KUBERNETES_DEPLOYMENT_GUIDE.md      # Complete K8s guide
│   ├── DOCKER_BUILD_GUIDE.md               # Docker image building
│   └── TROUBLESHOOTING.md                  # Common issues & fixes
│
├── backend/                                # Backend application
│   ├── src/
│   ├── requirements.txt
│   └── ...
│
├── frontend/                               # Frontend application
│   ├── app/
│   ├── package.json
│   └── ...
│
├── docker-compose.yml                      # Local testing
├── README.md
└── ...
```

---

## 🚀 Next Steps

### **1. Start Local Testing (Kind)**

```bash
# Create local cluster
kind create cluster --name parsehub

# Build images locally
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

# Test
kubectl port-forward svc/frontend-svc 3000:3000 -n parsehub
kubectl port-forward svc/backend-svc 5000:5000 -n parsehub
```

### **2. Deploy to Production (AWS)**

```bash
# Push images to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag parsehub-backend YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/parsehub-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/parsehub-backend:latest

# Update image registry in production overlay
# vim infrastructure/kubernetes/overlays/production/kustomization.yaml

# Deploy
cd infrastructure/kubernetes/scripts
bash deploy.sh production

# Get Ingress IP
kubectl get ingress -n parsehub
```

### **3. Configure Domain**

- Update GoDaddy DNS records with Ingress IP
- Point `app.yourdomain.com` → Ingress IP
- Point `api.yourdomain.com` → Ingress IP
- Wait for DNS propagation (5-15 min)
- HTTPS certificate auto-created via cert-manager

---

## 📖 Documentation

### Read in This Order:

1. **[KUBERNETES_DEPLOYMENT_GUIDE.md](docs/deployment/KUBERNETES_DEPLOYMENT_GUIDE.md)**
   - Complete overview
   - Quick start
   - Common commands
   - Customization guide

2. **[DOCKER_BUILD_GUIDE.md](docs/deployment/DOCKER_BUILD_GUIDE.md)**
   - Building images
   - Local testing
   - Pushing to registries
   - Image optimization

3. **[TROUBLESHOOTING.md](docs/deployment/TROUBLESHOOTING.md)**
   - Debugging common issues
   - Pod problems
   - Network issues
   - Database connectivity

---

## 🔑 Key Files for Customization

### Update Domain
→ `infrastructure/kubernetes/base/ingress.yaml` (lines with `yourdomain.com`)

### Change Replicas
→ `infrastructure/kubernetes/overlays/*/backend-patch.yaml` (`replicas: 3`)

### Update Resources
→ `infrastructure/kubernetes/base/backend-deployment.yaml` (`resources:` section)

### Change Image Registry
→ `infrastructure/kubernetes/overlays/production/kustomization.yaml` (`newName:`)

### Add Environment Variables
→ `infrastructure/kubernetes/base/configmaps.yaml` + `backend-deployment.yaml`

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────┐
│          Your Domain (GoDaddy)              │
│      app.yourdomain.com + api.yourdomain.com│
└────────────────────┬────────────────────────┘
                     │ (DNS → Ingress IP)
                     ▼
┌─────────────────────────────────────────────┐
│        Kubernetes Cluster Controller        │
└────────────────────┬────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
   ┌─────────────┐          ┌──────────────┐
   │   Ingress   │          │  Services    │
   │   (Router)  │          │  (Internal)  │
   └─────────────┘          └──────────────┘
        │                         │
        ├────────────┬────────────┤
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌──────────┐
    │Frontend│  │Backend │  │Database  │
    │Pods(2)│  │Pods(3) │  │Snowflake │
    └────────┘  └────────┘  └──────────┘
      Port 3000 Port 5000   External
              │
    ┌─────────┴─────────────┐
    ▼                       ▼
  HPA                   Network Policy
  (Auto-scale)        (Security rules)
  Min 2 → Max 10
```

---

## ✅ What's Ready

- ✅ Docker images configured (optimize, secure, health checks)
- ✅ Kubernetes manifests using Kustomize (base + overlays)
- ✅ Multiple environments (local/dev/prod)
- ✅ Auto-scaling configured (HPA)
- ✅ Networking setup (Ingress, Services)
- ✅ Secrets management (external, not committed)
- ✅ Deployment scripts provided
- ✅ Complete documentation

---

## 🚦 Deployment Checklist

### Before Deploying:

- [ ] Cluster created (Kind for local, EKS/GKE for cloud)
- [ ] Docker images built and pushed
- [ ] Container registry credentials set up
- [ ] Snowflake account credentials ready
- [ ] Domain configured (GoDaddy DNS records)
- [ ] cert-manager installed (for HTTPS)
- [ ] nginx-ingress controller installed

### Deploy:

- [ ] Run `setup-secrets.sh` (enter credentials)
- [ ] Run `deploy.sh local` or `deploy.sh production`
- [ ] Verify pods are running: `kubectl get pods -n parsehub`
- [ ] Check services: `kubectl get svc -n parsehub`
- [ ] Test endpoints: `curl http://localhost:5000/health`

### Post-Deploy:

- [ ] Verify Ingress IP assigned: `kubectl get ingress -n parsehub`
- [ ] Update GoDaddy DNS with Ingress IP
- [ ] Wait for DNS propagation
- [ ] Test via domain: `https://app.yourdomain.com`
- [ ] Check logs for errors: `kubectl logs deployment/backend -n parsehub`

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Create cluster | `kind create cluster --name parsehub` |
| Build backend | `docker build -f infrastructure/docker/Dockerfile-backend .` |
| Create secrets | `cd infrastructure/kubernetes/scripts && bash setup-secrets.sh` |
| Deploy local | `bash deploy.sh local` |
| Deploy prod | `bash deploy.sh production` |
| View pods | `kubectl get pods -n parsehub` |
| View logs | `kubectl logs -f deployment/backend -n parsehub` |
| Port forward | `kubectl port-forward svc/backend-svc 5000:5000 -n parsehub` |
| Scale pods | `kubectl scale deployment backend --replicas=5 -n parsehub` |
| Rollback | `kubectl rollout history deployment/backend -n parsehub` |
| Cleanup | `bash cleanup.sh` |

---

## 🔗 Example Workflow

```bash
# 1. Local testing
kind create cluster --name parsehub
docker build -f infrastructure/docker/Dockerfile-backend -t parsehub-backend:latest .
kind load docker-image parsehub-backend --name parsehub
cd infrastructure/kubernetes/scripts
bash setup-secrets.sh
bash deploy.sh local
kubectl port-forward svc/frontend-svc 3000:3000
# Visit http://localhost:3000 ✅

# 2. Push to registry
docker tag parsehub-backend YOUR_REGISTRY/parsehub-backend:1.0.0
docker push YOUR_REGISTRY/parsehub-backend:1.0.0

# 3. Update production config
vim infrastructure/kubernetes/overlays/production/kustomization.yaml
# Update image registry URL

# 4. Deploy to AWS
eksctl create cluster --name parsehub-prod
cd infrastructure/kubernetes/scripts
bash setup-secrets.sh  # Enter production credentials
bash deploy.sh production

# 5. Configure domain
# Go to GoDaddy, add DNS A records pointing to Ingress IP
# Wait for propagation

# 6. Access via domain
# https://app.yourdomain.com ✅
```

---

## 🎉 You're Ready!

Your project is now **production-ready for Kubernetes**. Start with the **[KUBERNETES_DEPLOYMENT_GUIDE.md](docs/deployment/KUBERNETES_DEPLOYMENT_GUIDE.md)** and follow the next steps above.

Questions? See **[TROUBLESHOOTING.md](docs/deployment/TROUBLESHOOTING.md)** for common issues and their fixes.
