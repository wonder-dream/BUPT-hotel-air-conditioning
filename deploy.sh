#!/bin/bash

# 部署脚本 for Alibaba Cloud Linux
# 安装Docker CE和docker-compose

echo "更新系统..."
sudo yum update -y

echo "移除podman-docker（如果存在）..."
sudo yum remove -y podman-docker

echo "安装Docker CE..."
# 添加Docker官方repo
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker CE
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

echo "安装docker-compose..."
# 使用阿里云镜像加速下载
sudo curl -L "https://mirrors.aliyun.com/docker-toolbox/linux/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "构建和启动服务..."
docker-compose up --build -d

echo "部署完成！"
echo "前端访问: http://your-server-ip"
echo "后端API: http://your-server-ip:8000"