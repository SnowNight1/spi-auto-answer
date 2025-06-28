"""
按键监听模块
监听全局热键，触发OCR识别和答案查询流程
支持多种热键组合和自定义设置
"""

import logging
import threading
import time
from typing import Callable, Optional, Dict, Any
import keyboard
import queue

from utils import ConfigManager, safe_execute


class HotkeyListener:
    """热键监听器"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.is_running = False
        self.is_listening = False
        self.listener_thread = None
        self.event_queue = queue.Queue()
        
        # 回调函数
        self.trigger_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        
        # 热键配置
        self.trigger_key = self.config.get('hotkey.trigger_key', 'F12')
        self.exit_key = self.config.get('hotkey.exit_key', 'F11')
        
        # 防抖设置
        self.last_trigger_time = 0
        self.debounce_interval = 1.0  # 1秒防抖
        
        # 状态信息
        self.stats = {
            'total_triggers': 0,
            'successful_triggers': 0,
            'failed_triggers': 0,
            'start_time': None
        }
    
    def set_trigger_callback(self, callback: Callable) -> None:
        """
        设置触发回调函数
        
        Args:
            callback: 热键触发时调用的函数
        """
        self.trigger_callback = callback
        logging.info("触发回调函数已设置")
    
    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        """
        设置状态回调函数
        
        Args:
            callback: 状态更新回调函数
        """
        self.status_callback = callback
        logging.info("状态回调函数已设置")
    
    def start_listening(self) -> bool:
        """
        开始监听热键
        
        Returns:
            是否启动成功
        """
        try:
            if self.is_listening:
                logging.warning("热键监听已在运行")
                return True
            
            # 尝试注册热键
            try:
                self._register_hotkeys()
                hotkey_registered = True
            except Exception as e:
                logging.warning(f"热键注册失败，但程序将继续运行: {e}")
                logging.info("提示：在Linux系统中，热键功能需要root权限")
                logging.info("您可以使用 sudo python3 main.py 来启用热键功能")
                logging.info("或者通过其他方式（如命令行参数）触发功能")
                hotkey_registered = False
            
            # 即使热键注册失败，也启动监听线程（用于其他功能）
            self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listener_thread.start()
            
            self.is_listening = True
            self.is_running = True
            self.stats['start_time'] = time.time()
            
            if hotkey_registered:
                self._update_status(f"热键监听已启动 - 触发键: {self.trigger_key}")
                logging.info(f"热键监听已启动，触发键: {self.trigger_key}")
            else:
                self._update_status("程序已启动（热键功能受限）")
                logging.info("程序已启动，但热键功能不可用")
            
            return True
            
        except Exception as e:
            logging.error(f"启动热键监听失败: {e}")
            self._update_status(f"启动失败: {e}")
            return False
    
    def stop_listening(self) -> None:
        """停止监听热键"""
        try:
            self.is_running = False
            self.is_listening = False
            
            # 注销热键
            self._unregister_hotkeys()
            
            # 等待线程结束
            if self.listener_thread and self.listener_thread.is_alive():
                self.listener_thread.join(timeout=2)
            
            self._update_status("热键监听已停止")
            logging.info("热键监听已停止")
            
        except Exception as e:
            logging.error(f"停止热键监听失败: {e}")
    
    def _register_hotkeys(self) -> None:
        """注册热键"""
        try:
            # 检查权限
            if not self._check_permissions():
                logging.warning("权限不足，热键功能将受限")
                return
                
            # 注册触发热键
            keyboard.add_hotkey(self.trigger_key, self._on_trigger_key)
            logging.info(f"已注册触发热键: {self.trigger_key}")
            
            # 注册退出热键
            keyboard.add_hotkey(self.exit_key, self._on_exit_key)
            logging.info(f"已注册退出热键: {self.exit_key}")
            
            # 注册其他功能热键
            keyboard.add_hotkey('ctrl+shift+r', self._on_reload_config)
            keyboard.add_hotkey('ctrl+shift+s', self._on_show_stats)
            
        except Exception as e:
            logging.error(f"注册热键失败: {e}")
            raise
    
    def _check_permissions(self) -> bool:
        """检查是否有足够权限使用热键功能"""
        try:
            import os
            # 检查是否为root用户
            if os.geteuid() == 0:
                return True
            
            # 检查是否在支持的环境中
            if not os.environ.get('DISPLAY'):
                logging.warning("无GUI环境，热键功能可能不可用")
                return False
                
            # 尝试简单测试
            keyboard.is_pressed('ctrl')
            return True
            
        except Exception as e:
            logging.warning(f"权限检查失败: {e}")
            return False
    
    def _unregister_hotkeys(self) -> None:
        """注销热键"""
        try:
            keyboard.unhook_all_hotkeys()
            logging.info("所有热键已注销")
        except Exception as e:
            logging.error(f"注销热键失败: {e}")
    
    def _listen_loop(self) -> None:
        """监听循环"""
        try:
            while self.is_running:
                try:
                    # 处理事件队列
                    self._process_event_queue()
                    
                    # 短暂休眠避免CPU占用过高
                    time.sleep(0.1)
                    
                except Exception as e:
                    logging.error(f"监听循环异常: {e}")
                    time.sleep(1)
            
            logging.info("热键监听循环已退出")
            
        except Exception as e:
            logging.error(f"监听循环严重错误: {e}")
    
    def _process_event_queue(self) -> None:
        """处理事件队列"""
        try:
            while not self.event_queue.empty():
                event = self.event_queue.get_nowait()
                self._handle_event(event)
        except queue.Empty:
            pass
        except Exception as e:
            logging.error(f"处理事件队列失败: {e}")
    
    def _handle_event(self, event: Dict[str, Any]) -> None:
        """处理事件"""
        try:
            event_type = event.get('type')
            
            if event_type == 'trigger':
                self._execute_trigger()
            elif event_type == 'reload_config':
                self._reload_config()
            elif event_type == 'show_stats':
                self._show_statistics()
            elif event_type == 'exit':
                self._handle_exit()
                
        except Exception as e:
            logging.error(f"处理事件失败: {e}")
    
    def _on_trigger_key(self) -> None:
        """触发键按下处理"""
        try:
            current_time = time.time()
            
            # 防抖检查
            if current_time - self.last_trigger_time < self.debounce_interval:
                logging.debug("触发过于频繁，已忽略")
                return
            
            self.last_trigger_time = current_time
            self.stats['total_triggers'] += 1
            
            # 添加到事件队列
            self.event_queue.put({'type': 'trigger', 'timestamp': current_time})
            
            logging.info(f"触发键 {self.trigger_key} 已按下")
            
        except Exception as e:
            logging.error(f"处理触发键失败: {e}")
    
    def _on_exit_key(self) -> None:
        """退出键按下处理"""
        try:
            logging.info(f"退出键 {self.exit_key} 已按下")
            self.event_queue.put({'type': 'exit'})
        except Exception as e:
            logging.error(f"处理退出键失败: {e}")
    
    def _on_reload_config(self) -> None:
        """重新加载配置"""
        try:
            logging.info("配置重载热键已按下")
            self.event_queue.put({'type': 'reload_config'})
        except Exception as e:
            logging.error(f"处理配置重载失败: {e}")
    
    def _on_show_stats(self) -> None:
        """显示统计信息"""
        try:
            logging.info("统计信息热键已按下")
            self.event_queue.put({'type': 'show_stats'})
        except Exception as e:
            logging.error(f"处理统计信息失败: {e}")
    
    def _execute_trigger(self) -> None:
        """执行触发操作"""
        try:
            self._update_status("正在处理...")
            
            if self.trigger_callback:
                # 在新线程中执行回调，避免阻塞热键监听
                trigger_thread = threading.Thread(
                    target=self._safe_trigger_callback,
                    daemon=True
                )
                trigger_thread.start()
            else:
                logging.warning("触发回调函数未设置")
                self._update_status("触发回调函数未设置")
                
        except Exception as e:
            logging.error(f"执行触发操作失败: {e}")
            self.stats['failed_triggers'] += 1
            self._update_status(f"触发失败: {e}")
    
    def _safe_trigger_callback(self) -> None:
        """安全执行触发回调"""
        try:
            start_time = time.time()
            self.trigger_callback()
            end_time = time.time()
            
            self.stats['successful_triggers'] += 1
            processing_time = end_time - start_time
            
            self._update_status(f"处理完成 ({processing_time:.1f}s)")
            logging.info(f"触发回调执行成功，用时: {processing_time:.1f}秒")
            
        except Exception as e:
            logging.error(f"触发回调执行失败: {e}")
            self.stats['failed_triggers'] += 1
            self._update_status(f"处理失败: {e}")
    
    def _reload_config(self) -> None:
        """重新加载配置"""
        try:
            # 停止当前监听
            old_trigger_key = self.trigger_key
            self._unregister_hotkeys()
            
            # 重新加载配置
            self.config._load_config()
            self.trigger_key = self.config.get('hotkey.trigger_key', 'F12')
            self.exit_key = self.config.get('hotkey.exit_key', 'F11')
            
            # 重新注册热键
            self._register_hotkeys()
            
            self._update_status(f"配置已重载 - 触发键: {self.trigger_key}")
            logging.info(f"配置已重载，触发键从 {old_trigger_key} 更改为 {self.trigger_key}")
            
        except Exception as e:
            logging.error(f"重新加载配置失败: {e}")
            self._update_status(f"配置重载失败: {e}")
    
    def _show_statistics(self) -> None:
        """显示统计信息"""
        try:
            if self.stats['start_time']:
                runtime = time.time() - self.stats['start_time']
                runtime_str = f"{runtime/3600:.1f}小时" if runtime > 3600 else f"{runtime/60:.1f}分钟"
            else:
                runtime_str = "未知"
            
            success_rate = 0
            if self.stats['total_triggers'] > 0:
                success_rate = (self.stats['successful_triggers'] / self.stats['total_triggers']) * 100
            
            stats_text = (
                f"运行时间: {runtime_str} | "
                f"总触发: {self.stats['total_triggers']} | "
                f"成功: {self.stats['successful_triggers']} | "
                f"失败: {self.stats['failed_triggers']} | "
                f"成功率: {success_rate:.1f}%"
            )
            
            self._update_status(stats_text)
            logging.info(f"统计信息: {stats_text}")
            
        except Exception as e:
            logging.error(f"显示统计信息失败: {e}")
    
    def _handle_exit(self) -> None:
        """处理退出"""
        try:
            self._update_status("正在退出...")
            logging.info("收到退出信号")
            
            # 通知主程序退出
            if hasattr(self, 'exit_callback') and self.exit_callback:
                self.exit_callback()
            else:
                self.stop_listening()
                
        except Exception as e:
            logging.error(f"处理退出失败: {e}")
    
    def _update_status(self, message: str) -> None:
        """更新状态信息"""
        try:
            if self.status_callback:
                self.status_callback(message)
        except Exception as e:
            logging.error(f"更新状态失败: {e}")
    
    def update_hotkeys(self, trigger_key: str, exit_key: str = None) -> bool:
        """
        更新热键配置
        
        Args:
            trigger_key: 新的触发键
            exit_key: 新的退出键
            
        Returns:
            是否更新成功
        """
        try:
            # 临时停止监听
            was_listening = self.is_listening
            if was_listening:
                self._unregister_hotkeys()
            
            # 更新配置
            self.trigger_key = trigger_key
            if exit_key:
                self.exit_key = exit_key
            
            self.config.update('hotkey.trigger_key', trigger_key)
            if exit_key:
                self.config.update('hotkey.exit_key', exit_key)
            
            # 重新注册
            if was_listening:
                self._register_hotkeys()
            
            self._update_status(f"热键已更新 - 触发键: {trigger_key}")
            logging.info(f"热键已更新，触发键: {trigger_key}")
            
            return True
            
        except Exception as e:
            logging.error(f"更新热键失败: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        if stats['start_time']:
            stats['runtime'] = time.time() - stats['start_time']
        else:
            stats['runtime'] = 0
        
        if stats['total_triggers'] > 0:
            stats['success_rate'] = (stats['successful_triggers'] / stats['total_triggers']) * 100
        else:
            stats['success_rate'] = 0
        
        return stats
    
    def is_key_available(self, key: str) -> bool:
        """
        检查热键是否可用
        
        Args:
            key: 要检查的热键
            
        Returns:
            热键是否可用
        """
        try:
            # 尝试注册临时热键
            test_callback = lambda: None
            keyboard.add_hotkey(key, test_callback)
            keyboard.remove_hotkey(key)
            return True
        except:
            return False


def test_hotkey_listener():
    """测试热键监听器"""
    def mock_trigger():
        print("触发回调被调用！")
        time.sleep(1)  # 模拟处理时间
        print("处理完成")
    
    def mock_status(message):
        print(f"状态更新: {message}")
    
    config = ConfigManager()
    listener = HotkeyListener(config)
    
    # 设置回调
    listener.set_trigger_callback(mock_trigger)
    listener.set_status_callback(mock_status)
    
    # 启动监听
    if listener.start_listening():
        print(f"热键监听已启动，按 {listener.trigger_key} 触发，按 {listener.exit_key} 退出")
        
        try:
            # 保持运行
            while listener.is_listening:
                time.sleep(1)
        except KeyboardInterrupt:
            print("收到中断信号")
        finally:
            listener.stop_listening()
            print("测试结束")
    else:
        print("启动热键监听失败")


if __name__ == "__main__":
    test_hotkey_listener()
