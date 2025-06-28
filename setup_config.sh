#!/bin/bash

# SPI自动答题工具配置向导
# 帮助用户快速配置config.json文件

set -e

echo "SPI自动答题工具配置向导"
echo "========================"
echo ""

# 检查是否已存在配置文件
if [ -f "config.json" ]; then
    echo "检测到已存在的config.json文件"
    read -p "是否要重新配置? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "配置取消"
        exit 0
    fi
    
    # 备份现有配置
    cp config.json config.json.backup.$(date +%Y%m%d_%H%M%S)
    echo "已备份现有配置文件"
fi

# 从模板创建配置文件
if [ -f "config.json.template" ]; then
    cp config.json.template config.json
else
    echo "错误: 找不到配置模板文件 config.json.template"
    exit 1
fi

echo "开始配置向导..."
echo ""

# API配置
echo "=== 1. Azure OpenAI API配置 ==="
echo "请访问 https://portal.azure.com 获取以下信息："
echo ""

read -p "请输入Azure OpenAI API密钥: " api_key
if [ -z "$api_key" ]; then
    echo "错误: API密钥不能为空"
    exit 1
fi

read -p "请输入API端点 (例: https://myai.openai.azure.com/): " api_endpoint
if [ -z "$api_endpoint" ]; then
    echo "错误: API端点不能为空"
    exit 1
fi

# 确保端点以斜杠结尾
if [[ ! "$api_endpoint" =~ /$ ]]; then
    api_endpoint="${api_endpoint}/"
fi

read -p "请输入部署名称 (默认: gpt-4): " deployment_name
deployment_name=${deployment_name:-gpt-4}

read -p "请输入模型名称 (默认: gpt-4): " model_name
model_name=${model_name:-gpt-4}

# 更新API配置
python3 -c "
import json
import sys

try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    config['api']['api_key'] = '$api_key'
    config['api']['api_endpoint'] = '$api_endpoint'
    config['api']['deployment_name'] = '$deployment_name'
    config['api']['model'] = '$model_name'
    
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print('API配置已更新')
except Exception as e:
    print(f'更新配置失败: {e}')
    sys.exit(1)
"

echo ""
echo "=== 2. 热键配置 ==="
echo "当前默认设置: F12触发, F11退出"
read -p "是否修改热键配置? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "请输入触发键 (默认: F12): " trigger_key
    trigger_key=${trigger_key:-F12}
    
    read -p "请输入退出键 (默认: F11): " exit_key
    exit_key=${exit_key:-F11}
    
    # 更新热键配置
    python3 -c "
import json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
config['hotkey']['trigger_key'] = '$trigger_key'
config['hotkey']['exit_key'] = '$exit_key'
with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
print('热键配置已更新')
"
fi

echo ""
echo "=== 3. Excel题库配置 ==="
echo "当前配置支持以下题库格式:"
echo "  - 数学问题: A列题目, B-E列选项, F列答案"
echo "  - 语言问题: A列题目, B-D列选项, E列答案"  
echo "  - 逻辑问题: 题目列, 选项A-D列, 正确答案列"
echo ""

read -p "Excel题库文件名 (默认: questions.xlsx): " excel_file
excel_file=${excel_file:-questions.xlsx}

# 更新Excel配置
python3 -c "
import json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
config['excel']['file_path'] = '$excel_file'
with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
print('Excel配置已更新')
"

read -p "是否需要自定义sheet配置? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "请编辑config.json文件中的excel.sheets_config部分"
    echo "详细说明请参考CONFIG_GUIDE.md文件"
fi

echo ""
echo "=== 4. 截图区域配置 ==="
echo "当前默认截图区域: 0,0,800,600 (左上角800x600区域)"
read -p "是否修改截图区域? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "请输入X坐标 (默认: 0): " screenshot_x
    screenshot_x=${screenshot_x:-0}
    
    read -p "请输入Y坐标 (默认: 0): " screenshot_y
    screenshot_y=${screenshot_y:-0}
    
    read -p "请输入宽度 (默认: 800): " screenshot_width
    screenshot_width=${screenshot_width:-800}
    
    read -p "请输入高度 (默认: 600): " screenshot_height
    screenshot_height=${screenshot_height:-600}
    
    # 更新截图配置
    python3 -c "
import json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
config['screenshot']['region']['x'] = int('$screenshot_x')
config['screenshot']['region']['y'] = int('$screenshot_y')
config['screenshot']['region']['width'] = int('$screenshot_width')
config['screenshot']['region']['height'] = int('$screenshot_height')
with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
print('截图配置已更新')
"
fi

echo ""
echo "=== 5. GUI主题配置 ==="
echo "请选择悬浮窗口主题:"
echo "1) 经典绿色 (黑底绿字)"
echo "2) 深色主题 (深灰底白字)"
echo "3) 浅色主题 (白底黑字)"
echo "4) 保持默认"

read -p "请选择主题 (1-4, 默认: 1): " theme_choice
theme_choice=${theme_choice:-1}

case $theme_choice in
    1)
        bg_color="#000000"
        text_color="#00FF00"
        border_color="#FFFFFF"
        ;;
    2)
        bg_color="#2b2b2b"
        text_color="#ffffff"
        border_color="#555555"
        ;;
    3)
        bg_color="#ffffff"
        text_color="#000000"
        border_color="#cccccc"
        ;;
    *)
        echo "保持默认主题"
        bg_color=""
        ;;
esac

if [ -n "$bg_color" ]; then
    python3 -c "
import json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
config['gui']['colors']['background'] = '$bg_color'
config['gui']['colors']['text'] = '$text_color'
config['gui']['colors']['border'] = '$border_color'
with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
print('主题配置已更新')
"
fi

echo ""
echo "=== 配置完成 ==="

# 验证配置文件
echo "正在验证配置文件..."
python3 -c "
import json
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 基本验证
    required_keys = ['api.api_key', 'api.api_endpoint']
    missing = []
    
    for key in required_keys:
        keys = key.split('.')
        value = config
        for k in keys:
            value = value.get(k, {})
        if not value or value in ['YOUR_AZURE_OPENAI_API_KEY']:
            missing.append(key)
    
    if missing:
        print(f'警告: 以下配置项需要检查: {missing}')
    else:
        print('配置文件验证通过!')
        
except Exception as e:
    print(f'配置文件验证失败: {e}')
"

echo ""
echo "配置文件已保存到: config.json"
echo ""
echo "下一步:"
echo "1. 确保Excel题库文件存在: $excel_file"
echo "2. 运行部署脚本: ./deploy.sh"
echo "3. 查看详细配置说明: CONFIG_GUIDE.md"
echo ""
echo "如需修改配置，可以:"
echo "- 重新运行此脚本: ./setup_config.sh"
echo "- 直接编辑: config.json"
echo "- 参考文档: CONFIG_GUIDE.md"
