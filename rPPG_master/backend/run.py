#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rPPG Backend Server
启动Flask应用服务器
"""

import os
import sys
from app import app, socketio

def main():
    """启动rPPG后端服务器"""
    print("启动rPPG后端服务器...")
    print(f"模型文件路径: {os.path.join(os.path.dirname(__file__), 'linknet18.pth')}")
    
    # 检查模型文件是否存在
    model_path = os.path.join(os.path.dirname(__file__), 'linknet18.pth')
    if not os.path.exists(model_path):
        print(f"错误: 模型文件不存在: {model_path}")
        sys.exit(1)
    
    # 启动服务器
    try:
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=True,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()