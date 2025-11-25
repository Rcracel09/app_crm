#!/bin/bash
# Quick deployment script for customer-db + customer-viewer

set -e

echo "🚀 Customer DB + Viewer - Quick Deployment"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Check if we're deploying to Minikube or Docker
if [ "$1" == "minikube" ]; then
    DEPLOY_MODE="minikube"
    print_step "Deployment mode: Minikube"
echo ""


# ============================================
# MINIKUBE DEPLOYMENT
# ============================================
else
    print_step "Step 1: Checking Minikube..."
    if ! minikube status | grep -q "Running"; then
        echo "❌ Minikube is not running. Starting..."
        minikube start
    fi
    print_success "Minikube running"
    
    print_step "Step 2: Using Minikube Docker daemon..."
    eval $(minikube docker-env)
    print_success "Docker configured for Minikube"
    
    print_step "Step 3: Building customer-db in Minikube..."
    cd customer-db
    docker build -t customer-db:local .
    print_success "customer-db image built"
    
    print_step "Step 4: Building customer-viewer in Minikube..."
    cd ../customer-viewer
    docker build -t customer-viewer:local .
    print_success "customer-viewer image built"
    cd ..
    
    print_step "Step 5: Creating namespace..."
    kubectl create namespace ecatalog --dry-run=client -o yaml | kubectl apply -f -
    print_success "Namespace ready"
    
    print_step "Step 6: Deploying customer-db..."
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
EOF
    print_success "customer-db deployed"
    
    print_step "Step 7: Waiting for database..."
    kubectl wait --for=condition=ready pod -l app=customer-db -n ecatalog --timeout=60s
    print_success "Database ready"
    
    print_step "Step 8: Deploying customer-viewer..."
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
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: customer-viewer-secret
              key: DB_PASSWORD
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
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
    print_success "customer-viewer deployed"
    
    print_step "Step 9: Waiting for app..."
    kubectl wait --for=condition=ready pod -l app=customer-viewer -n ecatalog --timeout=60s
    print_success "App ready"
    
    echo ""
    echo "=========================================="
    echo "✅ DEPLOYMENT COMPLETE!"
    echo "=========================================="
    echo ""
    echo "📊 Access the app:"
    APP_URL=$(minikube service customer-viewer -n ecatalog --url)
    echo "   Web UI:  $APP_URL"
    echo ""
    echo "   Or open directly:"
    echo "   minikube service customer-viewer -n ecatalog"
    echo ""
    echo "🔍 Check status:"
    echo "   kubectl get all -n ecatalog"
    echo ""
    echo "📝 View logs:"
    echo "   kubectl logs -l app=customer-db -n ecatalog"
    echo "   kubectl logs -l app=customer-viewer -n ecatalog"
    echo ""
    echo "🧹 Cleanup:"
    echo "   kubectl delete namespace ecatalog"
    echo ""
fi