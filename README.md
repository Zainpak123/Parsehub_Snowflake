# ParseHub Dashboard

A comprehensive real-time monitoring and data collection platform for ParseHub projects, built with Flask, Next.js, and Snowflake.

## 🎯 Project Overview

ParseHub Dashboard provides:
- ✅ Real-time monitoring of ParseHub scraping projects
- ✅ Automatic data ingestion and consolidation
- ✅ Advanced analytics and reporting
- ✅ Multi-project management with metadata tracking
- ✅ Incremental scraping with recovery operations
- ✅ Kubernetes-native deployment
- ✅ Snowflake integration for scalable data storage

## 📊 Tech Stack

### Backend
- **Framework:** Flask 3.0.0
- **Server:** Gunicorn 21.2.0
- **Database:** Snowflake (primary), SQLite (local dev)
- **Python:** 3.12+
- **Task Queue:** APScheduler

### Frontend
- **Framework:** Next.js 14
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Charting:** Recharts
- **Package Manager:** npm/yarn

### Infrastructure
- **Container:** Docker
- **Orchestration:** Kubernetes
- **Database:** Snowflake (serverless, managed)
- **Deployment:** CI/CD ready

## 📂 Project Structure

```
parsehub-dashboard/
├── backend/
│   ├── src/
│   │   ├── api/                 # REST API endpoints
│   │   ├── services/            # Business logic services
│   │   ├── models/              # Database models & ORM
│   │   ├── utils/               # Utility functions
│   │   └── config/              # Configuration & env vars
│   ├── migrations/              # Database migrations
│   ├── logs/                    # Application logs
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Container definition
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js app router
│   │   ├── components/          # React components
│   │   └── lib/                 # Utility functions
│   ├── public/                  # Static assets
│   └── package.json             # NPM dependencies
├── infrastructure/
│   ├── kubernetes/              # K8s manifests & deployments
│   ├── docker/                  # Docker configurations
│   └── scripts/                 # Deployment scripts
├── docs/                        # Documentation
├── scripts/                     # Utility scripts
├── docker-compose.yml           # Local development
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose (optional)
- Snowflake account (for production)

### Local Development

#### 1. Clone & Setup

```bash
git clone https://github.com/yourorg/parsehub-dashboard.git
cd parsehub-dashboard
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv_sf
source venv_sf/bin/activate  # On Windows: venv_sf\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp src/config/.env.example src/config/.env
# Edit src/config/.env with your credentials
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with backend URL
```

#### 4. Run Locally

**Backend:**
```bash
cd backend
python -m flask run --host=0.0.0.0 --port=5000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

Access the dashboard at `http://localhost:3000`

### Docker Compose

```bash
docker-compose up -d
```

This starts both backend and frontend with proper networking and health checks.

## 🔧 Configuration

### Backend Configuration

Environment variables are in `backend/src/config/.env`:

```env
# ParseHub API
PARSEHUB_API_KEY=your_key_here
PARSEHUB_BASE_URL=https://www.parsehub.com/api/v2

# Snowflake
SNOWFLAKE_ACCOUNT=your_account_id
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=PARSEHUB_DB
SNOWFLAKE_SCHEMA=PARSEHUB_DB

# Server
PORT=5000
DEBUG=False
```

### Frontend Configuration

Environment variables are in `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## 📦 API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /api/projects` - List projects
- `GET /api/projects/:id` - Get project details
- `POST /api/projects` - Create project
- `GET /api/runs/:projectId` - Get project runs
- `GET /api/analytics/:projectId` - Get analytics

### Documentation
Full API documentation: [docs/API.md](docs/API.md)

## 🗄️ Database

### Schema

- **projects** - Project registry
- **runs** - Scraping execution records
- **product_data** - Scraped products
- **monitoring_sessions** - Real-time monitoring
- **metadata** - Project metadata & tracking
- Plus 16+ supporting tables

### Migrations

Run database migrations:

```bash
cd backend/migrations
python migrate_sqlite_to_snowflake.py
```

