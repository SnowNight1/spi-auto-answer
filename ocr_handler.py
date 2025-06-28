"""
OCR处理模块
负责屏幕截图、图像预处理和文字识别
专门针对日文SPI题目优化
"""

import logging
import os
import time
from typing import Optional, Tuple, Dict, Any

# 尝试导入所需的依赖，并提供友好的错误提示
try:
    # 检查是否有GUI环境
    import os
    if 'DISPLAY' not in os.environ or not os.environ['DISPLAY']:
        PYAUTOGUI_AVAILABLE = False
        logging.info("无GUI环境，跳过pyautogui导入")
    else:
        import pyautogui
        PYAUTOGUI_AVAILABLE = True
except Exception as e:
    PYAUTOGUI_AVAILABLE = False
    logging.warning(f"pyautogui不可用: {e}")
    logging.warning("截图功能将受限。请确保在GUI环境中运行或安装: pip install pyautogui")

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    logging.error("pytesseract未安装，OCR功能将不可用。请运行: pip install pytesseract")

try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.error("PIL(Pillow)未安装，图像处理功能将不可用。请运行: pip install Pillow")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("OpenCV未安装，高级图像处理功能将受限。请运行: pip install opencv-python")

from utils import ConfigManager, ImageProcessor, safe_execute


class OCRHandler:
    """OCR处理器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.image_processor = ImageProcessor(config_manager) if CV2_AVAILABLE else None
        
        # 检查关键依赖
        self._check_dependencies()
        
        # 设置OCR引擎
        if PYTESSERACT_AVAILABLE:
            self._setup_tesseract()
        
        # 配置pyautogui
        if PYAUTOGUI_AVAILABLE:
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0.1
    
    def _check_dependencies(self) -> None:
        """检查依赖包是否完整"""
        missing_deps = []
        
        if not PIL_AVAILABLE:
            missing_deps.append("Pillow")
        if not PYTESSERACT_AVAILABLE:
            missing_deps.append("pytesseract")
        if not CV2_AVAILABLE:
            missing_deps.append("opencv-python")
        
        # 只有在GUI环境下才将pyautogui视为关键依赖
        import os
        if 'DISPLAY' in os.environ and os.environ['DISPLAY'] and not PYAUTOGUI_AVAILABLE:
            missing_deps.append("pyautogui")
        
        if missing_deps:
            error_msg = f"缺少关键依赖: {', '.join(missing_deps)}"
            logging.error(error_msg)
            logging.error("请运行以下命令安装缺失的依赖:")
            for dep in missing_deps:
                logging.error(f"  pip install {dep}")
            
            # 如果缺少核心依赖，抛出异常
            if not PIL_AVAILABLE or not PYTESSERACT_AVAILABLE:
                raise ImportError("OCR模块需要PIL和pytesseract才能正常工作")
    
    def _setup_tesseract(self) -> None:
        """配置Tesseract OCR"""
        if not PYTESSERACT_AVAILABLE:
            logging.error("pytesseract未安装，无法配置Tesseract")
            return
            
        try:
            # 设置Tesseract路径（根据操作系统选择不同路径）
            tesseract_cmd = self.config.get('ocr.tesseract_cmd', 'tesseract')
            
            # 尝试不同的Tesseract路径（包含Windows路径）
            import platform
            system = platform.system().lower()
            
            if system == 'windows':
                possible_paths = [
                    tesseract_cmd,
                    'tesseract',
                    'C:\\Program Files\\Tesseract-OCR\\tesseract.exe',
                    'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe',
                    'C:\\Tesseract-OCR\\tesseract.exe'
                ]
            else:
                possible_paths = [
                    '/usr/bin/tesseract',
                    '/usr/local/bin/tesseract', 
                    'tesseract',
                    tesseract_cmd
                ]
            
            tesseract_found = False
            for path in possible_paths:
                if path and (os.path.exists(path) or path == 'tesseract'):
                    try:
                        pytesseract.pytesseract.tesseract_cmd = path
                        # 测试是否可用
                        version = pytesseract.get_tesseract_version()
                        logging.info(f"Tesseract版本: {version} (路径: {path})")
                        tesseract_found = True
                        break
                    except Exception:
                        continue
            
            if not tesseract_found:
                raise RuntimeError("找不到可用的Tesseract安装")
                
            # 检查日文语言包
            try:
                langs = pytesseract.get_languages(config='')
                if 'jpn' not in langs:
                    logging.warning("未检测到日文语言包，OCR可能无法正确识别日文")
                    if system == 'windows':
                        logging.warning("请重新安装Tesseract并选择日文语言包")
                        logging.warning("下载地址: https://github.com/UB-Mannheim/tesseract/wiki")
                    else:
                        logging.warning("请安装日文语言包: sudo apt-get install tesseract-ocr-jpn")
                else:
                    logging.info("日文语言包已安装")
            except Exception as e:
                logging.warning(f"无法检查语言包: {e}")
            
        except Exception as e:
            logging.error(f"Tesseract配置失败: {e}")
            logging.error("请确保已正确安装Tesseract OCR:")
            import platform
            if platform.system().lower() == 'windows':
                logging.error("  Windows: 下载并安装 https://github.com/UB-Mannheim/tesseract/wiki")
                logging.error("  安装时请选择日文语言包")
            else:
                logging.error("  Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-jpn")
                logging.error("  macOS: brew install tesseract tesseract-lang")
    
    def capture_screen_region(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Image.Image]:
        """
        截取屏幕指定区域
        
        Args:
            region: (x, y, width, height) 截图区域，None则使用配置中的默认区域
            
        Returns:
            PIL图像对象或None
        """
        if not PIL_AVAILABLE:
            logging.error("PIL未安装，无法进行截图")
            return None
            
        try:
            if region is None:
                # 使用配置中的默认区域
                x = self.config.get('screenshot.region.x', 0)
                y = self.config.get('screenshot.region.y', 0)
                width = self.config.get('screenshot.region.width', 800)
                height = self.config.get('screenshot.region.height', 600)
                region = (x, y, x + width, y + height)
            else:
                # 转换为PIL ImageGrab需要的格式 (left, top, right, bottom)
                x, y, width, height = region
                region = (x, y, x + width, y + height)
            
            logging.info(f"截取屏幕区域: {region}")
            
            screenshot = None
            
            # 方法1: 使用PIL ImageGrab (推荐)
            try:
                screenshot = ImageGrab.grab(bbox=region)
                logging.debug("使用PIL ImageGrab截图成功")
            except Exception as e:
                logging.warning(f"PIL ImageGrab截图失败: {e}")
            
            # 方法2: 使用pyautogui作为备用
            if screenshot is None and PYAUTOGUI_AVAILABLE:
                try:
                    x, y, right, bottom = region
                    width, height = right - x, bottom - y
                    screenshot = pyautogui.screenshot(region=(x, y, width, height))
                    logging.debug("使用pyautogui截图成功")
                except Exception as e:
                    logging.warning(f"pyautogui截图失败: {e}")
            
            if screenshot is None:
                logging.error("所有截图方法都失败了")
                return None
            
            # 验证截图是否有效
            if screenshot.size[0] == 0 or screenshot.size[1] == 0:
                logging.error("截图尺寸无效")
                return None
            
            # 保存调试图像
            if self.config.get('logging.level') == 'DEBUG':
                timestamp = int(time.time())
                if self.image_processor:
                    self.image_processor.save_debug_image(
                        screenshot, f"screenshot_{timestamp}.png"
                    )
            
            return screenshot
            
        except Exception as e:
            logging.error(f"屏幕截图失败: {e}")
            return None
    
    def auto_detect_text_region(self, image: Image.Image) -> Optional[Tuple[int, int, int, int]]:
        """
        自动检测图像中的文字区域
        
        Args:
            image: PIL图像对象
            
        Returns:
            (x, y, width, height) 文字区域坐标或None
        """
        if not CV2_AVAILABLE:
            logging.warning("OpenCV未安装，跳过自动文字区域检测")
            return None
            
        try:
            # 转换为OpenCV格式
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # 尝试多种文字检测方法
            text_region = None
            
            # 方法1: MSER检测
            try:
                mser = cv2.MSER_create()
                regions, _ = mser.detectRegions(gray)
                
                if regions:
                    # 计算所有文字区域的边界框
                    hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]
                    
                    # 合并所有区域
                    all_points = np.vstack(hulls)
                    x, y, w, h = cv2.boundingRect(all_points)
                    
                    # 添加一些边距
                    margin = 10
                    x = max(0, x - margin)
                    y = max(0, y - margin)
                    w = min(image.width - x, w + 2 * margin)
                    h = min(image.height - y, h + 2 * margin)
                    
                    text_region = (x, y, w, h)
                    logging.info(f"MSER检测到文字区域: {text_region}")
                    
            except Exception as e:
                logging.warning(f"MSER检测失败: {e}")
            
            # 方法2: 轮廓检测作为备用
            if text_region is None:
                try:
                    # 边缘检测
                    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
                    
                    # 形态学操作连接文字
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
                    
                    # 查找轮廓
                    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    if contours:
                        # 找到最大的轮廓区域
                        largest_contour = max(contours, key=cv2.contourArea)
                        x, y, w, h = cv2.boundingRect(largest_contour)
                        
                        # 过滤太小的区域
                        if w > 50 and h > 20:
                            margin = 5
                            x = max(0, x - margin)
                            y = max(0, y - margin)
                            w = min(image.width - x, w + 2 * margin)
                            h = min(image.height - y, h + 2 * margin)
                            
                            text_region = (x, y, w, h)
                            logging.info(f"轮廓检测到文字区域: {text_region}")
                            
                except Exception as e:
                    logging.warning(f"轮廓检测失败: {e}")
            
            if text_region is None:
                logging.warning("未检测到文字区域")
            
            return text_region
            
        except Exception as e:
            logging.error(f"自动检测文字区域失败: {e}")
            return None
    
    def extract_text(self, image: Image.Image, preprocess: bool = True) -> str:
        """
        从图像中提取文字
        
        Args:
            image: PIL图像对象
            preprocess: 是否进行预处理
            
        Returns:
            识别出的文字
        """
        if not PYTESSERACT_AVAILABLE:
            logging.error("pytesseract未安装，无法进行文字识别")
            return ""
            
        if not PIL_AVAILABLE:
            logging.error("PIL未安装，无法处理图像")
            return ""
            
        try:
            original_image = image.copy()
            
            # 图像预处理
            if preprocess and self.image_processor:
                try:
                    image = self.image_processor.enhance_image(image)
                    image = self.image_processor.preprocess_for_ocr(image)
                    
                    # 保存预处理后的调试图像
                    if self.config.get('logging.level') == 'DEBUG':
                        timestamp = int(time.time())
                        self.image_processor.save_debug_image(
                            image, f"preprocessed_{timestamp}.png"
                        )
                except Exception as e:
                    logging.warning(f"图像预处理失败，使用原图: {e}")
                    image = original_image
            
            # 尝试多种OCR配置
            text_results = []
            
            # 配置1: 标准日文配置
            try:
                config1 = self._build_tesseract_config()
                text1 = pytesseract.image_to_string(image, config=config1)
                if text1.strip():
                    text_results.append(text1)
                    logging.debug(f"配置1识别结果: {text1[:50]}...")
            except Exception as e:
                logging.warning(f"OCR配置1失败: {e}")
            
            # 配置2: 单行模式
            try:
                config2 = self._build_tesseract_config(psm=8)  # 单词模式
                text2 = pytesseract.image_to_string(image, config=config2)
                if text2.strip():
                    text_results.append(text2)
                    logging.debug(f"配置2识别结果: {text2[:50]}...")
            except Exception as e:
                logging.warning(f"OCR配置2失败: {e}")
            
            # 配置3: 如果前两个都失败，尝试基础配置
            if not text_results:
                try:
                    config3 = '-l jpn'
                    text3 = pytesseract.image_to_string(image, config=config3)
                    if text3.strip():
                        text_results.append(text3)
                        logging.debug(f"配置3识别结果: {text3[:50]}...")
                except Exception as e:
                    logging.warning(f"OCR配置3失败: {e}")
            
            # 选择最佳结果（通常是最长的有意义文本）
            if text_results:
                best_text = max(text_results, key=lambda x: len(x.strip()))
                cleaned_text = self._clean_text(best_text)
                logging.info(f"OCR识别结果 (长度:{len(cleaned_text)}): {cleaned_text[:100]}...")
                return cleaned_text
            else:
                logging.warning("所有OCR配置都未能识别出文字")
                return ""
            
        except Exception as e:
            logging.error(f"OCR文字提取失败: {e}")
            return ""
    
    def _build_tesseract_config(self, psm: Optional[int] = None, oem: Optional[int] = None) -> str:
        """构建Tesseract配置字符串"""
        language = self.config.get('ocr.language', 'jpn')
        psm = psm or self.config.get('ocr.psm', 6)
        oem = oem or self.config.get('ocr.oem', 3)
        
        config = f'-l {language} --psm {psm} --oem {oem}'
        
        # 添加日文优化参数
        if language == 'jpn':
            config += ' -c preserve_interword_spaces=1'
            
            # 扩展的日文字符白名单
            whitelist = ('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                        'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん'
                        'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフへホマミムメモヤユヨラリルレロワヲン'
                        'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽゃゅょっー'
                        'ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポャュョッー'
                        '。、！？（）「」【】〔〕〈〉《》[]{}()<>""''・…'
                        '①②③④⑤⑥⑦⑧⑨⑩ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ'
                        '＋－×÷＝≠≤≥＜＞％‰∞√∴∵∈∋∪∩∧∨'
                        '　')  # 添加全角空格
            
            # 限制字符集以提高准确性
            if self.config.get('ocr.use_whitelist', True):
                config += f' -c tessedit_char_whitelist={whitelist}'
            
            # 其他日文优化参数
            config += ' -c textord_heavy_nr=1'  # 改进行检测
            config += ' -c textord_min_linesize=2.5'  # 最小行高
            
        return config
    
    def _clean_text(self, text: str) -> str:
        """
        清理OCR识别的文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = ' '.join(text.split())
        
        # 移除常见的OCR错误字符
        error_chars = ['|', '_', '~', '^', '`', '¢', '£', '¥', '©', '®', '™']
        for char in error_chars:
            text = text.replace(char, '')
        
        # 修正常见OCR错误
        replacements = {
            'O': '0',  # 字母O误识别为数字0（在数字上下文中）
            'l': '1',  # 小写l误识别为数字1（在数字上下文中）
            'I': '1',  # 大写I误识别为数字1（在数字上下文中）
            '…': '...',  # 省略号标准化
            '―': '—',   # 破折号标准化
        }
        
        # 应用替换（仅在特定上下文中）
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # 处理日文标点符号的空格
        text = text.replace(' 。', '。').replace(' 、', '、')
        text = text.replace(' ！', '！').replace(' ？', '？')
        text = text.replace('( ', '（').replace(' )', '）')
        text = text.replace('[ ', '「').replace(' ]', '」')
        text = text.replace('{ ', '【').replace(' }', '】')
        
        # 处理数字和符号之间的空格
        import re
        
        # 移除数字和运算符之间不必要的空格
        text = re.sub(r'(\d)\s*([+\-×÷=])\s*(\d)', r'\1\2\3', text)
        
        # 移除标点符号前的空格
        text = re.sub(r'\s+([。、！？：；])', r'\1', text)
        
        # 规范化连续的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除行首行尾空白
        text = text.strip()
        
        # 过滤掉过短的无意义文本
        if len(text.strip()) < 2:
            logging.warning(f"文本过短，可能识别有误: '{text}'")
        
        return text
    
    def capture_and_extract(self, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        一键截图并提取文字
        
        Args:
            region: 截图区域
            
        Returns:
            识别出的文字
        """
        # 截图
        screenshot = self.capture_screen_region(region)
        if not screenshot:
            return ""
        
        # 自动检测文字区域
        if self.config.get('screenshot.auto_detect', True):
            text_region = self.auto_detect_text_region(screenshot)
            if text_region:
                x, y, w, h = text_region
                screenshot = screenshot.crop((x, y, x + w, y + h))
        
        # 提取文字
        return self.extract_text(screenshot)
    
    def get_screen_info(self) -> Dict[str, Any]:
        """
        获取屏幕信息
        
        Returns:
            屏幕信息字典
        """
        try:
            screen_info = {}
            
            # 尝试使用pyautogui获取屏幕尺寸
            if PYAUTOGUI_AVAILABLE:
                try:
                    screen_size = pyautogui.size()
                    screen_info.update({
                        'width': screen_size.width,
                        'height': screen_size.height,
                        'method': 'pyautogui'
                    })
                except Exception as e:
                    logging.warning(f"pyautogui获取屏幕尺寸失败: {e}")
            
            # 备用方法：使用PIL
            if not screen_info and PIL_AVAILABLE:
                try:
                    # 获取全屏截图来确定屏幕尺寸
                    full_screenshot = ImageGrab.grab()
                    screen_info.update({
                        'width': full_screenshot.width,
                        'height': full_screenshot.height,
                        'method': 'PIL'
                    })
                except Exception as e:
                    logging.warning(f"PIL获取屏幕尺寸失败: {e}")
            
            # 添加当前截图区域配置
            screen_info['current_region'] = {
                'x': self.config.get('screenshot.region.x', 0),
                'y': self.config.get('screenshot.region.y', 0),
                'width': self.config.get('screenshot.region.width', 800),
                'height': self.config.get('screenshot.region.height', 600)
            }
            
            # 添加依赖状态信息
            screen_info['dependencies'] = {
                'pyautogui': PYAUTOGUI_AVAILABLE,
                'PIL': PIL_AVAILABLE,
                'opencv': CV2_AVAILABLE,
                'pytesseract': PYTESSERACT_AVAILABLE
            }
            
            # 如果无法获取屏幕尺寸，使用默认值
            if 'width' not in screen_info:
                screen_info.update({
                    'width': 1920,
                    'height': 1080,
                    'method': 'default'
                })
                logging.warning("无法获取屏幕尺寸，使用默认值 1920x1080")
            
            return screen_info
            
        except Exception as e:
            logging.error(f"获取屏幕信息失败: {e}")
            return {
                'width': 1920,
                'height': 1080,
                'method': 'fallback',
                'error': str(e)
            }
    
    def update_capture_region(self, x: int, y: int, width: int, height: int) -> None:
        """
        更新截图区域配置
        
        Args:
            x: X坐标
            y: Y坐标  
            width: 宽度
            height: 高度
        """
        self.config.update('screenshot.region.x', x)
        self.config.update('screenshot.region.y', y)
        self.config.update('screenshot.region.width', width)
        self.config.update('screenshot.region.height', height)
        
        logging.info(f"截图区域已更新: ({x}, {y}, {width}, {height})")


    def health_check(self) -> Dict[str, Any]:
        """
        OCR模块健康检查
        
        Returns:
            健康检查结果
        """
        health_status = {
            'status': 'healthy',
            'components': {},
            'recommendations': []
        }
        
        try:
            # 检查依赖包
            health_status['components']['dependencies'] = {
                'PIL': PIL_AVAILABLE,
                'pytesseract': PYTESSERACT_AVAILABLE,
                'opencv': CV2_AVAILABLE,
                'pyautogui': PYAUTOGUI_AVAILABLE
            }
            
            # 检查Tesseract
            if PYTESSERACT_AVAILABLE:
                try:
                    version = pytesseract.get_tesseract_version()
                    health_status['components']['tesseract'] = {
                        'available': True,
                        'version': str(version)
                    }
                    
                    # 检查日文语言包
                    try:
                        langs = pytesseract.get_languages(config='')
                        health_status['components']['tesseract']['languages'] = langs
                        health_status['components']['tesseract']['japanese'] = 'jpn' in langs
                        
                        if 'jpn' not in langs:
                            health_status['recommendations'].append(
                                "安装日文语言包: sudo apt-get install tesseract-ocr-jpn"
                            )
                    except Exception:
                        health_status['components']['tesseract']['languages'] = 'unknown'
                        health_status['components']['tesseract']['japanese'] = False
                        
                except Exception as e:
                    health_status['components']['tesseract'] = {
                        'available': False,
                        'error': str(e)
                    }
                    health_status['status'] = 'degraded'
            else:
                health_status['components']['tesseract'] = {'available': False}
                health_status['status'] = 'unhealthy'
                health_status['recommendations'].append("安装pytesseract: pip install pytesseract")
            
            # 检查图像处理能力
            if not PIL_AVAILABLE:
                health_status['status'] = 'unhealthy'
                health_status['recommendations'].append("安装Pillow: pip install Pillow")
            
            if not CV2_AVAILABLE:
                health_status['recommendations'].append("安装OpenCV (可选): pip install opencv-python")
            
            if not PYAUTOGUI_AVAILABLE:
                health_status['recommendations'].append("安装pyautogui (可选): pip install pyautogui")
            
            # 测试基本功能
            if PIL_AVAILABLE and PYTESSERACT_AVAILABLE:
                try:
                    # 创建测试图像
                    from PIL import Image, ImageDraw, ImageFont
                    test_img = Image.new('RGB', (200, 50), color='white')
                    draw = ImageDraw.Draw(test_img)
                    draw.text((10, 10), "テスト", fill='black')
                    
                    # 测试OCR
                    test_result = self.extract_text(test_img, preprocess=False)
                    health_status['components']['ocr_test'] = {
                        'success': bool(test_result.strip()),
                        'result': test_result
                    }
                    
                except Exception as e:
                    health_status['components']['ocr_test'] = {
                        'success': False,
                        'error': str(e)
                    }
            
            return health_status
            
        except Exception as e:
            logging.error(f"健康检查失败: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


def test_ocr_handler():
    """测试OCR处理器"""
    print("=== OCR模块测试 ===")
    
    try:
        config = ConfigManager()
        ocr = OCRHandler(config)
        
        # 健康检查
        print("\n1. 健康检查:")
        health = ocr.health_check()
        print(f"状态: {health['status']}")
        
        for component, status in health.get('components', {}).items():
            print(f"  {component}: {status}")
        
        if health.get('recommendations'):
            print("\n建议:")
            for rec in health['recommendations']:
                print(f"  - {rec}")
        
        # 获取屏幕信息
        print("\n2. 屏幕信息:")
        screen_info = ocr.get_screen_info()
        print(f"  屏幕尺寸: {screen_info.get('width', 'unknown')}x{screen_info.get('height', 'unknown')}")
        print(f"  检测方法: {screen_info.get('method', 'unknown')}")
        print(f"  当前截图区域: {screen_info.get('current_region', {})}")
        
        # 依赖状态
        print("\n3. 依赖状态:")
        deps = screen_info.get('dependencies', {})
        for dep, available in deps.items():
            status = "✓" if available else "✗"
            print(f"  {status} {dep}")
        
        # 测试截图和OCR（如果依赖都可用）
        if health['status'] in ['healthy', 'degraded']:
            print("\n4. 测试截图和OCR:")
            try:
                text = ocr.capture_and_extract()
                print(f"  识别结果: {text[:100]}{'...' if len(text) > 100 else ''}")
            except Exception as e:
                print(f"  错误: {e}")
        else:
            print("\n4. 跳过功能测试 (依赖不完整)")
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_ocr_handler()
