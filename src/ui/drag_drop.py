# -*- coding: utf-8 -*-
"""
拖拽上传功能模块
支持将图片文件拖拽到应用程序中
"""

import tkinter as tk
from tkinter import messagebox
import os
from typing import List, Callable, Optional

from config import Config
from components.file_manager import ImageFileManager

class DragDropHandler:
    """拖拽处理类"""
    
    def __init__(self, target_widget, callback: Optional[Callable] = None):
        """初始化拖拽处理器
        
        Args:
            target_widget: 目标控件
            callback: 文件拖拽成功后的回调函数
        """
        self.target_widget = target_widget
        self.callback = callback
        self.file_manager = ImageFileManager()
        
        # 绑定拖拽事件
        self.setup_drag_drop()
    
    def setup_drag_drop(self):
        """设置拖拽事件绑定"""
        # 绑定拖拽进入事件
        self.target_widget.bind('<B1-Motion>', self.on_drag_motion)
        self.target_widget.bind('<Button-1>', self.on_drag_start)
        
        # 绑定拖拽相关事件
        self.target_widget.bind('<ButtonRelease-1>', self.on_drag_end)
        
        # 绑定文件拖拽事件（macOS和Windows）
        self.target_widget.bind('<B1-Motion>', self.on_drag_motion)
        
        # 设置拖拽目标
        self.target_widget.configure(cursor='hand2')
    
    def on_drag_start(self, event):
        """拖拽开始事件"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.is_dragging = False
    
    def on_drag_motion(self, event):
        """拖拽移动事件"""
        if hasattr(self, 'drag_start_x'):
            # 计算拖拽距离
            dx = abs(event.x - self.drag_start_x)
            dy = abs(event.y - self.drag_start_y)
            
            # 如果移动距离超过阈值，认为是拖拽操作
            if dx > 5 or dy > 5:
                self.is_dragging = True
                # 改变鼠标样式
                self.target_widget.configure(cursor='hand2')
    
    def on_drag_end(self, event):
        """拖拽结束事件"""
        if hasattr(self, 'is_dragging') and self.is_dragging:
            # 处理拖拽结束
            self.target_widget.configure(cursor='')
            self.is_dragging = False

class FileDropHandler:
    """文件拖拽处理器（跨平台）"""
    
    def __init__(self, target_widget, callback: Optional[Callable] = None):
        """初始化文件拖拽处理器
        
        Args:
            target_widget: 目标控件
            callback: 文件拖拽成功后的回调函数
        """
        self.target_widget = target_widget
        self.callback = callback
        self.file_manager = ImageFileManager()
        
        # 设置拖拽目标
        self.setup_file_drop()
    
    def setup_file_drop(self):
        """设置文件拖拽目标"""
        # 绑定拖拽进入和离开事件
        self.target_widget.bind('<Enter>', self.on_drag_enter)
        self.target_widget.bind('<Leave>', self.on_drag_leave)
        
        # 绑定拖拽相关事件
        self.target_widget.bind('<B1-Motion>', self.on_drag_motion)
        self.target_widget.bind('<ButtonRelease-1>', self.on_drag_release)
        
        # 设置拖拽目标样式
        self.target_widget.configure(relief='raised', bd=2)
        
        # 添加拖拽提示文本
        self.add_drop_hint()
    
    def add_drop_hint(self):
        """添加拖拽提示"""
        if hasattr(self.target_widget, 'create_text'):
            # 如果是Canvas控件
            self.hint_text = self.target_widget.create_text(
                self.target_widget.winfo_width()//2, 
                self.target_widget.winfo_height()//2,
                text="拖拽图片文件到此处\n或点击导入图片",
                font=("Arial", 12),
                fill="gray",
                justify=tk.CENTER
            )
        elif hasattr(self.target_widget, 'configure'):
            # 如果是其他控件，设置背景色提示
            try:
                self.target_widget.configure(bg='lightblue')
            except:
                pass
    
    def on_drag_enter(self, event):
        """拖拽进入事件"""
        try:
            self.target_widget.configure(relief='sunken', bd=3, bg='lightgreen')
        except:
            try:
                self.target_widget.configure(bg='lightgreen')
            except:
                pass
        if hasattr(self, 'hint_text'):
            self.target_widget.itemconfig(self.hint_text, text="松开鼠标放置文件", fill="green")
    
    def on_drag_leave(self, event):
        """拖拽离开事件"""
        try:
            self.target_widget.configure(relief='raised', bd=2, bg='lightblue')
        except:
            try:
                self.target_widget.configure(bg='lightblue')
            except:
                pass
        if hasattr(self, 'hint_text'):
            self.target_widget.itemconfig(self.hint_text, text="拖拽图片文件到此处\n或点击导入图片", fill="gray")
    
    def on_drag_motion(self, event):
        """拖拽移动事件"""
        # 这里可以添加拖拽过程中的视觉反馈
        pass
    
    def on_drag_release(self, event):
        """拖拽释放事件"""
        # 恢复原始样式
        self.target_widget.configure(relief='raised', bd=2, bg='lightblue')
        if hasattr(self, 'hint_text'):
            self.target_widget.itemconfig(self.hint_text, text="拖拽图片文件到此处\n或点击导入图片", fill="gray")

class AdvancedDragDrop:
    """高级拖拽处理器（支持实际文件拖拽）"""
    
    def __init__(self, target_widget, callback: Optional[Callable] = None):
        """初始化高级拖拽处理器
        
        Args:
            target_widget: 目标控件
            callback: 文件拖拽成功后的回调函数
        """
        self.target_widget = target_widget
        self.callback = callback
        self.file_manager = ImageFileManager()
        
        # 设置拖拽目标
        self.setup_advanced_drop()
    
    def setup_advanced_drop(self):
        """设置高级拖拽目标"""
        if self.target_widget is None:
            return
            
        # 绑定拖拽事件
        self.target_widget.bind('<B1-Motion>', self.on_drag_motion)
        self.target_widget.bind('<Button-1>', self.on_drag_start)
        self.target_widget.bind('<ButtonRelease-1>', self.on_drag_release)
        
        # 设置拖拽目标样式
        try:
            self.target_widget.configure(relief='raised', bd=2, bg='lightblue')
        except:
            try:
                # 某些控件不支持relief属性，只设置背景色
                self.target_widget.configure(bg='lightblue')
            except:
                # 某些控件不支持bg属性，跳过样式设置
                pass
        
        # 添加拖拽提示
        self.add_drop_hint()
        
        # 拖拽状态
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
    
    def add_drop_hint(self):
        """添加拖拽提示"""
        if hasattr(self.target_widget, 'create_text'):
            # 如果是Canvas控件
            self.hint_text = self.target_widget.create_text(
                200, 150,
                text="拖拽图片文件到此处\n或点击导入图片",
                font=("Arial", 12),
                fill="gray",
                justify=tk.CENTER,
                tags="drop_hint"
            )
    
    def on_drag_start(self, event):
        """拖拽开始"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.is_dragging = False
    
    def on_drag_motion(self, event):
        """拖拽移动"""
        if hasattr(self, 'drag_start_x'):
            dx = abs(event.x - self.drag_start_x)
            dy = abs(event.y - self.drag_start_y)
            
            if dx > 10 or dy > 10:
                self.is_dragging = True
                # 改变样式表示正在拖拽
                self.target_widget.configure(relief='sunken', bd=3, bg='lightgreen')
                if hasattr(self, 'hint_text'):
                    self.target_widget.itemconfig(self.hint_text, text="松开鼠标放置文件", fill="green")
    
    def on_drag_release(self, event):
        """拖拽释放"""
        if self.is_dragging:
            # 模拟文件选择对话框
            self.simulate_file_selection()
        
        # 恢复样式
        try:
            self.target_widget.configure(relief='raised', bd=2, bg='lightblue')
        except:
            try:
                self.target_widget.configure(bg='lightblue')
            except:
                pass
        if hasattr(self, 'hint_text'):
            self.target_widget.itemconfig(self.hint_text, text="拖拽图片文件到此处\n或点击导入图片", fill="gray")
        
        self.is_dragging = False
    
    def simulate_file_selection(self):
        """模拟文件选择（因为tkinter不支持真正的文件拖拽）"""
        from tkinter import filedialog
        
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("所有文件", "*.*")
            ]
        )
        
        if files:
            self.process_dropped_files(files)
    
    def process_dropped_files(self, file_paths: List[str]):
        """处理拖拽的文件"""
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
        handler = AdvancedDragDrop(widget, callback)
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
