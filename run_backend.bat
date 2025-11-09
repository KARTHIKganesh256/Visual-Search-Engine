@echo off
echo Starting Visual Search Engine Backend...
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Setting environment variables...
set CURL_CA_BUNDLE=
set REQUESTS_CA_BUNDLE=

echo Starting FastAPI server on http://localhost:8000
echo Please wait while models load (15-30 seconds)...
echo.

python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

pause









