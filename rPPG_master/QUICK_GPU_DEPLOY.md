# rPPG GPU服务器快速部署指南

## 一键部署

### 前提条件
- Ubuntu 20.04+ 系统
- NVIDIA RTX 3060 GPU
- 已安装NVIDIA驱动

### 快速部署命令

```bash
# 1. 上传项目文件到服务器
scp -r rPPG_master/ user@server_ip:/opt/

# 2. 登录服务器
ssh user@server_ip

# 3. 进入项目目录
cd /opt/rPPG_master

# 4. 运行部署脚本
chmod +x deploy_gpu_server.sh
./deploy_gpu_server.sh
```

### 访问系统

部署完成后，通过以下地址访问：
- **HTTP**: `http://服务器IP:8080`
- **HTTPS**: `https://服务器IP:8080`

## 手动部署（如果脚本失败）

### 1. 安装依赖
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 安装NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 2. 部署应用
```bash
# 创建SSL证书
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/server.key -out ssl/server.crt \
    -subj "/C=CN/ST=State/L=City/O=Org/CN=localhost"

# 启动服务
docker-compose -f docker-compose.gpu-server.yml up -d
```

## 验证部署

```bash
# 检查容器状态
docker-compose -f docker-compose.gpu-server.yml ps

# 检查GPU使用
nvidia-smi

# 测试API
curl http://localhost:5000/api/health
```

## 常用管理命令

```bash
# 查看日志
docker-compose -f docker-compose.gpu-server.yml logs -f

# 重启服务
docker-compose -f docker-compose.gpu-server.yml restart

# 停止服务
docker-compose -f docker-compose.gpu-server.yml down

# 更新应用
docker-compose -f docker-compose.gpu-server.yml down
docker-compose -f docker-compose.gpu-server.yml build --no-cache
docker-compose -f docker-compose.gpu-server.yml up -d
```

## 故障排除

### GPU不可用
```bash
# 检查驱动
nvidia-smi

# 测试Docker GPU支持
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi
```

### 端口被占用
```bash
# 检查端口
sudo netstat -tlnp | grep :8080

# 修改端口（编辑docker-compose.gpu-server.yml）
```

### 服务无法启动
```bash
# 查看详细错误
docker-compose -f docker-compose.gpu-server.yml logs

# 检查磁盘空间
df -h

# 清理Docker
docker system prune -a
```

## 性能监控

```bash
# GPU使用率
watch -n 1 nvidia-smi

# 容器资源使用
docker stats

# 系统资源
htop
```

## 安全配置

```bash
# 配置防火墙
sudo ufw allow 8080/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 更改默认密钥（编辑.env文件）
SECRET_KEY=your-new-secret-key
JWT_SECRET_KEY=your-new-jwt-key
```

详细部署说明请参考 `GPU_SERVER_DEPLOYMENT.md`