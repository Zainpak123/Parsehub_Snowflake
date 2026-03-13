# Backend Development Guide

## Project Structure

```
backend/
├── src/
│   ├── api/                 # REST API layer
│   │   ├── __init__.py
│   │   └── api_server.py   # Flask app & routes
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── analytics_service.py
│   │   ├── monitoring_service.py
│   │   ├── auto_sync_service.py
│   │   └── ...
│   ├── models/              # Data models & database
│   │   ├── __init__.py
│   │   ├── database.py      # SQLAlchemy models
│   │   └── db_pool.py       # Connection pooling
│   ├── utils/               # Utilities
│   │   ├── __init__.py
│   │   └── url_generator.py
│   └── config/              # Configuration
│       ├── __init__.py
│       ├── .env             # Environment variables
│       └── .env.example     # Template
├── migrations/              # Database migrations
├── logs/                    # Application logs
├── requirements.txt         # Python packages
├── requirements-python312.txt
├── Dockerfile               # Container image
└── Procfile                 # Deployment config
```

## Running the Backend

### Development with Flask

```bash
cd backend

# Activate virtual environment
source venv_sf/bin/activate  # On Windows: venv_sf\Scripts\activate

# Install dependencies
pip install -r requirements-python312.txt

# Run Flask development server
python -m flask run --host=0.0.0.0 --port=5000 --reload

# Access at http://localhost:5000
```

### Production with Gunicorn

```bash
# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 src.api.api_server:app
```

## Environment Configuration

Create `.env` file in `backend/src/config/`:

```env
# Flask
FLASK_ENV=production
FLASK_APP=src.api.api_server
DEBUG=False

# Snowflake
SNOWFLAKE_ACCOUNT=YOUR_ACCOUNT
SNOWFLAKE_USER=YOUR_USER
SNOWFLAKE_PASSWORD=YOUR_PASSWORD
SNOWFLAKE_DATABASE=PARSEHUB_DB
SNOWFLAKE_SCHEMA=PARSEHUB_DB

# ParseHub API
PARSEHUB_API_KEY=YOUR_KEY
PARSEHUB_BASE_URL=https://www.parsehub.com/api/v2

# Server
PORT=5000
HOST=0.0.0.0
```

## Services Overview

### API Server (api_server.py)
- REST API endpoints
- Request/response handling
- Health checks
- CORS support

### Analytics Service (analytics_service.py)
- Compute project statistics
- Generate reports
- Cache analytics data

### Monitoring Service (monitoring_service.py)
- Real-time project monitoring
- Session management
- Progress tracking

### Auto Sync Service (auto_sync_service.py)
- Automatic project synchronization
- Background job scheduling
- Error recovery

### Data Ingestion Service (data_ingestion_service.py)
- ETL pipeline
- Data validation
- Deduplication

## Adding New Services

1. Create service file in `src/services/`:
```python
# src/services/my_service.py

class MyService:
    def __init__(self):
        self.db = ParseHubDatabase()
    
    def process_data(self, data):
        # Implementation
        pass
```

2. Import and use in API:
```python
from src.services.my_service import MyService

service = MyService()
result = service.process_data(data)
```

## Database

### SQLite (Development)
- File-based database: `parsehub.db`
- Located in project root

### Snowflake (Production)
- Cloud-based data warehouse
- Configured via environment variables
- Connection pooling via `db_pool.py`

### Switching Databases

Edit `.env`:
```env
# For SQLite
DATABASE_PATH=parsehub.db

# For Snowflake  
SNOWFLAKE_ACCOUNT=account_id
SNOWFLAKE_USER=user
SNOWFLAKE_PASSWORD=password
SNOWFLAKE_DATABASE=PARSEHUB_DB
```

## Database Migrations

### Initial Setup
```bash
cd backend/migrations

# Run migration
python migrate_sqlite_to_snowflake.py

# Validate
python validate_migration.py

# Diagnose
python diagnose_migration.py
```

See `MIGRATION_GUIDE.md` for detailed information.

## API Endpoints

### Health Checks
```
GET /health
GET /health/detailed
```

### Projects
```
GET /api/projects                    # List all projects
GET /api/projects/:id               # Get project
POST /api/projects                  # Create project
PUT /api/projects/:id               # Update project
```

### Runs
```
GET /api/runs/:projectId            # List runs
GET /api/runs/:runId                # Get run details
POST /api/runs                      # Create run
```

### Analytics
```
GET /api/analytics/:projectId       # Get analytics
GET /api/analytics/:projectId/report # Download report
```

See `../docs/API.md` for complete documentation.

## Logging

### Configuration

Edit logs in `src/config/.env`:
```env
LOG_LEVEL=INFO
LOG_FILE=logs/parsehub.log
```

### Viewing Logs

```bash
tail -f backend/logs/parsehub.log
```

### Log Levels
- DEBUG: Detailed development info
- INFO: General information
- WARNING: Warnings
- ERROR: Errors
- CRITICAL: Critical errors

## Error Handling

### Expected Errors
```python
try:
    result = service.process()
except SpecificError as e:
    logger.error(f"Error: {e}")
    return jsonify({"error": str(e)}), 500
```

### Health Check Monitoring
```bash
curl http://localhost:5000/health/detailed
```

## Testing

```bash
# Run all tests
pytest backend/tests/

# Run specific test
pytest backend/tests/test_api.py

# With coverage
pytest --cov=src backend/tests/
```

## Performance Tips

1. **Database**: Use connection pooling
2. **Caching**: Cache frequently accessed data
3. **Async**: Use APScheduler for background jobs
4. **Monitoring**: Check logs for slow queries

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000  # On Mac/Linux
netstat -ano | findstr :5000  # On Windows

# Kill process
kill -9 <PID>
```

### Import Errors
- Check virtual environment is activated
- Verify all dependencies installed: `pip list`
- Check Python path: `sys.path`

### Database Connection Issues
- Verify `.env` configuration
- Test connection with: `python -c "from src.models.database import ParseHubDatabase; db = ParseHubDatabase(); print(db.connect())"`

## Deployment

See `infrastructure/README.md` for deployment instructions.

---

**Last Updated:** March 8, 2026
