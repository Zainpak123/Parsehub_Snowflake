# Kubernetes Troubleshooting Guide

## Pod Issues

### Pod not starting / ImagePullBackOff

**Symptom:** Pod stuck in ImagePullBackOff

```bash
kubectl get pods -n parsehub
# NAME                        READY   STATUS             
# backend-5d7c4f8b-xyz        0/1     ImagePullBackOff
```

**Causes & Solutions:**

1. **Image doesn't exist in registry**
   ```bash
   # Check image exists
   docker images | grep parsehub
   
   # Push to registry
   docker push your-registry/parsehub-backend:latest
   
   # Verify in registry
   docker pull your-registry/parsehub-backend:latest
   ```

2. **Wrong image URL in manifest**
   ```bash
   # Check manifest
   kubectl get deployment backend -n parsehub -o yaml | grep image:
   
   # Update manifest
   vim infrastructure/kubernetes/base/backend-deployment.yaml
   ```

3. **Image pull secret missing**
   ```bash
   # For private registries, create secret
   kubectl create secret docker-registry regcred \
     --docker-server=your-registry \
     --docker-username=USERNAME \
     --docker-password=PASSWORD \
     -n parsehub
   ```

### Pods CrashLoopBackOff

**Symptom:** Pod crashes repeatedly

```bash
kubectl get pods -n parsehub
# NAME                        READY   STATUS            
# backend-5d7c4f8b-xyz        0/1     CrashLoopBackOff
```

**Debug:**
```bash
# Get pod name
POD_NAME=$(kubectl get pods -n parsehub -l app=backend -o jsonpath='{.items[0].metadata.name}')

# View logs
kubectl logs $POD_NAME -n parsehub

# View last logs (if container was restarted)
kubectl logs $POD_NAME -n parsehub --previous

# Describe pod for more details
kubectl describe pod $POD_NAME -n parsehub
```

**Common Causes:**

1. **Application error (check logs)**
   ```
   ERROR: Snowflake connection failed
   ERROR: API key invalid
   ```

2. **Missing environment variables**
   ```bash
   # Check secrets exist
   kubectl get secrets -n parsehub
   
   # Check configmaps
   kubectl get configmaps -n parsehub
   
   # Recreate secrets if needed
   cd infrastructure/kubernetes/scripts
   bash setup-secrets.sh
   ```

3. **Port conflict**
   ```bash
   # Check what port is being used
   kubectl describe pod $POD_NAME -n parsehub | grep -i port
   ```

### Pod Pending

**Symptom:** Pod stuck in Pending state

```bash
kubectl get pods -n parsehub
# NAME                        READY   STATUS    
# backend-5d7c4f8b-xyz        0/1     Pending
```

**Causes & Solutions:**

1. **Insufficient resources**
   ```bash
   # Check node resources
   kubectl top nodes
   kubectl top pods -n parsehub
   
   # Check requested vs available
   kubectl describe pod $POD_NAME -n parsehub | grep -A 5 "Limits\|Requests"
   
   # Reduce resource requests
   vim infrastructure/kubernetes/overlays/local/backend-patch.yaml
   ```

2. **Node affinity/anti-affinity issue**
   ```bash
   # Check node labels
   kubectl get nodes --show-labels
   
   # Check pod affinity rules
   kubectl get pod $POD_NAME -n parsehub -o yaml | grep -A 10 affinity
   ```

3. **PersistentVolumeClaim not bound**
   ```bash
   kubectl get pvc -n parsehub
   kubectl describe pvc -n parsehub
   ```

## Service & Network Issues

### Cannot reach backend from frontend

**Symptom:** Frontend gets connection refused / timeout

**Debug:**
```bash
# 1. Check service exists
kubectl get svc -n parsehub
NAME              TYPE        CLUSTER-IP     PORT(S)
backend-svc       ClusterIP   10.96.123.45   5000/TCP

# 2. Check service has endpoints
kubectl get endpoints -n parsehub backend-svc
NAME              ENDPOINTS                   AGE
backend-svc       10.244.0.5:5000             2m

# 3. Test from a debug pod
kubectl run -it --rm debug --image=alpine --restart=Never -n parsehub -- sh
# Inside pod:
/ # wget http://backend-svc:5000/health
```

**Common Issues:**

1. **Service not finding pods**
   ```bash
   # Check pod labels match selector
   kubectl get pods -n parsehub --show-labels
   
   # Check service selector
   kubectl get svc backend-svc -n parsehub -o yaml | grep selector -A 2
   ```

2. **Frontend using wrong backend URL**
   ```bash
   # Check configmap
   kubectl get configmap frontend-config -n parsehub -o yaml
   
   # Update if needed
   kubectl set env deployment/frontend NEXT_PUBLIC_API_URL=http://backend-svc:5000 -n parsehub
   ```

### Ingress not routing traffic

**Symptom:** `curl app.yourdomain.com` → connection refused / 404

```bash
# 1. Check ingress exists
kubectl get ingress -n parsehub
NAME                 CLASS   HOSTS                    ADDRESS         AGE
parsehub-ingress     nginx   app.yourdomain.com ...   203.0.113.45    2m

# 2. Check ingress controller is running
kubectl get pods -n ingress-nginx

# 3. Check ingress routing rules
kubectl describe ingress parsehub-ingress -n parsehub

# 4. Check DNS resolves to ingress IP
nslookup app.yourdomain.com
# Should show: 203.0.113.45

# 5. Test via curl
curl -H "Host: app.yourdomain.com" http://203.0.113.45
```

**Common Issues:**

1. **Ingress controller not installed**
   ```bash
   # Install nginx-ingress
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.0/deploy/static/provider/kind/deploy.yaml
   ```

