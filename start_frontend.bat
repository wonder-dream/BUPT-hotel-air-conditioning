@echo off
chcp 65001 >nul
echo ========================================
echo Hotel AC System - Frontend Start Script
echo ========================================

cd /d %~dp0frontend

echo.
echo [1/2] Checking dependencies...
if not exist "node_modules" (
    echo Installing npm dependencies...
    npm install
)

echo.
echo [2/2] Starting frontend dev server...
echo.
echo ========================================
echo Frontend server starting...
echo URL: http://localhost:5173
echo.
echo Routes:
echo   /customer  - AC Control Panel
echo   /reception - Reception Service
echo   /monitor   - AC Monitor
echo   /report    - Statistics Report
echo ========================================
echo.

npm run dev

pause
