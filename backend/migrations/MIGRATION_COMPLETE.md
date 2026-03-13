# SQLite to Snowflake Migration - Quick Start

## ✅ Migration Complete!

Your database has been successfully migrated from SQLite to Snowflake.

**Migration Results:**
- ✓ 21 tables created in Snowflake
- ✓ 240 rows successfully migrated
- ✓ All row counts verified and matched

## 📋 System Status

### Environment Setup
- ✓ Python 3.12 virtual environment (venv_sf) created
- ✓ All Snowflake packages installed (snowflake-connector-python, snowflake-sqlalchemy)
- ✓ Snowflake credentials configured in `.env` file
- ✓ Connection to Snowflake verified and working

### Fixed Issues
- ✓ SNOWFLAKE_ACCOUNT corrected from `VFHSGYP-GD78100.snowflakecomputing.com` to `VFHSGYP-GD78100`
  - The Snowflake connector automatically appends `.snowflakecomputing.com`

## 🚀 Running the Migration Yourself

If you need to re-run the migration or migrate fresh data:

### Step 1: Backup
```powershell
cd D:\Parsehub-Dashboard\Parsehub
Copy-Item parsehub.db parsehub.db.backup
```

### Step 2: Activate Virtual Environment
```powershell
cd D:\Parsehub-Dashboard\Parsehub\backend
.\venv_sf\Scripts\Activate.ps1
```

### Step 3: Run Diagnostics (Optional)
```powershell
python diagnose_migration.py
```

This shows:
- Snowflake connection status
- SQL that will be executed
- Migration statistics
- Total rows and tables to be migrated

### Step 4: Run Migration
```powershell
python migrate_sqlite_to_snowflake.py
```

**Expected output:**
```
[Migration starts]
✓ Connected to SQLite
✓ Connected to Snowflake

STEP 1: Creating Snowflake Tables
  ✓ Created table: projects
  ✓ Created table: runs
  ... (all 21 tables)

STEP 2: Migrating Data
  ✓ Migrated 105 rows to projects
  ✓ Migrated 50 rows to runs
  ... (all tables with row counts)

Migration Summary
✓ Tables created: 21
✓ Tables migrated: 21
✓ Rows migrated: 240

✅ Migration complete!
```

### Step 5: Validate
```powershell
python validate_migration.py
```

**Expected output:**
```
Database Migration Validation

✓ Tables matched: 21
✓ Row counts verified: 21

Total Statistics:
  SQLite total rows: 240
  Snowflake total rows: 240

✅ Validation PASSED
```

## 📁 Migration Scripts

All scripts are in `backend/`:

| Script | Purpose |
|--------|---------|
| `migrate_sqlite_to_snowflake.py` | Main migration script - creates tables and transfers data |
| `validate_migration.py` | Verifies that all data was migrated correctly |
| `diagnose_migration.py` | Tests connection and shows what would be migrated |
| `MIGRATION_GUIDE.md` | Comprehensive migration documentation |

## 🗄️ Tables Migrated

### Core Project Tables (21 total)
- `projects` - 105 rows
- `runs` - 50 rows
- `metadata` - 25 rows
- `product_data` - 20 rows
- Plus 17 more supporting tables

See `MIGRATION_GUIDE.md` for complete table list.

## ⚙️ Configuration

Your Snowflake configuration (in `backend/.env`):
```
SNOWFLAKE_ACCOUNT=VFHSGYP-GD78100
SNOWFLAKE_USER=ziauldin
SNOWFLAKE_WAREHOUSE=PARSEHUB_DB
SNOWFLAKE_DATABASE=PARSEHUB_DB
SNOWFLAKE_SCHEMA=PARSEHUB_DB
```

## 🧪 Testing Your Setup

### Test 1: Complete Setup Validation
```powershell
.\venv_sf\Scripts\python.exe test_complete_setup.py
```

This verifies:
- Environment variables
- All packages installed
- Snowflake connection
- Flask app readiness

### Test 2: Start Backend Server
```powershell
.\venv_sf\Scripts\python.exe -m flask run --host=0.0.0.0 --port=5000
```

Or with Gunicorn (production):
```powershell
.\venv_sf\Scripts\gunicorn.exe -w 4 -b 0.0.0.0:5000 api_server:app
```

## 🐳 Docker & Kubernetes Ready

Your setup is ready for containerization:

### Build Docker Image
```bash
docker build -f backend/Dockerfile -t parsehub-backend:latest .
```

### Test with Docker Compose
```bash
docker-compose up
```

Both frontend and backend will start with:
- Python 3.12 runtime
- All Snowflake packages
- Health checks configured
- Proper environment variables

### Deploy to Kubernetes
See `K8S_DEPLOYMENT_GUIDE.py` for step-by-step K8s deployment.

## 🔄 Rollback (If Needed)

If you need to rollback the migration:

### Restore SQLite
```powershell
cd D:\Parsehub-Dashboard\Parsehub

# Restore from backup
Remove-Item parsehub.db
Copy-Item parsehub.db.backup parsehub.db
```

### Drop Snowflake Tables (via SQL console)
```sql
DROP SCHEMA PARSEHUB_DB CASCADE;
CREATE SCHEMA PARSEHUB_DB;
```

Then run `migrate_sqlite_to_snowflake.py` again.

## 📊 Monitoring

After deployment, monitor your Snowflake database:

### Check Table Sizes
```sql
SELECT 
  TABLE_NAME,
  ROW_COUNT,
  BYTES / (1024 * 1024) as SIZE_MB
FROM INFORMATION_SCHEMA.TABLE_STORAGE_METRICS
WHERE SCHEMA_NAME = 'PARSEHUB_DB'
ORDER BY BYTES DESC;
```

### Monitor Queries
```sql
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE DATABASE_NAME = 'PARSEHUB_DB'
ORDER BY START_TIME DESC
LIMIT 20;
```

## 🐛 Troubleshooting

### "Could not connect to Snowflake backend"
**Fix:** Check `.env` file - account should be `VFHSGYP-GD78100` (without `.snowflakecomputing.com`)

### "Certificate did not match"
**Fix:** Ensure SNOWFLAKE_ACCOUNT doesn't include `.snowflakecomputing.com`

### Some tables are empty after migration
**Expected:** Not all tables have data initially. This is normal. Tables populate as you use the application.

### Migration is slow
**Solution:** Check network connectivity to Snowflake. Large datasets may take time. Be patient!

## ✨ What's Next

1. **Test Flask Backend** - Run `test_complete_setup.py` to verify all systems
2. **Local Docker Testing** - Use `docker-compose up` to test both services together
3. **Kubernetes Deployment** - Use `K8S_DEPLOYMENT_GUIDE.py` for step-by-step deployment
4. **Update Backend Code** - Update `database.py` to prefer Snowflake over SQLite
5. **Production Deployment** - Push to container registry and deploy to K8s cluster

## 📞 Support

For issues:
1. Check the migration logs in terminal output
2. Review `MIGRATION_GUIDE.md` for detailed information
3. Verify Snowflake credentials and account access
4. Check network connectivity to Snowflake
5. Review application logs in `/backend/logs/` if available

---

**Migration Date:** March 8, 2026  
**Status:** ✅ COMPLETE AND VERIFIED  
**Next Step:** Deploy to Kubernetes
