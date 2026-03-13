# Project Structure

## Complete Directory Tree

```
parsehub-dashboard/
│
├── 📄 README.md                          # Main project documentation
├── 📄 CONTRIBUTING.md                    # Contributing guidelines
├── 📄 pyproject.toml                     # Python project configuration
├── 📄 docker-compose.yml                 # Local development setup
├── 📄 .gitignore                         # Git ignore rules
├── 📄 Procfile                           # Deployment process file
├── 📄 requirements.txt                   # Python 3.14 dependencies
├── 📄 requirements-python312.txt         # Python 3.12 dependencies (recommended)
│
├── 📁 backend/                           # Backend Python Flask application
│   ├── 📄 __init__.py                   # Package initialization
│   ├── 📁 src/                          # Source code
│   │   ├── 📄 __init__.py
│   │   ├── 📁 api/                      # REST API layer
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 api_server.py         # Flask app & main routes
│   │   │   └── 📄 fetch_projects.py     # Project fetching logic
│   │   ├── 📁 services/                 # Business logic services
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 analytics_service.py
│   │   │   ├── 📄 analytics.py
│   │   │   ├── 📄 advanced_analytics.py
│   │   │   ├── 📄 monitoring_service.py
│   │   │   ├── 📄 auto_sync_service.py
│   │   │   ├── 📄 auto_runner_service.py
│   │   │   ├── 📄 incremental_scraping_scheduler.py
│   │   │   ├── 📄 incremental_scraping_manager.py
│   │   │   ├── 📄 scraping_session_service.py
│   │   │   ├── 📄 excel_import_service.py
│   │   │   ├── 📄 data_ingestion_service.py
│   │   │   ├── 📄 data_consolidation_service.py
│   │   │   ├── 📄 recovery_service.py
│   │   │   ├── 📄 pagination_service.py
│   │   │   └── 📄 monitor.py
│   │   ├── 📁 models/                   # Database models & ORM
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 database.py           # SQLAlchemy models
│   │   │   └── 📄 db_pool.py            # Connection pooling
│   │   ├── 📁 utils/                    # Utility functions
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 url_generator.py
│   │   └── 📁 config/                   # Configuration & env variables
│   │       ├── 📄 __init__.py
│   │       ├── 📄 .env                  # Environment variables (gitignored)
│   │       └── 📄 .env.example          # Environment template
│   ├── 📁 migrations/                   # Database migrations
│   │   ├── 📄 migrate_sqlite_to_snowflake.py  # SQLite → Snowflake script
│   │   ├── 📄 init_postgres.sql         # PostgreSQL schema
│   │   ├── 📄 MIGRATION_GUIDE.md        # Migration documentation
│   │   └── 📄 MIGRATION_COMPLETE.md     # Quick reference
│   ├── 📁 logs/                         # Application logs directory
│   ├── 📄 Dockerfile                    # Container image definition
│   └── 📁 venv_sf/                      # Python 3.12 virtual environment
│       ├── Scripts/
│       ├── Lib/
│       └── ...
│
├── 📁 frontend/                         # Frontend Next.js application
│   ├── 📁 src/                          # Source code
│   │   ├── 📁 app/                      # Next.js app router
│   │   ├── 📁 components/               # React components
│   │   └── 📁 lib/                      # Utilities & hooks
│   ├── 📁 public/                       # Static assets
│   ├── 📄 package.json                  # Dependencies & scripts
│   ├── 📄 Dockerfile                    # Container image
│   └── 📄 .env.example                  # Environment template
│
├── 📁 infrastructure/                   # Deployment & infrastructure
│   ├── 📄 README.md                     # Infrastructure guide
│   ├── 📁 kubernetes/                   # Kubernetes manifests
│   │   ├── 📄 README.md
│   │   ├── 📄 backend-deployment.yaml   # Backend K8s deployment
│   │   ├── 📄 backend-service.yaml      # Backend service
│   │   ├── 📄 backend-hpa.yaml          # Horizontal Pod Autoscaler
│   │   ├── 📄 frontend-deployment.yaml
│   │   ├── 📄 frontend-service.yaml
│   │   ├── 📄 configmap.yaml            # Configuration
│   │   ├── 📄 secrets.yaml              # Secrets template
│   │   └── 📄 namespace.yaml
│   ├── 📁 docker/                       # Docker configurations
│   │   ├── 📄 Dockerfile-backend        # Backend image
│   │   ├── 📄 Dockerfile-frontend       # Frontend image
│   │   └── 📄 .dockerignore
│   └── 📁 scripts/                      # Deployment automation
│       ├── 📄 deploy.sh
│       ├── 📄 rollback.sh
│       └── 📄 health-check.sh
│
├── 📁 docs/                             # Project documentation
│   ├── 📄 BACKEND.md                    # Backend development guide
│   ├── 📄 INFRASTRUCTURE.md             # Infrastructure guide
│   ├── 📄 API.md                        # API documentation (if available)
│   ├── 📄 DATABASE.md                   # Database schema (if available)
│   ├── 📄 DEPLOYMENT.md                 # Deployment guide (if available)
│   └── 📄 ARCHITECTURE.md               # Architecture (if available)
│
├── 📁 scripts/                          # Utility scripts
│   ├── 📄 setup.sh                      # Initial setup script (if available)
│   └── 📄 dev-setup.sh                  # Dev environment setup (if available)
│
├── 📁 .github/                          # GitHub configuration
│   ├── 📁 workflows/                    # CI/CD workflows
│   │   ├── 📄 tests.yml                 # Test pipeline
│   │   ├── 📄 deploy.yml                # Deployment pipeline
│   │   └── ...
│   └── ...
│
├── 📁 .vscode/                          # VS Code configuration
│   ├── 📄 settings.json
│   ├── 📄 launch.json
│   └── ...
│
└── 📁 .git/                             # Git repository
```

