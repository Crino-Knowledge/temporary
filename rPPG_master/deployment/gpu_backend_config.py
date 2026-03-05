# GPU后端配置文件
# 针对Linux服务器部署优化

import os

# 基础配置
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# CORS配置
CORS_ORIGINS = [
    "http://localhost:80",
    "http://localhost:8080", 
    "https://localhost:443",
    "https://localhost:8080",
    "http://127.0.0.1:80",
    "http://127.0.0.1:8080",
    "https://127.0.0.1:443",
    "https://127.0.0.1:8080",
    "*"  # 生产环境中应该指定具体域名
]

# Socket.IO CORS配置
SOCKETIO_CORS_ALLOWED_ORIGINS = [
    "http://localhost:80",
    "http://localhost:8080",
    "https://localhost:443", 
    "https://localhost:8080",
    "http://127.0.0.1:80",
    "http://127.0.0.1:8080",
    "https://127.0.0.1:443",
    "https://127.0.0.1:8080",
    "*"  # 生产环境中应该指定具体域名
]

# GPU配置
USE_GPU = True
GPU_DEVICE_ID = 0
CUDA_VISIBLE_DEVICES = "0"

# 模型配置
MODEL_PATH = "/app/linknet18.pth"
MODEL_CACHE_SIZE = 1  # 缓存的模型数量

# 会话配置
MAX_ACTIVE_SESSIONS = 10
SESSION_TIMEOUT = 300  # 5分钟
FRAME_BUFFER_SIZE = 30  # 帧缓冲区大小

# 性能配置
MAX_WORKERS = 4
THREAD_POOL_SIZE = 8
PROCESS_TIMEOUT = 30

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = '/var/log/rppg-backend.log'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# 安全配置
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')

# 数据库配置（如果需要）
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///rppg.db')

# Redis配置（如果需要缓存）
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# 监控配置
MONITORING_ENABLED = True
METRICS_PORT = 9090

# 健康检查配置
HEALTH_CHECK_ENABLED = True
HEALTH_CHECK_INTERVAL = 30

# 文件上传配置
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
UPLOAD_FOLDER = '/tmp/uploads'

# 心率检测配置
HEART_RATE_MIN = 40
HEART_RATE_MAX = 200
SAMPLE_RATE = 30  # FPS
WINDOW_SIZE = 150  # 5秒窗口

# 图像处理配置
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
FACE_DETECTION_CONFIDENCE = 0.5
FACE_TRACKING_ENABLED = True

# 缓存配置
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300

# 环境特定配置
if os.getenv('FLASK_ENV') == 'production':
    DEBUG = False
    LOG_LEVEL = 'WARNING'
else:
    DEBUG = True
    LOG_LEVEL = 'DEBUG'