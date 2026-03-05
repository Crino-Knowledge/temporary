# 后端生产环境配置文件
# 将此文件放在后端目录下，并在app.py中导入使用

import os

class ProductionConfig:
    """生产环境配置"""
    
    # Flask配置
    DEBUG = False
    TESTING = False
    
    # 服务器配置
    HOST = '0.0.0.0'  # 监听所有接口
    PORT = 5000
    
    # CORS配置 - 允许前端板子访问
    CORS_ORIGINS = [
        "http://localhost:8080",
        "http://192.168.1.100",  # 替换为Linux板子的实际IP
        "http://your-frontend-domain.com",  # 替换为实际域名
    ]
    
    # WebSocket配置
    SOCKETIO_CORS_ALLOWED_ORIGINS = CORS_ORIGINS
    
    # 模型配置
    MODEL_PATH = '/opt/rppg-backend/linknet18.pth'
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/rppg-backend.log'
    
    # 性能配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_TIMEOUT = 30  # 秒
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # 数据库配置（如果需要）
    # DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Redis配置（如果需要缓存）
    # REDIS_URL = os.environ.get('REDIS_URL')

class DevelopmentConfig:
    """开发环境配置"""
    
    DEBUG = True
    TESTING = False
    HOST = 'localhost'
    PORT = 5000
    
    CORS_ORIGINS = ["http://localhost:8080"]
    SOCKETIO_CORS_ALLOWED_ORIGINS = ["http://localhost:8080"]
    
    MODEL_PATH = './linknet18.pth'
    LOG_LEVEL = 'DEBUG'

# 根据环境变量选择配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """获取当前环境配置"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])