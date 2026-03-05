# rPPG系统GPU服务器部署指南

## 概述

本指南详细说明如何将rPPG实时心率监测系统部署到配备NVIDIA RTX 3060的Linux服务器上。

## 系统要求

### 硬件要求
- **GPU**: NVIDIA RTX 3060 或更高
- **内存**: 至少8GB RAM
- **存储**: 至少20GB可用空间
- **网络**: 稳定的网络连接

### 软件要求
- **操作系统**: Ubuntu 20.04 LTS 或更高版本
- **NVIDIA驱动**: 470.x 或更高版本
- **Docker**: 20.10 或更高版本
- **Docker Compose**: 2.0 或更高版本
- **NVIDIA Container Toolkit**: 最新版本

## 部署步骤

### 1. 准备服务器环境

#### 1.1 更新系统
```bash
sudo apt update && sudo apt upgrade -y
```

#### 1.2 安装NVIDIA驱动
```bash
# 检查GPU
lspci | grep -i nvidia

# 安装驱动
sudo apt install nvidia-driver-470
sudo reboot

# 验证安装
nvidia-smi
```

#### 1.3 安装Docker
```bash
# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

# 添加用户到docker组
sudo usermod -aG docker $USER
newgrp docker
```

#### 1.4 安装Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 1.5 安装NVIDIA Container Toolkit
```bash
# 添加NVIDIA仓库
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# 安装
sudo apt update
sudo apt install nvidia-container-toolkit
sudo systemctl restart docker
```

### 2. 部署应用

#### 2.1 克隆项目
```bash
# 创建项目目录
sudo mkdir -p /opt/rppg
sudo chown $USER:$USER /opt/rppg
cd /opt/rppg

# 上传项目文件到此目录
# 或使用git clone（如果有仓库）
```

#### 2.2 使用自动部署脚本
```bash
# 给脚本执行权限
chmod +x deploy_gpu_server.sh

# 运行部署脚本
./deploy_gpu_server.sh
```

#### 2.3 手动部署（可选）

如果自动脚本失败，可以手动执行以下步骤：

```bash
# 创建SSL证书
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/server.key \
    -out ssl/server.crt \
    -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"

# 创建日志目录
mkdir -p logs

# 构建镜像
docker-compose -f docker-compose.gpu-server.yml build

# 启动服务
docker-compose -f docker-compose.gpu-server.yml up -d
```

### 3. 验证部署

#### 3.1 检查容器状态
```bash
docker-compose -f docker-compose.gpu-server.yml ps
```

#### 3.2 检查GPU使用
```bash
# 在宿主机上
nvidia-smi

# 在容器内
docker exec rppg-backend-gpu nvidia-smi
```

#### 3.3 测试API
```bash
# 健康检查
curl http://localhost:5000/api/health

# 系统状态
curl http://localhost:5000/api/system/status
```

#### 3.4 访问前端
- HTTP: `http://服务器IP:8080`
- HTTPS: `https://服务器IP:8080`

## 配置说明

### 主要配置文件

1. **docker-compose.gpu-server.yml**: Docker Compose配置
2. **deployment/nginx-server.conf**: Nginx反向代理配置
3. **deployment/gpu_backend_config.py**: 后端GPU配置
4. **deployment/requirements_gpu.txt**: Python依赖包

### 环境变量配置

创建 `.env` 文件：
```bash
# 生产环境配置
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# GPU配置
CUDA_VISIBLE_DEVICES=0
NVIDIA_VISIBLE_DEVICES=all
NVIDIA_DRIVER_CAPABILITIES=compute,utility

# 日志配置
LOG_LEVEL=INFO
```

### 端口配置

- **5000**: 后端API服务
- **80**: 前端服务（容器内）
- **8080**: Nginx代理（HTTP）
- **443**: Nginx代理（HTTPS）

## 管理命令

### 服务管理
```bash
# 启动服务
docker-compose -f docker-compose.gpu-server.yml up -d

# 停止服务
docker-compose -f docker-compose.gpu-server.yml down

# 重启服务
docker-compose -f docker-compose.gpu-server.yml restart

# 查看状态
docker-compose -f docker-compose.gpu-server.yml ps

# 查看日志
docker-compose -f docker-compose.gpu-server.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.gpu-server.yml logs -f rppg-backend-gpu
```

### 容器管理
```bash
# 进入后端容器
docker exec -it rppg-backend-gpu bash

# 进入前端容器
docker exec -it rppg-frontend sh

# 进入Nginx容器
docker exec -it rppg-nginx sh
```

### 监控命令
```bash
# 查看资源使用
docker stats

# 查看GPU使用
watch -n 1 nvidia-smi

# 查看系统资源
htop
```

## 性能优化

### GPU优化
1. 确保CUDA版本兼容
2. 调整批处理大小
3. 启用混合精度训练
4. 优化内存使用

### 网络优化
1. 启用Nginx gzip压缩
2. 配置适当的缓存策略
3. 使用CDN（如需要）

### 系统优化
1. 调整Docker资源限制
2. 优化系统内核参数
3. 配置日志轮转

## 故障排除

### 常见问题

#### 1. GPU不可用
```bash
# 检查NVIDIA驱动
nvidia-smi

# 检查Docker GPU支持
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi
```

#### 2. 容器启动失败
```bash
# 查看详细日志
docker-compose -f docker-compose.gpu-server.yml logs

# 检查端口占用
sudo netstat -tlnp | grep :5000
```

#### 3. 前端无法访问
```bash
# 检查Nginx配置
docker exec rppg-nginx nginx -t

# 重新加载Nginx配置
docker exec rppg-nginx nginx -s reload
```

#### 4. API请求失败
```bash
# 检查后端健康状态
curl http://localhost:5000/api/health

# 检查网络连接
docker network ls
docker network inspect rppg_rppg-network
```

### 日志分析

```bash
# 后端日志
docker-compose -f docker-compose.gpu-server.yml logs rppg-backend-gpu

# 前端日志
docker-compose -f docker-compose.gpu-server.yml logs rppg-frontend

# Nginx日志
docker-compose -f docker-compose.gpu-server.yml logs nginx

# 系统日志
sudo journalctl -u docker.service
```

## 安全配置

### 防火墙设置
```bash
# 开放必要端口
sudo ufw allow 8080/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### SSL证书
- 生产环境建议使用Let's Encrypt证书
- 定期更新证书
- 配置HTTPS重定向

### 访问控制
- 配置Nginx访问限制
- 使用JWT认证
- 设置API速率限制

## 备份和恢复

### 数据备份
```bash
# 备份配置文件
tar -czf rppg-config-$(date +%Y%m%d).tar.gz deployment/ ssl/ .env

# 备份日志
tar -czf rppg-logs-$(date +%Y%m%d).tar.gz logs/
```

### 系统恢复
```bash
# 恢复配置
tar -xzf rppg-config-YYYYMMDD.tar.gz

# 重新部署
docker-compose -f docker-compose.gpu-server.yml up -d
```

## 更新和维护

### 应用更新
```bash
# 停止服务
docker-compose -f docker-compose.gpu-server.yml down

# 更新代码
git pull  # 或上传新文件

# 重新构建
docker-compose -f docker-compose.gpu-server.yml build --no-cache

# 启动服务
docker-compose -f docker-compose.gpu-server.yml up -d
```

### 系统维护
```bash
# 清理Docker资源
docker system prune -a

# 更新系统包
sudo apt update && sudo apt upgrade

# 重启系统（如需要）
sudo reboot
```

## 联系支持

如遇到问题，请提供以下信息：
1. 系统版本和硬件配置
2. 错误日志
3. 复现步骤
4. 环境配置