# 一键部署脚本 for BUPT Hotel Air Conditioning System
# 适用于CentOS/RHEL Linux服务器 (使用yum包管理器)
# 参考了deploy/目录下的旧版本配置，包括nginx和systemd优化
# 使用前请确保：
# 1. 项目已上传到服务器 /usr/BUPT-hotel-air-conditioning
# 2. 已配置数据库连接（PostgreSQL/MySQL）
# 3. 已设置环境变量（如SECRET_KEY）

set -e  # 遇到错误立即退出

PROJECT_DIR="/usr/BUPT-hotel-air-conditioning"  # 使用/usr路径
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"

echo "=== 开始部署 BUPT 酒店空调管理系统 ==="

# 1. 更新系统并安装基础依赖
echo "1. 更新系统并安装依赖..."
sudo yum update -y

# 处理阿里云EPEL冲突
if rpm -q epel-aliyuncs-release &>/dev/null; then
    echo "移除阿里云EPEL包..."
    sudo yum remove -y epel-aliyuncs-release
fi

# 检查并安装标准EPEL
if ! yum repolist | grep -q epel; then
    echo "安装标准EPEL仓库..."
    sudo yum install -y epel-release
else
    echo "EPEL仓库已启用"
fi

# 安装基础包
# 首先确保python3可用
if ! command -v python3 &> /dev/null; then
    echo "安装Python3..."
    sudo yum install -y python3 python3-pip python3-devel
fi

sudo yum install -y nodejs npm nginx postgresql-server postgresql-contrib

# 安装Python 3.8（强制升级）
echo "安装Python 3.8..."

# 检查是否已安装python38，如果没有则安装
if ! command -v python3.8 &> /dev/null; then
    echo "安装python38..."
    sudo yum install -y python38 python38-pip python38-devel
fi

# 设置python3命令指向python3.8
echo "设置python3命令指向python3.8..."
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
sudo alternatives --set python3 /usr/bin/python3.8

# 验证版本
python3 --version

# 如果Node.js版本太旧，尝试安装新版本
if ! command -v node &> /dev/null || [[ $(node --version | sed 's/v//' | cut -d. -f1) -lt 14 ]]; then
    echo "Node.js版本太旧，尝试安装新版本..."
    curl -fsSL https://rpm.nodesource.com/setup_16.x | sudo bash -
    sudo yum install -y nodejs
fi

# 初始化PostgreSQL（如果使用）
# sudo postgresql-setup initdb
# sudo systemctl start postgresql
# sudo systemctl enable postgresql

# 2. 设置后端
echo "2. 设置后端..."
cd $BACKEND_DIR

# 创建虚拟环境
echo "创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 更新pip到最新版本
echo "更新pip..."
pip3 install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装Python依赖
echo "安装Python依赖包..."
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

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
sudo tee /etc/nginx/conf.d/hotel_ac.conf <<EOF
server {
    listen 80;
    server_name _;  # 匹配所有域名，生产环境改为实际域名

    # 前端静态文件
    location / {
        root $FRONTEND_DIR/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;  # Vue Router history 模式支持
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Django Admin（可选）
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # 静态文件缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root $FRONTEND_DIR/dist;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # 日志
    access_log /var/log/nginx/hotel-ac.access.log;
    error_log /var/log/nginx/hotel-ac.error.log;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    gzip_min_length 1000;
}
EOF

# 移除默认配置
sudo rm -f /etc/nginx/conf.d/default.conf
sudo nginx -t
sudo systemctl reload nginx

# 5. 创建systemd服务
echo "5. 创建systemd服务..."
sudo tee /etc/systemd/system/hotel_ac.service <<EOF
[Unit]
Description=Hotel AC System - Django Backend
After=network.target

[Service]
Type=simple
User=ec2-user  # 修改为你的用户名
Group=ec2-user
WorkingDirectory=$BACKEND_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn \
    --workers 2 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /var/log/hotel-ac/access.log \
    --error-logfile /var/log/hotel-ac/error.log \
    hotel_ac.wsgi:application

Restart=always
RestartSec=5

# 创建日志目录
ExecStartPre=/bin/mkdir -p /var/log/hotel-ac

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start hotel_ac
sudo systemctl enable hotel_ac

# 设置日志权限
sudo chown -R ec2-user:ec2-user /var/log/hotel-ac

# 6. 设置防火墙（firewalld）
echo "6. 设置防火墙..."
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --reload

echo "=== 部署完成！ ==="
echo "前端访问: http://your-server-ip"
echo "后端API: http://your-server-ip/api/"
echo "检查服务状态: sudo systemctl status hotel_ac"
echo "查看日志: sudo journalctl -u hotel_ac -f"