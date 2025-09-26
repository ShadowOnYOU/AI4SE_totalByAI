# -*- coding: utf-8 -*-
"""
图片水印工具主程序入口
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from main_window import MainWindow
from ui.real_drag_drop import create_dnd_root

class WatermarkApp:
    """主应用程序类"""
    
    def __init__(self):
        """初始化应用程序"""
        self.root = None
        self.config = None
        self.init_app()
    
    def init_app(self):
        """初始化应用"""
        try:
            # 加载配置
            self.config = Config.load_config()
            
            # 确保必要目录存在
            Config.ensure_directories()
            
            # 创建主窗口
            self.create_main_window()
            
        except Exception as e:
            error_msg = "App initialization failed"
            print(f"{error_msg}: {e}")
            messagebox.showerror("Error", f"{error_msg}: {e}")
            sys.exit(1)
    
    def create_main_window(self):
        """创建主窗口"""
        self.root = create_dnd_root()
        
        # 设置窗口属性
        self.root.title(Config.WINDOW_TITLE)
        self.root.geometry(self.config.get('window_geometry', Config.WINDOW_SIZE))
        self.root.minsize(*Config.MIN_WINDOW_SIZE)
        
        # 设置窗口图标（如果有的话）
        try:
            # 这里可以设置应用图标
            pass
        except:
            pass
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主界面
        self.main_window = MainWindow(self.root)
        
        # 居中显示窗口
        self.center_window()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入图片", command=self.import_images)
        file_menu.add_command(label="导入文件夹", command=self.import_folder)
        file_menu.add_separator()
        file_menu.add_command(label="导出图片", command=self.export_images)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="清空列表", command=self.clear_image_list)
        
        # 水印菜单
        watermark_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="水印", menu=watermark_menu)
        watermark_menu.add_command(label="文本水印", command=self.set_text_watermark)
        watermark_menu.add_command(label="图片水印", command=self.set_image_watermark)
        watermark_menu.add_command(label="EXIF时间水印", command=self.set_exif_watermark)
        
        # 模板菜单
        template_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="模板", menu=template_menu)
        template_menu.add_command(label="保存模板", command=self.save_template)
        template_menu.add_command(label="加载模板", command=self.load_template)
        template_menu.add_separator()
        template_menu.add_command(label="管理模板", command=self.manage_templates)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def update_status(self, message: str):
        """更新状态栏"""
        if hasattr(self, 'main_window'):
            self.main_window.update_status(message)
    
    # 菜单命令方法（占位符，后续实现）
    def import_images(self):
        """导入图片"""
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.import_images()
        else:
            messagebox.showinfo("提示", "请先启动主窗口")
    
    def import_folder(self):
        """导入文件夹"""
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.import_folder()
        else:
            messagebox.showinfo("提示", "请先启动主窗口")
    
    def export_images(self):
        """导出图片"""
        self.update_status("导出图片功能开发中...")
        messagebox.showinfo("提示", "导出图片功能开发中...")
    
    def clear_image_list(self):
        """清空图片列表"""
        self.update_status("清空图片列表功能开发中...")
        messagebox.showinfo("提示", "清空图片列表功能开发中...")
    
    def set_text_watermark(self):
        """设置文本水印"""
        self.update_status("文本水印功能开发中...")
        messagebox.showinfo("提示", "文本水印功能开发中...")
    
    def set_image_watermark(self):
        """设置图片水印"""
        if hasattr(self, 'main_window') and self.main_window:
            # 切换到图片水印模式
            self.main_window.watermark_type_var.set("image")
            self.main_window.on_watermark_type_changed()
            self.update_status("已切换到图片水印模式")
        else:
            messagebox.showinfo("提示", "请先启动主窗口")
    
    def set_exif_watermark(self):
        """设置EXIF时间水印"""
        if hasattr(self, 'main_window') and self.main_window:
            # 切换到EXIF水印模式
            self.main_window.watermark_type_var.set("exif")
            self.main_window.on_watermark_type_changed()
            self.update_status("已切换到EXIF时间水印模式")
        else:
            messagebox.showinfo("提示", "请先启动主窗口")
    
    def save_template(self):
        """保存模板"""
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.save_current_template()
        else:
            messagebox.showinfo("提示", "请先启动主窗口")
    
    def load_template(self):
        """加载模板"""
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.load_template()
        else:
            messagebox.showinfo("提示", "请先启动主窗口")
    
    def manage_templates(self):
        """管理模板"""
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.manage_templates()
        else:
            messagebox.showinfo("提示", "请先启动主窗口")
    
    def show_about(self):
        """显示关于对话框"""
        about_text = f"""
图片水印工具 v1.0

基于Python 3.6开发
使用tkinter作为GUI框架

功能特性：
- 支持多种图片格式
- 文本水印和图片水印
- EXIF时间水印
- 批量处理
- 模板管理

开发时间：2025年
        """
        messagebox.showinfo("关于", about_text)
    
    def on_closing(self):
        """窗口关闭事件处理"""
        try:
            # 保存当前配置
            if self.config:
                Config.save_config(self.config)
            self.root.destroy()
        except Exception as e:
            print("Error during app closing:", str(e))
            self.root.destroy()
    
    def run(self):
        """运行应用程序"""
        try:
            self.update_status("应用程序启动完成")
            self.root.mainloop()
        except Exception as e:
            print("Error during app running:", str(e))
            messagebox.showerror("Error", f"Error during app running: {e}")

def main():
    """主函数"""
    try:
        app = WatermarkApp()
        app.run()
    except Exception as e:
        print("Program startup failed:", str(e))
        messagebox.showerror("Error", f"Program startup failed: {e}")

if __name__ == "__main__":
    main()
