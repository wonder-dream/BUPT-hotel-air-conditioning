#!/bin/bash

echo "========================================"
echo "Hotel AC System - Backend Start Script"
echo "========================================"

cd backend

echo ""
echo "[1/4] Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo ""
echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo ""
echo "[3/4] Installing dependencies..."
pip install -r requirements.txt -q

echo ""
echo "[4/4] Starting Django server..."
echo ""
echo "Running database migrations..."
python manage.py makemigrations ac_system --no-input
python manage.py migrate --no-input

echo ""
echo "Initializing data..."
python init_data.py

echo ""
echo "========================================"
echo "Backend server starting..."
echo "URL: http://localhost:8000"
echo "API: http://localhost:8000/api/"
echo "========================================"
echo ""

python manage.py runserver