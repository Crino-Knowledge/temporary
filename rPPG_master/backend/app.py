from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import cv2
import numpy as np
import base64
import io
from PIL import Image
import threading
import time
import uuid
from datetime import datetime
import json
import os
import sys
import psutil

# 添加rPPG_master目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'rPPG_master'))

from rppg_processor import RPPGProcessor
import torch

# 尝试导入GPU配置
try:
    from gpu_backend_config import get_gpu_config, setup_gpu_environment, get_gpu_status
    config = get_gpu_config()
    setup_gpu_environment()
    USE_GPU_CONFIG = True
except ImportError:
    # 回退到基础配置
    class BasicConfig:
        USE_GPU = torch.cuda.is_available()
        TORCH_DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
        CORS_ORIGINS = ["*"]
        SOCKETIO_CORS_ALLOWED_ORIGINS = ["http://localhost:8082", "http://127.0.0.1:8082", "http://localhost:8081", "http://127.0.0.1:8081", "https://localhost:8082", "https://127.0.0.1:8082", "https://192.168.0.210:8082", "*"]
        SECRET_KEY = 'rppg_secret_key'
    config = BasicConfig()
    USE_GPU_CONFIG = False

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
CORS(app, origins=config.CORS_ORIGINS)
socketio = SocketIO(app, cors_allowed_origins=config.SOCKETIO_CORS_ALLOWED_ORIGINS, async_mode='threading')

# 全局变量
active_sessions = {}
device = torch.device(config.TORCH_DEVICE)

# GPU优化设置
if config.USE_GPU and torch.cuda.is_available():
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False
    # 预热GPU
    dummy_tensor = torch.randn(1, 3, 224, 224, device=device)
    del dummy_tensor
    torch.cuda.empty_cache()
    print(f"✅ GPU加速已启用: {torch.cuda.get_device_name(0)}")
else:
    print("⚠️ 使用CPU模式")

class RPPGSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.is_active = False
        self.results_buffer = []
        self.processor = None
        self.created_at = datetime.now()
        self.last_heartrate = 0
        self.last_bvp = []
        self.frame_count = 0
        
        # 初始化rPPG处理器
        self.init_processor()
    
    def init_processor(self):
        """初始化rPPG处理器"""
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'linknet18.pth')
            self.processor = RPPGProcessor(device=str(device), model_path=model_path)
            print(f"rPPG处理器初始化成功")
        except Exception as e:
            print(f"rPPG处理器初始化失败: {e}")
    
    def process_frame(self, frame_data):
        """处理单帧数据"""
        try:
            if not self.processor:
                return
                
            # 解码base64图像
            image_data = base64.b64decode(frame_data.split(',')[1])
            image = Image.open(io.BytesIO(image_data))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 使用rPPG处理器处理帧
            result = self.processor.process_frame(frame)
            
            if result:
                self.frame_count = result['frame_count']
                self.last_heartrate = result['heartrate']
                self.last_bvp = result['bvp_signal']
                
                # 构建完整结果
                full_result = {
                    'timestamp': datetime.now().isoformat(),
                    'heartrate': result['heartrate'],
                    'bvp': result['bvp_signal'],
                    'signal_quality': result.get('signal_quality', 0),
                    'frame_count': result['frame_count'],
                    'session_id': self.session_id,
                    'rgb_mean': result.get('rgb_mean', [0, 0, 0])
                }
                
                self.results_buffer.append(full_result)
                
                # 发送结果到前端
                socketio.emit('rppg_result', full_result, room=self.session_id)
                
                # 限制结果缓冲区大小
                if len(self.results_buffer) > 100:
                    self.results_buffer = self.results_buffer[-100:]
            else:
                # 当没有检测到有效数据时，发送清空信号
                if self.processor.no_face_count >= self.processor.max_no_face_frames:
                    clear_result = {
                        'timestamp': datetime.now().isoformat(),
                        'heartrate': 0,
                        'bvp': [],
                        'signal_quality': 0,
                        'frame_count': self.processor.frame_count,
                        'session_id': self.session_id,
                        'clear_data': True  # 标识需要清空数据
                    }
                    socketio.emit('rppg_result', clear_result, room=self.session_id)
                
        except Exception as e:
            print(f"帧处理错误: {e}")
    
    def get_latest_results(self, count=10):
        """获取最新的结果"""
        return self.results_buffer[-count:] if self.results_buffer else []
    
    def reset(self):
        """重置会话状态"""
        if self.processor:
            self.processor.reset()
        self.results_buffer = []
        self.last_heartrate = 0
        self.last_bvp = []
        self.frame_count = 0

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    health_info = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(active_sessions),
        'device': str(device),
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent
    }
    
    # 添加GPU信息
    if config.USE_GPU and torch.cuda.is_available():
        try:
            if USE_GPU_CONFIG:
                gpu_status = get_gpu_status()
                health_info.update(gpu_status)
            else:
                health_info.update({
                    'gpu_available': True,
                    'gpu_name': torch.cuda.get_device_name(0),
                    'gpu_memory_allocated': torch.cuda.memory_allocated(0) / 1024**3,
                    'gpu_memory_cached': torch.cuda.memory_reserved(0) / 1024**3
                })
        except Exception as e:
            health_info['gpu_error'] = str(e)
    else:
        health_info['gpu_available'] = False
    
    return jsonify(health_info)

