import numpy as np
import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image
import sys
import os
import threading

# 全局 GPU 锁，防止多线程并发访问 GPU 导致 CUDA 非法内存访问
_gpu_lock = threading.Lock()

# 添加rPPG_master目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'rPPG_master'))

from models import LinkNet18
from pulse import Pulse
from asf import ASF
from cdf import CDF

class RPPGProcessor:
    def __init__(self, device='cpu', model_path=None):
        self.device = torch.device(device)
        self.model = None
        self.pulse_processor = None
        self.frame_buffer = []
        self.rgb_buffer = []
        self.signal_size = 270
        self.batch_size = 30
        self.frame_rate = 28
        self.frame_count = 0
        self.no_face_count = 0  # 连续无人脸帧计数
        self.max_no_face_frames = 10  # 最大允许连续无人脸帧数
        
        # 图像预处理
        self.img_transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # 初始化模型和处理器
        self.init_model(model_path)
        self.init_pulse_processor()
    
    def init_model(self, model_path=None):
        """初始化LinkNet18模型"""
        try:
            self.model = LinkNet18()
            self.model.to(self.device)
            
            if model_path is None:
                model_path = os.path.join(os.path.dirname(__file__), 'linknet18.pth')
            
            if os.path.exists(model_path):
                pretrained_dict = torch.load(model_path, map_location=self.device)
                model_dict = self.model.state_dict()
                pretrained_dict = {k: v for k, v in pretrained_dict.items() 
                                 if k in model_dict and v.size() == model_dict[k].size()}
                model_dict.update(pretrained_dict)
                self.model.load_state_dict(model_dict, strict=False)
                self.model.eval()
                print(f"模型加载成功: {model_path}")
            else:
                print(f"警告: 模型文件不存在: {model_path}")
                
        except Exception as e:
            print(f"模型初始化失败: {e}")
    
    def init_pulse_processor(self):
        """初始化脉搏处理器"""
        try:
            self.pulse_processor = Pulse(self.frame_rate, self.signal_size, self.batch_size)
            print("脉搏处理器初始化成功")
        except Exception as e:
            print(f"脉搏处理器初始化失败: {e}")
    
    def process_frame(self, frame):
        """处理单帧图像"""
        try:
            if self.model is None:
                return None
            
            # 确保frame是numpy数组
            if isinstance(frame, Image.Image):
                frame = np.array(frame)
            
            # 转换颜色空间
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                if frame.shape[2] == 3:  # BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                else:
                    frame_rgb = frame
            else:
                return None
            
            # 预处理图像
            pil_image = Image.fromarray(frame_rgb)
            input_tensor = self.img_transform(pil_image).unsqueeze(0).to(self.device)
            
            # 模型推理（加锁防止多线程并发访问 GPU）
            with _gpu_lock:
                with torch.no_grad():
                    mask = self.model(input_tensor)
                    mask = torch.sigmoid(mask)
                    mask = mask.squeeze().cpu().numpy()
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
            
            # 调整mask尺寸到原图大小
            original_shape = frame.shape[:2]
            mask_resized = cv2.resize(mask, (original_shape[1], original_shape[0]))
            
            # 应用阈值
            mask_binary = (mask_resized > 0.5).astype(np.uint8)
            
            # 提取皮肤区域的RGB均值
            rgb_mean = self.extract_rgb_mean(frame_rgb, mask_binary)
            
            if rgb_mean is not None:
                # 检测到人脸，重置无人脸计数
                self.no_face_count = 0
                self.rgb_buffer.append(rgb_mean)
                self.frame_count += 1
                
                # 保持缓冲区大小
                if len(self.rgb_buffer) > self.signal_size:
                    self.rgb_buffer = self.rgb_buffer[-self.signal_size:]
                
                # 当有足够数据时计算心率
                if len(self.rgb_buffer) >= self.batch_size:
                    return self.calculate_heartrate_and_bvp()
            else:
                # 未检测到人脸，增加无人脸计数
                self.no_face_count += 1
                
                # 如果连续多帧未检测到人脸，清空缓冲区
                if self.no_face_count >= self.max_no_face_frames:
                    self.rgb_buffer.clear()
                    print(f"连续{self.max_no_face_frames}帧未检测到人脸，清空信号缓冲区")
            
            return None
            
        except Exception as e:
            print(f"帧处理错误: {e}")
            return None
    
    def extract_rgb_mean(self, frame, mask):
        """从皮肤区域提取RGB均值"""
        try:
            if np.sum(mask) == 0:
                return None
            
            # 应用mask提取皮肤像素
            skin_pixels = frame[mask > 0]
            
            if len(skin_pixels) == 0:
                return None
            
            # 计算RGB通道均值
            rgb_mean = np.mean(skin_pixels, axis=0)
            return rgb_mean
            
        except Exception as e:
            print(f"RGB均值提取错误: {e}")
            return None
    
    def calculate_signal_quality(self, bvp_signal, heartrate):
        """计算信号质量"""
        try:
            if bvp_signal is None or len(bvp_signal) == 0:
                return 0
            
            # 确保bvp_signal是numpy数组
            if not isinstance(bvp_signal, np.ndarray):
                bvp_signal = np.array(bvp_signal)
            
            # 展平数组以避免形状问题
            bvp_signal = bvp_signal.flatten()
            
            # 计算信号的统计特性
            signal_std = np.std(bvp_signal)
            signal_mean = np.abs(np.mean(bvp_signal))
            signal_range = np.max(bvp_signal) - np.min(bvp_signal)
            
            # 基于心率合理性的质量评估
            hr_quality = 1.0 if 50 <= heartrate <= 120 else 0.5
            
            # 基于信号变化范围的质量评估
            range_quality = min(signal_range / 10.0, 1.0) if signal_range > 0 else 0
            
            # 基于信号标准差的质量评估
            std_quality = min(signal_std / 5.0, 1.0) if signal_std > 0 else 0
            
            # 综合质量评分
            overall_quality = (hr_quality * 0.5 + range_quality * 0.3 + std_quality * 0.2) * 100
            
            return max(0, min(100, overall_quality))
            
        except Exception as e:
            print(f"信号质量计算错误: {e}")
            return 0
    
    def calculate_heartrate_and_bvp(self):
        """计算心率和BVP信号"""
        try:
            if self.pulse_processor is None or len(self.rgb_buffer) < self.batch_size:
                return None
            
            # 检查是否有连续的无人脸帧
            if self.no_face_count > 0:
                return None
            
            # 转换为numpy数组
            rgb_array = np.array(self.rgb_buffer[-self.signal_size:])
            
            if rgb_array.shape[0] < self.batch_size:
                return None
            
            # 使用Pulse类计算BVP信号
            bvp_signal = self.pulse_processor.get_pulse(rgb_array)
            
            # 计算心率
            heartrate = self.pulse_processor.get_rfft_hr(bvp_signal)
            
            # 确保心率在合理范围内
            if heartrate < 40 or heartrate > 180:
                return None  # 不返回不合理的心率值
            
            # 计算信号质量
            signal_quality = self.calculate_signal_quality(bvp_signal, heartrate)
            
            return {
                'heartrate': round(float(heartrate), 1),
                'bvp_signal': bvp_signal.tolist() if isinstance(bvp_signal, np.ndarray) else bvp_signal,
                'signal_quality': round(float(signal_quality), 1),
                'frame_count': self.frame_count,
                'rgb_mean': rgb_array[-1].tolist() if len(rgb_array) > 0 else [0, 0, 0]
            }
            
        except Exception as e:
            print(f"心率计算错误: {e}")
            # 发生错误时不返回默认值
            return None
    
    def reset(self):
        """重置处理器状态"""
        self.frame_buffer = []
        self.rgb_buffer = []
        self.frame_count = 0
        self.no_face_count = 0
        print("处理器状态已重置")
    
    def get_status(self):
        """获取处理器状态"""
        return {
            'frame_count': self.frame_count,
            'buffer_size': len(self.rgb_buffer),
            'model_loaded': self.model is not None,
            'pulse_processor_loaded': self.pulse_processor is not None,
            'device': str(self.device)
        }

# 测试函数
if __name__ == "__main__":
    # 创建处理器实例
    processor = RPPGProcessor()
    
    # 测试状态
    status = processor.get_status()
    print("处理器状态:", status)
    
    # 创建测试图像
    test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # 处理测试帧
    result = processor.process_frame(test_frame)
    print("测试结果:", result)