## Key Files Description

### Root Level

| File | Purpose |
|------|---------|
| README.md | Project overview, quick start, features |
| CONTRIBUTING.md | Contribution guidelines |
| pyproject.toml | Python project metadata & config |
| docker-compose.yml | Local development environment |
| .gitignore | Git ignore patterns |
| requirements.txt | Python dependencies (Python 3.14) |
| requirements-python312.txt | Python dependencies (Python 3.12 - recommended) |

### Backend Structure

| Directory | Purpose |
|-----------|---------|
| src/api/ | REST API endpoints and routing |
| src/services/ | Business logic services |
| src/models/ | Database models and queries |
| src/utils/ | Helper functions and utilities |
| src/config/ | Configuration and environment setup |
| migrations/ | Database migration scripts |
| logs/ | Application log files |
| venv_sf/ | Python 3.12 virtual environment |

### Frontend Structure

| Directory | Purpose |
|-----------|---------|
| src/app/ | Next.js app router and pages |
| src/components/ | Reusable React components |
| src/lib/ | Frontend utilities and helpers |
| public/ | Static files (images, fonts, etc) |

### Infrastructure

| Directory | Purpose |
|-----------|---------|
| kubernetes/ | Kubernetes deployment manifests |
| docker/ | Docker image definitions |
| scripts/ | Deployment automation scripts |

### Documentation

| File | Purpose |
|------|---------|
| docs/BACKEND.md | Backend development guide |
| docs/INFRASTRUCTURE.md | Infrastructure & deployment |
| docs/API.md | API reference documentation |
| docs/DATABASE.md | Database schema and queries |

## Database Organization

### Snowflake (Production)
- Account: `VFHSGYP-GD78100`
- Database: `PARSEHUB_DB`
- Schema: `PARSEHUB_DB`
- Tables: 21 (projects, runs, product_data, etc.)

### SQLite (Development)
- File: `parsehub.db` (in project root)
- Backup: `parsehub.db.backup`

## Environment Files

### .env Files (Not in Git)
```
backend/src/config/.env      # Backend configuration
frontend/.env.local          # Frontend configuration
```

### Example Files (In Git)
```
backend/src/config/.env.example
frontend/.env.example
```

## Configuration Files (In Git)

```
.gitignore                   # Git ignore rules
docker-compose.yml           # Local dev setup
pyproject.toml              # Python project config
infrastructure/kubernetes/  # K8s manifests
infrastructure/docker/      # Docker files
```

## Important Notes

1. **Never commit** `.env` files or credentials
2. **Always use** Python 3.12 for consistency
3. **Backend** virtual environment: `backend/venv_sf/`
4. **Database choice**: Snowflake for prod, SQLite for dev
5. **Port mapping**: Backend 5000, Frontend 3000
6. **Documentation** is in `docs/` directory
7. **Scripts** are in `infrastructure/scripts/`

## Quick Reference

### Start Development
```bash
# Backend
cd backend
source venv_sf/bin/activate
python -m flask run --port 5000

# Frontend
cd frontend
npm run dev
```

### View Project Structure
```bash
# Show directory tree
tree -L 3 -I 'node_modules|__pycache__|venv*'

# Or with PowerShell
Get-ChildItem -Recurse | Where-Object {$_.PSIsContainer}
```

### Database Setup
```bash
# View schema
cd backend
python inspect_sqlite_schema.py

# Migrate to Snowflake
python migrations/migrate_sqlite_to_snowflake.py

# Validate migration
python migrations/validate_migration.py
```

### Docker Setup
```bash
# Browse with compose
docker-compose up -d
docker-compose logs -f backend

# Build images
docker build -f infrastructure/docker/Dockerfile-backend -t parsehub-backend:latest .
docker build -f infrastructure/docker/Dockerfile-frontend -t parsehub-frontend:latest .
```

---

**Last Updated:** March 8, 2026  
**Status:** Professional Repository Structure ✅
