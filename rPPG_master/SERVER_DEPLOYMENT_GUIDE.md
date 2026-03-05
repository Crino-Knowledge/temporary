# rPPG系统服务器部署指南

本指南将帮助您将前端和后端都部署到服务器上，支持局域网内的电脑和手机访问。

## 📋 部署架构

```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐
│   客户端设备     │ ◄─────────────────► │   服务器         │
│   (电脑/手机)   │                     │   (前端+后端)   │
│                 │                     │                 │
│ - 浏览器访问    │                     │ - Vue.js前端    │
│ - 摄像头调用    │                     │ - Flask后端     │
│ - 实时显示      │                     │ - rPPG算法      │
│                 │                     │ - GPU加速(可选) │
└─────────────────┘                     └─────────────────┘
```

## 🚀 快速部署步骤

### 步骤1：准备服务器环境

**系统要求：**
- Ubuntu 18.04+ 或 CentOS 7+
- Python 3.8+
- Node.js 16+
- 至少4GB RAM
- 至少20GB存储空间
- 公网IP或局域网IP

**安装基础依赖：**
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv -y

# 安装Node.js和npm
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install nodejs -y

# 安装Nginx
sudo apt install nginx -y

# 安装Git
sudo apt install git -y
```

### 步骤2：部署后端服务

**1. 上传代码到服务器：**
```bash
# 克隆或上传代码到服务器
cd /opt
sudo git clone <your-repo-url> rppg-system
# 或者使用scp上传代码包

cd /opt/rppg-system
sudo chown -R $USER:$USER .
```

**2. 配置后端环境：**
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**3. 配置后端设置：**
创建生产环境配置文件 `backend/config_production.py`：
```python
class ProductionConfig:
    DEBUG = False
    HOST = '0.0.0.0'  # 监听所有接口
    PORT = 5000
    
    # CORS配置 - 允许所有来源访问（生产环境建议限制具体IP）
    CORS_ORIGINS = ["*"]
    SOCKETIO_CORS_ALLOWED_ORIGINS = ["*"]
    
    # 模型路径
    MODEL_PATH = './linknet18.pth'
    
    # 日志配置
    LOG_LEVEL = 'INFO'
```

**4. 修改app.py使用生产配置：**
在 `backend/app.py` 中添加：
```python
# 在文件开头添加
import os
if os.path.exists('config_production.py'):
    from config_production import ProductionConfig as config
else:
    # 使用默认配置
    class config:
        CORS_ORIGINS = ["*"]
        SOCKETIO_CORS_ALLOWED_ORIGINS = ["*"]
        HOST = '0.0.0.0'
        PORT = 5000
```

**5. 创建systemd服务：**
```bash
sudo nano /etc/systemd/system/rppg-backend.service
```

添加以下内容：
```ini
[Unit]
Description=rPPG Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/rppg-system/backend
Environment=PATH=/opt/rppg-system/backend/venv/bin
ExecStart=/opt/rppg-system/backend/venv/bin/python app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**6. 启动后端服务：**
```bash
sudo systemctl daemon-reload
sudo systemctl enable rppg-backend
sudo systemctl start rppg-backend
sudo systemctl status rppg-backend
```

### 步骤3：部署前端服务

**1. 配置前端环境变量：**
创建 `frontend/.env.production`：
```bash
# 替换为服务器的实际IP地址
VUE_APP_API_BASE_URL=http://YOUR_SERVER_IP:5000
VUE_APP_WS_URL=ws://YOUR_SERVER_IP:5000
VUE_APP_TITLE=rPPG心率监测系统
NODE_ENV=production
VUE_APP_DEBUG=false
```

**2. 构建前端：**
```bash
cd /opt/rppg-system/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

**3. 配置Nginx：**
```bash
sudo nano /etc/nginx/sites-available/rppg-frontend
```

添加以下配置：
```nginx
server {
    listen 80;
    server_name YOUR_SERVER_IP;  # 替换为服务器IP
    
    root /opt/rppg-system/frontend/dist;
    index index.html;
    
    # 启用gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Vue.js SPA路由
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API代理到后端
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # WebSocket代理
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**4. 启用Nginx站点：**
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/rppg-frontend /etc/nginx/sites-enabled/

# 删除默认站点
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 步骤4：配置防火墙

```bash
# 开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 5000  # 后端API（可选，如果直接访问）
sudo ufw enable
```

### 步骤5：测试部署

**1. 检查服务状态：**
```bash
# 检查后端服务
sudo systemctl status rppg-backend

# 检查Nginx
sudo systemctl status nginx

# 检查端口监听
sudo netstat -tlnp | grep -E ':(80|5000)'
```

**2. 访问测试：**
- 在浏览器中访问：`http://YOUR_SERVER_IP`
- 检查API健康状态：`http://YOUR_SERVER_IP:5000/api/health`

## 📱 客户端访问

### 电脑访问
1. 打开浏览器
2. 访问：`http://YOUR_SERVER_IP`
3. 允许摄像头权限
4. 开始心率监测

### 手机访问
1. 确保手机与服务器在同一网络
2. 打开手机浏览器
3. 访问：`http://YOUR_SERVER_IP`
4. 允许摄像头权限
5. 开始心率监测

## 🔧 故障排除

### 常见问题

**1. 无法访问前端页面**
```bash
# 检查Nginx状态
sudo systemctl status nginx

# 检查Nginx错误日志
sudo tail -f /var/log/nginx/error.log
```

**2. WebSocket连接失败**
```bash
# 检查后端服务
sudo systemctl status rppg-backend

# 查看后端日志
sudo journalctl -u rppg-backend -f
```

**3. 摄像头权限问题**
- 确保使用HTTPS（推荐）或localhost访问
- 检查浏览器摄像头权限设置

**4. 跨域问题**
- 检查后端CORS配置
- 确保前端API地址正确

### 日志查看
```bash
# 后端日志
sudo journalctl -u rppg-backend -f

# Nginx访问日志
sudo tail -f /var/log/nginx/access.log

# Nginx错误日志
sudo tail -f /var/log/nginx/error.log
```

## 🔒 安全建议

1. **使用HTTPS**：配置SSL证书
2. **限制CORS**：在生产环境中限制允许的域名
3. **防火墙配置**：只开放必要端口
4. **定期更新**：保持系统和依赖包更新
5. **监控日志**：定期检查访问和错误日志

## 📈 性能优化

1. **启用Gzip压缩**：减少传输数据量
2. **静态资源缓存**：提高加载速度
3. **CDN加速**：使用CDN分发静态资源
4. **数据库优化**：如果使用数据库，优化查询
5. **负载均衡**：高并发时使用负载均衡

---

部署完成后，您的rPPG心率监测系统将可以通过服务器IP地址在局域网内的任何设备上访问使用！