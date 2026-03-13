# SQLite to Snowflake Database Migration Guide

## Overview

This guide walks through migrating your ParseHub Dashboard database from SQLite (`parsehub.db`) to Snowflake for Kubernetes deployment.

## Migration Architecture

```
SQLite (parsehub.db)
    ↓
    ├─→ Schema Inspection
    ├─→ Type Mapping (SQLite → Snowflake)
    ├─→ Table Creation (Snowflake)
    └─→ Data Migration (batch insert)
    ↓
Snowflake Database
    ↓
    Validation & Verification
```

## Prerequisites

✅ **Already Installed in Your venv_sf:**
- `snowflake-connector-python==3.10.1`
- `python-dotenv==1.0.0`
- `requests==2.31.0`

✅ **Environment Configuration:**
- `.env` file with Snowflake credentials configured
- Access to Snowflake account (VFHSGYP-GD78100.snowflakecomputing.com)

## Step-by-Step Migration

### Step 1: Review Migration Scripts

```bash
cd D:\Parsehub-Dashboard\Parsehub\backend

# View migration script
type migrate_sqlite_to_snowflake.py

# View validation script
type validate_migration.py
```

### Step 2: Backup SQLite Database

Before running migration, **backup your SQLite database**:

```powershell
cd D:\Parsehub-Dashboard\Parsehub

# Create backup
Copy-Item parsehub.db parsehub.db.backup
Write-Host "Backup created: parsehub.db.backup"
```

### Step 3: Run Schema Migration

Create all Snowflake tables and migrate data:

```powershell
cd D:\Parsehub-Dashboard\Parsehub\backend

# Activate virtual environment
.\venv_sf\Scripts\Activate.ps1

# Run migration
python migrate_sqlite_to_snowflake.py
```

**Expected Output:**

```
================================================================================
🚀 SQLite to Snowflake Database Migration
================================================================================

✓ Connected to SQLite: d:\Parsehub-Dashboard\Parsehub\parsehub.db
✓ Connected to Snowflake
  Database: PARSEHUB_DB
  Schema: PARSEHUB_DB

Found 20 tables

================================================================================
STEP 1: Creating Snowflake Tables
================================================================================
  ✓ Created table: projects
  ✓ Created table: runs
  ✓ Created table: scraped_data
  ✓ Created table: metrics
  ...

================================================================================
STEP 2: Migrating Data
================================================================================
  ✓ Migrated 5 rows to projects
  ✓ Migrated 25 rows to runs
  ✓ Migrated 1200 rows to scraped_data
  ✓ Migrated 0 rows to metrics
  ...

================================================================================
📊 Migration Summary
================================================================================
✓ Tables created: 20
✓ Tables migrated: 20
✓ Rows migrated: 2,547

✅ Migration complete!
================================================================================
```

### Step 4: Validate Migration

Verify that all data was successfully migrated:

```powershell
cd D:\Parsehub-Dashboard\Parsehub\backend

# Activate virtual environment
.\venv_sf\Scripts\Activate.ps1

# Run validation
python validate_migration.py
```

**Expected Output:**

```
================================================================================
🔍 Database Migration Validation
================================================================================

✓ Connected to SQLite
✓ Connected to Snowflake

SQLite tables: 20
Snowflake tables: 20

================================================================================
Table Validation
================================================================================
✓ projects: 5 rows ✓
✓ runs: 25 rows ✓
✓ scraped_data: 1200 rows ✓
✓ metrics: 0 rows ✓
...

================================================================================
📋 Validation Report
================================================================================

✓ Tables matched: 20
✓ Row counts verified: 20

📊 Total Statistics:
  SQLite total rows: 2,547
  Snowflake total rows: 2,547

================================================================================
✅ Validation PASSED
================================================================================
```

## Tables Migrated

### Core Tables

| Table | Purpose | Rows |
|-------|---------|------|
| `projects` | Project registration | ~5 |
| `runs` | Scraping runs | ~25 |
| `metadata` | Project metadata from imports | ~100 |

### Data Tables

| Table | Purpose | Rows |
|-------|---------|------|
| `scraped_data` | Raw scraped records | ~1000+ |
| `product_data` | Structured product data | ~500+ |
| `analytics_records` | Analytics aggregations | ~200+ |

### Session & Monitoring

| Table | Purpose | Rows |
|-------|---------|------|
| `monitoring_sessions` | Real-time monitoring | ~50 |
| `scraping_sessions` | Campaign sessions | ~10 |
| `iteration_runs` | Iteration tracking | ~50 |

### Operating Tables

| Table | Purpose | Rows |
|-------|---------|------|
| `recovery_operations` | Recovery tracking | 0-10 |
| `run_checkpoints` | Progress checkpoints | ~100 |
| `data_lineage` | Data provenance | ~500 |
| `url_patterns` | URL patterns | ~5 |
| `import_batches` | Batch imports | ~10 |

### Cache Tables

| Table | Purpose | Rows |
|-------|---------|------|
| `analytics_cache` | Cached analytics | ~5 |
| `csv_exports` | Cached CSV data | ~5 |
| `combined_scraped_data` | Combined results | ~5 |

### Linking Tables

| Table | Purpose |
|-------|---------|
| `project_metadata` | Projects ↔ Metadata link |

