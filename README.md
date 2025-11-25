# 👁️ Customer Viewer

**Simple web app to visualize customer database data**

Part of LTPLabs E-Catalog - Requisitos e Arquiteturas de Software (MEI, UMinho 2025/2026)

---

## 📋 Overview

Aplicação web simples que conecta à `customer-db` e visualiza os dados em tabelas HTML.

### Features
- 📊 Visualização de clientes em tabela
- 💬 Visualização de interações
- 📈 Estatísticas da base de dados
- 🔍 Campos PII destacados visualmente
- 🌐 API REST para acesso programático

---

## 🏗️ Estrutura

```
customer-viewer/
├── Dockerfile          # Container da app
├── app.py             # Flask application
├── requirements.txt   # Dependências Python
├── templates/
│   └── index.html     # Template HTML
├── k8s/
│   └── values.yaml    # Configuração K8s
└── README.md
```

---

## 🚀 Quick Start

### Pré-requisitos
A `customer-db` deve estar a correr e acessível.

### Local (Docker)

```bash
# Build
docker build -t customer-viewer:local .

# Run (assumindo customer-db em localhost:5432)
docker run -d \
  --name customer-viewer \
  -p 8080:8080 \
  -e DB_HOST=host.docker.internal \
  customer-viewer:local

# Access
open http://localhost:8080
```

### Minikube (Kubernetes)

```bash
# Build for Minikube
eval $(minikube docker-env)
docker build -t customer-viewer:local .

# Deploy (via umbrella chart)
# A app conecta automaticamente a customer-db via service name

# Access
minikube service customer-viewer
```

---

## 🔧 Configuration

### Environment Variables

```bash
DB_HOST=customer-db        # Service name no K8s
DB_PORT=5432
DB_NAME=demo_db
DB_USER=postgres
DB_PASSWORD=postgres123
```

### Kubernetes (k8s/values.yaml)

```yaml
image: customer-viewer:local
port: 8080
env:
  DB_HOST: "customer-db"
```

---

## 📊 Endpoints

### Web Interface
- `GET /` - Homepage com tabelas de dados

### API
- `GET /api/customers` - Lista clientes (JSON)
- `GET /api/interactions` - Lista interações (JSON)

### Health Checks
- `GET /health` - Health check
- `GET /ready` - Readiness probe (verifica DB)

---

## 🎨 Interface

A interface mostra:

### Estatísticas
- Total de clientes
- Total de interações
- Total de emails .pt

### Tabela de Customers
Colunas: ID | Name | Email | Phone | Company | Address | Notes

### Tabela de Interactions
Colunas: ID | Customer | Type | Subject | Description | Created By | Date

**Campos PII destacados** com fundo amarelo para fácil identificação.

---

## 🧪 Testing

```bash
# Test connection
curl http://localhost:8080/health

# Test API
curl http://localhost:8080/api/customers | jq
curl http://localhost:8080/api/interactions | jq

# Check readiness
curl http://localhost:8080/ready
```

---

## 🐛 Troubleshooting

### "Error connecting to database"

```bash
# Verify customer-db is running
docker ps | grep customer-db
# or
kubectl get pods | grep customer-db

# Check connection from viewer
docker exec -it customer-viewer \
  psql -h customer-db -U postgres -d demo_db
```

### App não conecta no K8s

```bash
# Verify service exists
kubectl get svc customer-db

# Check logs
kubectl logs deployment/customer-viewer
```

---

## 📦 Dependencies

```
flask==3.0.0
psycopg2-binary==2.9.9
```

---

## 🔗 Integration

Esta app funciona em conjunto com:
- **customer-db** - PostgreSQL com dados PII
- **Umbrella chart** - Deploy orchestration

---

## ✅ Checklist

Antes de considerar pronta:
- [x] Conecta à customer-db
- [x] Mostra todos os clientes
- [x] Mostra todas as interações
- [x] Campos PII destacados
- [x] Health checks funcionam
- [x] API endpoints funcionam
- [x] Interface responsiva

---

**Status**: ✅ Ready for deployment

---

*Built for LTPLabs E-Catalog - Universidade do Minho MEI 2025/2026*