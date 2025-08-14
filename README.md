# Product Catalog Service

A small backend microservice exposing a REST API to manage a product catalog with CRUD and search, containerized with Docker, tested via GitHub Actions, and deployable to **Azure Container Apps** (scripts included). It includes a `/health` endpoint and simple console logging.

> Built to satisfy the assignment requirements【7†source】.

---

## Stack
- **Python** + **FastAPI** (REST)
- **SQLite** + SQLAlchemy (lightweight DB)
- **Docker** (containerization)
- **GitHub Actions** (CI: test + build)
- **Azure Container Apps** (example cloud deploy script)
- **Kubernetes YAML** (bonus)

## API

Base URL: `http://localhost:8000`

- `GET /health` — Health check
- `GET /products` — List products
- `POST /products` — Create product
- `PUT /products/{id}` — Update product by ID
- `DELETE /products/{id}` — Delete product by ID
- `GET /products/search?query=` — Search by name or category

### Product Schema
```json
{
  "id": 1,
  "name": "Acoustic Guitar",
  "description": "A 6-string acoustic guitar",
  "price": 199.99,
  "category": "Instruments"
}
```

### Example cURL
```bash
# Health
curl -s http://localhost:8000/health

# Create
curl -s -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Acoustic Guitar","description":"A 6-string","price":"199.99","category":"Instruments"}'

# List
curl -s http://localhost:8000/products | jq .

# Update
curl -s -X PUT http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Electric Guitar","description":"A strat","price":"299.99","category":"Instruments"}'

# Search
curl -s "http://localhost:8000/products/search?query=guitar"
```

---

## Run Locally

### 1) Python (no Docker)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL="sqlite:///./app.db"  # optional
uvicorn app.main:app --reload
```

### 2) Docker
```bash
docker build -t product-catalog:local .
docker run -p 8000:8000 --name product-catalog product-catalog:local
```

> Docker image has a healthcheck that calls `/health`.

FastAPI auto-docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Tests (Pytest)
```bash
pip install -r requirements.txt
pytest -q
```

---

## CI/CD (GitHub Actions)

Workflow file: `.github/workflows/ci.yml`  
- Installs dependencies
- Runs tests
- Builds a Docker image
- Optionally logs into Docker Hub & pushes (if `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` are set as repo secrets)

> Matches the pipeline expectations of the assignment【7†source】.

---

## Cloud Deployment (Azure Container Apps)

Script: `scripts/deploy-azure-containerapp.sh`

### Steps
```bash
# Login & select subscription
az login
az account set --subscription "<SUBSCRIPTION_ID>"

# Set variables
export RESOURCE_GROUP="rg-product-catalog"
export LOCATION="eastus"
export ACR_NAME="pcatalogacr$RANDOM"
export ACA_ENV="pcatalog-env"
export APP_NAME="pcatalog-api"
export IMAGE="pcatalog/product-catalog:latest"

# Run deploy
bash scripts/deploy-azure-containerapp.sh
# Script prints the public URL at the end
```

If you prefer **AWS ECS/EKS**, the same Docker image can be deployed. (ECS Fargate with ALB is typical.) Include a task definition with port 8000 and a health check on `/health`.

---

## Kubernetes (Bonus)

Apply from `k8s/` after replacing the image:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl get pods
kubectl port-forward svc/product-catalog-svc 8080:80
```

---

## Configuration

Environment variables:
- `DATABASE_URL` — default `sqlite:///./app.db`
- `LOG_LEVEL` — default `INFO`
- `PORT` — default `8000`

---

## Notes on Design

- **Validation & Errors**: Pydantic models validate inputs; missing product → `404`.
- **Search**: Simple case-insensitive LIKE on `name` and `category`.
- **Logging**: Basic structured console logs for create/update/delete/search.
- **Depth > breadth**: Clean, readable code and working pipeline vs. too many extras【7†source】.
