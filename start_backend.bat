@echo off
REM Start Flask Backend - Simple wrapper

cd /d "%~dp0\backend"

echo Starting ParseHub Flask Backend...
echo Port: 5000
echo.

python -u src/api/api_server.py

pause
