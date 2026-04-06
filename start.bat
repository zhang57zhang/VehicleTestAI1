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

echo [INFO] Starting Backend Server (Port 5000)...
cd backend
start "VehicleTestAI Backend" cmd /k python app.py
cd ..

REM Wait for backend to start
timeout /t 3 /nobreak >nul

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
echo Press any key to open the browser...
pause >nul

start http://localhost:8080/index.html

echo.
echo [INFO] Press Ctrl+C in the server windows to stop the servers
