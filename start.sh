#!/bin/bash

echo "========================================"
echo "Hotel AC System - Full Start Script"
echo "========================================"

# 启动后端
echo "Starting backend..."
./start_backend.sh &
BACKEND_PID=$!

# 等待后端启动
sleep 5

# 启动前端（如果需要开发服务器）
echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Services started!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Frontend: http://localhost:5173 (Vite dev server)"
echo "Backend: http://localhost:8000"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop all services"

# 等待中断信号
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# 保持脚本运行
wait