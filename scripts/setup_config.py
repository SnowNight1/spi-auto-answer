#!/usr/bin/env python3
"""
Windows快速配置脚本
帮助用户快速配置SPI自动答题工具
"""

import json
import os
import sys
from pathlib import Path

def load_config():
    """加载现有配置"""
    config_path = Path("config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return None
    return None

def save_config(config):
    """保存配置"""
    try:
        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("✅ 配置已保存到 config.json")
        return True
    except Exception as e:
        print(f"❌ 保存配置失败: {e}")
        return False

def get_default_config():
    """获取默认配置"""
    return {
        "api": {
            "api_key": "YOUR_AZURE_OPENAI_API_KEY",
            "api_endpoint": "YOUR_AZURE_OPENAI_ENDPOINT",
            "api_version": "2024-02-01",
            "deployment_name": "gpt-4",
            "max_tokens": 500,
            "temperature": 0.3
        },
        "ocr": {
            "language": "jpn",
            "psm": 6,
            "oem": 3,
            "tesseract_cmd": "tesseract",
            "use_whitelist": True
        },
        "screenshot": {
            "region": {
                "x": 0,
                "y": 0,
                "width": 800,
                "height": 600
            },
            "auto_detect": True
        },
        "excel": {
            "file_path": "questions.xlsx",
            "sheets": ["Sheet1"],
            "question_column": "问题",
            "answer_column": "答案",
            "similarity_threshold": 0.8
        },
        "hotkey": {
            "trigger_key": "F12",
            "exit_key": "F11"
        },
        "gui": {
            "transparency": 0.9,
            "auto_hide_delay": 10,
            "position": {
                "x": 100,
                "y": 100
            }
        },
        "logging": {
            "level": "INFO",
            "file": "spi_auto_answer.log",
            "max_size_mb": 10
        }
    }

def configure_api():
    """配置API设置"""
    print("\n=== API配置 ===")
    print("请输入您的Azure OpenAI配置信息：")
    
    api_key = input("API密钥 (api_key): ").strip()
    if not api_key:
        print("❌ API密钥不能为空")
        return None
    
    api_endpoint = input("API端点 (api_endpoint): ").strip()
    if not api_endpoint:
        print("❌ API端点不能为空")
        return None
    
    # 可选配置
    deployment_name = input("部署名称 (deployment_name) [默认: gpt-4]: ").strip()
    if not deployment_name:
        deployment_name = "gpt-4"
    
    api_version = input("API版本 (api_version) [默认: 2024-02-01]: ").strip()
    if not api_version:
        api_version = "2024-02-01"
    
    return {
        "api_key": api_key,
        "api_endpoint": api_endpoint,
        "deployment_name": deployment_name,
        "api_version": api_version,
        "max_tokens": 500,
        "temperature": 0.3
    }

def configure_tesseract():
    """配置Tesseract路径"""
    print("\n=== Tesseract配置 ===")
    
    # Windows常见路径
    common_paths = [
        "tesseract",
        "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
        "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
    ]
    
    print("常见Tesseract路径:")
    for i, path in enumerate(common_paths, 1):
        print(f"{i}. {path}")
    
    choice = input(f"请选择路径 (1-{len(common_paths)}) 或输入自定义路径: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(common_paths):
        tesseract_cmd = common_paths[int(choice) - 1]
    else:
        tesseract_cmd = choice if choice else "tesseract"
    
    # 测试路径
    try:
        import subprocess
        result = subprocess.run([tesseract_cmd, "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Tesseract路径有效: {tesseract_cmd}")
            return tesseract_cmd
        else:
            print(f"⚠️  Tesseract路径可能无效: {tesseract_cmd}")
            return tesseract_cmd
    except Exception as e:
        print(f"⚠️  无法测试Tesseract路径: {e}")
        return tesseract_cmd

def configure_hotkeys():
    """配置热键"""
    print("\n=== 热键配置 ===")
    
    trigger_key = input("触发键 [默认: F12]: ").strip()
    if not trigger_key:
        trigger_key = "F12"
    
    exit_key = input("退出键 [默认: F11]: ").strip()
    if not exit_key:
        exit_key = "F11"
    
    return {
        "trigger_key": trigger_key,
        "exit_key": exit_key
    }

def configure_screenshot():
    """配置截图区域"""
    print("\n=== 截图区域配置 ===")
    print("请输入截图区域坐标 (留空使用默认值):")
    
    try:
        x = input("X坐标 [默认: 0]: ").strip()
        x = int(x) if x else 0
        
        y = input("Y坐标 [默认: 0]: ").strip()
        y = int(y) if y else 0
        
        width = input("宽度 [默认: 800]: ").strip()
        width = int(width) if width else 800
        
        height = input("高度 [默认: 600]: ").strip()
        height = int(height) if height else 600
        
        return {
            "region": {
                "x": x,
                "y": y,
                "width": width,
                "height": height
            },
            "auto_detect": True
        }
    except ValueError:
        print("⚠️  输入格式错误，使用默认值")
        return {
            "region": {
                "x": 0,
                "y": 0,
                "width": 800,
                "height": 600
            },
            "auto_detect": True
        }

def interactive_setup():
    """交互式配置"""
    print("SPI自动答题工具 - Windows配置向导")
    print("=" * 50)
    
    # 检查是否已有配置
    existing_config = load_config()
    if existing_config:
        print("检测到现有配置文件")
        overwrite = input("是否覆盖现有配置? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("配置取消")
            return False
    
    # 开始配置
    config = get_default_config()
    
    print("\n开始配置向导...")
    print("注意: 必需配置 API 设置，其他设置可以跳过使用默认值")
    
    # API配置 (必需)
    api_config = configure_api()
    if not api_config:
        print("❌ API配置失败，配置终止")
        return False
    config["api"].update(api_config)
    
    # 询问是否配置其他选项
    configure_optional = input("\n是否配置其他选项? (y/N): ").strip().lower()
    
    if configure_optional == 'y':
        # Tesseract配置
        tesseract_cmd = configure_tesseract()
        config["ocr"]["tesseract_cmd"] = tesseract_cmd
        
        # 热键配置
        hotkey_config = configure_hotkeys()
        config["hotkey"].update(hotkey_config)
        
        # 截图配置
        screenshot_config = configure_screenshot()
        config["screenshot"].update(screenshot_config)
    
    # 保存配置
    if save_config(config):
        print("\n🎉 配置完成!")
        print("\n下一步:")
        print("1. python main.py --test-api    # 测试API连接")
        print("2. python main.py --test-ocr    # 测试OCR功能")
        print("3. python main.py               # 启动程序")
        return True
    else:
        print("❌ 配置保存失败")
        return False

def quick_api_setup():
    """快速API配置"""
    print("快速API配置模式")
    print("=" * 30)
    
    config = load_config()
    if not config:
        config = get_default_config()
    
    api_config = configure_api()
    if api_config:
        config["api"].update(api_config)
        if save_config(config):
            print("✅ API配置已保存")
            return True
    
    print("❌ API配置失败")
    return False

def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--api-only":
            quick_api_setup()
            return
        elif sys.argv[1] == "--help":
            print("用法:")
            print("  python setup_config.py          # 完整配置向导")
            print("  python setup_config.py --api-only  # 仅配置API")
            print("  python setup_config.py --help      # 显示帮助")
            return
    
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    interactive_setup()

if __name__ == "__main__":
    main()
