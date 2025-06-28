#!/bin/bash

# OCR配置优化脚本
# 根据系统环境和用户需求优化OCR配置

set -e

echo "=== SPI自动答题工具 - OCR配置优化 ==="
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CONFIG_FILE="config.json"
CONFIG_TEMPLATE="config.json.template"

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    if [ -f "$CONFIG_TEMPLATE" ]; then
        echo "复制配置模板..."
        cp "$CONFIG_TEMPLATE" "$CONFIG_FILE"
    else
        echo -e "${RED}错误: 找不到配置文件和模板${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}1. 检测系统性能${NC}"

# 检测CPU核心数
CPU_CORES=$(nproc)
echo "CPU核心数: $CPU_CORES"

# 检测内存
if command -v free &> /dev/null; then
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    echo "系统内存: ${MEMORY_GB}GB"
else
    MEMORY_GB=4  # 默认值
    echo "无法检测内存，使用默认值: ${MEMORY_GB}GB"
fi

# 检测显卡
if command -v nvidia-smi &> /dev/null; then
    echo "检测到NVIDIA显卡"
    GPU_AVAILABLE=true
else
    echo "未检测到NVIDIA显卡"
    GPU_AVAILABLE=false
fi

echo

echo -e "${BLUE}2. 检测Tesseract性能${NC}"

# 测试Tesseract性能
if command -v tesseract &> /dev/null; then
    # 创建测试图像
    python3 << 'EOF'
from PIL import Image, ImageDraw, ImageFont
import time

# 创建测试图像
img = Image.new('RGB', (400, 100), color='white')
draw = ImageDraw.Draw(img)

# 绘制日文测试文本
test_text = "これはテストです。SPI問題を解決します。"
draw.text((10, 30), test_text, fill='black')

# 保存测试图像
img.save('/tmp/ocr_test.png')
print("测试图像已创建")
EOF
    
    echo "测试OCR性能..."
    START_TIME=$(date +%s.%N)
    tesseract /tmp/ocr_test.png /tmp/ocr_result -l jpn > /dev/null 2>&1
    END_TIME=$(date +%s.%N)
    
    OCR_TIME=$(echo "$END_TIME - $START_TIME" | bc)
    echo "OCR处理时间: ${OCR_TIME}秒"
    
    # 清理测试文件
    rm -f /tmp/ocr_test.png /tmp/ocr_result.txt
else
    echo -e "${YELLOW}Tesseract未安装，跳过性能测试${NC}"
    OCR_TIME=1.0
fi

echo

echo -e "${BLUE}3. 生成优化配置${NC}"

# 根据系统性能生成配置
if (( $(echo "$OCR_TIME < 0.5" | bc -l) )); then
    PERFORMANCE_LEVEL="high"
    echo "系统性能: 高"
elif (( $(echo "$OCR_TIME < 1.0" | bc -l) )); then
    PERFORMANCE_LEVEL="medium"
    echo "系统性能: 中"
else
    PERFORMANCE_LEVEL="low"
    echo "系统性能: 低"
fi

# 生成优化配置
python3 << EOF
import json
import sys

# 读取当前配置
try:
    with open('$CONFIG_FILE', 'r', encoding='utf-8') as f:
        config = json.load(f)
except:
    config = {}

# 确保OCR配置存在
if 'ocr' not in config:
    config['ocr'] = {}

# 根据性能级别设置参数
performance = '$PERFORMANCE_LEVEL'
memory_gb = $MEMORY_GB
cpu_cores = $CPU_CORES

if performance == 'high':
    # 高性能配置
    config['ocr']['preprocess'] = {
        'resize_factor': 3.0,
        'blur_kernel': 1,
        'threshold_type': 'adaptive'
    }
    config['ocr']['psm'] = 6
    config['ocr']['oem'] = 3
    config['ocr']['use_whitelist'] = True
    config['screenshot']['auto_detect'] = True
    
elif performance == 'medium':
    # 中等性能配置
    config['ocr']['preprocess'] = {
        'resize_factor': 2.0,
        'blur_kernel': 1,
        'threshold_type': 'adaptive'
    }
    config['ocr']['psm'] = 6
    config['ocr']['oem'] = 3
    config['ocr']['use_whitelist'] = True
    config['screenshot']['auto_detect'] = True
    
else:
    # 低性能配置
    config['ocr']['preprocess'] = {
        'resize_factor': 1.5,
        'blur_kernel': 0,
        'threshold_type': 'otsu'
    }
    config['ocr']['psm'] = 8
    config['ocr']['oem'] = 1
    config['ocr']['use_whitelist'] = False
    config['screenshot']['auto_detect'] = False