## Data Type Mappings

| SQLite Type | Snowflake Type | Notes |
|-------------|----------------|-------|
| INTEGER | NUMBER(18,0) | Supports up to 18 digits |
| BOOLEAN | BOOLEAN | True/False values |
| REAL | FLOAT | Floating point numbers |
| NUMERIC | NUMBER(18,2) | Decimal with 2 places |
| TEXT | VARCHAR(16777216) | Max 16MB per cell |
| BLOB | BINARY | Binary data |
| DATE | DATE | Date only |
| TIME | TIME | Time only |
| TIMESTAMP | TIMESTAMP_NTZ | No timezone |

## Rollback Procedure

If migration fails, restore from backup:

```powershell
cd D:\Parsehub-Dashboard\Parsehub

# Restore SQLite backup
Remove-Item parsehub.db
Copy-Item parsehub.db.backup parsehub.db

Write-Host "SQLite restored from backup"

# Drop Snowflake tables (if needed)
# Access Snowflake via SQL client and run:
# DROP SCHEMA PARSEHUB_DB CASCADE
```

## Troubleshooting

### Issue: Connection Failed

**Error:** `Could not connect to Snowflake backend`

**Solution:**
1. Verify `.env` file has correct credentials
2. Check Snowflake account/user/password are correct
3. Ensure network can reach Snowflake (may need IP whitelisting)

### Issue: Missing Tables After Migration

**Error:** Some tables appear in validation report as missing

**Solution:**
1. Check SQLite database has tables: `python inspect_sqlite_schema.py`
2. Check Snowflake user has CREATE TABLE permission
3. Review migration script error messages for specific failures

### Issue: Row Count Mismatch

**Error:** Validation shows different row counts

**Solution:**
1. Check for NULL values in data (may cause insertion failures)
2. Verify character encoding in text fields
3. Look for data type conversion issues in migration logs

### Issue: Memory Issues with Large Data

If migration is slow or times out with large datasets:

```powershell
# Modify batch size in migrate_sqlite_to_snowflake.py
# Line 179: Change batch_size = 100 to smaller value (e.g., 50)

# Then run migration again
python migrate_sqlite_to_snowflake.py
```

## Next Steps After Migration

### 1. Update Backend Configuration

Update `backend/database.py` to use Snowflake instead of SQLite:

```python
# Add this at the top of ParseHubDatabase.__init__
self.use_snowflake = True
self.snowflake_config = {
    'account': os.getenv('SNOWFLAKE_ACCOUNT'),
    'user': os.getenv('SNOWFLAKE_USER'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
    'database': os.getenv('SNOWFLAKE_DATABASE'),
    'schema': os.getenv('SNOWFLAKE_SCHEMA')
}
```

### 2. Test with Flask Backend

```powershell
cd D:\Parsehub-Dashboard\Parsehub\backend

# Activate venv
.\venv_sf\Scripts\Activate.ps1

# Run complete setup test
python test_complete_setup.py

# Start Flask server
python -m flask run --host=0.0.0.0 --port=5000
```

### 3. Test with Docker

```bash
# Build Docker image
docker build -f backend/Dockerfile -t parsehub-backend:latest .

# Run container
docker run -p 5000:5000 --env-file backend/.env parsehub-backend:latest
```

### 4. Deploy to Kubernetes

See `K8S_DEPLOYMENT_GUIDE.py` for full Kubernetes deployment instructions.

## Performance Optimization

### Enable Clustering (optional)

```sql
-- In Snowflake SQL console
ALTER TABLE product_data CLUSTER BY (project_id, extraction_date);
ALTER TABLE scraped_data CLUSTER BY (project_id, created_at);
```

### Create Materialized Views (optional)

```sql
-- Cache expensive aggregations
CREATE MATERIALIZED VIEW project_stats_mv AS
SELECT 
  p.id,
  p.token,
  COUNT(DISTINCT r.id) as total_runs,
  COUNT(DISTINCT pd.id) as total_products,
  MAX(r.end_time) as last_run_date
FROM projects p
LEFT JOIN runs r ON p.id = r.project_id
LEFT JOIN product_data pd ON p.id = pd.project_id
GROUP BY p.id, p.token;
```

## Monitoring Migration

Monitor Snowflake performance after migration:

```sql
-- Check table sizes
SELECT 
  TABLE_NAME,
  ROW_COUNT,
  BYTES / (1024 * 1024) as SIZE_MB
FROM INFORMATION_SCHEMA.TABLE_STORAGE_METRICS
WHERE SCHEMA_NAME = 'PARSEHUB_DB'
ORDER BY BYTES DESC;

-- Check query performance
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE DATABASE_NAME = 'PARSEHUB_DB'
ORDER BY START_TIME DESC
LIMIT 20;
```

## Support

For issues or questions:
1. Check migration logs in console output
2. Review error messages in `migrate_sqlite_to_snowflake.py` output
3. Verify Snowflake credentials and permissions
4. Check SQLite database integrity before migration

---

**Last Updated:** March 8, 2026
**Migration Scripts:** `migrate_sqlite_to_snowflake.py`, `validate_migration.py`
**Status:** Production-Ready for Kubernetes Deployment
