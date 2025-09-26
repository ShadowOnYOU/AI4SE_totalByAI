# -*- coding: utf-8 -*-
"""
改进的拖拽上传功能模块
使用更简单和可靠的方法实现拖拽上传
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from typing import List, Callable, Optional

from config import Config
from file_manager import ImageFileManager

class SimpleDragDrop:
    """简化的拖拽处理器"""
    
    def __init__(self, target_widget, callback: Optional[Callable] = None):
        """初始化拖拽处理器
        
        Args:
            target_widget: 目标控件
            callback: 文件选择成功后的回调函数
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
        
        # 绑定点击事件来触发文件选择
        self.target_widget.bind('<Button-1>', self.on_click)
        
        # 绑定拖拽相关事件
        self.target_widget.bind('<B1-Motion>', self.on_drag_motion)
        self.target_widget.bind('<ButtonRelease-1>', self.on_drag_release)
        
        # 设置拖拽目标样式
        self.setup_style()
        
        # 添加拖拽提示
        self.add_drop_hint()
        
        # 拖拽状态
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
    
    def setup_style(self):
        """设置样式"""
        try:
            # 尝试设置背景色
            if hasattr(self.target_widget, 'configure'):
                self.target_widget.configure(bg='lightblue')
        except:
            pass
    
    def add_drop_hint(self):
        """添加拖拽提示"""
        if hasattr(self.target_widget, 'create_text'):
            # 如果是Canvas控件
            self.hint_text = self.target_widget.create_text(
                200, 120,
                text="点击选择图片文件",
                font=("Arial", 14),
                fill="gray",
                justify=tk.CENTER,
                tags="drop_hint"
            )
            self.hint_text2 = self.target_widget.create_text(
                200, 150,
                text="或拖拽图片到此处",
                font=("Arial", 12),
                fill="lightgray",
                justify=tk.CENTER,
                tags="drop_hint"
            )
    
    def on_click(self, event):
        """点击事件处理"""
        # 如果正在拖拽，不处理点击
        if self.is_dragging:
            return
        
        # 打开文件选择对话框
        self.select_files()
    
    def on_drag_motion(self, event):
        """拖拽移动事件"""
        if not hasattr(self, 'drag_start_x'):
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.is_dragging = False
            return
        
        # 计算拖拽距离
        dx = abs(event.x - self.drag_start_x)
        dy = abs(event.y - self.drag_start_y)
        
        # 如果移动距离超过阈值，认为是拖拽操作
        if dx > 10 or dy > 10:
            self.is_dragging = True
            # 改变样式表示正在拖拽
            try:
                if hasattr(self.target_widget, 'configure'):
                    self.target_widget.configure(bg='lightgreen')
            except:
                pass
            
            if hasattr(self, 'hint_text'):
                self.target_widget.itemconfig(self.hint_text, text="松开鼠标选择文件", fill="green")
    
    def on_drag_release(self, event):
        """拖拽释放事件"""
        if self.is_dragging:
            # 恢复样式
            try:
                if hasattr(self.target_widget, 'configure'):
                    self.target_widget.configure(bg='lightblue')
            except:
                pass
            
            if hasattr(self, 'hint_text'):
                self.target_widget.itemconfig(self.hint_text, text="点击选择图片文件", fill="gray")
                self.target_widget.itemconfig(self.hint_text2, text="或拖拽图片到此处", fill="lightgray")
            
            # 打开文件选择对话框
            self.select_files()
        
        self.is_dragging = False
    
    def select_files(self):
        """选择文件"""
        try:
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
                self.process_files(files)
                
        except Exception as e:
            messagebox.showerror("错误", f"选择文件失败: {e}")
    
    def process_files(self, file_paths: List[str]):
        """处理选择的文件"""
        try:
            valid_files = []
            invalid_files = []
            
            for file_path in file_paths:
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
            
            if valid_files and self.callback:
                self.callback(valid_files)
            
            # 更新提示文本
            if valid_files and hasattr(self, 'hint_text'):
                self.target_widget.itemconfig(
                    self.hint_text, 
                    text=f"已选择 {len(valid_files)} 个文件", 
                    fill="green"
                )
                if len(valid_files) == 1:
                    filename = os.path.basename(valid_files[0])
                    self.target_widget.itemconfig(
                        self.hint_text2, 
                        text=filename, 
                        fill="darkgreen"
                    )
                else:
                    self.target_widget.itemconfig(
                        self.hint_text2, 
                        text=f"包含 {len(valid_files)} 个文件", 
                        fill="darkgreen"
                    )
            
        except Exception as e:
            messagebox.showerror("错误", f"处理文件失败: {e}")
    
    def update_hint_text(self, text: str):
        """更新提示文本"""
        if hasattr(self, 'hint_text'):
            self.target_widget.itemconfig(self.hint_text, text=text)

class DragDropManager:
    """拖拽管理器"""
    
    def __init__(self, main_window):
        """初始化拖拽管理器"""
        self.main_window = main_window
        self.drop_handlers = {}
    
    def add_drop_target(self, widget, target_name: str, callback: Optional[Callable] = None):
        """添加拖拽目标
        
        Args:
            widget: 目标控件
            target_name: 目标名称
            callback: 回调函数
        """
        handler = SimpleDragDrop(widget, callback)
        self.drop_handlers[target_name] = handler
        return handler
    
    def remove_drop_target(self, target_name: str):
        """移除拖拽目标"""
        if target_name in self.drop_handlers:
            del self.drop_handlers[target_name]
    
    def update_drop_hints(self, target_name: str, text: str):
        """更新拖拽提示"""
        if target_name in self.drop_handlers:
            self.drop_handlers[target_name].update_hint_text(text)

