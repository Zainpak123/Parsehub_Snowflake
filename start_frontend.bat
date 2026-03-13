@echo off
REM Start Next.js Frontend - Simple wrapper

cd /d "%~dp0\frontend"

echo Starting ParseHub Frontend...
echo Port: 3000
echo.

npm run dev

pause
