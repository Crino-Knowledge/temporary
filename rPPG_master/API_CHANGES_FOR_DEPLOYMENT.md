# API配置修改说明

## 概述

本文档详细说明了将rPPG系统从开发环境迁移到Linux GPU服务器生产环境时需要进行的API和配置修改。

## 主要变更

### 1. 前端API配置变更

#### 开发环境 → 生产环境

**文件**: `frontend/.env.local` → `.env.production`

```bash
# 开发环境配置
VUE_APP_API_BASE_URL=http://192.168.0.210:5000
VUE_APP_WS_URL=http://192.168.0.210:5000

# 生产环境配置
VUE_APP_API_BASE_URL=/api
VUE_APP_WS_URL=/
```

**变更原因**:
- 生产环境使用Nginx反向代理
- 相对路径避免硬编码IP地址
- 支持HTTPS和HTTP自动适配

### 2. 后端CORS配置变更

**文件**: `backend/app.py`

```python
# 开发环境CORS配置
CORS_ORIGINS = [
    "http://localhost:8082",
    "https://localhost:8082",
    "http://192.168.0.210:8082",
    "https://192.168.0.210:8082"
]

# 生产环境CORS配置
CORS_ORIGINS = [
    "http://localhost:80",
    "http://localhost:8080", 
    "https://localhost:443",
    "https://localhost:8080",
    "*"  # 生产环境中应该指定具体域名
]
```

### 3. Docker网络配置

#### 服务间通信变更

**开发环境**:
- 直接通过IP:端口访问
- 前端开发服务器代理到后端

**生产环境**:
- Docker内部网络通信
- 服务名解析（如：`rppg-backend-gpu:5000`）
- Nginx统一入口

### 4. 端口映射变更

| 服务 | 开发环境 | 生产环境 | 说明 |
|------|----------|----------|------|
| 前端 | 8082 | 80 (容器内) | 通过Nginx代理 |
| 后端 | 5000 | 5000 | 保持不变 |
| Nginx | - | 8080 (HTTP), 443 (HTTPS) | 新增反向代理 |

## 详细配置文件变更

### 1. Nginx反向代理配置

**新增文件**: `deployment/nginx-server.conf`

```nginx
# API代理配置
location /api/ {
    proxy_pass http://rppg-backend-gpu:5000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# WebSocket代理配置
location /socket.io/ {
    proxy_pass http://rppg-backend-gpu:5000/socket.io/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### 2. Docker Compose配置

**新增文件**: `docker-compose.gpu-server.yml`

```yaml
services:
  rppg-backend-gpu:
    build:
      context: .
      dockerfile: deployment/Dockerfile.gpu-backend
    environment:
      - FLASK_ENV=production
      - CUDA_VISIBLE_DEVICES=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 3. 前端构建配置

**修改文件**: `deployment/Dockerfile.frontend`

```dockerfile
# 构建参数变更
ARG VUE_APP_API_BASE_URL=/api
ARG VUE_APP_WS_URL=/
ARG VUE_APP_TITLE=rPPG实时心率监测系统
```

### 4. 后端GPU配置

**新增文件**: `deployment/gpu_backend_config.py`

```python
# GPU配置
USE_GPU = True
GPU_DEVICE_ID = 0
CUDA_VISIBLE_DEVICES = "0"

# 生产环境CORS
CORS_ORIGINS = [
    "http://localhost:80",
    "http://localhost:8080",
    "https://localhost:443",
    "https://localhost:8080",
    "*"
]
```

## 网络架构变更

### 开发环境架构
```
用户浏览器 → 前端开发服务器(8082) → 后端API(5000)
           ↓
        WebSocket连接
```

### 生产环境架构
```
用户浏览器 → Nginx(8080/443) → 前端容器(80)
           ↓                 ↓
        API/WebSocket → 后端GPU容器(5000)
```

## 环境变量配置

### 开发环境
```bash
# frontend/.env.local
VUE_APP_API_BASE_URL=http://192.168.0.210:5000
VUE_APP_WS_URL=http://192.168.0.210:5000
```

### 生产环境
```bash
# .env.production
VUE_APP_API_BASE_URL=/api
VUE_APP_WS_URL=/
FLASK_ENV=production
CUDA_VISIBLE_DEVICES=0
```

## SSL/HTTPS配置

### 开发环境
- 前端开发服务器直接提供HTTPS
- 自签名证书
- 直接访问前端服务

### 生产环境
- Nginx提供HTTPS终止
- 可配置Let's Encrypt证书
- 统一入口点

## API端点变更

### 前端API调用

**开发环境**:
```javascript
// 直接调用后端API
axios.get('http://192.168.0.210:5000/api/health')
```

**生产环境**:
```javascript
// 通过相对路径调用，由Nginx代理
axios.get('/api/health')
```

### WebSocket连接

**开发环境**:
```javascript
// 直接连接后端WebSocket
io('http://192.168.0.210:5000')
```

**生产环境**:
```javascript
// 通过相对路径连接，由Nginx代理
io('/')
```

## 部署后验证

### 1. API连通性测试
```bash
# 健康检查
curl http://服务器IP:8080/api/health

# 系统状态
curl http://服务器IP:8080/api/system/status
```

### 2. WebSocket连接测试
```bash
# 使用浏览器开发者工具检查WebSocket连接
# 或使用wscat工具
wscat -c ws://服务器IP:8080/socket.io/
```

### 3. 前端访问测试
```bash
# HTTP访问
curl http://服务器IP:8080/

# HTTPS访问
curl -k https://服务器IP:8080/
```

## 故障排除

### 1. API 404错误
- 检查Nginx代理配置
- 确认后端服务运行状态
- 验证Docker网络连接

### 2. WebSocket连接失败
- 检查Nginx WebSocket代理配置
- 确认Socket.IO CORS设置
- 验证防火墙端口开放

### 3. CORS错误
- 更新后端CORS_ORIGINS配置
- 检查请求头设置
- 验证域名配置

## 性能优化建议

### 1. Nginx优化
- 启用gzip压缩
- 配置静态文件缓存
- 设置适当的超时时间

### 2. Docker优化
- 设置资源限制
- 使用多阶段构建
- 优化镜像大小

### 3. GPU优化
- 配置CUDA内存管理
- 优化批处理大小
- 监控GPU使用率

## 安全配置

### 1. 生产环境安全
- 更改默认密钥
- 配置具体的CORS域名
- 启用HTTPS重定向
- 设置安全头

### 2. 网络安全
- 配置防火墙规则
- 限制API访问频率
- 启用访问日志

### 3. 容器安全
- 使用非root用户
- 限制容器权限
- 定期更新基础镜像