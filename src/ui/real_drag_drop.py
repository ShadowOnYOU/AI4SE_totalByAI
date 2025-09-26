# -*- coding: utf-8 -*-
"""
真正的拖拽上传功能模块
使用tkinterdnd2实现真正的文件拖拽功能
"""

import tkinter as tk
from tkinter import messagebox
import os
from typing import List, Callable, Optional

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False
    print("Warning: tkinterdnd2 not available, falling back to click-to-select mode")

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import Config
from components.file_manager import ImageFileManager

class RealDragDrop:
    """真正的拖拽处理器"""
    
    def __init__(self, target_widget, callback: Optional[Callable] = None):
        """初始化拖拽处理器
        
        Args:
            target_widget: 目标控件
            callback: 文件拖拽成功后的回调函数
        """
        self.target_widget = target_widget
        self.callback = callback
        self.file_manager = ImageFileManager()
        
        # 设置拖拽目标
        self.setup_drag_drop()
    
    def setup_drag_drop(self):
        """设置拖拽目标"""
        if self.target_widget is None:
            return
        
        # 设置拖拽目标样式
        self.setup_style()
        
        # 添加拖拽提示
        self.add_drop_hint()
        
        if DRAG_DROP_AVAILABLE:
            # 使用tkinterdnd2进行真正的文件拖拽
            self.setup_real_drag_drop()
        else:
            # 降级到点击选择模式
            self.setup_fallback_mode()
    
    def setup_style(self):
        """设置样式"""
        try:
            # 设置拖拽区域样式
            if hasattr(self.target_widget, 'configure'):
                # 检查控件类型，不同控件支持不同属性
                widget_class = self.target_widget.__class__.__name__
                if widget_class == 'Canvas':
                    self.target_widget.configure(
                        bg='#f0f8ff',  # 浅蓝色背景
                        relief='raised',
                        bd=2
                    )
                elif widget_class == 'Treeview':
                    # Treeview不支持bg属性，跳过样式设置
                    pass
                else:
                    # 尝试设置基本样式
                    try:
                        self.target_widget.configure(bg='#f0f8ff')
                    except:
                        pass
        except Exception as e:
            print(f"设置样式失败: {e}")
    
    def add_drop_hint(self):
        """添加拖拽提示"""
        if hasattr(self.target_widget, 'create_text'):
            # 如果是Canvas控件
            if DRAG_DROP_AVAILABLE:
                hint_text = "拖拽图片文件到此处"
                hint_subtext = "支持 JPG, PNG, BMP, TIFF 格式"
            else:
                hint_text = "点击选择图片文件"
                hint_subtext = "拖拽功能不可用，请点击选择"
            
            # 清除现有提示
            self.target_widget.delete("drop_hint")
            
            # 获取Canvas尺寸
            canvas_width = self.target_widget.winfo_width()
            canvas_height = self.target_widget.winfo_height()
            
            # 如果Canvas还没有显示，使用默认尺寸
            if canvas_width <= 1:
                canvas_width = 400
            if canvas_height <= 1:
                canvas_height = 300
            
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            
            # 主提示文本
            self.hint_text = self.target_widget.create_text(
                center_x, center_y - 20,
                text=hint_text,
                font=("Arial", 14, "bold"),
                fill="#4a90e2",
                justify=tk.CENTER,
                tags="drop_hint"
            )
            
            # 副提示文本
            self.hint_subtext = self.target_widget.create_text(
                center_x, center_y + 10,
                text=hint_subtext,
                font=("Arial", 10),
                fill="#7d7d7d",
                justify=tk.CENTER,
                tags="drop_hint"
            )
    
    def setup_real_drag_drop(self):
        """设置真正的拖拽功能"""
        try:
            # 注册拖拽目标
            self.target_widget.drop_target_register(DND_FILES)
            
            # 绑定拖拽事件
            self.target_widget.dnd_bind('<<DropEnter>>', self.on_drag_enter)
            self.target_widget.dnd_bind('<<DropPosition>>', self.on_drag_position)
            self.target_widget.dnd_bind('<<DropLeave>>', self.on_drag_leave)
            self.target_widget.dnd_bind('<<Drop>>', self.on_drop)
            
            print("真正的拖拽功能已启用")
            
        except Exception as e:
            print(f"设置真正拖拽功能失败: {e}")
            # 降级到点击选择模式
            self.setup_fallback_mode()
    
    def setup_fallback_mode(self):
        """设置降级模式（点击选择）"""
        self.target_widget.bind('<Button-1>', self.on_click)
        self.target_widget.bind('<Double-Button-1>', self.on_click)
        print("使用点击选择模式")
    
    def on_drag_enter(self, event):
        """拖拽进入事件"""
        try:
            # 改变样式表示拖拽进入
            widget_class = self.target_widget.__class__.__name__
            if widget_class == 'Canvas':
                self.target_widget.configure(bg='#e8f5e8', relief='sunken', bd=3)
            elif widget_class != 'Treeview':
                try:
                    self.target_widget.configure(bg='#e8f5e8')
                except:
                    pass
            
            # 更新提示文本
            if hasattr(self, 'hint_text'):
                self.target_widget.itemconfig(
                    self.hint_text, 
                    text="松开鼠标放置文件", 
                    fill="green"
                )
                self.target_widget.itemconfig(
                    self.hint_subtext, 
                    text="检测到文件拖拽", 
                    fill="darkgreen"
                )
        except Exception as e:
            print(f"拖拽进入事件处理失败: {e}")
    
    def on_drag_position(self, event):
        """拖拽位置事件"""
        # 可以在这里添加拖拽位置的视觉反馈
        pass
    
    def on_drag_leave(self, event):
        """拖拽离开事件"""
        try:
            # 恢复原始样式
            widget_class = self.target_widget.__class__.__name__
            if widget_class == 'Canvas':
                self.target_widget.configure(bg='#f0f8ff', relief='raised', bd=2)
            elif widget_class != 'Treeview':
                try:
                    self.target_widget.configure(bg='#f0f8ff')
                except:
                    pass
            
            # 恢复提示文本
            if hasattr(self, 'hint_text'):
                self.target_widget.itemconfig(
                    self.hint_text, 
                    text="拖拽图片文件到此处", 
                    fill="#4a90e2"
                )
                self.target_widget.itemconfig(
                    self.hint_subtext, 
                    text="支持 JPG, PNG, BMP, TIFF 格式", 
                    fill="#7d7d7d"
                )
        except Exception as e:
            print(f"拖拽离开事件处理失败: {e}")
    
    def on_drop(self, event):
        """文件拖拽放置事件"""
        try:
            # 恢复样式
            widget_class = self.target_widget.__class__.__name__
            if widget_class == 'Canvas':
                self.target_widget.configure(bg='#f0f8ff', relief='raised', bd=2)
            elif widget_class != 'Treeview':
                try:
                    self.target_widget.configure(bg='#f0f8ff')
                except:
                    pass
            
            # 获取拖拽的文件路径
            files = self.target_widget.tk.splitlist(event.data)
            
            if files:
                self.process_dropped_files(files)
            
        except Exception as e:
            print(f"处理拖拽文件失败: {e}")
            messagebox.showerror("错误", f"处理拖拽文件失败: {e}")
    
    def on_click(self, event):
        """点击事件处理（降级模式）"""
        try:
            self.select_files()
        except Exception as e:
            print(f"点击选择文件失败: {e}")
    
    def select_files(self):
        """选择文件（降级模式）"""
        try:
            from tkinter import filedialog
            
            files = filedialog.askopenfilenames(
                title="选择图片文件",
                filetypes=[
                    ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                    ("JPEG文件", "*.jpg *.jpeg"),
                    ("PNG文件", "*.png"),
                    ("BMP文件", "*.bmp"),
                    ("TIFF文件", "*.tiff *.tif"),
                    ("所有文件", "*.*")
                ]
            )
            
            if files:
                self.process_dropped_files(files)
                
        except Exception as e:
            messagebox.showerror("错误", f"选择文件失败: {e}")
    
    def process_dropped_files(self, file_paths: List[str]):
        """处理拖拽的文件"""
        try:
            valid_files = []
            invalid_files = []
            
            for file_path in file_paths:
                # 处理可能的特殊字符
                file_path = file_path.strip('{}')
                
                if self.file_manager.validate_image_file(file_path):
                    valid_files.append(file_path)
                else:
                    invalid_files.append(os.path.basename(file_path))
            
            # 显示结果
            if invalid_files:
                messagebox.showwarning(
                    "警告", 
                    f"以下文件格式不支持，已跳过:\n{', '.join(invalid_files)}"
                )
            
            if valid_files:
                # 更新提示文本
                if hasattr(self, 'hint_text'):
                    self.target_widget.itemconfig(
                        self.hint_text, 
                        text=f"成功导入 {len(valid_files)} 个文件", 
                        fill="green"
                    )
                    
                    if len(valid_files) == 1:
                        filename = os.path.basename(valid_files[0])
                        self.target_widget.itemconfig(
                            self.hint_subtext, 
                            text=filename, 
                            fill="darkgreen"
                        )
                    else:
                        self.target_widget.itemconfig(
                            self.hint_subtext, 
                            text=f"包含 {len(valid_files)} 个图片文件", 
                            fill="darkgreen"
                        )
                
                # 调用回调函数
                if self.callback:
                    self.callback(valid_files)
            
        except Exception as e:
            print(f"处理文件失败: {e}")
            messagebox.showerror("错误", f"处理文件失败: {e}")
    
    def update_hint_text(self, text: str):
        """更新提示文本"""
        try:
            if hasattr(self, 'hint_text'):
                self.target_widget.itemconfig(self.hint_text, text=text)
        except Exception as e:
            print(f"更新提示文本失败: {e}")
    
    def refresh_hints(self):
        """刷新提示（在窗口大小改变时调用）"""
        try:
            self.add_drop_hint()
        except Exception as e:
            print(f"刷新提示失败: {e}")

