#!/bin/bash

# 一键部署脚本 for BUPT Hotel Air Conditioning System
# 适用于Ubuntu/Debian Linux服务器
# 使用前请确保：
# 1. 项目已上传到服务器 /home/ubuntu/BUPT-hotel-air-conditioning
# 2. 已配置数据库连接（PostgreSQL/MySQL）
# 3. 已设置环境变量（如SECRET_KEY）

set -e  # 遇到错误立即退出

PROJECT_DIR="/home/ubuntu/BUPT-hotel-air-conditioning"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"

echo "=== 开始部署 BUPT 酒店空调管理系统 ==="

# 1. 更新系统并安装基础依赖
echo "1. 更新系统并安装依赖..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx postgresql postgresql-contrib

# 2. 设置后端
echo "2. 设置后端..."
cd $BACKEND_DIR

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt

# 运行数据库迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 3. 设置前端
echo "3. 设置前端..."
cd $FRONTEND_DIR

# 安装Node.js依赖
npm install

# 构建生产版本
npm run build

# 4. 配置Nginx
echo "4. 配置Nginx..."
sudo tee /etc/nginx/sites-available/hotel_ac <<EOF
server {
    listen 80;
    server_name localhost;  # 替换为你的域名

    # 前端静态文件
    location / {
        root $FRONTEND_DIR/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # 后端API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启用站点
sudo ln -sf /etc/nginx/sites-available/hotel_ac /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# 5. 创建systemd服务
echo "5. 创建systemd服务..."
sudo tee /etc/systemd/system/hotel_ac.service <<EOF
[Unit]
Description=BUPT Hotel AC Django App
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 hotel_ac.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start hotel_ac
sudo systemctl enable hotel_ac

# 6. 设置防火墙（可选）
echo "6. 设置防火墙..."
sudo ufw allow 80
sudo ufw allow 22
sudo ufw --force enable

echo "=== 部署完成！ ==="
echo "前端访问: http://your-server-ip"
echo "后端API: http://your-server-ip/api/"
echo "检查服务状态: sudo systemctl status hotel_ac"
echo "查看日志: sudo journalctl -u hotel_ac -f"