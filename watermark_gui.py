#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import piexif
from datetime import datetime
import shutil
import threading

class WatermarkApp(tk.Tk):
    def __init__(self):
        super(WatermarkApp, self).__init__()
        
        # 应用程序基本设置
        self.title("图片水印工具")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # 应用程序变量
        self.imported_images = []  # 存储导入的图片路径
        self.output_directory = ""
        self.current_preview_image = None
        
        # 创建主框架
        self.create_main_frame()
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建状态栏
        self.create_status_bar()
        
    def create_main_frame(self):
        """创建主框架，包含左侧图片列表和右侧预览/设置区域"""
        # 主分割窗口
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧框架 - 图片列表
        self.left_frame = ttk.LabelFrame(self.main_paned, text="导入的图片")
        self.main_paned.add(self.left_frame, weight=1)
        
        # 图片列表框架
        self.create_image_list_frame()
        
        # 右侧框架 - 预览和设置
        self.right_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.right_frame, weight=2)
        
        # 右侧上部 - 预览区域
        self.preview_frame = ttk.LabelFrame(self.right_frame, text="预览")
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 预览画布
        self.preview_canvas = tk.Canvas(self.preview_frame, bg="lightgray")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 右侧下部 - 设置区域
        self.settings_frame = ttk.LabelFrame(self.right_frame, text="导出设置")
        self.settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建导出设置
        self.create_export_settings()
        
    def create_image_list_frame(self):
        """创建图片列表区域"""
        # 图片列表框架内的工具栏
        self.image_toolbar = ttk.Frame(self.left_frame)
        self.image_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # 导入按钮
        self.import_btn = ttk.Button(self.image_toolbar, text="导入图片", command=self.import_images)
        self.import_btn.pack(side=tk.LEFT, padx=2)
        
        self.import_folder_btn = ttk.Button(self.image_toolbar, text="导入文件夹", command=self.import_folder)
        self.import_folder_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_btn = ttk.Button(self.image_toolbar, text="清空列表", command=self.clear_image_list)
        self.clear_btn.pack(side=tk.RIGHT, padx=2)
        
        # 图片列表
        self.image_list_frame = ttk.Frame(self.left_frame)
        self.image_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 滚动条
        self.scrollbar = ttk.Scrollbar(self.image_list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 使用Treeview显示图片列表
        self.image_list = ttk.Treeview(self.image_list_frame, 
                                       columns=("name", "format", "size"),
                                       show="headings",
                                       yscrollcommand=self.scrollbar.set)
        
        # 定义列
        self.image_list.heading("name", text="文件名")
        self.image_list.heading("format", text="格式")
        self.image_list.heading("size", text="大小")
        
        self.image_list.column("name", width=150)
        self.image_list.column("format", width=50)
        self.image_list.column("size", width=80)
        
        self.image_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.image_list.yview)
        
        # 绑定选择事件
        self.image_list.bind("<<TreeviewSelect>>", self.on_image_select)
        
    def create_export_settings(self):
        """创建导出设置区域"""
        # 输出文件夹设置
        output_frame = ttk.Frame(self.settings_frame)
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(output_frame, text="输出文件夹:").pack(side=tk.LEFT, padx=5)
        self.output_path_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="浏览...", command=self.select_output_folder).pack(side=tk.LEFT, padx=5)
        
        # 文件命名规则
        naming_frame = ttk.LabelFrame(self.settings_frame, text="文件命名规则")
        naming_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 命名选项
        self.naming_option = tk.StringVar(value="original")
        ttk.Radiobutton(naming_frame, text="保留原文件名", variable=self.naming_option, value="original").pack(anchor=tk.W, padx=5, pady=2)
        
        # 前缀选项
        prefix_frame = ttk.Frame(naming_frame)
        prefix_frame.pack(fill=tk.X, padx=5, pady=2)
        self.use_prefix = tk.BooleanVar(value=False)
        ttk.Checkbutton(prefix_frame, text="添加前缀", variable=self.use_prefix).pack(side=tk.LEFT)
        self.prefix_var = tk.StringVar(value="wm_")
        ttk.Entry(prefix_frame, textvariable=self.prefix_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # 后缀选项
        suffix_frame = ttk.Frame(naming_frame)
        suffix_frame.pack(fill=tk.X, padx=5, pady=2)
        self.use_suffix = tk.BooleanVar(value=False)
        ttk.Checkbutton(suffix_frame, text="添加后缀", variable=self.use_suffix).pack(side=tk.LEFT)
        self.suffix_var = tk.StringVar(value="_watermarked")
        ttk.Entry(suffix_frame, textvariable=self.suffix_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # 输出格式
        format_frame = ttk.LabelFrame(self.settings_frame, text="输出格式")
        format_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.output_format = tk.StringVar(value="jpeg")
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.output_format, value="jpeg", 
                        command=self.toggle_jpeg_options).pack(side=tk.LEFT, padx=15)
        ttk.Radiobutton(format_frame, text="PNG", variable=self.output_format, value="png", 
                        command=self.toggle_jpeg_options).pack(side=tk.LEFT, padx=15)
        
        # JPEG质量设置
        self.jpeg_quality_frame = ttk.Frame(format_frame)
        self.jpeg_quality_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(self.jpeg_quality_frame, text="JPEG质量:").pack(side=tk.LEFT, padx=5)
        self.jpeg_quality = tk.IntVar(value=85)
        self.jpeg_quality_scale = ttk.Scale(self.jpeg_quality_frame, from_=0, to=100, 
                                           variable=self.jpeg_quality, orient=tk.HORIZONTAL)
        self.jpeg_quality_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.jpeg_quality_label = ttk.Label(self.jpeg_quality_frame, text="85")
        self.jpeg_quality_label.pack(side=tk.LEFT, padx=5)
        self.jpeg_quality.trace_add("write", self.update_quality_label)
        
        # 图片尺寸调整
        resize_frame = ttk.LabelFrame(self.settings_frame, text="图片尺寸调整 (可选)")
        resize_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.resize_option = tk.StringVar(value="none")
        ttk.Radiobutton(resize_frame, text="保持原始尺寸", variable=self.resize_option, 
                        value="none", command=self.toggle_resize_options).pack(anchor=tk.W, padx=5, pady=2)
        
        # 按宽度调整
        width_frame = ttk.Frame(resize_frame)
        width_frame.pack(fill=tk.X, padx=5, pady=2)
        self.width_radio = ttk.Radiobutton(width_frame, text="按宽度调整:", 
                                          variable=self.resize_option, value="width",
                                          command=self.toggle_resize_options)
        self.width_radio.pack(side=tk.LEFT)
        self.width_var = tk.StringVar(value="800")
        self.width_entry = ttk.Entry(width_frame, textvariable=self.width_var, width=6)
        self.width_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(width_frame, text="像素").pack(side=tk.LEFT)
        
        # 按高度调整
        height_frame = ttk.Frame(resize_frame)
        height_frame.pack(fill=tk.X, padx=5, pady=2)
        self.height_radio = ttk.Radiobutton(height_frame, text="按高度调整:", 
                                           variable=self.resize_option, value="height",
                                           command=self.toggle_resize_options)
        self.height_radio.pack(side=tk.LEFT)
        self.height_var = tk.StringVar(value="600")
        self.height_entry = ttk.Entry(height_frame, textvariable=self.height_var, width=6)
        self.height_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(height_frame, text="像素").pack(side=tk.LEFT)
        
        # 按百分比调整
        percent_frame = ttk.Frame(resize_frame)
        percent_frame.pack(fill=tk.X, padx=5, pady=2)
        self.percent_radio = ttk.Radiobutton(percent_frame, text="按百分比调整:", 
                                            variable=self.resize_option, value="percent",
                                            command=self.toggle_resize_options)
        self.percent_radio.pack(side=tk.LEFT)
        self.percent_var = tk.StringVar(value="50")
        self.percent_entry = ttk.Entry(percent_frame, textvariable=self.percent_var, width=6)
        self.percent_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(percent_frame, text="%").pack(side=tk.LEFT)
        
        # 初始化调整尺寸选项状态
        self.toggle_resize_options()
        
        # 导出按钮
        export_btn_frame = ttk.Frame(self.settings_frame)
        export_btn_frame.pack(fill=tk.X, padx=5, pady=10)
        self.export_btn = ttk.Button(export_btn_frame, text="导出图片", command=self.export_images)
        self.export_btn.pack(side=tk.RIGHT, padx=5)
        
    def create_menu(self):
        """创建菜单栏"""
        self.menu_bar = tk.Menu(self)
        
        # 文件菜单
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="导入图片", command=self.import_images)
        file_menu.add_command(label="导入文件夹", command=self.import_folder)
        file_menu.add_separator()
        file_menu.add_command(label="导出图片", command=self.export_images)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit)
        self.menu_bar.add_cascade(label="文件", menu=file_menu)
        
        # 编辑菜单
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="清空图片列表", command=self.clear_image_list)
        self.menu_bar.add_cascade(label="编辑", menu=edit_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        self.menu_bar.add_cascade(label="帮助", menu=help_menu)
        
        self.config(menu=self.menu_bar)
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Label(self, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def import_images(self):
        """导入图片"""
        filetypes = (
            ("所有支持的图片", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("JPEG 图片", "*.jpg *.jpeg"),
            ("PNG 图片", "*.png"),
            ("BMP 图片", "*.bmp"),
            ("TIFF 图片", "*.tiff *.tif"),
            ("所有文件", "*.*")
        )
        
        file_paths = filedialog.askopenfilenames(
            title="选择图片",
            filetypes=filetypes
        )
        
        if file_paths:
            self.add_images_to_list(file_paths)
            
    def import_folder(self):
        """导入文件夹中的所有图片"""
        folder_path = filedialog.askdirectory(title="选择包含图片的文件夹")
        
        if not folder_path:
            return
            
        supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
        image_paths = []
        
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(supported_extensions):
                    image_paths.append(os.path.join(root, file))
        
        if image_paths:
            self.add_images_to_list(image_paths)
            self.status_bar.config(text="已从文件夹导入 {} 张图片".format(len(image_paths)))
        else:
            messagebox.showinfo("提示", "所选文件夹中没有找到支持的图片文件")
            
    def add_images_to_list(self, file_paths):
        """将图片添加到列表中"""
        for path in file_paths:
            # 检查是否已经在列表中
            if path in self.imported_images:
                continue
                
            try:
                # 获取图片信息
                with Image.open(path) as img:
                    format_name = img.format
                    width, height = img.size
                    file_size = os.path.getsize(path) / 1024  # KB
                    
                # 添加到列表
                filename = os.path.basename(path)
                self.image_list.insert("", tk.END, values=(
                    filename,
                    format_name,
                    "{:.1f} KB".format(file_size)
                ))
                
                # 保存路径
                self.imported_images.append(path)
                
            except Exception as e:
                messagebox.showerror("错误", "无法加载图片 {}: {}".format(path, str(e)))
                
        # 更新状态栏
        self.status_bar.config(text="已导入 {} 张图片".format(len(self.imported_images)))
        
        # 如果这是第一张图片，显示预览
        if len(self.imported_images) == 1:
            self.image_list.selection_set(self.image_list.get_children()[0])
            self.on_image_select(None)
            
    def on_image_select(self, event):
        """当选择图片时显示预览"""
        selected_items = self.image_list.selection()
        if not selected_items:
            return
            
        # 获取选中项的索引
        index = self.image_list.index(selected_items[0])
        if index < 0 or index >= len(self.imported_images):
            return
            
        # 加载并显示预览
        self.load_preview(self.imported_images[index])
        
    def load_preview(self, image_path):
        """加载并显示图片预览"""
        try:
            # 打开图片
            img = Image.open(image_path)
            
            # 调整图片大小以适应预览区域
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # 如果画布尚未完全初始化，使用默认尺寸
            if canvas_width <= 1:
                canvas_width = 500
            if canvas_height <= 1:
                canvas_height = 400
                
            # 计算缩放比例
            img_width, img_height = img.size
            scale = min(canvas_width / img_width, canvas_height / img_height)
            
            # 缩放图片
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            img_resized = img.resize((new_width, new_height), Image.LANCZOS)
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(img_resized)
            
            # 清除画布并显示新图片
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                canvas_width // 2, canvas_height // 2,
                image=photo, anchor=tk.CENTER
            )
            
            # 保持引用以防止垃圾回收
            self.current_preview_image = photo
            
            # 更新状态栏
            filename = os.path.basename(image_path)
            self.status_bar.config(text="预览: {} ({}x{})".format(filename, img_width, img_height))
            
        except Exception as e:
            messagebox.showerror("错误", "无法预览图片: {}".format(str(e)))
            
    def clear_image_list(self):
        """清空图片列表"""
        if not self.imported_images:
            return
            
        if messagebox.askyesno("确认", "确定要清空图片列表吗？"):
            self.image_list.delete(*self.image_list.get_children())
            self.imported_images = []
            self.preview_canvas.delete("all")
            self.current_preview_image = None
            self.status_bar.config(text="就绪")
            
    def select_output_folder(self):
        """选择输出文件夹"""
        folder_path = filedialog.askdirectory(title="选择输出文件夹")
        if folder_path:
            self.output_directory = folder_path
            self.output_path_var.set(folder_path)
            
    def toggle_jpeg_options(self):
        """根据选择的输出格式切换JPEG质量选项"""
        if self.output_format.get() == "jpeg":
            for child in self.jpeg_quality_frame.winfo_children():
                child.configure(state="normal")
        else:
            for child in self.jpeg_quality_frame.winfo_children():
                child.configure(state="disabled")
                
    def update_quality_label(self, *args):
        """更新JPEG质量标签"""
        self.jpeg_quality_label.config(text=str(self.jpeg_quality.get()))
        
    def toggle_resize_options(self):
        """根据选择的调整尺寸选项启用/禁用相应的输入框"""
        resize_option = self.resize_option.get()
        
        # 禁用所有输入框
        self.width_entry.configure(state="disabled")
        self.height_entry.configure(state="disabled")
        self.percent_entry.configure(state="disabled")
        
        # 根据选项启用相应的输入框
        if resize_option == "width":
            self.width_entry.configure(state="normal")
        elif resize_option == "height":
            self.height_entry.configure(state="normal")
        elif resize_option == "percent":
            self.percent_entry.configure(state="normal")
            
    def export_images(self):
        """导出处理后的图片"""
        if not self.imported_images:
            messagebox.showinfo("提示", "没有可导出的图片")
            return
            
        # 检查输出目录
        output_dir = self.output_path_var.get()
        if not output_dir:
            messagebox.showerror("错误", "请选择输出文件夹")
            return
            
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("错误", "无法创建输出文件夹: {}".format(str(e)))
                return
                
        # 获取导出设置
        export_settings = {
            'format': self.output_format.get(),
            'quality': self.jpeg_quality.get() if self.output_format.get() == "jpeg" else None,
            'resize_option': self.resize_option.get(),
            'width': int(self.width_var.get()) if self.width_var.get().isdigit() else None,
            'height': int(self.height_var.get()) if self.height_var.get().isdigit() else None,
            'percent': float(self.percent_var.get()) / 100 if self.percent_var.get().replace('.', '', 1).isdigit() else None,
            'use_prefix': self.use_prefix.get(),
            'prefix': self.prefix_var.get() if self.use_prefix.get() else "",
            'use_suffix': self.use_suffix.get(),
            'suffix': self.suffix_var.get() if self.use_suffix.get() else ""
        }
        
        # 开始导出
        self.status_bar.config(text="正在导出图片...")
        
        # 使用线程避免界面冻结
        export_thread = threading.Thread(
            target=self._export_images_thread,
            args=(self.imported_images, output_dir, export_settings)
        )
        export_thread.daemon = True
        export_thread.start()
        
    def _export_images_thread(self, image_paths, output_dir, settings):
        """在单独的线程中处理图片导出"""
        total = len(image_paths)
        success_count = 0
        error_count = 0
        
        for i, path in enumerate(image_paths):
            try:
                # 更新状态
                self.update_status("正在处理 {}/{}: {}".format(i+1, total, os.path.basename(path)))
                
                # 打开图片
                img = Image.open(path)
                
                # 调整图片尺寸
                if settings['resize_option'] != "none":
                    img = self.resize_image(img, settings)
                
                # 生成输出文件名
                filename = os.path.basename(path)
                name, ext = os.path.splitext(filename)
                
                # 应用命名规则
                output_name = "{}{}{}".format(settings['prefix'], name, settings['suffix'])
                
                # 设置输出格式
                if settings['format'] == "jpeg":
                    output_ext = ".jpg"
                else:
                    output_ext = ".png"
                    
                output_path = os.path.join(output_dir, "{}{}".format(output_name, output_ext))
                
                # 保存图片
                if settings['format'] == "jpeg":
                    # 如果原图有透明通道，添加白色背景
                    if img.mode == 'RGBA':
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                        img = background
                    
                    img.save(output_path, format="JPEG", quality=settings['quality'])
                else:
                    img.save(output_path, format="PNG")
                    
                success_count += 1
                
            except Exception as e:
                error_count += 1
                print("处理图片 {} 时出错: {}".format(path, str(e)))
                
        # 完成后更新状态
        self.update_status("导出完成: {} 成功, {} 失败".format(success_count, error_count))
        
        # 显示完成消息
        self.show_export_complete(success_count, error_count, output_dir)
        
    def update_status(self, message):
        """更新状态栏消息（线程安全）"""
        self.after(0, lambda: self.status_bar.config(text=message))
        
    def show_export_complete(self, success_count, error_count, output_dir):
        """显示导出完成消息（线程安全）"""
        self.after(0, lambda: messagebox.showinfo(
            "导出完成",
            "成功导出 {} 张图片\n"
            "失败 {} 张图片\n\n"
            "输出位置: {}".format(success_count, error_count, output_dir)
        ))
        
    def resize_image(self, img, settings):
        """根据设置调整图片尺寸"""
        original_width, original_height = img.size
        
        if settings['resize_option'] == "width" and settings['width']:
            new_width = settings['width']
            new_height = int(original_height * (new_width / original_width))
            return img.resize((new_width, new_height), Image.LANCZOS)
            
        elif settings['resize_option'] == "height" and settings['height']:
            new_height = settings['height']
            new_width = int(original_width * (new_height / original_height))
            return img.resize((new_width, new_height), Image.LANCZOS)
            
        elif settings['resize_option'] == "percent" and settings['percent']:
            new_width = int(original_width * settings['percent'])
            new_height = int(original_height * settings['percent'])
            return img.resize((new_width, new_height), Image.LANCZOS)
            
        return img
        
    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于图片水印工具",
            "图片水印工具 v1.0\n\n"
            "一个用于添加水印和处理图片的工具\n"
            "支持多种图片格式和导出选项"
        )
        
    def on_resize(self, event):
        """窗口大小改变时重新加载预览"""
        # 防止频繁刷新
        if hasattr(self, '_resize_timer'):
            self.after_cancel(self._resize_timer)
            
        # 设置定时器延迟刷新
        self._resize_timer = self.after(200, self.refresh_preview)
        
    def refresh_preview(self):
        """刷新当前预览图片"""
        selected_items = self.image_list.selection()
        if selected_items:
            index = self.image_list.index(selected_items[0])
            if 0 <= index < len(self.imported_images):
                self.load_preview(self.imported_images[index])

if __name__ == "__main__":
    app = WatermarkApp()
    # 绑定窗口大小改变事件
    app.preview_canvas.bind("<Configure>", app.on_resize)
    app.mainloop()