class RealDragDropManager:
    """真正的拖拽管理器"""
    
    def __init__(self, main_window):
        """初始化拖拽管理器"""
        self.main_window = main_window
        self.drop_handlers = {}
        
        # 如果支持真正的拖拽，初始化TkinterDnD
        if DRAG_DROP_AVAILABLE:
            try:
                # 确保主窗口支持DnD
                if hasattr(main_window, 'parent'):
                    root = main_window.parent
                else:
                    root = main_window
                
                # 初始化TkinterDnD
                if not hasattr(root, '_dnd_initialized'):
                    root._dnd_initialized = True
                    print("TkinterDnD 已初始化")
                
            except Exception as e:
                print(f"初始化TkinterDnD失败: {e}")
    
    def add_drop_target(self, widget, target_name: str, callback: Optional[Callable] = None):
        """添加拖拽目标
        
        Args:
            widget: 目标控件
            target_name: 目标名称
            callback: 回调函数
        """
        try:
            handler = RealDragDrop(widget, callback)
            self.drop_handlers[target_name] = handler
            return handler
        except Exception as e:
            print(f"添加拖拽目标失败: {e}")
            return None
    
    def remove_drop_target(self, target_name: str):
        """移除拖拽目标"""
        if target_name in self.drop_handlers:
            del self.drop_handlers[target_name]
    
    def update_drop_hints(self, target_name: str, text: str):
        """更新拖拽提示"""
        if target_name in self.drop_handlers:
            self.drop_handlers[target_name].update_hint_text(text)
    
    def refresh_all_hints(self):
        """刷新所有提示"""
        for handler in self.drop_handlers.values():
            handler.refresh_hints()

def create_dnd_root(root_class=tk.Tk):
    """创建支持DnD的根窗口"""
    if DRAG_DROP_AVAILABLE:
        try:
            # 使用TkinterDnD.Tk作为根窗口
            return TkinterDnD.Tk()
        except Exception as e:
            print(f"创建DnD根窗口失败: {e}")
            return root_class()
    else:
        return root_class()
