@echo off
echo Starting Visual Search Engine Frontend...
echo.

cd /d "%~dp0\frontend"

echo Setting environment variables...
set DANGEROUSLY_DISABLE_HOST_CHECK=true
set WDS_SOCKET_PORT=0
set SKIP_PREFLIGHT_CHECK=true

echo Starting React development server...
echo The browser will open automatically at http://localhost:3000
echo.

call npm start

pause