See [MIGRATION_GUIDE.md](backend/migrations/MIGRATION_GUIDE.md) for details.

## 🐳 Docker & Kubernetes

### Build Docker Images

```bash
# Backend
docker build -f infrastructure/docker/Dockerfile-backend -t parsehub-backend:latest .

# Frontend
docker build -f infrastructure/docker/Dockerfile-frontend -t parsehub-frontend:latest .
```

### Kubernetes Deployment

```bash
# Apply K8s manifests
kubectl apply -f infrastructure/kubernetes/

# Verify deployment
kubectl get pods -n parsehub
kubectl get svc -n parsehub
```

See [infrastructure/kubernetes/README.md](infrastructure/kubernetes/README.md) for K8s deployment guide.

## 📊 Services

### Backend Services

| Service | Purpose |
|---------|---------|
| API Server | REST API endpoints |
| Analytics Service | Compute project statistics |
| Monitoring Service | Real-time data collection |
| Auto Sync Service | Automatic project synchronization |
| Data Ingestion Service | Data pipeline management |
| Recovery Service | Handle failed runs |
| Pagination Service | URL pagination logic |

### Database

- **SQLite** - Local development
- **Snowflake** - Production data warehouse

## 📈 Features

### Project Management
- Create and manage ParseHub projects
- Track project metadata
- Bulk operations

### Real-time Monitoring
- Live progress updates
- Page-by-page tracking
- Error handling and recovery

### Data Analytics
- Product statistics
- Historical trends
- Custom reporting

### Data Management
- Incremental scraping
- Deduplication
- CSV exports
- Batch operations

## 🔐 Security

- Environment-based secrets management
- Role-based access control (RBAC) in K8s
- TLS/SSL encryption in transit
- Sensitive data logging redaction
- API key rotation support

## 📝 Documentation

- [Backend API Documentation](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Configuration Guide](docs/CONFIG.md)

## 🧪 Testing

```bash
cd backend

# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

## 🚢 Deployment

### Development
```bash
docker-compose up -d
```

### Production (Kubernetes)
```bash
kubectl apply -f infrastructure/kubernetes/parsehub-deployment.yaml
```

### Environment Checklist
- [ ] Snowflake credentials configured
- [ ] ParseHub API key configured
- [ ] Database initialized
- [ ] SSL certificates provisioned
- [ ] Secrets configured in K8s

## 🔄 CI/CD Pipeline

See `.github/workflows/` for GitHub Actions configuration:
- Unit test pipeline
- Integration tests
- Docker build & push
- Kubernetes deployment

## 📊 Monitoring & Logging

### Application Logs
```bash
# View logs
tail -f backend/logs/parsehub.log

# Via Docker
docker logs parsehub-backend
```

### Metrics
- CPU/Memory usage via Kubernetes metrics
- Request latency via Flask logging
- Database query performance via Snowflake

## 🐛 Troubleshooting

### Snowflake Connection Issues
1. Verify account ID format: `ACCOUNT_ID` (not full URL)
2. Check network connectivity to Snowflake
3. Verify credentials and permissions
4. Check IP whitelisting in Snowflake

### API Server Won't Start
1. Check Python version: `python --version` (requires 3.12+)
2. Verify virtual environment activated
3. Check `.env` configuration
4. Review logs: `tail -f backend/logs/parsehub.log`

### Frontend Issues
1. Verify `NEXT_PUBLIC_API_URL` is correct
2. Check CORS settings in backend
3. Clear Next.js cache: `rm -rf .next`
4. Check browser console for errors

## 📞 Support & Contributing

### Reporting Issues
- Use GitHub Issues with detailed reproduction steps
- Include environment details and logs
- Tag with appropriate labels

### Contributing
1. Create feature branch
2. Ensure tests pass
3. Submit pull request
4. Wait for review & merge

## 📄 License

[Add your license here]

## 🎉 Acknowledgments

- ParseHub for the amazing API
- Flask & Next.js communities
- Snowflake for the data warehouse platform

---

**Last Updated:** March 8, 2026  
**Version:** 1.0.0  
**Status:** Production Ready ✅
