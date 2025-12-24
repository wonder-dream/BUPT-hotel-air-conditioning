# 部署指南

## 概述
此项目包含一个酒店空调系统的后端（Django）和前端（Vue.js）。使用Docker进行容器化部署，适用于Alibaba Cloud Linux。

## 要求
- Docker
- docker-compose
- Python 3.10（在Docker中提供）

## 部署步骤

1. **克隆项目**
   ```bash
   git clone <your-repo-url>
   cd BUPT-hotel-air-conditioning
   ```

2. **运行部署脚本**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

   或者手动：
   ```bash
   docker-compose up --build -d
   ```

3. **访问应用**
   - 前端：http://your-server-ip
   - 后端API：http://your-server-ip:8000

## 注意事项
- 确保防火墙开放80和8000端口。
- 对于生产环境，修改`backend/hotel_ac/settings.py`中的`DEBUG=False`和`SECRET_KEY`。
- SQLite数据库文件`hotel.db`会持久化在`backend/`目录中。