2. **Wrong DNS routing**
   ```bash
   # Verify DNS A record points to ingress IP
   nslookup app.yourdomain.com +nocmd +noall +answer
   # Should show ingress IP from earlier
   ```

3. **Service not exposed via ingress**
   ```bash
   # Check ingress backend services exist
   kubectl get svc -n parsehub frontend-svc
   ```

## Database Connectivity

### Cannot connect to Snowflake

**Symptom:** Backend logs show "Snowflake connection failed"

```bash
# 1. Check secrets exist
kubectl get secrets snowflake-credentials -n parsehub -o yaml

# 2. Verify secret values
kubectl get secret snowflake-credentials -n parsehub -o jsonpath='{.data.account}' | base64 -d
kubectl get secret snowflake-credentials -n parsehub -o jsonpath='{.data.user}' | base64 -d

# 3. Check backend pod has env vars
POD_NAME=$(kubectl get pods -n parsehub -l app=backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD_NAME -n parsehub -- env | grep SNOWFLAKE

# 4. Test connection from pod
kubectl exec -it $POD_NAME -n parsehub -- python
# >>> import snowflake.connector
# >>> conn = snowflake.connector.connect(
#       account='YOUR_ACCOUNT',
#       user='YOUR_USER',
#       password='YOUR_PASSWORD'
#   )
# >>> conn.cursor().execute("SELECT 1")
```

**Solutions:**

1. **Recreate secrets with correct values**
   ```bash
   cd infrastructure/kubernetes/scripts
   rm snowflake-credentials secret first (optional)
   bash setup-secrets.sh
   
   # Restart backend pods to pick up new secrets
   kubectl rollout restart deployment/backend -n parsehub
   ```

2. **Verify Snowflake credentials**
   - Check account ID, user, password in GoDaddy/Snowflake console
   - Ensure user has correct permissions
   - Check warehouse exists

3. **Check network connectivity**
   ```bash
   # From pod, can you reach Snowflake?
   kubectl exec -it $POD_NAME -n parsehub -- sh
   # $ ping snowflakecomputing.com
   # $ telnet ACCOUNT.snowflakecomputing.com 443
   ```

## Health Check Issues

### readiness/livenessProbe failures

**Symptom:** Pod shows as not ready

```bash
kubectl get pods -n parsehub
# Ready column shows 0/1

kubectl describe pod $POD_NAME -n parsehub | grep -A 10 "Ready\|Liveness\|Readiness"
```

**Debug:**

1. **Test health endpoint manually**
   ```bash
   POD_NAME=$(kubectl get pods -n parsehub -l app=backend -o jsonpath='{.items[0].metadata.name}')
   kubectl exec $POD_NAME -n parsehub -- curl -f http://localhost:5000/health || echo "FAILED"
   ```

2. **Get health check details**
   ```bash
   kubectl describe pod $POD_NAME -n parsehub | grep -A 20 "Liveness\|Readiness"
   
   # Example output:
   # Readiness:  http-get http://:5000/health delay=5s timeout=3s period=5s
   ```

3. **Increase probe timeout if slow**
   ```bash
   # Edit deployment
   vim infrastructure/kubernetes/base/backend-deployment.yaml
   
   # Change timeoutSeconds
   readinessProbe:
     httpGet:
       path: /health
       port: 5000
     initialDelaySeconds: 10  # Increase if needed
     timeoutSeconds: 5        # Increase if needed
   ```

## Scaling Issues

### HPA not scaling pods

**Symptom:** Pod stays at same count even under load

```bash
# Check HPA status
kubectl get hpa -n parsehub
NAME            REFERENCE             TARGETS                    MINPODS   MAXPODS
backend-hpa     Deployment/backend    cpu: 15%, memory: 25%       2         10

# Get HPA details
kubectl describe hpa backend-hpa -n parsehub
```

**Common Issues:**

1. **Metrics server not installed**
   ```bash
   # Check if metrics available
   kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/parsehub/pods
   
   # If error, install metrics-server
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```

2. **Resource requests not set**
   - HPA uses resource requests to calculate percentage
   - If requests are 0, scaling won't work
   - Always set requests in deployments

## Quick Diagnostic Commands

```bash
# Overall cluster health
kubectl get all -n parsehub

# Pod details
kubectl describe pods -n parsehub

# Node resources
kubectl top nodes
kubectl top pods -n parsehub

# Events (recent errors)
kubectl get events -n parsehub --sort-by='.lastTimestamp'

# Check all secrets/configmaps
kubectl get secrets,configmaps -n parsehub

# Export deployment for inspection
kubectl get deployment backend -n parsehub -o yaml > backend-deploy.yaml

# Check node disk/memory
kubectl get nodes -o custom-columns=NAME:.metadata.name,MEMORY:.status.capacity.memory,DISK:.status.capacity.storage
```

## Getting Help

1. **Check logs comprehensively**
   ```bash
   # Current pod logs
   kubectl logs POD -n parsehub
   
   # Previous pod logs (if restarted)
   kubectl logs POD -n parsehub --previous
   
   # Follow logs live
   kubectl logs -f POD -n parsehub
   
   # Last N lines
   kubectl logs POD -n parsehub --tail=100
   ```

2. **Describe resources**
   ```bash
   kubectl describe pod/service/deployment POD_NAME -n parsehub
   ```

3. **Export and analyze manifest**
   ```bash
   kubectl get deployment backend -n parsehub -o yaml > debug.yaml
   cat debug.yaml | less
   ```

4. **Shell into container for debugging**
   ```bash
   kubectl exec -it POD -n parsehub -- /bin/bash
   ```

See main **KUBERNETES_DEPLOYMENT_GUIDE.md** for configuration help.