@app.route('/api/system/gpu', methods=['GET'])
def get_gpu_info():
    """获取GPU详细信息"""
    if not (config.USE_GPU and torch.cuda.is_available()):
        return jsonify({'error': 'GPU不可用'}), 404
    
    try:
        if USE_GPU_CONFIG:
            return jsonify(get_gpu_status())
        else:
            return jsonify({
                'gpu_count': torch.cuda.device_count(),
                'current_device': torch.cuda.current_device(),
                'device_name': torch.cuda.get_device_name(0),
                'memory_allocated': torch.cuda.memory_allocated(0),
                'memory_cached': torch.cuda.memory_reserved(0),
                'memory_total': torch.cuda.get_device_properties(0).total_memory
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """创建新的监测会话"""
    try:
        session_id = str(uuid.uuid4())
        session = RPPGSession(session_id)
        active_sessions[session_id] = session
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'message': '会话创建成功'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'会话创建失败: {str(e)}'
        })

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """删除监测会话"""
    try:
        if session_id in active_sessions:
            session = active_sessions[session_id]
            session.is_active = False
            del active_sessions[session_id]
            
            return jsonify({
                'status': 'success',
                'message': '会话删除成功'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '会话不存在'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'会话删除失败: {str(e)}'
        })

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session_status(session_id):
    """获取会话状态"""
    try:
        if session_id in active_sessions:
            session = active_sessions[session_id]
            return jsonify({
                'status': 'success',
                'session': {
                    'id': session_id,
                    'is_active': session.is_active,
                    'created_at': session.created_at.isoformat(),
                    'frame_count': session.frame_count,
                    'last_heartrate': session.last_heartrate
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '会话不存在'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取会话状态失败: {str(e)}'
        })

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """列出所有活跃会话"""
    try:
        sessions = []
        for session_id, session in active_sessions.items():
            sessions.append({
                'id': session_id,
                'is_active': session.is_active,
                'created_at': session.created_at.isoformat(),
                'frame_count': session.frame_count,
                'last_heartrate': session.last_heartrate
            })
        
        return jsonify({
            'status': 'success',
            'sessions': sessions
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取会话列表失败: {str(e)}'
        })

@app.route('/api/sessions/<session_id>/results', methods=['GET'])
def get_session_results(session_id):
    """获取会话的历史结果"""
    try:
        if session_id not in active_sessions:
            return jsonify({
                'status': 'error',
                'message': '会话不存在'
            })
        
        session = active_sessions[session_id]
        count = request.args.get('count', 50, type=int)
        results = session.get_latest_results(count)
        
        return jsonify({
            'status': 'success',
            'results': results,
            'total_count': len(session.results_buffer)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取会话结果失败: {str(e)}'
        })

@app.route('/api/sessions/<session_id>/reset', methods=['POST'])
def reset_session(session_id):
    """重置会话状态"""
    try:
        if session_id not in active_sessions:
            return jsonify({
                'status': 'error',
                'message': '会话不存在'
            })
        
        session = active_sessions[session_id]
        session.reset()
        
        return jsonify({
            'status': 'success',
            'message': '会话状态已重置'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'重置会话失败: {str(e)}'
        })

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    print(f'客户端连接: {request.sid}')
    emit('connected', {'message': '连接成功'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'客户端断开连接: {request.sid}')

@socketio.on('join_session')
def handle_join_session(data):
    session_id = data.get('session_id')
    if session_id and session_id in active_sessions:
        join_room(session_id)
        active_sessions[session_id].is_active = True
        emit('session_joined', {'status': 'success', 'session_id': session_id})
        print(f'客户端 {request.sid} 加入会话 {session_id}')
    else:
        emit('session_joined', {'status': 'error', 'message': '无效的会话ID'})
        emit('error', {'message': '无效的会话ID'})

@socketio.on('leave_session')
def handle_leave_session(data):
    session_id = data.get('session_id')
    if session_id and session_id in active_sessions:
        leave_room(session_id)
        active_sessions[session_id].is_active = False
        emit('session_left', {'session_id': session_id})
        print(f'客户端 {request.sid} 离开会话 {session_id}')

@socketio.on('frame_data')
def handle_frame_data(data):
    """处理前端发送的帧数据"""
    try:
        session_id = data.get('session_id')
        frame_data = data.get('frame')
        
        if session_id and session_id in active_sessions and frame_data:
            session = active_sessions[session_id]
            session.process_frame(frame_data)
        else:
            emit('error', {'message': '无效的会话或帧数据'})
            
    except Exception as e:
        print(f'帧数据处理错误: {e}')
        emit('error', {'message': f'帧数据处理失败: {str(e)}'})

if __name__ == '__main__':
    print("启动rPPG后端服务...")
    print(f"使用设备: {device}")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)