"""
SPI自动答题工具主程序
整合所有模块，提供完整的自动答题功能
"""

import logging
import sys
import signal
import time
import threading
from typing import Dict, Any, Optional

from utils import ConfigManager, Logger, validate_config
from ocr_handler import OCRHandler
from excel_handler import ExcelHandler
from api_handler import APIHandler
from gui_handler import FloatingWindow
from hotkey_listener import HotkeyListener


class SPIAutoAnswerApp:
    """SPI自动答题应用主类"""
    
    def __init__(self):
        self.config = None
        self.logger = None
        self.ocr_handler = None
        self.excel_handler = None
        self.api_handler = None
        self.gui_window = None
        self.hotkey_listener = None
        
        self.is_running = False
        self.is_processing = False
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'excel_matches': 0,
            'api_calls': 0,
            'successful_answers': 0,
            'failed_answers': 0,
            'start_time': None
        }
    
    def initialize(self) -> bool:
        """
        初始化应用
        
        Returns:
            是否初始化成功
        """
        try:
            print("正在初始化SPI自动答题工具...")
            
            # 加载配置
            self.config = ConfigManager()
            if not validate_config(self.config):
                print("配置文件验证失败，请检查config.json")
                return False
            
            # 设置日志
            self.logger = Logger(self.config)
            logging.info("SPI自动答题工具启动中...")
            
            # 初始化各个模块
            self._initialize_modules()
            
            # 设置信号处理
            self._setup_signal_handlers()
            
            logging.info("应用初始化完成")
            return True
            
        except Exception as e:
            print(f"初始化失败: {e}")
            logging.error(f"应用初始化失败: {e}")
            return False
    
    def _initialize_modules(self) -> None:
        """初始化各个功能模块"""
        try:
            # OCR处理器
            logging.info("初始化OCR处理器...")
            self.ocr_handler = OCRHandler(self.config)
            
            # Excel题库处理器
            logging.info("初始化Excel题库处理器...")
            self.excel_handler = ExcelHandler(self.config)
            
            # API处理器
            logging.info("初始化API处理器...")
            self.api_handler = APIHandler(self.config)
            
            # GUI悬浮窗口
            logging.info("初始化GUI悬浮窗口...")
            self.gui_window = FloatingWindow(self.config)
            
            # 热键监听器
            logging.info("初始化热键监听器...")
            self.hotkey_listener = HotkeyListener(self.config)
            self.hotkey_listener.set_trigger_callback(self._on_hotkey_triggered)
            self.hotkey_listener.set_status_callback(self._on_status_update)
            
            logging.info("所有模块初始化完成")
            
        except Exception as e:
            logging.error(f"模块初始化失败: {e}")
            raise
    
    def _setup_signal_handlers(self) -> None:
        """设置信号处理器"""
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            logging.info("信号处理器设置完成")
        except Exception as e:
            logging.warning(f"设置信号处理器失败: {e}")
    
    def _signal_handler(self, signum, frame) -> None:
        """信号处理函数"""
        logging.info(f"收到信号 {signum}，正在退出...")
        self.shutdown()
    
    def run(self) -> None:
        """运行应用"""
        try:
            self.is_running = True
            self.stats['start_time'] = time.time()
            
            # 显示启动信息
            self._show_startup_info()
            
            # 启动热键监听
            if not self.hotkey_listener.start_listening():
                logging.error("启动热键监听失败")
                return
            
            # 显示初始状态
            self.gui_window.show_status("就绪 - 等待热键触发")
            
            logging.info("SPI自动答题工具启动完成")
            print("应用已启动，等待热键触发...")
            print(f"触发键: {self.config.get('hotkey.trigger_key', 'F12')}")
            print(f"退出键: {self.config.get('hotkey.exit_key', 'F11')}")
            
            # 主循环
            self._main_loop()
            
        except Exception as e:
            logging.error(f"运行应用失败: {e}")
            print(f"应用运行错误: {e}")
        finally:
            self.shutdown()
    
    def _show_startup_info(self) -> None:
        """显示启动信息"""
        try:
            # 获取各模块状态
            excel_stats = self.excel_handler.get_statistics()
            ocr_info = self.ocr_handler.get_screen_info()
            
            startup_info = f"""
=== SPI自动答题工具 ===
配置文件: config.json
题库文件: {self.config.get('excel.file_path', 'questions.xlsx')}
题库sheets: {excel_stats['total_sheets']}个
总题目数: {excel_stats['total_questions']}
屏幕分辨率: {ocr_info.get('width', '未知')}x{ocr_info.get('height', '未知')}
触发热键: {self.config.get('hotkey.trigger_key', 'F12')}
OCR语言: {self.config.get('ocr.language', 'jpn')}
API模型: {self.config.get('api.model', 'gpt-4')}
========================
"""
            print(startup_info)
            logging.info("启动信息已显示")
            
        except Exception as e:
            logging.error(f"显示启动信息失败: {e}")
    
    def _main_loop(self) -> None:
        """主循环"""
        try:
            while self.is_running and self.hotkey_listener.is_listening:
                # 检查应用状态
                self._check_application_health()
                
                # 休眠避免CPU占用过高
                time.sleep(1)
                
        except KeyboardInterrupt:
            logging.info("收到键盘中断")
        except Exception as e:
            logging.error(f"主循环异常: {e}")
    
    def _check_application_health(self) -> None:
        """检查应用健康状态"""
        try:
            # 这里可以添加健康检查逻辑
            # 例如检查模块是否正常工作
            pass
        except Exception as e:
            logging.error(f"健康检查失败: {e}")
    
    def _on_hotkey_triggered(self) -> None:
        """热键触发时的回调函数"""
        if self.is_processing:
            logging.warning("上一次处理尚未完成，忽略本次触发")
            self.gui_window.show_status("处理中，请稍候...")
            return
        
        self.is_processing = True
        self.stats['total_requests'] += 1
        
        try:
            logging.info("开始处理热键触发事件")
            
            # 执行完整的答题流程
            result = self._process_question()
            
            if result and result.get('success'):
                self.stats['successful_answers'] += 1
                logging.info("答题处理成功")
            else:
                self.stats['failed_answers'] += 1
                error_msg = result.get('error', '未知错误') if result else '处理失败'
                logging.error(f"答题处理失败: {error_msg}")
                self.gui_window.show_error(f"处理失败: {error_msg}")
                
        except Exception as e:
            self.stats['failed_answers'] += 1
            logging.error(f"处理热键触发事件失败: {e}")
            self.gui_window.show_error(f"处理异常: {e}")
        finally:
            self.is_processing = False
    
    def _process_question(self) -> Optional[Dict[str, Any]]:
        """
        处理题目的完整流程
        
        Returns:
            处理结果
        """
        try:
            # 步骤1: OCR识别
            self.gui_window.show_status("正在识别题目...")
            question_text = self.ocr_handler.capture_and_extract()
            
            if not question_text or len(question_text.strip()) < 3:
                return {
                    'success': False,
                    'error': 'OCR识别失败或文本过短'
                }
            
            logging.info(f"OCR识别结果: {question_text[:100]}...")
            
            # 步骤2: 查询Excel题库
            self.gui_window.show_status("正在查询题库...")
            excel_results = self.excel_handler.search_question(question_text)
            
            if excel_results:
                # 找到题库匹配
                best_match = excel_results[0]
                self.stats['excel_matches'] += 1
                
                result = {
                    'success': True,
                    'source': 'excel',
                    'match_score': best_match['match_score'],
                    'answer_info': best_match['answer_info'],
                    'question': best_match['question']
                }
                
                # 显示答案
                self.gui_window.show_answer(result)
                logging.info(f"题库匹配成功，匹配度: {best_match['match_score']:.2f}")
                
                return result
            
            # 步骤3: 调用API
            self.gui_window.show_status("正在调用AI解答...")
            self.stats['api_calls'] += 1
            
            api_result = self.api_handler.solve_question(question_text)
            
            if api_result['success']:
                # API调用成功
                result = {
                    'success': True,
                    'source': 'api',
                    'answer': api_result['answer'],
                    'raw_response': api_result.get('raw_response'),
                    'usage': api_result.get('usage')
                }
                
                # 显示答案
                self.gui_window.show_answer(result)
                logging.info("API解答成功")
                
                # 可选：将API答案添加到题库
                self._save_api_answer_to_excel(question_text, api_result['answer'])
                
                return result
            else:
                # API调用失败
                return {
                    'success': False,
                    'error': f"API调用失败: {api_result.get('error')}"
                }
                
        except Exception as e:
            logging.error(f"处理题目失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_api_answer_to_excel(self, question: str, answer: Dict[str, Any]) -> None:
        """
        将API答案保存到Excel题库（可选功能）
        
        Args:
            question: 题目文本
            answer: 答案信息
        """
        try:
            # 这里可以实现将API答案自动添加到题库的逻辑
            # 根据需要决定是否启用此功能
            pass
        except Exception as e:
            logging.error(f"保存API答案到Excel失败: {e}")
    
    def _on_status_update(self, status: str) -> None:
        """状态更新回调"""
        try:
            self.gui_window.show_status(status)
        except Exception as e:
            logging.error(f"更新状态失败: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取应用统计信息"""
        stats = self.stats.copy()
        
        if stats['start_time']:
            stats['runtime'] = time.time() - stats['start_time']
        else:
            stats['runtime'] = 0
        
        # 添加各模块统计
        if self.excel_handler:
            stats['excel_stats'] = self.excel_handler.get_statistics()
        
        if self.hotkey_listener:
            stats['hotkey_stats'] = self.hotkey_listener.get_statistics()
        
        if self.api_handler:
            stats['api_stats'] = self.api_handler.get_usage_statistics()
        
        return stats
    
    def shutdown(self) -> None:
        """关闭应用"""
        try:
            logging.info("正在关闭应用...")
            self.is_running = False
            
            # 停止热键监听
            if self.hotkey_listener:
                self.hotkey_listener.stop_listening()
            
            # 关闭GUI窗口
            if self.gui_window:
                self.gui_window.destroy()
            
            # 显示统计信息
            self._show_exit_statistics()
            
            logging.info("应用已关闭")
            print("应用已退出")
            
        except Exception as e:
            logging.error(f"关闭应用失败: {e}")
    
    def _show_exit_statistics(self) -> None:
        """显示退出时的统计信息"""
        try:
            stats = self.get_statistics()
            
            exit_info = f"""
=== 运行统计 ===
运行时间: {stats['runtime']/3600:.1f} 小时
总请求数: {stats['total_requests']}
成功答题: {stats['successful_answers']}
失败答题: {stats['failed_answers']}
题库匹配: {stats['excel_matches']}
API调用: {stats['api_calls']}
成功率: {(stats['successful_answers']/max(stats['total_requests'], 1)*100):.1f}%
===============
"""
            print(exit_info)
            logging.info(f"退出统计: {stats}")
            
        except Exception as e:
            logging.error(f"显示退出统计失败: {e}")


def main():
    """主函数"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='SPI自动答题工具')
    parser.add_argument('--manual', '-m', action='store_true', 
                       help='手动模式：通过命令行触发答题（适用于无GUI环境或权限不足时）')
    parser.add_argument('--test-api', action='store_true',
                       help='测试API连接')
    parser.add_argument('--test-ocr', action='store_true',
                       help='测试OCR功能')
    args = parser.parse_args()
    
    print("SPI自动答题工具 v1.0")
    print("=" * 30)
    
    app = SPIAutoAnswerApp()
    
    if not app.initialize():
        print("初始化失败，程序退出")
        sys.exit(1)
    
    try:
        if args.test_api:
            # 测试API连接
            print("测试API连接...")
            if app.api_handler.test_connection():
                print("✓ API连接正常")
            else:
                print("✗ API连接失败")
            return
            
        elif args.test_ocr:
            # 测试OCR功能
            print("测试OCR功能...")
            health = app.ocr_handler.health_check()
            print(f"OCR状态: {health['status']}")
            return
            
        elif args.manual:
            # 手动模式
            run_manual_mode(app)
        else:
            # 正常热键模式
            app.run()
            
    except Exception as e:
        print(f"运行错误: {e}")
        logging.error(f"主程序运行错误: {e}")
    finally:
        app.shutdown()


def run_manual_mode(app):
    """运行手动模式"""
    print("\n=== 手动模式 ===")
    print("在此模式下，您可以通过命令触发答题功能")
    print("命令列表:")
    print("  answer  - 启动自动答题")
    print("  status  - 显示系统状态")
    print("  config  - 显示配置信息")
    print("  quit    - 退出程序")
    print("  help    - 显示帮助")
    print()
    
    app.is_running = True
    app.stats['start_time'] = time.time()
    
    try:
        while app.is_running:
            try:
                command = input("请输入命令 (help查看帮助): ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    break
                elif command == 'answer':
                    print("启动自动答题...")
                    app._on_hotkey_triggered()
                elif command == 'status':
                    show_system_status(app)
                elif command == 'config':
                    show_config_info(app)
                elif command == 'help':
                    print("命令列表:")
                    print("  answer  - 启动自动答题")
                    print("  status  - 显示系统状态") 
                    print("  config  - 显示配置信息")
                    print("  quit    - 退出程序")
                    print("  help    - 显示帮助")
                elif command == '':
                    continue
                else:
                    print(f"未知命令: {command}，输入 'help' 查看帮助")
                    
            except KeyboardInterrupt:
                print("\n收到中断信号，正在退出...")
                break
            except EOFError:
                print("\n收到EOF信号，正在退出...")
                break
            except Exception as e:
                print(f"命令执行错误: {e}")
                
    finally:
        app.is_running = False


def show_system_status(app):
    """显示系统状态"""
    print("\n=== 系统状态 ===")
    
    # OCR状态
    print("OCR模块:")
    health = app.ocr_handler.health_check()
    print(f"  状态: {health['status']}")
    deps = health.get('components', {}).get('dependencies', {})
    for dep, available in deps.items():
        status = "✓" if available else "✗"
        print(f"  {status} {dep}")
    
    # API状态
    print("API模块:")
    if app.api_handler.test_connection():
        print("  ✓ API连接正常")
    else:
        print("  ✗ API连接失败")
    
    # 统计信息
    print("运行统计:")
    runtime = time.time() - app.stats['start_time'] if app.stats['start_time'] else 0
    print(f"  运行时间: {runtime/3600:.1f} 小时")
    print(f"  总请求数: {app.stats['total_requests']}")
    print(f"  成功答题: {app.stats['successful_answers']}")
    print(f"  失败答题: {app.stats['failed_answers']}")
    
    
def show_config_info(app):
    """显示配置信息"""
    print("\n=== 配置信息 ===")
    print(f"API端点: {app.config.get('api.api_endpoint', 'N/A')}")
    print(f"API模型: {app.config.get('api.deployment_name', 'N/A')}")
    print(f"OCR语言: {app.config.get('ocr.language', 'jpn')}")
    print(f"触发热键: {app.config.get('hotkey.trigger_key', 'F12')}")
    print(f"题库文件: {app.config.get('excel.file_path', 'questions.xlsx')}")
    print(f"日志级别: {app.config.get('logging.level', 'INFO')}")


if __name__ == "__main__":
    main()
