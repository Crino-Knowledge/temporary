# HTTPS配置指南

## 问题说明

现代浏览器出于安全考虑，要求在HTTPS环境下才能访问用户的摄像头和麦克风。当其他设备通过局域网IP地址（如 `http://192.168.0.210:8082/`）访问rPPG系统时，会遇到"浏览器不支持摄像头"的错误。

## 解决方案

### 方案一：使用自签名SSL证书（推荐）

#### 1. 生成SSL证书

```bash
# 安装OpenSSL（如果未安装）
# Windows: 下载并安装 OpenSSL
# Linux: sudo apt-get install openssl
# macOS: brew install openssl

# 生成私钥
openssl genrsa -out server.key 2048

# 生成证书签名请求
openssl req -new -key server.key -out server.csr
# 填写信息时，Common Name 填写服务器IP地址：192.168.0.210

# 生成自签名证书
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
```

#### 2. 配置Nginx支持HTTPS

创建 `nginx-https.conf`：

```nginx
server {
    listen 80;
    server_name 192.168.0.210;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name 192.168.0.210;
    
    ssl_certificate /path/to/server.crt;
    ssl_certificate_key /path/to/server.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 前端静态文件
    location / {
        proxy_pass http://192.168.0.210:8082;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 后端API
    location /api/ {
        proxy_pass http://192.168.0.210:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket支持
    location /socket.io/ {
        proxy_pass http://192.168.0.210:5000/socket.io/;
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

#### 3. 启动Nginx

```bash
# 使用Docker启动Nginx
docker run -d \
  --name rppg-nginx \
  -p 80:80 \
  -p 443:443 \
  -v /path/to/nginx-https.conf:/etc/nginx/conf.d/default.conf \
  -v /path/to/server.crt:/etc/nginx/ssl/server.crt \
  -v /path/to/server.key:/etc/nginx/ssl/server.key \
  nginx:alpine
```

#### 4. 客户端信任证书

由于使用自签名证书，客户端浏览器会显示安全警告：

1. 访问 `https://192.168.0.210`
2. 浏览器显示"不安全"警告
3. 点击"高级"→"继续访问"
4. 或者将证书添加到系统信任列表

### 方案二：使用mkcert生成本地CA证书

#### 1. 安装mkcert

```bash
# Windows (使用Chocolatey)
choco install mkcert

# macOS
brew install mkcert

# Linux
curl -JLO "https://dl.filippo.io/mkcert/latest?for=linux/amd64"
chmod +x mkcert-v*-linux-amd64
sudo mv mkcert-v*-linux-amd64 /usr/local/bin/mkcert
```

#### 2. 生成证书

```bash
# 安装本地CA
mkcert -install

# 生成证书
mkcert 192.168.0.210 localhost 127.0.0.1
```

### 方案三：临时解决方案（仅用于测试）

#### Chrome浏览器

启动Chrome时添加参数：

```bash
chrome.exe --unsafely-treat-insecure-origin-as-secure=http://192.168.0.210:8082 --user-data-dir=/tmp/chrome_dev_test
```

#### Firefox浏览器

1. 在地址栏输入 `about:config`
2. 搜索 `media.devices.insecure.enabled`
3. 设置为 `true`

## 推荐配置

### 完整的HTTPS部署脚本

创建 `setup_https.sh`：

```bash
#!/bin/bash

# 设置变量
SERVER_IP="192.168.0.210"
CERT_DIR="./ssl"

# 创建证书目录
mkdir -p $CERT_DIR

# 生成SSL证书
echo "生成SSL证书..."
openssl genrsa -out $CERT_DIR/server.key 2048
openssl req -new -key $CERT_DIR/server.key -out $CERT_DIR/server.csr -subj "/C=CN/ST=State/L=City/O=Organization/CN=$SERVER_IP"
openssl x509 -req -days 365 -in $CERT_DIR/server.csr -signkey $CERT_DIR/server.key -out $CERT_DIR/server.crt

# 创建Nginx配置
cat > nginx-https.conf << EOF
server {
    listen 80;
    server_name $SERVER_IP;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl;
    server_name $SERVER_IP;
    
    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;
    
    location / {
        proxy_pass http://$SERVER_IP:8082;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /api/ {
        proxy_pass http://$SERVER_IP:5000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /socket.io/ {
        proxy_pass http://$SERVER_IP:5000/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启动Nginx容器
echo "启动HTTPS代理..."
docker run -d \
  --name rppg-https-proxy \
  -p 80:80 \
  -p 443:443 \
  -v $(pwd)/nginx-https.conf:/etc/nginx/conf.d/default.conf \
  -v $(pwd)/$CERT_DIR:/etc/nginx/ssl \
  nginx:alpine

echo "HTTPS配置完成！"
echo "访问地址: https://$SERVER_IP"
echo "注意：首次访问时需要在浏览器中信任自签名证书"
```

## 使用说明

1. **配置HTTPS后**，用户访问 `https://192.168.0.210` 即可正常使用摄像头
2. **首次访问**时，浏览器会提示证书不受信任，点击"继续访问"即可
3. **移动设备**同样支持，在手机浏览器中访问HTTPS地址

## 故障排除

### 常见问题

1. **证书错误**：确保证书的Common Name与访问IP一致
2. **端口冲突**：确保80和443端口未被占用
3. **防火墙**：确保防火墙允许80和443端口

### 检查命令

```bash
# 检查证书
openssl x509 -in server.crt -text -noout

# 检查端口
netstat -tlnp | grep :443

# 测试HTTPS连接
curl -k https://192.168.0.210
```

## 总结

通过配置HTTPS，可以完美解决摄像头访问问题，让其他设备能够正常使用rPPG心率监测系统。推荐使用方案一（自签名证书）进行快速部署。