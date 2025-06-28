# OCR实现技术详解

## 概述

本项目采用 **Tesseract OCR** 作为核心识别引擎，专门针对日文SPI题目进行优化。通过多层图像预处理和智能区域检测，确保高精度的文字识别。

## 技术架构

### 核心依赖

```bash
# OCR引擎
tesseract-ocr
tesseract-ocr-jpn

# Python库
pytesseract>=0.3.10
Pillow>=9.0.0
opencv-python>=4.5.0
pyautogui>=0.9.53
numpy>=1.21.0
```

### 模块结构

```
OCRHandler (ocr_handler.py)
├── 屏幕截图 (capture_screen_region)
├── 区域检测 (auto_detect_text_region)
├── 图像预处理 (preprocess_for_ocr)
├── 文字识别 (extract_text)
└── 文本清理 (_clean_text)
```

## 详细实现

### 1. 屏幕截图机制

#### 截图方式
- **主要方式**: `PIL.ImageGrab.grab()` - 高效、跨平台
- **备用方式**: `pyautogui.screenshot()` - 兼容性更好
- **区域截图**: 支持指定坐标区域，减少处理量

#### 截图优化
```python
# 配置示例
{
  "screenshot": {
    "region": {
      "x": 100,        # 起始X坐标
      "y": 100,        # 起始Y坐标
      "width": 800,    # 截图宽度
      "height": 600    # 截图高度
    },
    "auto_detect": true  # 是否自动检测文字区域
  }
}
```

### 2. 智能区域检测

#### MSER算法
使用 **Maximally Stable Extremal Regions** 算法检测文字区域：

```python
# 核心代码
mser = cv2.MSER_create()
regions, _ = mser.detectRegions(gray_image)
```

#### 算法优势
- **稳定性**: 对光照变化、噪声不敏感
- **准确性**: 能精确定位文字边界
- **效率**: 计算速度快，适合实时处理

#### 区域合并策略
- 计算所有检测区域的凸包
- 合并重叠区域，形成统一边界框
- 自动添加边距，避免文字截断

### 3. 图像预处理流水线

#### 3.1 图像增强
```python
# 对比度增强
contrast_enhancer = ImageEnhance.Contrast(image)
image = contrast_enhancer.enhance(1.5)

# 锐度增强
sharpness_enhancer = ImageEnhance.Sharpness(image)
image = sharpness_enhancer.enhance(1.2)

# USM锐化
image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
```

#### 3.2 预处理步骤
1. **灰度转换**: RGB → Gray，减少数据量
2. **尺寸放大**: 2倍放大，提高小字识别率
3. **降噪处理**: 中值滤波去除椒盐噪声
4. **二值化**: 自适应阈值或OTSU算法

#### 3.3 二值化策略
```python
# 自适应阈值 (推荐)
img_binary = cv2.adaptiveThreshold(
    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
)

# OTSU自动阈值
_, img_binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

### 4. Tesseract优化配置

#### 4.1 日文识别配置
```python
config = '-l jpn --psm 6 --oem 3'  # 基础配置

# 日文优化参数
config += ' -c preserve_interword_spaces=1'  # 保持词间空格
config += ' -c tessedit_char_whitelist=...'  # 字符白名单
```

#### 4.2 PSM模式说明
- **PSM 6**: 统一文本块 (默认，适合段落)
- **PSM 8**: 单词识别 (适合单个词汇)
- **PSM 13**: 原始行，无方向检测 (适合单行文本)

#### 4.3 OEM引擎模式
- **OEM 3**: 默认，基于LSTM (推荐)
- **OEM 1**: 传统引擎
- **OEM 2**: 仅LSTM引擎

#### 4.4 日文字符集优化
包含完整的日文字符支持：
- **平假名**: あいうえお...
- **片假名**: アイウエオ...
- **浊音半浊音**: がぎぐげご、ぱぴぷぺぽ...
- **小字符**: ゃゅょっー
- **标点符号**: 。、！？（）「」...

### 5. 文本后处理

#### 5.1 噪声清理
```python
# 移除OCR常见错误字符
text = text.replace('|', '').replace('_', '')

# 标准化空白字符
text = ' '.join(text.split())
```

#### 5.2 日文格式优化
```python
# 标点符号处理
text = text.replace(' 。', '。').replace(' 、', '、')
text = text.replace('( ', '（').replace(' )', '）')
```

## 性能优化策略

### 1. 内存管理
- 及时释放大型图像对象
- 使用生成器处理批量图像
- 限制同时处理的图像数量

### 2. 速度优化
- **区域预设**: 避免每次全屏截图
- **缓存预处理**: 相似图像复用处理结果
- **并行处理**: 多线程处理多个区域

### 3. 准确性提升
- **多尺度处理**: 不同放大倍数并行识别
- **集成学习**: 多种预处理方法投票
- **字典校正**: 基于题库的后处理校正

## 环境配置

### Ubuntu/Debian系统
```bash
# 安装Tesseract
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-jpn

# 验证安装
tesseract --version
tesseract --list-langs
```

### Docker环境
```dockerfile
# Dockerfile中的配置
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-jpn \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*
```

### 常见问题解决

#### 1. Tesseract未找到
```bash
# 检查安装路径
which tesseract
# 设置环境变量
export PATH="/usr/bin:$PATH"
```

#### 2. 日文语言包缺失
```bash
# 单独安装日文包
sudo apt-get install tesseract-ocr-jpn
# 验证
tesseract --list-langs | grep jpn
```

#### 3. 权限问题
```bash
# 修改权限
sudo chmod +x /usr/bin/tesseract
# 或使用非root用户
sudo usermod -a -G sudo username
```

## 调试与监控

### 调试图像保存
```python
# 开启DEBUG模式
{
  "logging": {
    "level": "DEBUG"
  }
}
```

自动保存以下调试图像：
- `screenshot_*.png`: 原始截图
- `preprocessed_*.png`: 预处理后图像
- 保存路径: `debug_images/` 目录

### 性能监控
- **识别耗时**: 记录每次OCR执行时间
- **准确率统计**: 基于题库匹配度评估
- **错误率监控**: 识别失败案例收集

## 最佳实践

### 1. 截图区域优化
- 尽量精确框选文字区域
- 避免包含无关背景和图形
- 确保文字清晰、对比度高

### 2. 预处理参数调优
```python
# 针对不同场景的配置
{
  "high_quality": {
    "resize_factor": 3.0,
    "blur_kernel": 1,
    "threshold_type": "adaptive"
  },
  "fast_mode": {
    "resize_factor": 1.5,
    "blur_kernel": 0,
    "threshold_type": "otsu"
  }
}
```

### 3. 识别质量评估
- 设置置信度阈值
- 对低置信度结果进行二次处理
- 建立识别结果反馈机制

## 扩展方向

### 1. 深度学习集成
- 考虑集成PaddleOCR或EasyOCR
- 训练专门的SPI题目识别模型
- 使用CRNN网络提升准确率

### 2. 多模态融合
- 结合图像分割和OCR
- 表格结构化识别
- 数学公式专门处理

### 3. 自适应优化
- 基于历史数据自动调参
- 场景自动识别和配置切换
- 用户反馈学习机制