# 根据内存调整缓存设置
if memory_gb >= 8:
    config['performance'] = {
        'cache_size': 100,
        'parallel_processing': True,
        'max_workers': min(cpu_cores, 4)
    }
elif memory_gb >= 4:
    config['performance'] = {
        'cache_size': 50,
        'parallel_processing': True,
        'max_workers': min(cpu_cores, 2)
    }
else:
    config['performance'] = {
        'cache_size': 20,
        'parallel_processing': False,
        'max_workers': 1
    }

# 保存优化后的配置
with open('$CONFIG_FILE', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print("配置已优化")
EOF

echo

echo -e "${BLUE}4. 配置说明${NC}"
echo "根据您的系统性能，已应用以下优化:"

case $PERFORMANCE_LEVEL in
    "high")
        echo "- 图像放大倍数: 3.0x (高质量)"
        echo "- 预处理模式: 自适应阈值"
        echo "- OCR模式: PSM 6 (段落模式)"
        echo "- 自动区域检测: 启用"
        ;;
    "medium")
        echo "- 图像放大倍数: 2.0x (平衡)"
        echo "- 预处理模式: 自适应阈值"
        echo "- OCR模式: PSM 6 (段落模式)"
        echo "- 自动区域检测: 启用"
        ;;
    "low")
        echo "- 图像放大倍数: 1.5x (性能优先)"
        echo "- 预处理模式: OTSU阈值"
        echo "- OCR模式: PSM 8 (单词模式)"
        echo "- 自动区域检测: 禁用"
        ;;
esac

echo
echo "内存优化:"
echo "- 缓存大小: $(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['performance']['cache_size'])")"
echo "- 并行处理: $(python3 -c "import json; print('启用' if json.load(open('$CONFIG_FILE'))['performance']['parallel_processing'] else '禁用')")"
echo "- 工作线程: $(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['performance']['max_workers'])")"

echo
echo -e "${BLUE}5. 性能调优建议${NC}"

if [ "$PERFORMANCE_LEVEL" = "low" ]; then
    echo -e "${YELLOW}建议:${NC}"
    echo "- 关闭其他应用程序以释放系统资源"
    echo "- 考虑升级硬件以获得更好的性能"
    echo "- 使用较小的截图区域减少处理量"
fi

if [ "$MEMORY_GB" -lt 4 ]; then
    echo -e "${YELLOW}内存不足警告:${NC}"
    echo "- 系统内存不足4GB，可能影响性能"
    echo "- 建议增加虚拟内存或升级RAM"
fi

echo
echo -e "${GREEN}6. 配置优化完成! 🎉${NC}"
echo "优化后的配置已保存到: $CONFIG_FILE"
echo
echo "您可以运行以下命令测试优化效果:"
echo "  python3 -c \"from ocr_handler import test_ocr_handler; test_ocr_handler()\""

# 创建性能基准测试脚本
cat > ocr_benchmark.py << 'EOF'
#!/usr/bin/env python3
"""
OCR性能基准测试
"""

import time
from utils import ConfigManager
from ocr_handler import OCRHandler
from PIL import Image, ImageDraw

def create_test_image():
    """创建测试图像"""
    img = Image.new('RGB', (800, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # 日文测试文本
    texts = [
        "これはSPI問題のテストです。",
        "数学的能力を測定します。",
        "正解を選択してください。",
        "A) 選択肢1  B) 選択肢2  C) 選択肢3"
    ]
    
    y = 20
    for text in texts:
        draw.text((20, y), text, fill='black')
        y += 40
    
    return img

def benchmark_ocr():
    """OCR性能基准测试"""
    print("=== OCR性能基准测试 ===")
    
    config = ConfigManager()
    ocr = OCRHandler(config)
    
    # 创建测试图像
    test_image = create_test_image()
    
    # 预热
    print("预热中...")
    ocr.extract_text(test_image, preprocess=False)
    
    # 基准测试
    tests = [
        ("无预处理", False),
        ("完整预处理", True)
    ]
    
    for test_name, preprocess in tests:
        print(f"\n测试: {test_name}")
        
        times = []
        for i in range(5):
            start_time = time.time()
            result = ocr.extract_text(test_image, preprocess=preprocess)
            end_time = time.time()
            
            elapsed = end_time - start_time
            times.append(elapsed)
            print(f"  第{i+1}次: {elapsed:.3f}秒")
        
        avg_time = sum(times) / len(times)
        print(f"  平均时间: {avg_time:.3f}秒")
        print(f"  识别结果长度: {len(result)}字符")

if __name__ == "__main__":
    benchmark_ocr()
EOF

chmod +x ocr_benchmark.py

echo
echo "性能基准测试脚本已创建: ocr_benchmark.py"
echo "运行 python3 ocr_benchmark.py 来测试OCR性能"
