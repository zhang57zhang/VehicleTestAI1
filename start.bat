@echo off
echo ========================================
echo VehicleTestAI Platform Startup Script
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [INFO] Checking configuration...
if not exist backend\.env (
    echo [WARN] backend\.env not found, creating default...
    echo GLM_API_KEY=your_api_key_here > backend\.env
    echo GLM_MODEL=glm-4.7 >> backend\.env
)

echo [INFO] Starting Backend Server (Port 5000)...
cd backend
start "VehicleTestAI Backend" cmd /k python app.py
cd ..

REM Wait for backend to start
timeout /t 5 /nobreak >nul

echo [INFO] Checking backend health...
curl -s http://localhost:5000/api/health >nul 2>&1
if errorlevel 1 (
    echo [WARN] Backend may not be ready yet, please wait...
)

echo [INFO] Starting Frontend Server (Port 8080)...
start "VehicleTestAI Frontend" cmd /k python -m http.server 8080

echo.
echo ========================================
echo Servers Started Successfully!
echo ========================================
echo.
echo Backend API:  http://localhost:5000
echo Frontend:     http://localhost:8080/index.html
echo.
echo Features:
echo   - GLM-4.7 AI Integration
echo   - SQLite Database
echo   - 38/49 API Endpoints Working (77.6%%)
echo.
echo Press any key to open the browser...
pause >nul

start http://localhost:8080/index.html

echo.
echo [INFO] Press Ctrl+C in the server windows to stop the servers
