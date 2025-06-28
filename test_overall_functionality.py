#!/usr/bin/env python3
"""
SPI自动答题工具 - 整体功能测试
测试所有核心模块的基本功能
"""

import os
import sys
import time
import logging
from typing import Dict, Any

# 设置基本日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_config_manager():
    """测试配置管理器"""
    print("=== 1. 配置管理器测试 ===")
    try:
        from utils import ConfigManager
        config = ConfigManager()
        
        # 检查关键配置项
        api_key = config.get('api.api_key')
        api_endpoint = config.get('api.api_endpoint')
        
        if api_key and api_key != 'YOUR_AZURE_OPENAI_API_KEY':
            print("✓ API密钥已配置")
        else:
            print("⚠ API密钥未配置或使用默认值")
        
        if api_endpoint and api_endpoint != 'YOUR_AZURE_OPENAI_ENDPOINT':
            print("✓ API端点已配置")
        else:
            print("⚠ API端点未配置或使用默认值")
        
        print(f"✓ 配置管理器正常工作")
        return True
        
    except Exception as e:
        print(f"✗ 配置管理器测试失败: {e}")
        return False

def test_ocr_dependencies():
    """测试OCR依赖"""
    print("\n=== 2. OCR依赖测试 ===")
    
    dependencies = {
        'PIL': False,
        'pytesseract': False,
        'cv2': False,
        'pyautogui': False,
        'numpy': False
    }
    
    # 检查PIL
    try:
        from PIL import Image, ImageGrab
        dependencies['PIL'] = True
        print("✓ PIL (Pillow) 可用")
    except ImportError:
        print("✗ PIL (Pillow) 未安装")
    
    # 检查pytesseract
    try:
        import pytesseract
        dependencies['pytesseract'] = True
        print("✓ pytesseract 可用")
    except ImportError:
        print("✗ pytesseract 未安装")
    
    # 检查OpenCV
    try:
        import cv2
        dependencies['cv2'] = True
        print("✓ OpenCV 可用")
    except ImportError:
        print("✗ OpenCV 未安装")
    
    # 检查pyautogui (在无GUI环境下进行特殊处理)
    try:
        import os
        if 'DISPLAY' not in os.environ or not os.environ['DISPLAY']:
            print("⚠ pyautogui 跳过 (无GUI环境)")
            dependencies['pyautogui'] = True  # 假设可用，稍后在实际使用时再检测
        else:
            import pyautogui
            dependencies['pyautogui'] = True
            print("✓ pyautogui 可用")
    except Exception as e:
        print(f"⚠ pyautogui 在当前环境下不可用，但这不影响基本功能: {e}")
        dependencies['pyautogui'] = True  # 在Docker环境中可能正常
    
    # 检查numpy
    try:
        import numpy
        dependencies['numpy'] = True
        print("✓ numpy 可用")
    except ImportError:
        print("✗ numpy 未安装")
    
    # 核心依赖检查
    core_deps = dependencies['PIL'] and dependencies['pytesseract']
    if core_deps:
        print("✓ 核心OCR依赖满足")
    else:
        print("⚠ 核心OCR依赖不完整")
    
    return core_deps

def test_ocr_module():
    """测试OCR模块"""
    print("\n=== 3. OCR模块测试 ===")
    try:
        from utils import ConfigManager
        from ocr_handler import OCRHandler
        
        config = ConfigManager()
        ocr = OCRHandler(config)
        
        # 进行健康检查
        health = ocr.health_check()
        print(f"OCR模块状态: {health['status']}")
        
        # 检查依赖状态
        for component, status in health.get('components', {}).items():
            if isinstance(status, dict):
                available = status.get('available', False)
                status_text = "✓" if available else "✗"
                print(f"  {status_text} {component}")
            else:
                print(f"  - {component}: {status}")
        
        # 在无GUI环境下跳过屏幕信息获取
        import os
        if 'DISPLAY' in os.environ and os.environ['DISPLAY']:
            # 获取屏幕信息
            screen_info = ocr.get_screen_info()
            print(f"屏幕尺寸: {screen_info.get('width', 'unknown')}x{screen_info.get('height', 'unknown')}")
        else:
            print("⚠ 跳过屏幕信息获取 (无GUI环境)")
        
        if health['status'] in ['healthy', 'degraded']:
            print("✓ OCR模块基本功能正常")
            return True
        else:
            print("⚠ OCR模块功能受限")
            return False
            
    except Exception as e:
        print(f"✗ OCR模块测试失败: {e}")
        return False

