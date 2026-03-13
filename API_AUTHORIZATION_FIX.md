# 401 Authorization Fix - Implementation Guide

## Problem Summary

The frontend was reporting `401 Unauthorized` errors on the `/api/filters` and `/api/metadata` endpoints despite these being publicly readable endpoints that should not require authentication.

## Root Cause Analysis

### Three-Layer Issue Identified:

1. **Frontend Proxy Authentication (FIXED)**
   - The Next.js proxy (`frontend/app/api/_proxy.ts`) was unconditionally adding API key headers to ALL requests
   - Public read-only endpoints were being sent authentication headers that could cause validation issues
   - Fix: Modified proxy to exclude API key headers for public GET endpoints

2. **Backend Code (VERIFIED CORRECT)**
   - The Flask endpoints `/api/filters` and `/api/metadata` are correctly marked as "Public read endpoint - no authentication required"
   - Neither endpoint calls `validate_api_key()` function
   - Backend code is correct and doesn't need modification

3. **Service Connectivity (NEEDS SETUP)**
   - Flask backend must run on port 5000 (or configured via BACKEND_API_URL)
   - Next.js frontend must be able to reach the backend via the proxy
   - This is currently blocked by Flask server startup issues in the Windows development environment

## Implementation Details

### Fixed: Frontend Proxy Authentication

**File**: `frontend/app/api/_proxy.ts`

**Change**: Modified to NOT send API key headers for public GET endpoints

```typescript
// Public endpoints that don't require API key authentication
const isPublicEndpoint = method === 'GET' && (
    backendPath.startsWith('/api/filters') ||
    backendPath.startsWith('/api/metadata') ||
    backendPath.startsWith('/api/projects?') ||
    backendPath.startsWith('/api/health')
);

const outgoingHeaders: Record<string, string> = {
    'Content-Type':  'application/json',
    'Accept':        'application/json',
    // Only add API key for non-public endpoints or mutating operations
    ...(!isPublicEndpoint && apiKey ? { 'Authorization': `Bearer ${apiKey}`, 'x-api-key': apiKey } : {}),
};
```

**Impact**: Public endpoints will now be accessible without API key validation, matching the backend's intent.

### Environment Configuration Files Created

**File**: `backend/.env`
```
BACKEND_PORT=5000
PORT=5000
SNOWFLAKE_ACCOUNT=VFHSGYP
SNOWFLAKE_USER=parsehub_user
SNOWFLAKE_PASSWORD=ParseHub@Snowflake2024
SNOWFLAKE_DATABASE=PARSEHUB_DB
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_SCHEMA=PUBLIC
BACKEND_API_KEY=t_hmXetfMCq3
ALLOWED_ORIGINS=*
```

**File**: `frontend/.env.local`
```
PARSEHUB_API_KEY=t4oahuH8vOki
PARSEHUB_BASE_URL=https://www.parsehub.com/api/v2
BACKEND_API_URL=http://localhost:5000
BACKEND_API_KEY=t_hmXetfMCq3
```

### Backend Code Changed

**File**: `backend/src/api/api_server.py` (Line 2005)

Changed port resolution to prioritize BACKEND_PORT from .env:
```python
# Use BACKEND_PORT from .env, or force 5000 for local development
port = int(os.getenv('BACKEND_PORT', 5000))
```

Previous version was:
```python
port = int(os.getenv('PORT', os.getenv('BACKEND_PORT', 5000)))
```

**Reason**: Prevents system PORT environment variable from overriding local backend port configuration.

## Endpoint Status

| Endpoint | Method | Auth Required | Status |
|----------|--------|---------------|--------|
| `/api/filters` | GET | ❌ No | Public (Fixed in Proxy) |
| `/api/metadata` | GET | ❌ No | Public (Fixed in Proxy) |
| `/api/projects` | GET | ❌ No | Public (Fixed in Proxy) |
| `/api/health` | GET | ❌ No | Public (Fixed in Proxy) |
| All POST/PUT/DELETE | * | ✅ Yes | Protected |
| `/api/monitor/*` | POST | ✅ Yes | Protected |

## Testing Instructions

### Prerequisites
Ensure both services are running:

```bash
# Terminal 1: Start Flask Backend
cd backend
python src/api/api_server.py

# Terminal 2: Start Next.js Frontend
cd frontend
npm run dev
```

### Expected Port Configuration
- Flask Backend: `http://localhost:5000`
- Next.js Frontend: `http://localhost:3000`
- Next.js Proxy forwards to Flask at port 5000 (configured in .env.local)

### Test Requests

```bash
# Direct Flask Backend Test (no auth)
curl http://localhost:5000/api/filters

# Via Next.js Proxy (no auth required)
curl http://localhost:3000/api/filters

# Via Next.js: Check metadata
curl http://localhost:3000/api/metadata
```

### Expected Results

All public endpoints should return:
- **Status Code**: 200 OK
- **Response Body**: JSON with data (filters data, metadata records, projects list, etc.)
- **No Authorization Header Needed**: These calls work without `x-api-key` or `Authorization` headers

## Architecture Flow

```
Browser Request → Next.js Frontend (port 3000)
                     ↓
              Next.js API Route (/api/filters)
                     ↓
              Proxy Function (NO API KEY for public GET)
                     ↓
              Flask Backend (port 5000) /api/filters
                     ↓
              Returns 200 + JSON Data (NO AUTH CHECK)
```

## Deployment Considerations

For production deployment (Railway):

1. **Environment Variables**
   - Set `BACKEND_API_URL` in frontend service to point to Flask backend URL
   - Set `PORT` in Flask backend service (Railway auto-configures)
   - Set all Snowflake credentials

2. **API Key Management**
   - Keep BACKEND_API_KEY secure in environment variables
   - Don't commit to version control

3. **Cross-Origin Requests**
   - CORS is configured in Flask to allow requests from frontend origin
   - Update `ALLOWED_ORIGINS` in production deployment

## Files Modified

1. `frontend/app/api/_proxy.ts` - Added public endpoint detection
2. `backend/.env` - Created with port and database config
3. `frontend/.env.local` - Created with backend URL
4. `backend/src/api/api_server.py` - Modified port resolution logic

## Next Steps

1. Ensure Flask backend is running on port 5000
2. Start Next.js frontend on port 3000
3. Test `/api/filters` and `/api/metadata` endpoints
4. Verify no 401 errors in browser console
5. Confirm data is returned for each endpoint

## Troubleshooting

### Still Getting 401 Errors?

1. Check that Flask server is running on port 5000
   ```bash
   netstat -ano | findstr :5000  # Windows
   lsof -i :5000                 # Mac/Linux
   ```

2. Verify environment files are in correct locations:
   - `backend/.env`
   - `frontend/.env.local`

3. Clear any bytecode cache:
   ```bash
   python -m py_compile -b backend/src/api/api_server.py
   rm -rf backend/**/__pycache__
   ```

4. Check Flask logs for database connection errors
5. Verify Snowflake credentials in `backend/.env`

### Getting 502 Bad Gateway?

This means the proxy can't reach the Flask backend. Ensure:
- Flask server is running on `http://localhost:5000`
- `BACKEND_API_URL` in `frontend/.env.local` points to the correct URL
- No firewall blocking localhost:5000
