#!/bin/bash

# 部署脚本 for Alibaba Cloud Linux
# 确保系统已安装Docker（现代Docker已内置compose）

echo "更新系统..."
sudo yum update -y

echo "安装Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker

# 检查Docker版本，如果支持compose则无需额外安装
if docker compose version >/dev/null 2>&1; then
    echo "Docker compose 已内置，无需额外安装"
else
    echo "安装docker-compose..."
    # 使用国内镜像加速下载
    sudo curl -L "https://get.daocloud.io/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo "构建和启动服务..."
docker compose up --build -d

echo "部署完成！"
echo "前端访问: http://your-server-ip"
echo "后端API: http://your-server-ip:8000"