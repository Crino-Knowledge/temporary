# 🚀 rPPG前端启动指南

## 快速启动

### 方法1: 使用Python脚本（推荐）
```bash
cd frontend
python start_simple.py
```

### 方法2: 直接使用npm
```bash
cd frontend
npm install
npm run serve
```

## 环境要求

- Node.js 16+ 
- npm 8+
- Python 3.7+ (如果使用Python脚本)

## 常见问题解决

### 1. 依赖安装失败
```bash
# 清除缓存
npm cache clean --force

# 删除node_modules重新安装
rm -rf node_modules package-lock.json
npm install
```

### 2. 端口被占用
```bash
# 查找占用端口的进程
netstat -ano | findstr :8080

# 杀死进程
taskkill /PID <进程ID> /F
```

### 3. 编译错误
```bash
# 使用简化配置
cp vue.config.simple.js vue.config.js

# 重新启动
npm run serve
```

### 4. 浏览器兼容性
- 确保浏览器支持ES6+
- 启用JavaScript
- 允许摄像头访问权限

## 开发模式

### 热重载
前端支持热重载，修改代码后会自动刷新浏览器。

### 调试
- 打开浏览器开发者工具
- 查看Console面板的错误信息
- 使用Vue DevTools插件

## 生产构建

```bash
npm run build
```

构建后的文件在 `dist/` 目录中。

## 技术栈

- Vue 3.3.4
- Vue Router 4.2.5
- Vuex 4.1.0
- Element Plus 2.4.4
- Chart.js 4.4.0
- Socket.io-client 4.7.2

## 项目结构

```
frontend/
├── src/
│   ├── views/          # 页面组件
│   ├── store/          # 状态管理
│   ├── router/         # 路由配置
│   ├── api/            # API服务
│   └── styles/         # 样式文件
├── public/             # 静态资源
├── package.json        # 依赖配置
├── vue.config.js       # Vue配置
└── start_simple.py     # 启动脚本
```

## 访问地址

- 开发环境: http://localhost:8080
- 生产环境: 根据部署配置

## 注意事项

1. 确保后端服务已启动（默认端口5000）
2. 首次启动可能需要较长时间安装依赖
3. 如果遇到SCSS编译问题，使用简化配置
4. 确保摄像头权限已授权
