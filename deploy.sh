#!/bin/bash

# 部署脚本 for Ubuntu
# 安装Python 3.10、Node.js、nginx并部署酒店空调系统

echo "更新系统..."
sudo apt update && sudo apt upgrade -y

echo "安装必要工具..."
sudo apt install -y curl wget build-essential software-properties-common

echo "安装Python 3.10..."
# 添加deadsnakes PPA以获取Python 3.10
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-pip

# 设置python3.10为默认（可选）
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
sudo update-alternatives --set python3 /usr/bin/python3.10

echo "配置pip使用国内源..."
mkdir -p ~/.pip
tee ~/.pip/pip.conf <<-'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

echo "安装后端依赖..."
cd backend
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "运行数据库迁移..."
python3 manage.py migrate

echo "启动后端服务器（后台）..."
python3 manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!
echo "后端PID: $BACKEND_PID"

echo "安装Node.js..."
# 使用NodeSource仓库安装最新LTS版本
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

echo "构建前端..."
cd ../frontend
npm install
npm run build

echo "安装和配置nginx..."
sudo apt install -y nginx

# 创建nginx配置
sudo tee /etc/nginx/sites-available/hotel <<-'EOF'
server {
    listen 80;
    server_name _;
    root /home/ubuntu/BUPT-hotel-air-conditioning/frontend/dist;
    index index.html index.htm;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 启用站点
sudo ln -sf /etc/nginx/sites-available/hotel /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 测试nginx配置
sudo nginx -t

# 启动nginx
sudo systemctl start nginx
sudo systemctl enable nginx

echo "配置防火墙..."
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp
sudo ufw --force enable

echo "部署完成！"
echo "前端访问: 8.130.29.228"
echo "后端API: 8.130.29.228:8000"
echo "后端进程PID: $BACKEND_PID"
echo ""
echo "管理命令："
echo "停止后端: kill $BACKEND_PID"
echo "重启nginx: sudo systemctl restart nginx"
echo "查看日志: tail -f /var/log/nginx/access.log"