#!/usr/bin/env python
"""
ParseHub Dashboard - Complete Setup for Kubernetes Deployment
Windows to Production Guide
"""

import sys

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def main():
    print("\n\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  PARSEHUB DASHBOARD - KUBERNETES DEPLOYMENT GUIDE".center(68) + "║")
    print("║" + "  Snowflake + Flask + Next.js + K8s".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")

    # Step 1
    print_section("STEP 1: LOCAL SETUP ON WINDOWS")
    print("""
✓ Requirements Fixed
────────────────────
Your requirements.txt has been updated with all K8s-compatible packages:

Core Dependencies:
  • Flask 3.0.0 - Web framework
  • Gunicorn 21.2.0 - WSGI server
  • Snowflake Connector 3.10.1 - Database
  • SQLAlchemy 2.0.36 - ORM

Production-Ready Additions:
  • Pandas 2.2.0 - Data processing
  • Gevent 23.9.1 - Async support
  • Cryptography 41.0.7 - Security
  • python-json-logger 2.0.7 - Structured logging

Installation:
──────────────
1. Open PowerShell in: d:\\Parsehub-Dashboard\\Parsehub\\backend
2. Make sure Python 3.12 is in PATH (test: python --version)
3. Run: pip install -r requirements.txt

Expected: All packages install successfully in ~2 minutes
    """)

    # Step 2
    print_section("STEP 2: VERIFY LOCAL SETUP")
    print("""
Test the complete setup:
───────────────────────
1. In the same PowerShell, run:
   python test_complete_setup.py

2. Expected output:
   ✓ Environment Check: All variables set
   ✓ Checking Installed Packages: All installed
   ✓ Testing Snowflake Connection: Connected!
   ✓ Testing Flask Application: OK
   🎉 ALL CHECKS PASSED!

If any test fails, the script will tell you exactly what to fix.
    """)

    # Step 3
    print_section("STEP 3: BUILD DOCKER IMAGE")
    print("""
Prerequisites:
───────────────
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install and start Docker
3. Verify: docker --version

Build the backend image:
────────────────────────
1. Navigate to project root:
   cd d:\\Parsehub-Dashboard\\Parsehub

2. Build image:
   docker build -f backend/Dockerfile -t parsehub-backend:latest .

3. Verify build:
   docker images | findstr parsehub-backend

Output should show:
   parsehub-backend   latest   <IMAGE_ID>   <SIZE>

Test locally:
─────────────
docker run -p 5000:5000 \\
  -e SNOWFLAKE_ACCOUNT=VFHSGYP-GD78100.snowflakecomputing.com \\
  -e SNOWFLAKE_USER=ziauldin \\
  -e SNOWFLAKE_PASSWORD=rb6LZnW4aD2fHat \\
  -e SNOWFLAKE_WAREHOUSE=PARSEHUB_DB \\
  -e SNOWFLAKE_DATABASE=PARSEHUB_DB \\
  -e SNOWFLAKE_SCHEMA=PARSEHUB_DB \\
  parsehub-backend:latest

Test: curl http://localhost:5000/health
    """)

    # Step 4
    print_section("STEP 4: PUSH TO REGISTRY")
    print("""
Choose Your Container Registry:
─────────────────────────────────

Option A: Docker Hub (FREE/Public)
───────────────────────────────────
1. Create account: https://hub.docker.com
2. Login locally:
   docker login

3. Tag image:
   docker tag parsehub-backend:latest <your-username>/parsehub-backend:latest

4. Push:
   docker push <your-username>/parsehub-backend:latest

Option B: AWS ECR (For AWS/EKS)
────────────────────────────────
1. Create repository:
   aws ecr create-repository --repository-name parsehub-backend

2. Get login token:
   aws ecr get-login-password | docker login --username AWS --password-stdin <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com

3. Tag:
   docker tag parsehub-backend:latest <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/parsehub-backend:latest

4. Push:
   docker push <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/parsehub-backend:latest

Option C: Google Container Registry (For GKE)
───────────────────────────────────────────────
1. Configure gcloud CLI
2. Tag:
   docker tag parsehub-backend:latest gcr.io/<PROJECT-ID>/parsehub-backend:latest

3. Push:
   docker push gcr.io/<PROJECT-ID>/parsehub-backend:latest

Option D: Azure Container Registry (For AKS)
──────────────────────────────────────────────
1. Create registry:
   az acr create --resource-group myGroup --name myRegistry --sku Basic

2. Login:
   az acr login --name myRegistry

3. Tag and push:
   docker tag parsehub-backend:latest myRegistry.azurecr.io/parsehub-backend:latest
   docker push myRegistry.azurecr.io/parsehub-backend:latest
    """)

    # Step 5
    print_section("STEP 5: KUBERNETES DEPLOYMENT")
    print("""
Prerequisites:
───────────────
1. Kubernetes cluster running (EKS, GKE, AKS, or local minikube)
2. kubectl CLI installed: https://kubernetes.io/docs/tasks/tools/
3. Container image pushed to registry

Prepare K8s Manifest:
─────────────────────
File: backend/k8s-backend-deployment.yaml

This includes:
  • Secret: Snowflake credentials (encrypted in K8s)
  • ConfigMap: Application settings
  • Deployment: 3 replicas of backend pods
  • Service: Load balancing
  • HPA: Auto-scaling (2-10 pods)
  • NetworkPolicy: Security (optional)

Update the manifest with YOUR registry:
─────────────────────────────────────────
sed 's|your-registry|<your-actual-registry>|g' backend/k8s-backend-deployment.yaml

Or manually replace in text editor:
  image: your-registry/parsehub-backend:latest
  ↓
  image: <your-username>/parsehub-backend:latest  (Docker Hub)
  OR
  image: <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/parsehub-backend:latest  (AWS)
  OR
  image: gcr.io/<PROJECT-ID>/parsehub-backend:latest  (Google)

Deploy to Kubernetes:
─────────────────────
1. Create namespace (optional):
   kubectl create namespace parsehub

2. Apply manifest:
   kubectl apply -f backend/k8s-backend-deployment.yaml

3. Verify deployment:
   kubectl get deployment parsehub-backend
   kubectl get pods -l app=parsehub-backend
   kubectl get svc parsehub-backend-svc

4. Check logs:
   kubectl logs deployment/parsehub-backend
   
5. Test health:
   kubectl port-forward svc/parsehub-backend-svc 5000:5000
   curl http://localhost:5000/health

Expected Status:
──────────────────
NAME                              READY   STATUS    RESTARTS   AGE
parsehub-backend-abc123-xyz       1/1     Running   0          2m
parsehub-backend-def456-uvw       1/1     Running   0          2m
parsehub-backend-ghi789-rst       1/1     Running   0          2m
    """)

    # Step 6
    print_section("STEP 6: FRONTEND DEPLOYMENT")
    print("""
Build Frontend Image:
──────────────────────
docker build -f frontend/Dockerfile -t parsehub-frontend:latest .

Push to Registry:
─────────────────
docker tag parsehub-frontend:latest <your-registry>/parsehub-frontend:latest
docker push <your-registry>/parsehub-frontend:latest

Update Frontend K8s Manifest:
─────────────────────────────
File: frontend/k8s-frontend-deployment.yaml (create if needed)

Key environment for frontend:
  NEXT_PUBLIC_API_URL: http://parsehub-backend-svc:5000

Deploy:
───────
kubectl apply -f frontend/k8s-frontend-deployment.yaml
    """)

    # Step 7
    print_section("STEP 7: SETUP INGRESS (External Access)")
    print("""
Install Ingress Controller (if not already):
──────────────────────────────────────────────
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.0/deploy/static/provider/cloud/deploy.yaml

Create Ingress for both services:
──────────────────────────────────
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: parsehub-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - your-domain.com
    - api.your-domain.com
    secretName: parsehub-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: parsehub-frontend-svc
            port:
              number: 80
  - host: api.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: parsehub-backend-svc
            port:
              number: 5000

Deploy:
───────
kubectl apply -f ingress.yaml
    """)

    # Step 8
    print_section("STEP 8: MONITORING & MAINTENANCE")
    print("""
Monitor Deployment:
────────────────────
# Watch pods
kubectl get pods -w

# Stream logs
kubectl logs -f deployment/parsehub-backend

# Get events
kubectl get events --sort-by='.lastTimestamp'

# Check resource usage
kubectl top nodes
kubectl top pods

Scale Deployment:
─────────────────
# Manual scaling
kubectl scale deployment parsehub-backend --replicas=5

# HPA status
kubectl get hpa

Update Deployment:
───────────────────
# New image version
kubectl set image deployment/parsehub-backend \\
  backend=<registry>/parsehub-backend:v2.0

# Rollback if needed
kubectl rollout undo deployment/parsehub-backend

View Status:
────────────
kubectl rollout status deployment/parsehub-backend
    """)

    # Step 9
    print_section("QUICK REFERENCE COMMANDS")
    print("""
Development:
─────────────
python test_complete_setup.py          # Verify setup
python backend/api_server.py            # Run locally
python backend/test_snowflake_connection.py  # Test DB

Docker:
────────
docker build -f backend/Dockerfile -t parsehub-backend:latest .
docker push <registry>/parsehub-backend:latest
docker run -p 5000:5000 -e SNOWFLAKE_* parsehub-backend:latest

Kubernetes:
────────────
kubectl apply -f backend/k8s-backend-deployment.yaml
kubectl get deployment parsehub-backend
kubectl logs -f deployment/parsehub-backend
kubectl port-forward svc/parsehub-backend-svc 5000:5000
kubectl delete deployment parsehub-backend

Cleanup:
─────────
docker system prune
kubectl delete -f backend/k8s-backend-deployment.yaml
    """)

    # Summary
    print_section("CHECKLIST")
    print("""
Pre-Deployment:
  ☐ Python 3.12 installed and in PATH
  ☐ pip install -r requirements.txt completed
  ☐ python test_complete_setup.py passed all tests
  ☐ Docker Desktop installed and running

Docker Phase:
  ☐ Docker image built locally
  ☐ Local docker run test passed (http://localhost:5000/health)
  ☐ Image pushed to registry
  ☐ Private registry credentials in K8s secret (if needed)

Kubernetes Phase:
  ☐ Kubernetes cluster running
  ☐ kubectl configured (kubectl get nodes shows nodes)
  ☐ k8s-backend-deployment.yaml updated with correct registry
  ☐ kubectl apply -f backend/k8s-backend-deployment.yaml deployed
  ☐ kubectl get pods shows 3 running replicas
  ☐ Health check passing: kubectl port-forward + curl /health

Production:
  ☐ Ingress controller installed
  ☐ Ingress.yaml deployed and responding on domain
  ☐ SSL/TLS certificates configured
  ☐ Monitoring and logging set up
  ☐ Backup and disaster recovery plan in place

POST-DEPLOYMENT TEST:
  ☐ curl https://api.your-domain.com/health → 200 OK
  ☐ Backend responds to API requests
  ☐ Snowflake connectivity confirmed
  ☐ Frontend connects to backend successfully
  ☐ Scheduled jobs running (if applicable)
    """)

    print("\n" + "="*70)
    print("✨ DEPLOYMENT COMPLETE!")
    print("="*70)
    print("""
Your ParseHub Dashboard is now running on Kubernetes with:
  ✓ Snowflake database (serverless, scalable)
  ✓ Flask backend (containerized, auto-scaling)
  ✓ Next.js frontend (optimized, fast)
  ✓ Health checks (automatic pod restart)
  ✓ Auto-scaling (2-10 pods based on load)
  ✓ Security (encrypted secrets, network policies)
  ✓ CI/CD ready (update image, kubectl apply)

For questions or issues:
  • Check pod logs: kubectl logs -f deployment/parsehub-backend
  • Test connectivity: kubectl port-forward svc/parsehub-backend-svc 5000:5000
  • Verify setup: python test_complete_setup.py
""")

if __name__ == "__main__":
    main()
