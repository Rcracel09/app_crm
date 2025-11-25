# 🚀 Deployment Guide - Customer DB + Viewer

**Complete deployment guide for both apps in Minikube**

---

## 📦 Overview

Temos **2 apps separadas**:

1. **customer-db** - PostgreSQL com dados PII
2. **customer-viewer** - Web app para visualização

Ambas deployam **independentemente** no Minikube.

---

## 🏗️ Architecture

```
┌─────────────────────┐
│  customer-viewer    │
│  (Port 8080)        │
│                     │
│  Flask + HTML       │
└──────────┬──────────┘
           │
           │ connects to
           │
           ▼
┌─────────────────────┐
│  customer-db        │
│  (Port 5432)        │
│                     │
│  PostgreSQL + Data  │
└─────────────────────┘
```

---

## 🚀 Deployment Steps

### Step 1: Start Minikube

```bash
minikube start

# Enable ingress (optional)
minikube addons enable ingress
```

### Step 2: Build Images in Minikube

```bash
# Point Docker to Minikube's Docker daemon
eval $(minikube docker-env)

# Build customer-db
cd customer-db/
docker build -t customer-db:local .

# Build customer-viewer
cd ../customer-viewer/
docker build -t customer-viewer:local .

# Verify images
docker images | grep customer
```

### Step 3: Deploy customer-db First

```bash
# Create namespace (optional)
kubectl create namespace ecatalog

# Deploy database
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: customer-db-config
  namespace: ecatalog
data:
  POSTGRES_DB: "demo_db"
  POSTGRES_USER: "postgres"
---
apiVersion: v1
kind: Secret
metadata:
  name: customer-db-secret
  namespace: ecatalog
type: Opaque
stringData:
  POSTGRES_PASSWORD: "postgres123"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: customer-db
  namespace: ecatalog
spec:
  replicas: 1
  selector:
    matchLabels:
      app: customer-db
  template:
    metadata:
      labels:
        app: customer-db
    spec:
      containers:
      - name: postgres
        image: customer-db:local
        imagePullPolicy: Never
        ports:
        - containerPort: 5432
        envFrom:
        - configMapRef:
            name: customer-db-config
        - secretRef:
            name: customer-db-secret
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
          requests:
            cpu: "200m"
            memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: customer-db
  namespace: ecatalog
spec:
  selector:
    app: customer-db
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
EOF

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=customer-db -n ecatalog --timeout=60s
```

### Step 4: Deploy customer-viewer

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: customer-viewer-config
  namespace: ecatalog
data:
  DB_HOST: "customer-db"
  DB_PORT: "5432"
  DB_NAME: "demo_db"
  DB_USER: "postgres"
---
apiVersion: v1
kind: Secret
metadata:
  name: customer-viewer-secret
  namespace: ecatalog
type: Opaque
stringData:
  DB_PASSWORD: "postgres123"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: customer-viewer
  namespace: ecatalog
spec:
  replicas: 1
  selector:
    matchLabels:
      app: customer-viewer
  template:
    metadata:
      labels:
        app: customer-viewer
    spec:
      containers:
      - name: viewer
        image: customer-viewer:local
        imagePullPolicy: Never
        ports:
        - containerPort: 8080
        env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: customer-viewer-config
              key: DB_HOST
        - name: DB_PORT
          valueFrom:
            configMapKeyRef:
              name: customer-viewer-config
              key: DB_PORT
        - name: DB_NAME
          valueFrom:
            configMapKeyRef:
              name: customer-viewer-config
              key: DB_NAME
        - name: DB_USER
          valueFrom:
            configMapKeyRef:
              name: customer-viewer-config
              key: DB_USER
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: customer-viewer-secret
              key: DB_PASSWORD
        resources:
          limits:
            cpu: "300m"
            memory: "256Mi"
          requests:
            cpu: "100m"
            memory: "128Mi"
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: customer-viewer
  namespace: ecatalog
spec:
  selector:
    app: customer-viewer
  ports:
  - port: 8080
    targetPort: 8080
    nodePort: 30080
  type: NodePort
EOF

# Wait for app to be ready
kubectl wait --for=condition=ready pod -l app=customer-viewer -n ecatalog --timeout=60s
```

### Step 5: Access the App

```bash
# Get the URL
minikube service customer-viewer -n ecatalog --url

# Or open directly
minikube service customer-viewer -n ecatalog
```

---

## ✅ Verification

### Check Deployments

```bash
# View all resources
kubectl get all -n ecatalog

# Check pods
kubectl get pods -n ecatalog

# Should see:
# customer-db-xxx        1/1   Running
# customer-viewer-xxx    1/1   Running
```

### Check Logs

```bash
# Database logs
kubectl logs -l app=customer-db -n ecatalog

# Viewer logs
kubectl logs -l app=customer-viewer -n ecatalog
```

### Test Connectivity

```bash
# From viewer to database
kubectl exec -it deployment/customer-viewer -n ecatalog -- \
  psql -h customer-db -U postgres -d demo_db

# Should connect successfully
# Password: postgres123
```

### Test API

```bash
# Get service URL
URL=$(minikube service customer-viewer -n ecatalog --url)

# Health check
curl $URL/health

# Get customers
curl $URL/api/customers | jq

# Get interactions
curl $URL/api/interactions | jq
```

---

## 🧹 Cleanup

```bash
# Delete everything
kubectl delete namespace ecatalog

# Or individually
kubectl delete deployment customer-db customer-viewer -n ecatalog
kubectl delete service customer-db customer-viewer -n ecatalog
kubectl delete configmap customer-db-config customer-viewer-config -n ecatalog
kubectl delete secret customer-db-secret customer-viewer-secret -n ecatalog
```

---

## 🔧 Troubleshooting

### Pod not starting

```bash
# Describe pod
kubectl describe pod -l app=customer-db -n ecatalog
kubectl describe pod -l app=customer-viewer -n ecatalog

# Check events
kubectl get events -n ecatalog --sort-by='.lastTimestamp'
```

### Database connection failed

```bash
# Check if service exists
kubectl get svc customer-db -n ecatalog

# Test DNS resolution from viewer
kubectl exec -it deployment/customer-viewer -n ecatalog -- \
  nslookup customer-db

# Check database logs
kubectl logs -l app=customer-db -n ecatalog
```

### Image not found

```bash
# Verify you're using Minikube's Docker
eval $(minikube docker-env)

# Check images
docker images | grep customer

# Rebuild if needed
cd customer-db && docker build -t customer-db:local .
cd customer-viewer && docker build -t customer-viewer:local .
```

---

## 📊 Quick Status Check

```bash
# One-liner to check everything
kubectl get pods,svc -n ecatalog
```

Expected output:
```
NAME                                  READY   STATUS    RESTARTS   AGE
pod/customer-db-xxx                   1/1     Running   0          2m
pod/customer-viewer-xxx               1/1     Running   0          1m

NAME                      TYPE        CLUSTER-IP      PORT(S)
service/customer-db       ClusterIP   10.96.xxx.xxx   5432/TCP
service/customer-viewer   NodePort    10.96.xxx.xxx   8080:30080/TCP
```

---

## 🎯 Next Steps

1. ✅ Deploy both apps
2. ✅ Verify connectivity
3. ✅ Access web interface
4. ✅ View PII data
5. ⏳ Run anonymization script
6. ⏳ Verify anonymization

---

**Status**: ✅ Complete deployment guide ready!