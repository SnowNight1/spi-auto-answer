#!/usr/bin/env python3
"""
Windows环境依赖检查脚本
检查SPI自动答题工具在Windows系统下的依赖安装情况
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("=== Python版本检查 ===")
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要Python 3.8+")
        return False
    else:
        print("✅ Python版本满足要求")
        return True

def check_pip():
    """检查pip是否可用"""
    print("\n=== pip检查 ===")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True, text=True)
        print("✅ pip可用")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip不可用")
        return False

def check_required_packages():
    """检查必需的Python包"""
    print("\n=== Python包依赖检查 ===")
    
    required_packages = {
        'requests': 'requests',
        'Pillow': 'PIL', 
        'pytesseract': 'pytesseract',
        'opencv-python': 'cv2',
        'pandas': 'pandas',
        'openpyxl': 'openpyxl',
        'fuzzywuzzy': 'fuzzywuzzy',
        'keyboard': 'keyboard',
        'pyautogui': 'pyautogui',
        'numpy': 'numpy'
    }
    
    installed = []
    missing = []
    
    for package_name, import_name in required_packages.items():
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name}")
            installed.append(package_name)
        except ImportError:
            print(f"❌ {package_name}")
            missing.append(package_name)
    
    print(f"\n已安装: {len(installed)}/{len(required_packages)}")
    
    if missing:
        print(f"\n缺失的包: {', '.join(missing)}")
        print(f"安装命令: pip install {' '.join(missing)}")
    
    return len(missing) == 0

def check_tesseract():
    """检查Tesseract OCR"""
    print("\n=== Tesseract OCR检查 ===")
    
    # 常见的Windows Tesseract路径
    possible_paths = [
        "tesseract",  # 在PATH中
        "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
        "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe",
        "C:\\Tesseract-OCR\\tesseract.exe"
    ]
    
    tesseract_found = False
    tesseract_path = None
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                tesseract_found = True
                tesseract_path = path
                version = result.stdout.split('\n')[0]
                print(f"✅ Tesseract找到: {path}")
                print(f"   版本: {version}")
                break
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    if not tesseract_found:
        print("❌ Tesseract OCR未找到")
        print("   下载地址: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   安装时请选择日文语言包")
        return False
    
    # 检查语言包
    try:
        if tesseract_path:
            result = subprocess.run([tesseract_path, "--list-langs"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                langs = result.stdout.lower()
                if 'jpn' in langs:
                    print("✅ 日文语言包已安装")
                else:
                    print("⚠️  日文语言包未安装")
                    print("   请重新安装Tesseract并选择日文语言包")
    except Exception as e:
        print(f"⚠️  无法检查语言包: {e}")
    
    return True

def check_config_file():
    """检查配置文件"""
    print("\n=== 配置文件检查 ===")
    
    config_path = Path("config.json")
    if config_path.exists():
        print("✅ config.json存在")
        
        # 简单检查配置文件内容
        try:
            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 检查关键配置项
            api_key = config.get('api', {}).get('api_key', '')
            api_endpoint = config.get('api', {}).get('api_endpoint', '')
            
            if api_key and api_key != 'YOUR_AZURE_OPENAI_API_KEY':
                print("✅ API密钥已配置")
            else:
                print("⚠️  API密钥未配置或使用默认值")
            
            if api_endpoint and api_endpoint != 'YOUR_AZURE_OPENAI_ENDPOINT':
                print("✅ API端点已配置")
            else:
                print("⚠️  API端点未配置或使用默认值")
                
        except Exception as e:
            print(f"⚠️  配置文件格式错误: {e}")
    else:
        print("❌ config.json不存在")
        print("   请从config.json.example复制并编辑")
        return False
    
    return True

def check_windows_admin():
    """检查是否以管理员权限运行"""
    print("\n=== Windows权限检查 ===")
    
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if is_admin:
            print("✅ 当前以管理员权限运行")
        else:
            print("⚠️  当前非管理员权限")
            print("   热键功能需要管理员权限")
            print("   请右键命令提示符 -> 以管理员身份运行")
        return is_admin
    except Exception:
        print("⚠️  无法检查管理员权限")
        return False

def generate_report(results):
    """生成检查报告"""
    print("\n" + "="*50)
    print("           依赖检查报告")
    print("="*50)
    
    all_passed = True
    
    for check_name, (passed, message) in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{check_name:<20} {status}")
        if message and not passed:
            print(f"{'':>22} {message}")
        all_passed = all_passed and passed
    
    print("="*50)
    
    if all_passed:
        print("🎉 所有检查通过！系统准备就绪")
        print("\n下一步:")
        print("1. python main.py --test-api  # 测试API连接")
        print("2. python main.py --test-ocr  # 测试OCR功能") 
        print("3. python main.py             # 启动程序")
    else:
        print("⚠️  部分检查失败，请解决上述问题后重试")
        print("\n建议:")
        print("1. 运行 scripts/windows_setup.bat 进行自动安装")
        print("2. 手动安装缺失的依赖")
        print("3. 配置API密钥和端点")

def main():
    """主函数"""
    print("Windows环境依赖检查工具")
    print("=" * 50)
    
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    results = {}
    
    # 执行各项检查
    results["Python版本"] = (check_python_version(), "需要Python 3.8+")
    results["pip可用性"] = (check_pip(), "pip未安装或不可用")
    results["Python包"] = (check_required_packages(), "部分必需包未安装")
    results["Tesseract OCR"] = (check_tesseract(), "OCR引擎未安装")
    results["配置文件"] = (check_config_file(), "配置文件缺失或配置不完整")
    results["管理员权限"] = (check_windows_admin(), "非管理员权限，热键功能受限")
    
    # 生成报告
    generate_report(results)

if __name__ == "__main__":
    main()