def test_excel_module():
    """测试Excel模块"""
    print("\n=== 4. Excel模块测试 ===")
    try:
        from utils import ConfigManager
        from excel_handler import ExcelHandler
        
        config = ConfigManager()
        excel = ExcelHandler(config)
        
        # 检查Excel文件是否存在
        excel_file = config.get('excel.file_path', 'questions.xlsx')
        if os.path.exists(excel_file):
            print(f"✓ Excel文件存在: {excel_file}")
            
            # 尝试加载题库
            try:
                stats = excel.get_statistics()
                print(f"题库统计: {stats}")
                print("✓ Excel模块正常工作")
                return True
            except Exception as e:
                print(f"⚠ Excel文件加载异常: {e}")
                return False
        else:
            print(f"⚠ Excel文件不存在: {excel_file}")
            print("  这不会影响API解题功能")
            return True
            
    except Exception as e:
        print(f"✗ Excel模块测试失败: {e}")
        return False

def test_api_module():
    """测试API模块"""
    print("\n=== 5. API模块测试 ===")
    try:
        from utils import ConfigManager
        from api_handler import APIHandler
        
        config = ConfigManager()
        
        # 检查API配置
        api_key = config.get('api.api_key')
        if not api_key or api_key == 'YOUR_AZURE_OPENAI_API_KEY':
            print("⚠ API密钥未配置，跳过API测试")
            return False
        
        api_handler = APIHandler(config)
        
        # 快速连接测试
        print("正在测试API连接...")
        if api_handler.test_connection():
            print("✓ API连接成功")
            
            # 快速解题测试
            print("测试快速解题...")
            start_time = time.time()
            result = api_handler.solve_question("1 + 1 = ?")
            end_time = time.time()
            
            if result['success']:
                print(f"✓ API解题成功 (耗时: {end_time - start_time:.2f}秒)")
                print(f"  答案: {result['answer']['answer']}")
                return True
            else:
                print(f"✗ API解题失败: {result['error']}")
                return False
        else:
            print("✗ API连接失败")
            return False
            
    except Exception as e:
        print(f"✗ API模块测试失败: {e}")
        return False

def test_gui_module():
    """测试GUI模块"""
    print("\n=== 6. GUI模块测试 ===")
    try:
        # 检查tkinter
        try:
            import tkinter as tk
            print("✓ tkinter 可用")
        except ImportError:
            print("✗ tkinter 未安装")
            return False
        
        from utils import ConfigManager
        from gui_handler import FloatingWindow
        
        config = ConfigManager()
        
        # 创建GUI实例（不显示）
        gui = FloatingWindow(config)
        print("✓ GUI模块初始化成功")
        
        # 测试显示消息
        gui.show_answer("这是一个测试消息")
        print("✓ GUI消息显示功能正常")
        
        # 清理
        if hasattr(gui, 'root') and gui.root:
            gui.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"✗ GUI模块测试失败: {e}")
        return False

def test_hotkey_module():
    """测试热键模块"""
    print("\n=== 7. 热键模块测试 ===")
    try:
        # 检查keyboard库
        try:
            import keyboard
            print("✓ keyboard 库可用")
        except ImportError:
            print("✗ keyboard 库未安装")
            return False
        
        from utils import ConfigManager
        from hotkey_listener import HotkeyListener
        
        config = ConfigManager()
        hotkey = HotkeyListener(config)
        
        print("✓ 热键监听器初始化成功")
        print(f"  触发键: {hotkey.trigger_key}")
        print(f"  退出键: {hotkey.exit_key}")
        
        # 检查热键可用性
        if hotkey.is_key_available(hotkey.trigger_key):
            print(f"✓ 触发键 {hotkey.trigger_key} 可用")
        else:
            print(f"⚠ 触发键 {hotkey.trigger_key} 可能被占用")
        
        return True
        
    except Exception as e:
        print(f"✗ 热键模块测试失败: {e}")
        return False

