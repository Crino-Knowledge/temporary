#!/bin/bash
# rPPG系统GPU服务器部署脚本
# 适用于Ubuntu 20.04 + NVIDIA RTX 3060

set -e

echo "=== rPPG GPU服务器部署脚本 ==="
echo "开始部署到Linux GPU服务器..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}请不要使用root用户运行此脚本${NC}"
   exit 1
fi

# 检查系统
echo -e "${YELLOW}检查系统环境...${NC}"
if ! command -v lsb_release &> /dev/null; then
    echo -e "${RED}无法检测系统版本，请确保运行在Ubuntu系统上${NC}"
    exit 1
fi

OS_VERSION=$(lsb_release -rs)
echo "检测到系统版本: Ubuntu $OS_VERSION"

# 更新系统
echo -e "${YELLOW}更新系统包...${NC}"
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
echo -e "${YELLOW}安装基础依赖...${NC}"
sudo apt install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# 检查NVIDIA驱动
echo -e "${YELLOW}检查NVIDIA驱动...${NC}"
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}未检测到NVIDIA驱动，请先安装NVIDIA驱动${NC}"
    echo "安装命令: sudo apt install nvidia-driver-470"
    exit 1
else
    echo -e "${GREEN}NVIDIA驱动已安装${NC}"
    nvidia-smi
fi

# 安装Docker
echo -e "${YELLOW}安装Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $USER
    echo -e "${GREEN}Docker安装完成${NC}"
else
    echo -e "${GREEN}Docker已安装${NC}"
fi

# 安装Docker Compose
echo -e "${YELLOW}安装Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose安装完成${NC}"
else
    echo -e "${GREEN}Docker Compose已安装${NC}"
fi

# 安装NVIDIA Container Toolkit
echo -e "${YELLOW}安装NVIDIA Container Toolkit...${NC}"
if ! command -v nvidia-container-runtime &> /dev/null; then
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    sudo apt update
    sudo apt install -y nvidia-container-toolkit
    sudo systemctl restart docker
    echo -e "${GREEN}NVIDIA Container Toolkit安装完成${NC}"
else
    echo -e "${GREEN}NVIDIA Container Toolkit已安装${NC}"
fi

# 创建项目目录
echo -e "${YELLOW}创建项目目录...${NC}"
PROJECT_DIR="/opt/rppg"
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# 复制项目文件
echo -e "${YELLOW}复制项目文件...${NC}"
cp -r . $PROJECT_DIR/
cd $PROJECT_DIR

# 创建SSL证书目录
echo -e "${YELLOW}创建SSL证书...${NC}"
mkdir -p ssl
if [ ! -f ssl/server.key ] || [ ! -f ssl/server.crt ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/server.key \
        -out ssl/server.crt \
        -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
    echo -e "${GREEN}SSL证书创建完成${NC}"
fi

# 创建日志目录
echo -e "${YELLOW}创建日志目录...${NC}"
mkdir -p logs
sudo chown -R $USER:$USER logs

# 设置环境变量
echo -e "${YELLOW}配置环境变量...${NC}"
cat > .env << EOF
# 生产环境配置
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# GPU配置
CUDA_VISIBLE_DEVICES=0
NVIDIA_VISIBLE_DEVICES=all
NVIDIA_DRIVER_CAPABILITIES=compute,utility

# 日志配置
LOG_LEVEL=INFO

# 服务器配置
HOST=0.0.0.0
PORT=5000
EOF

# 构建和启动服务
echo -e "${YELLOW}构建Docker镜像...${NC}"
docker-compose -f docker-compose.gpu-server.yml build

echo -e "${YELLOW}启动服务...${NC}"
docker-compose -f docker-compose.gpu-server.yml up -d

# 等待服务启动
echo -e "${YELLOW}等待服务启动...${NC}"
sleep 30

# 检查服务状态
echo -e "${YELLOW}检查服务状态...${NC}"
docker-compose -f docker-compose.gpu-server.yml ps

# 测试服务
echo -e "${YELLOW}测试服务...${NC}"
if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}后端服务正常${NC}"
else
    echo -e "${RED}后端服务异常${NC}"
fi

if curl -f http://localhost:80 > /dev/null 2>&1; then
    echo -e "${GREEN}前端服务正常${NC}"
else
    echo -e "${RED}前端服务异常${NC}"
fi

echo -e "${GREEN}=== 部署完成 ===${NC}"
echo "服务访问地址:"
echo "  - HTTP:  http://$(hostname -I | awk '{print $1}'):8080"
echo "  - HTTPS: https://$(hostname -I | awk '{print $1}'):8080"
echo ""
echo "管理命令:"
echo "  - 查看日志: docker-compose -f docker-compose.gpu-server.yml logs -f"
echo "  - 停止服务: docker-compose -f docker-compose.gpu-server.yml down"
echo "  - 重启服务: docker-compose -f docker-compose.gpu-server.yml restart"
echo "  - 查看状态: docker-compose -f docker-compose.gpu-server.yml ps"
echo ""
echo -e "${YELLOW}注意: 如果使用HTTPS，浏览器会提示证书不安全，点击'继续访问'即可${NC}"