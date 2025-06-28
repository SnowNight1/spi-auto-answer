"""
GUI悬浮窗口模块
提供透明的悬浮窗口显示答案
支持拖拽、自动隐藏、多种显示模式
"""

import logging
import tkinter as tk
from tkinter import ttk, font
import threading
import time
from typing import Dict, Any, Optional, Callable

from utils import ConfigManager


class FloatingWindow:
    """悬浮答案窗口"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.root = None
        self.is_visible = False
        self.current_answer = ""
        self.auto_hide_timer = None
        self.drag_data = {"x": 0, "y": 0}
        
        # 创建主窗口
        self._create_window()
        
        # 启动GUI线程
        self.gui_thread = threading.Thread(target=self._run_gui, daemon=True)
        self.gui_thread.start()
    
    def _create_window(self) -> None:
        """创建悬浮窗口"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # 初始隐藏
            
            # 窗口配置
            self._configure_window()
            
            # 创建UI组件
            self._create_widgets()
            
            # 绑定事件
            self._bind_events()
            
            logging.info("悬浮窗口创建成功")
            
        except Exception as e:
            logging.error(f"创建悬浮窗口失败: {e}")
    
    def _configure_window(self) -> None:
        """配置窗口属性"""
        # 窗口基本设置
        self.root.title("SPI答案提示")
        self.root.overrideredirect(True)  # 移除标题栏
        self.root.attributes('-topmost', True)  # 保持最前
        
        # 获取配置
        width = self.config.get('gui.window.width', 300)
        height = self.config.get('gui.window.height', 150)
        alpha = self.config.get('gui.window.alpha', 0.9)
        init_x = self.config.get('gui.window.initial_position.x', 100)
        init_y = self.config.get('gui.window.initial_position.y', 100)
        
        # 设置窗口大小和位置
        self.root.geometry(f"{width}x{height}+{init_x}+{init_y}")
        self.root.attributes('-alpha', alpha)
        
        # 背景颜色
        bg_color = self.config.get('gui.colors.background', '#000000')
        self.root.configure(bg=bg_color)
    
    def _create_widgets(self) -> None:
        """创建UI组件"""
        # 主框架
        self.main_frame = tk.Frame(
            self.root,
            bg=self.config.get('gui.colors.background', '#000000'),
            relief='raised',
            bd=2
        )
        self.main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 标题标签
        self.title_label = tk.Label(
            self.main_frame,
            text="SPI答案提示",
            bg=self.config.get('gui.colors.background', '#000000'),
            fg=self.config.get('gui.colors.text', '#00FF00'),
            font=self._get_font(size=10, weight='bold')
        )
        self.title_label.pack(pady=(0, 5))
        
        # 答案显示区域
        self.answer_text = tk.Text(
            self.main_frame,
            bg=self.config.get('gui.colors.background', '#000000'),
            fg=self.config.get('gui.colors.text', '#00FF00'),
            font=self._get_font(),
            wrap=tk.WORD,
            relief='flat',
            bd=0,
            state='disabled',
            cursor='arrow'
        )
        self.answer_text.pack(fill='both', expand=True)
        
        # 滚动条
        scrollbar = tk.Scrollbar(self.answer_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.answer_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.answer_text.yview)
        
        # 状态栏
        self.status_frame = tk.Frame(
            self.main_frame,
            bg=self.config.get('gui.colors.background', '#000000')
        )
        self.status_frame.pack(fill='x', pady=(5, 0))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="等待中...",
            bg=self.config.get('gui.colors.background', '#000000'),
            fg=self.config.get('gui.colors.text', '#00FF00'),
            font=self._get_font(size=8)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # 关闭按钮
        self.close_button = tk.Button(
            self.status_frame,
            text="×",
            bg=self.config.get('gui.colors.background', '#000000'),
            fg=self.config.get('gui.colors.text', '#00FF00'),
            font=self._get_font(size=8, weight='bold'),
            relief='flat',
            bd=0,
            command=self.hide,
            cursor='hand2'
        )
        self.close_button.pack(side=tk.RIGHT)
    
    def _get_font(self, size: Optional[int] = None, weight: str = 'normal') -> font.Font:
        """获取字体配置"""
        family = self.config.get('gui.font.family', 'Arial Unicode MS')
        if size is None:
            size = self.config.get('gui.font.size', 12)
        
        return font.Font(family=family, size=size, weight=weight)
    
    def _bind_events(self) -> None:
        """绑定事件处理"""
        # 拖拽事件
        self.title_label.bind("<Button-1>", self._start_drag)
        self.title_label.bind("<B1-Motion>", self._on_drag)
        self.title_label.bind("<ButtonRelease-1>", self._stop_drag)
        
        # 双击隐藏
        self.title_label.bind("<Double-Button-1>", lambda e: self.hide())
        
        # 鼠标悬停事件
        self.root.bind("<Enter>", self._on_mouse_enter)
        self.root.bind("<Leave>", self._on_mouse_leave)
        
        # 键盘事件
        self.root.bind("<Key>", self._on_key_press)
        self.root.focus_set()
    
    def _start_drag(self, event) -> None:
        """开始拖拽"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def _on_drag(self, event) -> None:
        """拖拽处理"""
        x = self.root.winfo_x() + (event.x - self.drag_data["x"])
        y = self.root.winfo_y() + (event.y - self.drag_data["y"])
        self.root.geometry(f"+{x}+{y}")
    
    def _stop_drag(self, event) -> None:
        """停止拖拽，保存位置"""
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.config.update('gui.window.initial_position.x', x)
        self.config.update('gui.window.initial_position.y', y)
    
    def _on_mouse_enter(self, event) -> None:
        """鼠标进入窗口"""
        if self.auto_hide_timer:
            self.auto_hide_timer.cancel()
            self.auto_hide_timer = None
    
    def _on_mouse_leave(self, event) -> None:
        """鼠标离开窗口"""
        self._schedule_auto_hide()
    
    def _on_key_press(self, event) -> None:
        """键盘按键处理"""
        if event.keysym == 'Escape':
            self.hide()
        elif event.keysym == 'space':
            self.toggle_visibility()
    
    def _schedule_auto_hide(self, delay: int = 10) -> None:
        """安排自动隐藏"""
        if self.auto_hide_timer:
            self.auto_hide_timer.cancel()
        
        self.auto_hide_timer = threading.Timer(delay, self.hide)
        self.auto_hide_timer.start()
    
    def _run_gui(self) -> None:
        """运行GUI主循环"""
        try:
            self.root.mainloop()
        except Exception as e:
            logging.error(f"GUI线程异常: {e}")
    
    def show_answer(self, answer_data: Dict[str, Any]) -> None:
        """
        显示答案信息
        
        Args:
            answer_data: 答案数据字典
        """
        try:
            if not self.root:
                return
            
            # 格式化答案文本
            formatted_text = self._format_answer(answer_data)
            
            # 更新显示
            self.root.after(0, self._update_display, formatted_text, answer_data)
            
        except Exception as e:
            logging.error(f"显示答案失败: {e}")
    
    def _format_answer(self, answer_data: Dict[str, Any]) -> str:
        """
        格式化答案显示文本
        
        Args:
            answer_data: 答案数据
            
        Returns:
            格式化后的文本
        """
        lines = []
        
        # 来源标识
        source = answer_data.get('source', 'unknown')
        if source == 'excel':
            lines.append("📚 题库匹配")
            match_score = answer_data.get('match_score', 0)
            lines.append(f"匹配度: {match_score:.1%}")
        elif source == 'api':
            lines.append("🤖 AI解答")
        
        lines.append("-" * 20)
        
        # 答案内容
        if 'answer_info' in answer_data:
            info = answer_data['answer_info']
            
            # 选项
            if 'options' in info and info['options']:
                lines.append("选项:")
                for option, text in info['options'].items():
                    lines.append(f"  {option}. {text}")
                lines.append("")
            
            # 正确答案
            if 'correct_answer' in info:
                lines.append(f"答案: {info['correct_answer']}")
            
            if 'answer_text' in info and info['answer_text']:
                lines.append(f"解释: {info['answer_text']}")
        
        elif 'answer' in answer_data:
            # API回答格式
            api_answer = answer_data['answer']
            if isinstance(api_answer, dict):
                if 'question_type' in api_answer:
                    lines.append(f"类型: {api_answer['question_type']}")
                
                if 'reasoning' in api_answer and api_answer['reasoning']:
                    lines.append(f"解法: {api_answer['reasoning']}")
                
                if 'answer' in api_answer:
                    lines.append(f"答案: {api_answer['answer']}")
                
                if 'correct_option' in api_answer and api_answer['correct_option']:
                    lines.append(f"选项: {api_answer['correct_option']}")
            else:
                lines.append(str(api_answer))
        
        return "\n".join(lines)
    
    def _update_display(self, text: str, answer_data: Dict[str, Any]) -> None:
        """更新显示内容"""
        try:
            # 更新答案文本
            self.answer_text.config(state='normal')
            self.answer_text.delete(1.0, tk.END)
            self.answer_text.insert(1.0, text)
            self.answer_text.config(state='disabled')
            
            # 更新状态
            source = answer_data.get('source', 'unknown')
            timestamp = time.strftime("%H:%M:%S")
            status_text = f"{timestamp} - {source.upper()}"
            self.status_label.config(text=status_text)
            
            # 显示窗口
            self.show()
            
            # 设置自动隐藏
            self._schedule_auto_hide(15)  # 15秒后自动隐藏
            
        except Exception as e:
            logging.error(f"更新显示失败: {e}")
    
    def show(self) -> None:
        """显示窗口"""
        if self.root and not self.is_visible:
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.is_visible = True
            logging.debug("悬浮窗口已显示")
    
    def hide(self) -> None:
        """隐藏窗口"""
        if self.root and self.is_visible:
            self.root.withdraw()
            self.is_visible = False
            if self.auto_hide_timer:
                self.auto_hide_timer.cancel()
                self.auto_hide_timer = None
            logging.debug("悬浮窗口已隐藏")
    
    def toggle_visibility(self) -> None:
        """切换显示状态"""
        if self.is_visible:
            self.hide()
        else:
            self.show()
    
    def update_position(self, x: int, y: int) -> None:
        """更新窗口位置"""
        if self.root:
            self.root.geometry(f"+{x}+{y}")
            self.config.update('gui.window.initial_position.x', x)
            self.config.update('gui.window.initial_position.y', y)
    
    def set_theme(self, theme: str) -> None:
        """
        设置主题
        
        Args:
            theme: 主题名称 ('dark', 'light', 'green')
        """
        themes = {
            'dark': {
                'background': '#2b2b2b',
                'text': '#ffffff',
                'border': '#555555'
            },
            'light': {
                'background': '#ffffff',
                'text': '#000000',
                'border': '#cccccc'
            },
            'green': {
                'background': '#000000',
                'text': '#00ff00',
                'border': '#008800'
            }
        }
        
        if theme in themes:
            theme_config = themes[theme]
            self.config.update('gui.colors.background', theme_config['background'])
            self.config.update('gui.colors.text', theme_config['text'])
            self.config.update('gui.colors.border', theme_config['border'])
            
            # 重新配置组件颜色（需要重启窗口生效）
            logging.info(f"主题已更改为: {theme}")
    
    def show_error(self, error_message: str) -> None:
        """显示错误信息"""
        error_data = {
            'source': 'error',
            'answer': error_message
        }
        self.show_answer(error_data)
    
    def show_status(self, status_message: str) -> None:
        """显示状态信息"""
        if self.root:
            self.root.after(0, lambda: self.status_label.config(text=status_message))
    
    def destroy(self) -> None:
        """销毁窗口"""
        try:
            if self.auto_hide_timer:
                self.auto_hide_timer.cancel()
            
            if self.root:
                self.root.quit()
                self.root.destroy()
                
            logging.info("悬浮窗口已销毁")
            
        except Exception as e:
            logging.error(f"销毁窗口失败: {e}")


def test_floating_window():
    """测试悬浮窗口"""
    config = ConfigManager()
    window = FloatingWindow(config)
    
    # 测试显示答案
    test_answer = {
        'source': 'excel',
        'match_score': 0.95,
        'answer_info': {
            'options': {
                'A': '选项A内容',
                'B': '选项B内容',
                'C': '选项C内容',
                'D': '选项D内容'
            },
            'correct_answer': 'B',
            'answer_text': '选项B内容'
        }
    }
    
    # 延迟显示测试
    import threading
    def delayed_show():
        time.sleep(2)
        window.show_answer(test_answer)
    
    threading.Thread(target=delayed_show, daemon=True).start()
    
    # 保持程序运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        window.destroy()


if __name__ == "__main__":
    test_floating_window()