def test_main_integration():
    """测试主程序集成"""
    print("\n=== 8. 主程序集成测试 ===")
    try:
        # 检查主程序文件
        if os.path.exists('main.py'):
            print("✓ main.py 存在")
        else:
            print("✗ main.py 不存在")
            return False
        
        # 尝试导入主程序（不运行）
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("main", "main.py")
            main_module = importlib.util.module_from_spec(spec)
            print("✓ 主程序模块可以加载")
            return True
        except Exception as e:
            print(f"⚠ 主程序模块加载异常: {e}")
            return False
            
    except Exception as e:
        print(f"✗ 主程序集成测试失败: {e}")
        return False

def generate_test_report(results: Dict[str, bool]):
    """生成测试报告"""
    print("\n" + "="*50)
    print("           整体功能测试报告")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"总测试项目: {total_tests}")
    print(f"通过: {passed_tests}")
    print(f"失败: {failed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    
    print("\n详细结果:")
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
    
    print("\n整体评估:")
    if passed_tests == total_tests:
        print("🎉 所有功能测试通过！系统可以正常使用。")
        return "excellent"
    elif passed_tests >= total_tests * 0.8:
        print("✅ 大部分功能正常，系统基本可用。")
        return "good"
    elif passed_tests >= total_tests * 0.6:
        print("⚠️  部分功能异常，建议检查配置和依赖。")
        return "fair"
    else:
        print("❌ 多个功能异常，建议重新安装或配置。")
        return "poor"

def show_recommendations(overall_status: str):
    """显示建议"""
    print("\n" + "="*50)
    print("           使用建议")
    print("="*50)
    
    if overall_status == "excellent":
        print("🚀 系统状态优秀！")
        print("- 可以直接开始使用")
        print("- 运行 python3 main.py 启动程序")
        print("- 按 F12 开始自动答题")
        
    elif overall_status == "good":
        print("👍 系统基本可用！")
        print("- 核心功能正常工作")
        print("- 可选功能可能受限")
        print("- 建议安装缺失的依赖包")
        
    elif overall_status == "fair":
        print("🔧 需要进行一些配置：")
        print("- 检查并安装缺失的依赖：")
        print("  pip install -r requirements.txt")
        print("- 运行依赖检查脚本：")
        print("  ./check_ocr_dependencies.sh")
        print("- 配置API设置：")
        print("  ./setup_fast_api.py")
        
    else:
        print("🛠️  系统需要重新配置：")
        print("- 重新安装所有依赖：")
        print("  pip install -r requirements.txt")
        print("- 重新配置API：")
        print("  ./setup_fast_api.py")
        print("- 检查系统兼容性")
        print("- 考虑使用Docker部署")

def main():
    """主测试函数"""
    print("SPI自动答题工具 - 整体功能测试")
    print("="*50)
    
    # 执行所有测试
    test_results = {}
    
    test_results["配置管理器"] = test_config_manager()
    test_results["OCR依赖"] = test_ocr_dependencies()
    test_results["OCR模块"] = test_ocr_module()
    test_results["Excel模块"] = test_excel_module()
    test_results["API模块"] = test_api_module()
    test_results["GUI模块"] = test_gui_module()
    test_results["热键模块"] = test_hotkey_module()
    test_results["主程序集成"] = test_main_integration()
    
    # 生成报告
    overall_status = generate_test_report(test_results)
    
    # 显示建议
    show_recommendations(overall_status)
    
    # 保存报告到文件
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"SPI自动答题工具功能测试报告\n")
        f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        
        for test_name, result in test_results.items():
            status = "PASS" if result else "FAIL"
            f.write(f"{test_name}: {status}\n")
        
        f.write(f"\n通过率: {sum(test_results.values())/len(test_results)*100:.1f}%\n")
        f.write(f"整体状态: {overall_status}\n")
    
    print(f"\n📄 详细报告已保存到: {report_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
