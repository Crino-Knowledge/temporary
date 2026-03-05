# rPPG系统快速部署指南

本指南将帮助您快速将rPPG心率监测系统部署到服务器，支持局域网内的电脑和手机访问。

## 🎯 部署目标

将前端和后端都部署到服务器上，让局域网内的设备（电脑、手机）可以通过浏览器访问，调用本地摄像头进行实时心率监测。

## 📋 部署方式选择

### 方式一：Docker部署（推荐）
**优点：** 简单快速，环境隔离，易于管理  
**适用：** 开发测试、快速部署

### 方式二：传统部署
**优点：** 性能最佳，资源利用率高  
**适用：** 生产环境、长期运行

## 🚀 Docker快速部署

### 前置要求
- Linux服务器（Ubuntu/CentOS等）
- 已安装Docker和Docker Compose
- 服务器有公网IP或局域网IP

### 一键部署
```bash
# 1. 上传代码到服务器
scp -r rPPG_master/ user@your-server:/opt/

# 2. 登录服务器
ssh user@your-server

# 3. 进入项目目录
cd /opt/rPPG_master

# 4. 运行部署脚本
bash deploy_docker.sh
# 或指定服务器IP
bash deploy_docker.sh 192.168.1.100
```

### 手动Docker部署
```bash
# 1. 修改配置文件
cp docker-compose.server.yml docker-compose.yml
sed -i 's/YOUR_SERVER_IP/你的服务器IP/g' docker-compose.yml

# 2. 构建和启动
docker-compose build --build-arg VUE_APP_API_BASE_URL=http://你的服务器IP:5000 \
                     --build-arg VUE_APP_WS_URL=ws://你的服务器IP:5000
docker-compose up -d

# 3. 检查状态
docker-compose ps
```

## 🖥️ 传统部署

### 一键部署
```bash
# 1. 上传代码到服务器
scp -r rPPG_master/ user@your-server:/opt/

# 2. 登录服务器
ssh user@your-server

# 3. 进入项目目录
cd /opt/rPPG_master

# 4. 运行部署脚本（需要sudo权限）
sudo bash deploy_server.sh
# 或指定服务器IP
sudo bash deploy_server.sh 192.168.1.100
```

### 手动传统部署
详细步骤请参考 [SERVER_DEPLOYMENT_GUIDE.md](SERVER_DEPLOYMENT_GUIDE.md)

## 📱 客户端访问

### 电脑访问
1. 打开浏览器（Chrome/Firefox/Safari）
2. 访问：`http://服务器IP地址`
3. 允许摄像头权限
4. 点击"开始监测"按钮
5. 将脸部对准摄像头，保持稳定
6. 实时查看心率数据

### 手机访问
1. 确保手机与服务器在同一网络
2. 打开手机浏览器
3. 访问：`http://服务器IP地址`
4. 允许摄像头权限
5. 使用前置摄像头进行监测

## 🔧 常见问题

### Q1: 无法访问前端页面
**解决方案：**
```bash
# 检查服务状态
docker-compose ps  # Docker部署
sudo systemctl status nginx  # 传统部署

# 检查防火墙
sudo ufw status
sudo ufw allow 80
```

### Q2: WebSocket连接失败
**解决方案：**
```bash
# 检查后端服务
docker-compose logs rppg-backend  # Docker部署
sudo systemctl status rppg-backend  # 传统部署

# 检查端口监听
sudo netstat -tlnp | grep 5000
```

### Q3: 摄像头权限被拒绝
**解决方案：**
- 使用HTTPS访问（推荐）
- 在浏览器设置中允许摄像头权限
- 确保摄像头未被其他应用占用

### Q4: 心率检测不准确
**解决方案：**
- 确保光线充足
- 保持脸部稳定，避免大幅度移动
- 距离摄像头30-50cm
- 避免背景干扰

## 📊 服务管理

### Docker部署管理
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
docker-compose logs rppg-backend
docker-compose logs rppg-frontend

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新服务
docker-compose pull
docker-compose up -d
```

### 传统部署管理
```bash
# 后端服务管理
sudo systemctl status rppg-backend
sudo systemctl restart rppg-backend
sudo journalctl -u rppg-backend -f

# 前端服务管理
sudo systemctl status nginx
sudo systemctl restart nginx
sudo tail -f /var/log/nginx/error.log
```

## 🔒 安全配置

### 基础安全
```bash
# 配置防火墙
sudo ufw enable
sudo ufw allow 22   # SSH
sudo ufw allow 80   # HTTP
sudo ufw allow 443  # HTTPS（如果配置）
```

### HTTPS配置（推荐）
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

## 📈 性能优化

### 服务器配置建议
- **最低配置：** 2核CPU，4GB内存，20GB存储
- **推荐配置：** 4核CPU，8GB内存，50GB存储
- **网络带宽：** 至少10Mbps上行带宽

### 优化设置
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化内核参数
echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" >> /etc/sysctl.conf
sysctl -p
```

## 📞 技术支持

如果遇到问题，请按以下步骤排查：

1. **检查服务状态**：确认所有服务正常运行
2. **查看日志**：检查错误日志获取详细信息
3. **网络连通性**：确认端口开放和网络连接
4. **浏览器兼容性**：使用现代浏览器访问
5. **权限设置**：确认摄像头权限已授予

---

**部署完成后，您的rPPG心率监测系统将可以在局域网内的任何设备上使用！**