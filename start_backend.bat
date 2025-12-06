@echo off
chcp 65001 >nul
echo ========================================
echo Hotel AC System - Backend Start Script
echo ========================================

cd /d %~dp0backend

echo.
echo [1/4] Checking virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate

echo.
echo [3/4] Installing dependencies...
pip install -r requirements.txt -q

echo.
echo [4/4] Starting Django server...
echo.
echo Running database migrations...
python manage.py makemigrations ac_system --no-input
python manage.py migrate --no-input

echo.
echo Initializing data...
python init_data.py

echo.
echo ========================================
echo Backend server starting...
echo URL: http://localhost:8000
echo API: http://localhost:8000/api/
echo ========================================
echo.

python manage.py runserver

pause
