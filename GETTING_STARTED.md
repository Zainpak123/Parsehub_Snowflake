# 🚀 Quick Start Guide - ParseHub Dashboard

## Prerequisites
- Python 3.12+ with virtual environment (`backend/venv_sf`)
- Node.js 18+ with npm
- Snowflake database access (configured in `backend/.env`)

## Quick Start (Windows)

### Option 1: User-Friendly (Recommended)
Simply run these batch files from the root directory:

**Terminal 1 - Start Backend:**
```bash
start_backend.bat
```

**Terminal 2 - Start Frontend:**
```bash
start_frontend.bat
```

### Option 2: Manual Start

**Terminal 1 - Start Flask Backend:**
```bash
cd backend
python src/api/api_server.py
```

Expected output:
```
INFO:__main__:Starting ParseHub API Server on port 5000
 * Running on http://0.0.0.0:5000
```

**Terminal 2 - Start Next.js Frontend:**
```bash
cd frontend
npm run dev
```

Expected output:
```
▲ Next.js 16.1.6 (Turbopack)
- Local:         http://localhost:3000
- Network:       http://192.168.x.x:3000
```

## Verification

Once both are running, open your browser to:
- **Frontend:** http://localhost:3000
- **Backend Direct:** http://localhost:5000/health

### Testing Endpoints

```bash
# Root endpoint (returns API info)
curl http://localhost:5000/

# Health check
curl http://localhost:5000/health

# Get filters (via frontend proxy)
curl http://localhost:3000/api/filters

# Get metadata (via frontend proxy)
curl http://localhost:3000/api/metadata

# Get projects (via frontend proxy)
curl http://localhost:3000/api/projects?page=1&limit=50
```

## 🔧 Environment Configuration

**Backend** (`backend/.env`):
```
BACKEND_PORT=5000
SNOWFLAKE_ACCOUNT=VFHSGYP
SNOWFLAKE_USER=parsehub_user
SNOWFLAKE_PASSWORD=<your-password>
SNOWFLAKE_DATABASE=PARSEHUB_DB
BACKEND_API_KEY=t_hmXetfMCq3
ALLOWED_ORIGINS=*
```

**Frontend** (`frontend/.env.local`):
```
PARSEHUB_API_KEY=t4oahuH8vOki
BACKEND_API_URL=http://localhost:5000
BACKEND_API_KEY=t_hmXetfMCq3
```

## 📊 Architecture

```
Browser (port 3000)
    ↓
Next.js Frontend
    ↓
Next.js API Routes (/api/*)
    ↓
Proxy Service (PUBLIC endpoints: no auth)
    ↓
Flask Backend (port 5000)
    ↓
Snowflake Database
```

## ✅ Expected Behavior

| Endpoint | Method | Auth | Status |
|----------|--------|------|--------|
| `/` | GET | ❌ | 200 - API info |
| `/health` | GET | ❌ | 200 - OK |
| `/api/health` | GET | ❌ | 200 - OK |
| `/api/filters` | GET | ❌ | 200 - Returns filter options |
| `/api/metadata` | GET | ❌ | 200 - Returns metadata records |
| `/api/projects` | GET | ❌ | 200 - Returns projects list |

## 🐛 Troubleshooting

### Backend won't start
```bash
# Clear Python bytecode cache
python -m py_compile -b backend/src/api/api_server.py
del /s /q backend\**\__pycache__
del /s /q backend\**\*.pyc

# Try again
python backend/src/api/api_server.py
```

### Getting 502 Bad Gateway?
- Ensure Flask backend is running on port 5000
- Check `backend/.env` exists with correct config
- Verify `BACKEND_API_URL=http://localhost:5000` in `frontend/.env.local`

### Getting 404 "Endpoint not found"?
- This should be fixed with the new root "/" endpoint
- Make sure to restart Flask backend after updates

### Frontend still loading?
- Check browser console (F12) for specific error messages
- Verify network tab shows requests going to correct URLs
- Check that frontend can reach backend via proxy

## 📁 Important Files

- `backend/.env` - Flask configuration
- `frontend/.env.local` - Next.js configuration
- `backend/src/api/api_server.py` - Flask API server
- `frontend/app/page.tsx` - Dashboard homepage
- `frontend/app/api/_proxy.ts` - Backend proxy service

## 🚫 Common Issues

### Port Already in Use
```bash
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <PID> /F
```

### Module Not Found Errors
```bash
# Reinstall backend dependencies
cd backend
pip install -r requirements.txt

# Reinstall frontend dependencies
cd frontend
npm install
```

### Snowflake Connection Failed
- Verify credentials in `backend/.env`
- Check that all required env vars are set
- Run: `python backend/test_snowflake.py`

## 📝 Next Steps

1. ✅ Start both services using `start_backend.bat` and `start_frontend.bat`
2. ✅ Open http://localhost:3000 in browser
3. ✅ Verify no 404 errors in browser console
4. ✅ Check that filters, metadata, and projects are loading
5. ✅ Ready to use the dashboard!

## 📞 Support

For detailed information about the API authorization fix, see: `API_AUTHORIZATION_FIX.md`

For system architecture details, see: `ARCHITECTURE.md`
