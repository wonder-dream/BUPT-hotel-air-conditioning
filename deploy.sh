#!/bin/bash

# 部署脚本 for Alibaba Cloud Linux
# 确保系统已安装Docker和docker-compose

echo "更新系统..."
sudo yum update -y

echo "安装Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

echo "安装docker-compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "构建和启动服务..."
docker-compose up --build -d

echo "部署完成！"
echo "前端访问: http://your-server-ip"
echo "后端API: http://your-server-ip:8000"