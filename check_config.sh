#!/bin/bash

# 配置文件检查脚本
# 验证config.json的完整性和正确性

echo "SPI自动答题工具配置检查器"
echo "=========================="
echo ""

# 检查配置文件是否存在
if [ ! -f "config.json" ]; then
    echo "❌ 错误: config.json 文件不存在"
    echo ""
    echo "解决方案:"
    echo "1. 运行配置向导: ./setup_config.sh"
    echo "2. 或复制模板: cp config.json.template config.json"
    exit 1
fi

echo "📄 发现配置文件: config.json"
echo ""

# 使用Python检查配置
python3 << 'EOF'
import json
import sys
import os
from urllib.parse import urlparse

def check_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False
    
    print("✅ JSON格式正确")
    errors = []
    warnings = []
    
    # 检查API配置
    print("\n🔍 检查API配置...")
    api_config = config.get('api', {})
    
    api_key = api_config.get('api_key', '')
    if not api_key or api_key == 'YOUR_AZURE_OPENAI_API_KEY':
        errors.append("API密钥未配置或使用默认值")
    elif len(api_key) < 32:
        warnings.append("API密钥长度过短，可能不正确")
    else:
        print("  ✅ API密钥已配置")
    
    api_endpoint = api_config.get('api_endpoint', '')
    if not api_endpoint:
        errors.append("API端点未配置")
    else:
        try:
            parsed = urlparse(api_endpoint)
            if not parsed.scheme or not parsed.netloc:
                errors.append("API端点格式不正确")
            elif not api_endpoint.endswith('/'):
                warnings.append("API端点建议以'/'结尾")
            else:
                print("  ✅ API端点格式正确")
        except:
            errors.append("API端点格式无效")
    
    deployment_name = api_config.get('deployment_name', '')
    if not deployment_name:
        errors.append("部署名称未配置")
    else:
        print(f"  ✅ 部署名称: {deployment_name}")
    
    # 检查OCR配置
    print("\n🔍 检查OCR配置...")
    ocr_config = config.get('ocr', {})
    
    language = ocr_config.get('language', '')
    if language != 'jpn':
        warnings.append(f"OCR语言设置为'{language}'，推荐使用'jpn'")
    else:
        print("  ✅ OCR语言配置正确")
    
    psm = ocr_config.get('psm', 6)
    if not isinstance(psm, int) or psm < 0 or psm > 13:
        warnings.append(f"PSM值'{psm}'可能不正确，建议使用6")
    
    # 检查热键配置
    print("\n🔍 检查热键配置...")
    hotkey_config = config.get('hotkey', {})
    
    trigger_key = hotkey_config.get('trigger_key', '')
    if not trigger_key:
        errors.append("触发热键未配置")
    else:
        print(f"  ✅ 触发热键: {trigger_key}")
    
    exit_key = hotkey_config.get('exit_key', '')
    if not exit_key:
        warnings.append("退出热键未配置")
    else:
        print(f"  ✅ 退出热键: {exit_key}")
    
    # 检查Excel配置
    print("\n🔍 检查Excel配置...")
    excel_config = config.get('excel', {})
    
    excel_file = excel_config.get('file_path', 'questions.xlsx')
    if not os.path.exists(excel_file):
        warnings.append(f"Excel文件不存在: {excel_file}")
    else:
        print(f"  ✅ Excel文件存在: {excel_file}")
    
    sheets_config = excel_config.get('sheets_config', {})
    if not sheets_config:
        errors.append("Excel sheets配置为空")
    else:
        print(f"  ✅ 配置了 {len(sheets_config)} 个sheets")
        
        for sheet_name, sheet_config in sheets_config.items():
            if not sheet_config.get('question_column'):
                warnings.append(f"Sheet '{sheet_name}' 缺少题目列配置")
            if not sheet_config.get('answer_columns'):
                warnings.append(f"Sheet '{sheet_name}' 缺少选项列配置")
            if not sheet_config.get('correct_answer_column'):
                warnings.append(f"Sheet '{sheet_name}' 缺少答案列配置")
    
    # 检查GUI配置
    print("\n🔍 检查GUI配置...")
    gui_config = config.get('gui', {})
    
    window_config = gui_config.get('window', {})
    alpha = window_config.get('alpha', 0.9)
    if not 0.1 <= alpha <= 1.0:
        warnings.append(f"窗口透明度'{alpha}'超出范围，建议0.1-1.0")
    
    # 检查截图配置
    print("\n🔍 检查截图配置...")
    screenshot_config = config.get('screenshot', {})
    region = screenshot_config.get('region', {})
    
    width = region.get('width', 800)
    height = region.get('height', 600)
    if width <= 0 or height <= 0:
        errors.append("截图区域尺寸无效")
    elif width > 3840 or height > 2160:
        warnings.append("截图区域过大，可能影响性能")
    
    # 总结
    print("\n" + "="*50)
    if errors:
        print("❌ 发现严重错误:")
        for error in errors:
            print(f"   • {error}")
        print("\n❗ 请修复这些错误后再启动程序")
        return False
    
    if warnings:
        print("⚠️  发现警告:")
        for warning in warnings:
            print(f"   • {warning}")
        print("\n💡 建议修复这些警告以获得更好的体验")
    
    if not errors and not warnings:
        print("🎉 配置文件完美无缺!")
    elif not errors:
        print("✅ 配置文件可以使用，但建议优化警告项")
    
    return True

if __name__ == "__main__":
    success = check_config()
    sys.exit(0 if success else 1)
EOF

check_result=$?

echo ""
echo "检查完成!"
echo ""

if [ $check_result -eq 0 ]; then
    echo "📋 下一步操作:"
    echo "1. 运行部署脚本: ./deploy.sh"
    echo "2. 查看详细文档: README.md"
    echo "3. 配置问题参考: CONFIG_GUIDE.md"
else
    echo "🔧 修复建议:"
    echo "1. 重新运行配置向导: ./setup_config.sh"
    echo "2. 手动编辑配置文件: nano config.json"
    echo "3. 参考配置模板: config.json.template"
    echo "4. 查看详细说明: CONFIG_GUIDE.md"
fi

echo ""
echo "💡 提示: 运行 ./setup_config.sh 可以重新配置"
