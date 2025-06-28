#!/bin/bash

# OCR依赖检查和安装脚本
# 用于确保所有OCR相关依赖都正确安装

set -e

echo "=== SPI自动答题工具 - OCR依赖检查 ==="
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查函数
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 已安装"
        return 0
    else
        echo -e "${RED}✗${NC} $1 未安装"
        return 1
    fi
}

check_python_package() {
    if python3 -c "import $1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} Python包 $1 已安装"
        return 0
    else
        echo -e "${RED}✗${NC} Python包 $1 未安装"
        return 1
    fi
}

# 系统检查
echo -e "${BLUE}1. 系统环境检查${NC}"
echo "操作系统: $(uname -s)"
echo "架构: $(uname -m)"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "发行版: $NAME $VERSION"
fi
echo

# Python检查
echo -e "${BLUE}2. Python环境检查${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python3 未安装"
    exit 1
fi

if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo -e "${GREEN}✓${NC} $PIP_VERSION"
else
    echo -e "${RED}✗${NC} pip3 未安装"
    exit 1
fi
echo

# Tesseract检查
echo -e "${BLUE}3. Tesseract OCR检查${NC}"
TESSERACT_MISSING=false

if ! check_command tesseract; then
    TESSERACT_MISSING=true
fi

if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n1)
    echo "   版本: $TESSERACT_VERSION"
    
    echo "   检查语言包:"
    LANGS=$(tesseract --list-langs 2>/dev/null | tail -n +2)
    
    if echo "$LANGS" | grep -q "jpn"; then
        echo -e "   ${GREEN}✓${NC} 日文语言包 (jpn) 已安装"
    else
        echo -e "   ${RED}✗${NC} 日文语言包 (jpn) 未安装"
        TESSERACT_MISSING=true
    fi
    
    if echo "$LANGS" | grep -q "eng"; then
        echo -e "   ${GREEN}✓${NC} 英文语言包 (eng) 已安装"
    else
        echo -e "   ${YELLOW}⚠${NC} 英文语言包 (eng) 未安装"
    fi
fi
echo

# Python包检查
echo -e "${BLUE}4. Python依赖包检查${NC}"
PYTHON_PACKAGES_MISSING=false

REQUIRED_PACKAGES=("PIL" "pytesseract")
OPTIONAL_PACKAGES=("cv2" "numpy" "pyautogui")

echo "必需包:"
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if ! check_python_package "$pkg"; then
        PYTHON_PACKAGES_MISSING=true
    fi
done

echo "可选包:"
for pkg in "${OPTIONAL_PACKAGES[@]}"; do
    check_python_package "$pkg" || true
done
echo

# 显示安装建议
if [ "$TESSERACT_MISSING" = true ] || [ "$PYTHON_PACKAGES_MISSING" = true ]; then
    echo -e "${YELLOW}5. 安装建议${NC}"
    
    if [ "$TESSERACT_MISSING" = true ]; then
        echo -e "${YELLOW}安装Tesseract OCR:${NC}"
        
        if command -v apt-get &> /dev/null; then
            echo "  sudo apt-get update"
            echo "  sudo apt-get install -y tesseract-ocr tesseract-ocr-jpn"
        elif command -v yum &> /dev/null; then
            echo "  sudo yum install -y tesseract tesseract-langpack-jpn"
        elif command -v brew &> /dev/null; then
            echo "  brew install tesseract tesseract-lang"
        else
            echo "  请参考 https://tesseract-ocr.github.io/tessdoc/Installation.html"
        fi
        echo
    fi
    
    if [ "$PYTHON_PACKAGES_MISSING" = true ]; then
        echo -e "${YELLOW}安装Python依赖包:${NC}"
        echo "  pip3 install -r requirements.txt"
        echo "  或者:"
        echo "  pip3 install Pillow pytesseract opencv-python pyautogui numpy"
        echo
    fi
    
    echo -e "${YELLOW}Docker用户:${NC}"
    echo "  使用 docker-compose up 会自动安装所有依赖"
    echo
else
    echo -e "${GREEN}5. 所有依赖都已正确安装! 🎉${NC}"
fi

# 进行快速测试
echo -e "${BLUE}6. 功能测试${NC}"

if [ "$TESSERACT_MISSING" = false ] && [ "$PYTHON_PACKAGES_MISSING" = false ]; then
    echo "运行OCR模块测试..."
    
    cat > /tmp/test_ocr.py << 'EOF'
import sys
sys.path.append('.')

try:
    from ocr_handler import test_ocr_handler
    test_ocr_handler()
    print("\n✓ OCR模块测试通过")
except Exception as e:
    print(f"\n✗ OCR模块测试失败: {e}")
    sys.exit(1)
EOF
    
    if python3 /tmp/test_ocr.py; then
        echo -e "${GREEN}✓ 功能测试通过${NC}"
    else
        echo -e "${RED}✗ 功能测试失败${NC}"
    fi
    
    rm -f /tmp/test_ocr.py
else
    echo -e "${YELLOW}跳过功能测试 (依赖不完整)${NC}"
fi

echo
echo -e "${BLUE}检查完成!${NC}"

# 生成报告
REPORT_FILE="ocr_dependency_report.txt"
{
    echo "OCR依赖检查报告"
    echo "生成时间: $(date)"
    echo "=================="
    echo
    echo "系统信息:"
    echo "- 操作系统: $(uname -s)"
    echo "- 架构: $(uname -m)"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "- 发行版: $NAME $VERSION"
    fi
    echo
    echo "Python环境:"
    echo "- Python: $(python3 --version)"
    echo "- pip: $(pip3 --version)"
    echo
    echo "Tesseract状态:"
    if command -v tesseract &> /dev/null; then
        echo "- 版本: $(tesseract --version 2>&1 | head -n1)"
        echo "- 语言包: $(tesseract --list-langs 2>/dev/null | tail -n +2 | tr '\n' ' ')"
    else
        echo "- 状态: 未安装"
    fi
    echo
    echo "Python包状态:"
    for pkg in "${REQUIRED_PACKAGES[@]}" "${OPTIONAL_PACKAGES[@]}"; do
        if python3 -c "import $pkg" &> /dev/null; then
            echo "- $pkg: 已安装"
        else
            echo "- $pkg: 未安装"
        fi
    done
} > "$REPORT_FILE"

echo "详细报告已保存到: $REPORT_FILE"
