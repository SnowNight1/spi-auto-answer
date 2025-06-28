"""
通用工具函数模块
提供日志记录、配置加载、图像处理等公共功能
"""

import json
import logging
import os
from typing import Any, Dict, Optional
from functools import wraps

# 可选依赖导入
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("OpenCV未安装，高级图像处理功能将不可用。安装命令: pip install opencv-python")

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.error("PIL(Pillow)未安装，图像处理功能将不可用。安装命令: pip install Pillow")


def safe_execute(func):
    """安全执行装饰器，捕获异常并记录"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"执行 {func.__name__} 时发生错误: {e}")
            return None
    return wrapper


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"配置文件未找到: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"配置文件格式错误: {e}")
            return {}
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置值，支持嵌套键路径，如 'api.api_key'"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def update(self, key_path: str, value: Any) -> None:
        """更新配置值"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")


class Logger:
    """日志管理器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """设置日志配置"""
        log_level = getattr(logging, self.config.get('logging.level', 'INFO').upper())
        log_file = self.config.get('logging.file', 'spi_auto_answer.log')
        
        # 创建logs目录
        log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 文件处理器
        file_handler = logging.FileHandler(
            os.path.join(log_dir, os.path.basename(log_file)),
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        
        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)


class ImageProcessor:
    """图像处理工具"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        
        # 检查依赖可用性
        if not PIL_AVAILABLE:
            logging.error("PIL未安装，图像处理功能将不可用")
        if not CV2_AVAILABLE:
            logging.warning("OpenCV未安装，部分高级图像处理功能将不可用")
    
    @safe_execute
    def preprocess_for_ocr(self, image) -> Optional['Image.Image']:
        """
        为OCR预处理图像
        
        Args:
            image: PIL图像对象
            
        Returns:
            处理后的图像或None
        """
        if not PIL_AVAILABLE:
            logging.error("PIL未安装，无法进行图像预处理")
            return image if hasattr(image, 'copy') else None
            
        if not CV2_AVAILABLE:
            logging.warning("OpenCV未安装，使用基础预处理")
            return self._basic_preprocess(image)
        
        try:
            # 获取预处理配置
            resize_factor = self.config.get('ocr.preprocess.resize_factor', 2.0)
            blur_kernel = self.config.get('ocr.preprocess.blur_kernel', 1)
            threshold_type = self.config.get('ocr.preprocess.threshold_type', 'adaptive')
            
            # 转换为numpy数组
            img_array = np.array(image)
            
            # 如果是彩色图像，转换为灰度
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # 放大图像
            if resize_factor != 1.0:
                new_width = int(img_array.shape[1] * resize_factor)
                new_height = int(img_array.shape[0] * resize_factor)
                img_array = cv2.resize(img_array, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # 降噪
            if blur_kernel > 0:
                img_array = cv2.medianBlur(img_array, blur_kernel)
            
            # 二值化
            if threshold_type == 'adaptive':
                img_array = cv2.adaptiveThreshold(
                    img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                )
            elif threshold_type == 'otsu':
                _, img_array = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 转换回PIL图像
            return Image.fromarray(img_array)
            
        except Exception as e:
            logging.error(f"OpenCV图像预处理失败: {e}")
            return self._basic_preprocess(image)
    
    def _basic_preprocess(self, image) -> Optional['Image.Image']:
        """基础预处理（仅使用PIL）"""
        if not PIL_AVAILABLE:
            return None
            
        try:
            # 转换为灰度
            if image.mode != 'L':
                image = image.convert('L')
            
            # 放大图像
            resize_factor = self.config.get('ocr.preprocess.resize_factor', 2.0)
            if resize_factor != 1.0:
                new_size = (int(image.width * resize_factor), int(image.height * resize_factor))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # 增强对比度
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            return image
            
        except Exception as e:
            logging.error(f"基础图像预处理失败: {e}")
            return image
    
    @safe_execute
    def enhance_image(self, image) -> Optional['Image.Image']:
        """
        增强图像质量
        
        Args:
            image: PIL图像对象
            
        Returns:
            增强后的图像或None
        """
        if not PIL_AVAILABLE:
            logging.error("PIL未安装，无法增强图像")
            return image if hasattr(image, 'copy') else None
            
        try:
            # 增强对比度
            contrast_enhancer = ImageEnhance.Contrast(image)
            image = contrast_enhancer.enhance(1.5)
            
            # 增强锐度
            sharpness_enhancer = ImageEnhance.Sharpness(image)
            image = sharpness_enhancer.enhance(1.2)
            
            # 轻微锐化滤镜
            image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            return image
            
        except Exception as e:
            logging.error(f"图像增强失败: {e}")
            return image
    
    @safe_execute
    def save_debug_image(self, image, filename: str) -> bool:
        """
        保存调试用图像
        
        Args:
            image: PIL图像对象
            filename: 文件名
            
        Returns:
            是否保存成功
        """
        if not PIL_AVAILABLE:
            logging.error("PIL未安装，无法保存调试图像")
            return False
            
        try:
            debug_dir = "debug_images"
            os.makedirs(debug_dir, exist_ok=True)
            
            file_path = os.path.join(debug_dir, filename)
            image.save(file_path)
            logging.debug(f"调试图像已保存: {file_path}")
            return True
            
        except Exception as e:
            logging.error(f"保存调试图像失败: {e}")
            return False


def validate_config(config_manager: ConfigManager) -> bool:
    """
    验证配置文件的完整性
    
    Args:
        config_manager: 配置管理器
        
    Returns:
        配置是否有效
    """
    required_keys = [
        'api.api_key',
        'api.api_endpoint',
        'ocr.language',
        'excel.file_path',
        'hotkey.trigger_key'
    ]
    
    missing_keys = []
    for key in required_keys:
        if not config_manager.get(key):
            missing_keys.append(key)
    
    if missing_keys:
        logging.error(f"配置文件缺少必要项: {missing_keys}")
        return False
    
    return True


def safe_execute(func, *args, **kwargs):
    """
    安全执行函数，捕获异常并记录
    
    Args:
        func: 要执行的函数
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        函数执行结果或None
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logging.error(f"执行函数 {func.__name__} 时发生错误: {e}")
        return None
