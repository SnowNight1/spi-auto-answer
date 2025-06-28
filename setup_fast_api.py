#!/usr/bin/env python3
"""
API配置快速设置工具
专门用于配置快速响应模式的API参数
"""

import json
import sys
import os

def load_config():
    """加载当前配置"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("config.json不存在，将创建新配置")
        return {}
    except json.JSONDecodeError:
        print("配置文件格式错误，将重新创建")
        return {}

def save_config(config):
    """保存配置"""
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def setup_fast_api_config():
    """设置快速响应API配置"""
    print("=== SPI自动答题工具 - 快速API配置 ===\n")
    
    config = load_config()
    
    # 确保api配置节存在
    if 'api' not in config:
        config['api'] = {}
    
    print("请输入API配置信息（快速响应模式优化）：\n")
    
    # API密钥
    current_key = config['api'].get('api_key', '')
    if current_key and current_key != 'YOUR_AZURE_OPENAI_API_KEY':
        print(f"当前API密钥: {current_key[:8]}..." + "*" * 20)
        if input("是否保持当前密钥？(y/n): ").lower() != 'n':
            api_key = current_key
        else:
            api_key = input("请输入Azure OpenAI API密钥: ").strip()
    else:
        api_key = input("请输入Azure OpenAI API密钥: ").strip()
    
    # API端点
    current_endpoint = config['api'].get('api_endpoint', '')
    if current_endpoint and current_endpoint != 'YOUR_AZURE_OPENAI_ENDPOINT':
        print(f"当前API端点: {current_endpoint}")
        if input("是否保持当前端点？(y/n): ").lower() != 'n':
            api_endpoint = current_endpoint
        else:
            api_endpoint = input("请输入Azure OpenAI API端点: ").strip()
    else:
        api_endpoint = input("请输入Azure OpenAI API端点 (例: https://your-resource.openai.azure.com): ").strip()
    
    # API版本
    api_version = input("请输入API版本 [默认: 2024-02-01]: ").strip() or "2024-02-01"
    
    # 部署名称
    deployment_name = input("请输入部署名称 [默认: gpt-4]: ").strip() or "gpt-4"
    
    print("\n=== 快速响应模式优化参数 ===")
    print("以下参数已针对快速响应进行优化：")
    
    # 快速响应优化配置
    config['api'].update({
        'api_key': api_key,
        'api_endpoint': api_endpoint,
        'api_version': api_version,
        'deployment_name': deployment_name,
        'max_tokens': 300,      # 减少token以提高速度
        'temperature': 0.3,     # 平衡准确性和响应速度
        'timeout': 20           # 缩短超时时间
    })
    
    print(f"- max_tokens: {config['api']['max_tokens']} (减少token使用)")
    print(f"- temperature: {config['api']['temperature']} (提高一致性)")
    print(f"- timeout: {config['api']['timeout']}秒 (快速响应)")
    
    # 保存配置
    save_config(config)
    print(f"\n✓ 配置已保存到 config.json")
    
    # 测试连接
    print("\n=== 测试API连接 ===")
    if input("是否立即测试API连接？(y/n): ").lower() == 'y':
        test_api_connection()

def test_api_connection():
    """测试API连接"""
    try:
        # 动态导入避免循环导入
        from api_handler import APIHandler
        from utils import ConfigManager
        
        config_manager = ConfigManager()
        api_handler = APIHandler(config_manager)
        
        print("正在测试API连接...")
        
        if api_handler.test_connection():
            print("✓ API连接测试成功！")
            
            # 快速测试一个简单问题
            print("\n正在测试快速响应...")
            import time
            start_time = time.time()
            
            result = api_handler.solve_question("2 + 3 = ?")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if result['success']:
                print(f"✓ 快速响应测试成功！")
                print(f"  响应时间: {response_time:.2f}秒")
                print(f"  答案: {result['answer']['answer']}")
                
                if response_time <= 3:
                    print("  ✓ 响应速度优秀")
                elif response_time <= 5:
                    print("  ○ 响应速度良好")
                else:
                    print("  ⚠ 响应较慢，但仍在可接受范围")
            else:
                print(f"✗ 快速响应测试失败: {result['error']}")
        else:
            print("✗ API连接测试失败")
            print("请检查：")
            print("1. API密钥是否正确")
            print("2. API端点是否正确")
            print("3. 网络连接是否正常")
            print("4. Azure OpenAI服务是否可用")
            
    except ImportError as e:
        print(f"✗ 导入模块失败: {e}")
        print("请确保所有依赖都已安装")
    except Exception as e:
        print(f"✗ 测试失败: {e}")

def show_config_tips():
    """显示配置建议"""
    print("\n=== 快速响应配置建议 ===")
    print("1. 网络优化:")
    print("   - 使用稳定的网络连接")
    print("   - 选择地理位置较近的Azure区域")
    print("   - 避免高峰时段使用")
    
    print("\n2. 参数优化:")
    print("   - max_tokens: 200-500 (平衡速度和完整性)")
    print("   - temperature: 0.1-0.5 (低值更稳定)")
    print("   - timeout: 15-30秒 (根据网络情况调整)")
    
    print("\n3. 使用建议:")
    print("   - 保持问题描述简洁明了")
    print("   - 避免过于复杂的多步骤问题")
    print("   - 定期监控API配额使用情况")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            test_api_connection()
        elif sys.argv[1] == "--tips":
            show_config_tips()
        else:
            print("用法:")
            print("  python3 setup_fast_api.py        # 交互式配置")
            print("  python3 setup_fast_api.py --test # 仅测试连接")
            print("  python3 setup_fast_api.py --tips # 显示配置建议")
    else:
        try:
            setup_fast_api_config()
        except KeyboardInterrupt:
            print("\n\n配置已取消")
        except Exception as e:
            print(f"\n配置过程中出错: {e}")

if __name__ == "__main__":
    main()
