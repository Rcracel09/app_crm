# 🏢 app_crm

**CRM Application - React + FastAPI with Authentication**

Part of LTPLabs E-Catalog - Requisitos e Arquiteturas de Software (MEI, UMinho 2025/2026)

---

## 📋 Overview

Aplicação CRM completa que visualiza dados de clientes e interações. Integra com:
- ✅ **AuthGuard** do shared/auth (como app_draft)
- ✅ **database_crm** via service discovery
- ✅ **React** frontend com tabelas interativas
- ✅ **FastAPI** backend servindo API + static files

---

## 🏗️ Architecture

```
app_crm/
├── frontend/              # React + TypeScript
│   ├── src/
│   │   ├── main.tsx      # AuthGuard wrapper
│   │   ├── App.tsx       # Main component
│   │   ├── App.css       # Styles
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts    # @shared alias
│   ├── tsconfig.app.json # Path mapping
│   └── index.html
│
├── backend/              # FastAPI
│   ├── main.py          # API + serve React
│   └── requirements.txt
│
├── Dockerfile           # Multi-stage build
└── k8s/
    └── values.yaml      # K8s configuration
```

---

## 🚀 Deploy (via catalog_claudio)

```bash
cd catalog_claudio/

# 1. Deploy database FIRST
./scripts/build-deploy.sh database_crm local default

# 2. Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=database-crm --timeout=60s

# 3. Deploy CRM app
./scripts/build-deploy.sh app_crm local default

# 4. Access
minikube service app-crm
```

---

## 🔧 Configuration (k8s/values.yaml)

```yaml
image: app_crm:local
port: 8080
requiresAuth: true              # ← Integrates with projeto_ltp_labs

env:
  DB_HOST: "database-crm"       # ← Service discovery
  DB_PORT: "5432"
  DB_NAME: "demo_db"
  DB_USER: "postgres"
  DB_PASSWORD: "postgres123"

serviceType: NodePort
```

---

## 📊 Features

### Frontend (React)
- **AuthGuard** integration (skipValidation: true)
- Dashboard with statistics
- Customers table with PII highlighted
- Interactions table with type badges
- Responsive design

### Backend (FastAPI)
- `/api/customers` - Get all customers
- `/api/interactions` - Get all interactions
- `/api/stats` - Get database statistics
- `/api/health` - Health check
- `/api/ready` - Readiness probe (checks DB)
- Serves React static files for all other routes

---

## 🔗 Communication Flow

```
Browser
  ↓ HTTP
app_crm Pod (React + FastAPI)
  ↓ SQL query (DB_HOST=database-crm)
database-crm Service (ClusterIP)
  ↓
database-crm Pod (PostgreSQL)
```

---

## 🎨 UI Components

- **Statistics Dashboard**: Total customers, interactions, .pt emails
- **Customers Table**: All PII fields highlighted in yellow
- **Interactions Table**: Type badges (email, call, meeting, support)
- **Warning Banner**: Indicates demo data with PII

---

## 🐳 Dockerfile Breakdown

### Stage 1: Build React
```dockerfile
FROM node:20-alpine
# npm install + npm run build
# Output: /build/dist
```

### Stage 2: FastAPI + Static Files
```dockerfile
FROM python:3.11-slim
# Copy backend code
# Copy React build from stage 1
# Serve everything via FastAPI
```

---

## ✅ Integration Points

### 1. AuthGuard (shared/auth)
```tsx
import { AuthGuard } from '@shared/auth'

<AuthGuard skipValidation={true}>
  <App />
</AuthGuard>
```

### 2. Database Connection
```python
DB_HOST = os.getenv('DB_HOST', 'database-crm')
conn = psycopg2.connect(host=DB_HOST, ...)
```

### 3. Service Discovery
Kubernetes DNS automatically resolves `database-crm` to the database service.

---

## 🧪 Testing

### Local Development
```bash
# Terminal 1: Backend
cd app_crm/backend
pip install -r requirements.txt
DB_HOST=localhost python main.py

# Terminal 2: Frontend
cd app_crm/frontend
npm install
npm run dev
```

### In Kubernetes
```bash
# Check logs
kubectl logs -l app=app-crm -f

# Test API
kubectl port-forward svc/app-crm 8080:8080
curl http://localhost:8080/api/health
```

---

## 🔍 Troubleshooting

### "Database connection failed"
```bash
# Check if database_crm is running
kubectl get pods -l app=database-crm

# Check service exists
kubectl get svc database-crm

# Check app logs
kubectl logs -l app=app-crm
```

### AuthGuard not working
Make sure `shared/auth` exists in catalog_claudio root and the build script has linked it correctly.

---

## ✅ Ready for Deployment

This app is 100% compatible with:
- ✅ catalog_claudio umbrella chart
- ✅ build-deploy.sh script
- ✅ AuthGuard integration
- ✅ Service discovery
- ✅ Zero changes to catalog_claudio needed

**Status**: ✅ Production Ready