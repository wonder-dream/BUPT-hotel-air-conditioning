#!/bin/bash

echo "========================================"
echo "Hotel AC System - Frontend Start Script"
echo "========================================"

cd frontend

echo ""
echo "[1/3] Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Please install Node.js first."
    exit 1
fi

echo ""
echo "[2/3] Installing dependencies..."
if [ ! -d "node_modules" ]; then
    npm install
fi

echo ""
echo "[3/3] Building frontend..."
npm run build

echo ""
echo "========================================"
echo "Frontend build completed!"
echo "Files are in: frontend/dist/"
echo "========================================"
echo ""

# 如果需要启动开发服务器，取消注释下面一行
# npm run dev

# 对于生产，使用nginx服务dist目录
echo "To serve in production, configure nginx to serve the dist/ directory."