# -*- coding: utf-8 -*-
"""
主窗口模块
创建和管理主应用程序窗口
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from typing import Optional, Callable
from PIL import Image, ImageTk

from config import Config
from components.file_manager import ImageFileManager, ExportManager
from components.image_list import ImageListManager
from components.text_watermark import TextWatermark, TextWatermarkDialog
from ui.real_drag_drop import RealDragDropManager
from ui.simple_watermark_drag import SimpleWatermarkDrag

class MainWindow:
    """主窗口类"""
    
    def __init__(self, parent):
        """初始化主窗口"""
        self.parent = parent
        self.config = Config.load_config()
        
        # 创建管理器实例
        self.file_manager = ImageFileManager()
        self.export_manager = ExportManager()
        self.image_list_manager = ImageListManager()
        self.current_watermark = TextWatermark()
        self.drag_drop_manager = RealDragDropManager(self)
        self.watermark_drag_handler = None
        
        # UI组件
        self.main_frame = None
        self.image_list_widget = None
        self.preview_widget = None
        self.control_panel = None
        self.status_bar = None
        
        # 当前状态
        self.current_image_path = None
        
        # 创建界面
        self.create_interface()
        
        # 设置回调
        self.setup_callbacks()
        
        # 设置拖拽上传
        self.setup_drag_drop()
        
        # 设置水印拖拽
        self.setup_watermark_drag()
        
        # 延迟刷新拖拽提示（等待界面完全初始化）
        self.parent.after(100, self.refresh_drag_hints)
        
        # 预览更新防抖
        self._preview_update_pending = False
        
        # 水印拖拽状态
        self._watermark_dragging = False
    
    def create_interface(self):
        """创建主界面"""
        # 创建主框架
        self.main_frame = tk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建左侧面板（图片列表）
        self.create_image_list_panel()
        
        # 创建中间面板（预览区域）
        self.create_preview_panel()
        
        # 创建右侧面板（控制面板）
        self.create_control_panel()
        
        # 创建底部状态栏
        self.create_status_bar()
        
        # 配置网格权重
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
    
    def create_image_list_panel(self):
        """创建图片列表面板"""
        # 图片列表框架
        list_frame = tk.LabelFrame(self.main_frame, text="图片列表", width=200)
        list_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5))
        list_frame.grid_propagate(False)
        
        # 工具栏
        toolbar = tk.Frame(list_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # 导入按钮
        import_btn = tk.Button(toolbar, text="导入图片", command=self.import_images, width=8)
        import_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        import_folder_btn = tk.Button(toolbar, text="导入文件夹", command=self.import_folder, width=8)
        import_folder_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = tk.Button(toolbar, text="清空", command=self.clear_image_list, width=8)
        clear_btn.pack(side=tk.LEFT)
        
        # 图片列表
        list_container = tk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建Treeview
        columns = ('filename', 'size', 'format')
        self.image_list_widget = ttk.Treeview(list_container, columns=columns, show='tree headings', height=15)
        
        # 配置列
        self.image_list_widget.heading('#0', text='#')
        self.image_list_widget.heading('filename', text='文件名')
        self.image_list_widget.heading('size', text='尺寸')
        self.image_list_widget.heading('format', text='格式')
        
        self.image_list_widget.column('#0', width=30, minwidth=30)
        self.image_list_widget.column('filename', width=120, minwidth=100)
        self.image_list_widget.column('size', width=80, minwidth=60)
        self.image_list_widget.column('format', width=60, minwidth=50)
        
        # 滚动条
        list_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.image_list_widget.yview)
        self.image_list_widget.configure(yscrollcommand=list_scrollbar.set)
        
        # 布局
        self.image_list_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.image_list_widget.bind('<<TreeviewSelect>>', self.on_image_selected)
    
    def create_preview_panel(self):
        """创建预览面板"""
        # 预览框架
        preview_frame = tk.LabelFrame(self.main_frame, text="预览")
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=(0, 5))
        
        # 预览画布
        self.preview_widget = tk.Canvas(preview_frame, bg='lightgray', width=400, height=300)
        self.preview_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 预览控制按钮
        preview_controls = tk.Frame(preview_frame)
        preview_controls.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        prev_btn = tk.Button(preview_controls, text="上一张", command=self.previous_image, width=8)
        prev_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        next_btn = tk.Button(preview_controls, text="下一张", command=self.next_image, width=8)
        next_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        zoom_fit_btn = tk.Button(preview_controls, text="适应窗口", command=self.zoom_to_fit, width=8)
        zoom_fit_btn.pack(side=tk.LEFT)
        
        # 先不添加占位文本，让拖拽处理器来处理
    
    def create_control_panel(self):
        """创建控制面板"""
        # 控制面板框架
        control_frame = tk.LabelFrame(self.main_frame, text="水印设置", width=300)
        control_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(5, 0))
        control_frame.grid_propagate(False)
        
        # 创建滚动区域
        canvas = tk.Canvas(control_frame)
        scrollbar = ttk.Scrollbar(control_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 水印类型选择
        type_frame = tk.LabelFrame(scrollable_frame, text="水印类型", padx=5, pady=5)
        type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.watermark_type = tk.StringVar(value="text")
        text_radio = tk.Radiobutton(type_frame, text="文本水印", variable=self.watermark_type, 
                                   value="text", command=self.on_watermark_type_changed)
        text_radio.pack(anchor=tk.W)
        
        image_radio = tk.Radiobutton(type_frame, text="图片水印", variable=self.watermark_type, 
                                    value="image", command=self.on_watermark_type_changed)
        image_radio.pack(anchor=tk.W)
        
        exif_radio = tk.Radiobutton(type_frame, text="EXIF时间水印", variable=self.watermark_type, 
                                   value="exif", command=self.on_watermark_type_changed)
        exif_radio.pack(anchor=tk.W)
        
        # 文本水印设置
        self.text_frame = tk.LabelFrame(scrollable_frame, text="文本设置", padx=5, pady=5)
        self.text_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 文本输入
        tk.Label(self.text_frame, text="水印文本:").pack(anchor=tk.W)
        self.text_entry = tk.Entry(self.text_frame, width=30)
        self.text_entry.pack(fill=tk.X, pady=(0, 5))
        self.text_entry.insert(0, self.current_watermark.text)
        self.text_entry.bind('<KeyRelease>', self.on_text_changed)
        
        # 字体大小
        font_frame = tk.Frame(self.text_frame)
        font_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(font_frame, text="字体大小:").pack(side=tk.LEFT)
        self.font_size_var = tk.IntVar(value=self.current_watermark.font_size)
        font_size_scale = tk.Scale(font_frame, from_=8, to=100, orient=tk.HORIZONTAL, 
                                 variable=self.font_size_var, command=self.on_font_size_changed)
        font_size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 颜色设置
        color_frame = tk.Frame(self.text_frame)
        color_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(color_frame, text="颜色:").pack(side=tk.LEFT)
        self.color_var = tk.StringVar(value=self.current_watermark.color)
        color_entry = tk.Entry(color_frame, textvariable=self.color_var, width=10)
        color_entry.pack(side=tk.LEFT, padx=(5, 5))
        color_btn = tk.Button(color_frame, text="选择", command=self.choose_color, width=6)
        color_btn.pack(side=tk.LEFT)
        
        # 透明度
        transparency_frame = tk.Frame(self.text_frame)
        transparency_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(transparency_frame, text="透明度:").pack(side=tk.LEFT)
        self.transparency_var = tk.IntVar(value=self.current_watermark.transparency)
        transparency_scale = tk.Scale(transparency_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                    variable=self.transparency_var, command=self.on_transparency_changed)
        transparency_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 位置设置
        position_frame = tk.LabelFrame(scrollable_frame, text="位置设置", padx=5, pady=5)
        position_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(position_frame, text="位置:").pack(anchor=tk.W)
        self.position_var = tk.StringVar(value=self.current_watermark.position)
        position_combo = ttk.Combobox(position_frame, textvariable=self.position_var, width=20)
        position_combo['values'] = ('top_left', 'top_center', 'top_right',
                                  'center_left', 'center', 'center_right',
                                  'bottom_left', 'bottom_center', 'bottom_right')
        position_combo.pack(fill=tk.X, pady=(0, 5))
        position_combo.bind('<<ComboboxSelected>>', self.on_position_changed)
        
        # 拖拽调整开关
        self.drag_enabled_var = tk.BooleanVar(value=True)
        drag_check = tk.Checkbutton(position_frame, text="启用拖拽调整", 
                                   variable=self.drag_enabled_var, command=self.on_drag_toggle)
        drag_check.pack(anchor=tk.W, pady=(0, 5))
        
        # 效果设置
        effect_frame = tk.LabelFrame(scrollable_frame, text="效果设置", padx=5, pady=5)
        effect_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.shadow_var = tk.BooleanVar(value=self.current_watermark.shadow)
        shadow_check = tk.Checkbutton(effect_frame, text="阴影效果", variable=self.shadow_var,
                                     command=self.on_shadow_changed)
        shadow_check.pack(anchor=tk.W)
        
        self.outline_var = tk.BooleanVar(value=self.current_watermark.outline)
        outline_check = tk.Checkbutton(effect_frame, text="描边效果", variable=self.outline_var,
                                      command=self.on_outline_changed)
        outline_check.pack(anchor=tk.W)
        
        # 导出设置
        export_frame = tk.LabelFrame(scrollable_frame, text="导出设置", padx=5, pady=5)
        export_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 输出格式
        format_frame = tk.Frame(export_frame)
        format_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(format_frame, text="输出格式:").pack(side=tk.LEFT)
        self.output_format = tk.StringVar(value="jpg")
        format_combo = ttk.Combobox(format_frame, textvariable=self.output_format, width=10)
        format_combo['values'] = ('jpg', 'png')
        format_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # 输出文件夹
        folder_frame = tk.Frame(export_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(folder_frame, text="输出文件夹:").pack(anchor=tk.W)
        self.output_folder_var = tk.StringVar()
        folder_entry = tk.Entry(folder_frame, textvariable=self.output_folder_var, width=25)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        folder_btn = tk.Button(folder_frame, text="选择", command=self.choose_output_folder, width=6)
        folder_btn.pack(side=tk.LEFT)
        
        # 操作按钮
        button_frame = tk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        preview_btn = tk.Button(button_frame, text="预览水印", command=self.preview_watermark, width=12)
        preview_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        export_btn = tk.Button(button_frame, text="导出图片", command=self.export_images, width=12)
        export_btn.pack(side=tk.LEFT)
        
        # 布局滚动区域
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = tk.Frame(self.parent, relief=tk.SUNKEN, bd=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(self.status_bar, text="就绪", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 进度条（隐藏状态）
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_bar, variable=self.progress_var, 
                                          mode='determinate', length=200)
    
    def setup_callbacks(self):
        """设置回调函数"""
        self.image_list_manager.add_callback(self.on_image_list_changed)
    
    def setup_drag_drop(self):
        """设置拖拽上传功能"""
        # 为预览区域添加拖拽功能
        self.drag_drop_manager.add_drop_target(
            self.preview_widget, 
            "preview_area", 
            self.on_files_dropped
        )
        
        # 为图片列表区域添加拖拽功能
        self.drag_drop_manager.add_drop_target(
            self.image_list_widget, 
            "image_list_area", 
            self.on_files_dropped
        )
        
        # 添加双击事件作为备用方案
        self.preview_widget.bind('<Double-Button-1>', self.on_double_click)
        self.image_list_widget.bind('<Double-Button-1>', self.on_double_click)
    
    def on_double_click(self, event):
        """双击事件处理"""
        self.import_images()
    
    def setup_watermark_drag(self):
        """设置水印拖拽功能"""
        self.watermark_drag_handler = SimpleWatermarkDrag(
            self.preview_widget, 
            self.on_watermark_position_changed
        )
        
        # 设置拖拽状态回调
        self.watermark_drag_handler.set_drag_callbacks(
            on_start=self.on_watermark_drag_start,
            on_end=self.on_watermark_drag_end
        )
    
    def on_watermark_drag_start(self):
        """水印开始拖拽回调"""
        self._watermark_dragging = True
        print("Watermark drag started - preview updates disabled")
    
    def on_watermark_drag_end(self):
        """水印结束拖拽回调"""
        self._watermark_dragging = False
        print("Watermark drag ended - preview updates enabled")
        # 延迟更新预览，避免立即冲突
        self.parent.after(100, self.update_preview)
    
    def on_watermark_position_changed(self, position):
        """水印位置改变回调"""
        # 将画布坐标转换为图片坐标
        if hasattr(self, 'current_image_size') and self.current_image_size:
            scale_factor = self.calculate_scale_factor()
            if scale_factor > 0:
                # 计算图片在画布上的偏移量
                img_width, img_height = self.current_image_size
                canvas_img_width = int(img_width * scale_factor)
                canvas_img_height = int(img_height * scale_factor)
                
                canvas_width = self.preview_widget.winfo_width()
                canvas_height = self.preview_widget.winfo_height()
                offset_x = (canvas_width - canvas_img_width) // 2
                offset_y = (canvas_height - canvas_img_height) // 2
                
                # 转换为图片坐标（减去偏移量）
                image_x = int((position[0] - offset_x) / scale_factor)
                image_y = int((position[1] - offset_y) / scale_factor)
                
                # 确保坐标在图片范围内
                image_x = max(0, min(image_x, img_width))
                image_y = max(0, min(image_y, img_height))
                
                self.current_watermark.set_custom_position((image_x, image_y))
                print(f"Watermark position updated: canvas({position[0]}, {position[1]}) -> image({image_x}, {image_y}) [offset: ({offset_x}, {offset_y}), scale: {scale_factor:.3f}]")
                # 不立即更新预览，避免循环
    
    def on_files_dropped(self, file_paths):
        """处理拖拽的文件"""
        try:
            if not file_paths:
                return
            
            # 验证并添加文件
            valid_count = 0
            invalid_files = []
            
            for file_path in file_paths:
                if self.file_manager.validate_image_file(file_path):
                    success = self.image_list_manager.add_image(file_path)
                    if success:
                        valid_count += 1
                else:
                    invalid_files.append(os.path.basename(file_path))
            
            # 显示结果
            if invalid_files:
                messagebox.showwarning(
                    "警告", 
                    f"以下文件格式不支持，已跳过:\n{', '.join(invalid_files)}"
                )
            
            if valid_count > 0:
                self.update_status(f"通过拖拽成功导入 {valid_count} 张图片")
                # 更新图片列表显示
                self.update_image_list_display()
                # 更新预览
                self.update_preview()
            
        except Exception as e:
            messagebox.showerror("错误", f"处理拖拽文件失败: {e}")
    
    def update_status(self, message: str):
        """更新状态栏"""
        self.status_label.config(text=message)
        self.parent.update_idletasks()
    
    def show_progress(self, show: bool = True):
        """显示/隐藏进度条"""
        if show:
            self.progress_bar.pack(side=tk.RIGHT, padx=5)
        else:
            self.progress_bar.pack_forget()
    
    def update_progress(self, value: float):
        """更新进度条"""
        self.progress_var.set(value)
        self.parent.update_idletasks()
    
    # 文件操作相关方法
    def import_images(self):
        """导入图片"""
        try:
            files = self.file_manager.import_multiple_images(self.parent)
            if files:
                for file_path in files:
                    self.image_list_manager.add_image(file_path)
                self.update_status(f"已导入 {len(files)} 张图片")
        except Exception as e:
            messagebox.showerror("错误", f"导入图片失败: {e}")
    
    def import_folder(self):
        """导入文件夹"""
        try:
            files = self.file_manager.import_folder(self.parent)
            if files:
                for file_path in files:
                    self.image_list_manager.add_image(file_path)
                self.update_status(f"已导入 {len(files)} 张图片")
        except Exception as e:
            messagebox.showerror("错误", f"导入文件夹失败: {e}")
    
    def clear_image_list(self):
        """清空图片列表"""
        self.image_list_manager.clear_list()
        self.current_image_path = None
        self.update_preview()
        self.update_status("已清空图片列表")
    
    def choose_output_folder(self):
        """选择输出文件夹"""
        from tkinter import filedialog
        folder = filedialog.askdirectory(
            parent=self.parent,
            title="选择输出文件夹"
        )
        if folder:
            self.output_folder_var.set(folder)
            self.export_manager.output_folder = folder
    
    def export_images(self):
        """导出图片"""
        try:
            if not self.output_folder_var.get():
                messagebox.showwarning("警告", "请先选择输出文件夹")
                return
            
            if not self.image_list_manager.get_image_count():
                messagebox.showwarning("警告", "没有图片可以导出")
                return
            
            # 设置导出参数
            self.export_manager.output_folder = self.output_folder_var.get()
            self.export_manager.update_export_settings({
                'format': self.output_format.get(),
                'quality': 95
            })
            
            print(f"Export settings: output_folder={self.export_manager.output_folder}")
            print(f"Export settings: format={self.export_manager.export_settings}")
            
            # 开始导出
            self.export_all_images()
            
        except Exception as e:
            print(f"Export error details: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("错误", f"导出失败: {e}")
    
    def export_all_images(self):
        """导出所有图片"""
        try:
            self.show_progress(True)
            self.update_status("正在导出图片...")
            
            image_list = self.image_list_manager.get_image_list()
            total_count = len(image_list)
            success_count = 0
            
            for i, image_data in enumerate(image_list):
                try:
                    print(f"Processing image {i+1}/{total_count}: {image_data['filename']}")
                    
                    # 加载图片
                    image = self.image_list_manager.load_image(image_data['path'])
                    if not image:
                        print(f"Failed to load image: {image_data['path']}")
                        continue
                    
                    print(f"Loaded image: {image.size}, mode: {image.mode}")
                    
                    # 应用水印
                    watermarked_image = self.current_watermark.apply_to_image(image)
                    if not watermarked_image:
                        print("Failed to apply watermark")
                        continue
                    
                    print(f"Applied watermark: {watermarked_image.size}, mode: {watermarked_image.mode}")
                    
                    # 导出图片
                    if self.export_manager.export_single_image(image_data['path'], watermarked_image):
                        success_count += 1
                        print(f"Successfully exported: {image_data['filename']}")
                    else:
                        print(f"Failed to export: {image_data['filename']}")
                    
                    # 更新进度
                    progress = (i + 1) / total_count * 100
                    self.update_progress(progress)
                    
                except Exception as e:
                    print(f"Export image failed {image_data['path']}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            self.show_progress(False)
            self.update_status(f"导出完成: {success_count}/{total_count} 张图片")
            messagebox.showinfo("完成", f"成功导出 {success_count} 张图片")
            
        except Exception as e:
            self.show_progress(False)
            messagebox.showerror("错误", f"导出过程出错: {e}")
    
    # 图片列表相关方法
    def on_image_list_changed(self, event: str, data):
        """图片列表变化回调"""
        if event == 'image_added':
            self.update_image_list_display()
        elif event == 'image_removed':
            self.update_image_list_display()
        elif event == 'list_cleared':
            self.update_image_list_display()
        elif event == 'current_changed':
            self.update_preview()
    
    def update_image_list_display(self):
        """更新图片列表显示"""
        # 清空现有项目
        for item in self.image_list_widget.get_children():
            self.image_list_widget.delete(item)
        
        # 添加图片项目
        image_list = self.image_list_manager.get_image_list()
        for i, image_data in enumerate(image_list):
            size_text = f"{image_data['size'][0]}x{image_data['size'][1]}"
            self.image_list_widget.insert('', 'end', 
                                        text=str(i+1),
                                        values=(image_data['filename'], size_text, image_data['format']))
    
    def on_image_selected(self, event):
        """图片选择事件"""
        selection = self.image_list_widget.selection()
        if selection:
            item = self.image_list_widget.item(selection[0])
            index = int(item['text']) - 1
            self.image_list_manager.set_current_index(index)
    
    def previous_image(self):
        """上一张图片"""
        self.image_list_manager.get_previous_image()
    
    def next_image(self):
        """下一张图片"""
        self.image_list_manager.get_next_image()
    
    def zoom_to_fit(self):
        """适应窗口大小"""
        self.update_preview()
    
    def update_preview(self):
        """更新预览"""
        # 如果正在拖拽水印，不更新预览
        if self._watermark_dragging:
            return
            
        # 防抖处理，避免频繁更新
        if self._preview_update_pending:
            return
        
        self._preview_update_pending = True
        self.parent.after(50, self._do_update_preview)
    
    def _do_update_preview(self):
        """实际执行预览更新"""
        try:
            self._preview_update_pending = False
            current_image = self.image_list_manager.get_current_image()
            
            if not current_image:
                self.preview_widget.delete("all")
                self.preview_widget.create_text(200, 100, text="请导入图片开始使用", 
                                              font=("Arial", 16), fill="gray")
                self.preview_widget.create_text(200, 130, text="点击'导入图片'按钮", 
                                              font=("Arial", 12), fill="lightgray")
                self.preview_widget.create_text(200, 150, text="或双击此区域选择文件", 
                                              font=("Arial", 12), fill="lightgray")
                return
            
            # 加载图片
            image = self.image_list_manager.load_image(current_image['path'])
            if not image:
                return
            
            # 应用水印
            watermarked_image = self.current_watermark.apply_to_image(image)
            if not watermarked_image:
                watermarked_image = image
            
            # 保存图片尺寸用于坐标转换
            self.current_image_size = image.size
            
            # 显示水印拖拽预览（只在非拖拽状态下）
            if self.watermark_drag_handler and not self._watermark_dragging:
                # 计算画布上的水印位置
                canvas_pos = self.calculate_canvas_position(image.size, self.current_watermark)
                self.watermark_drag_handler.show_watermark(canvas_pos, self.current_watermark.text)
            
            # 计算显示尺寸
            canvas_width = self.preview_widget.winfo_width()
            canvas_height = self.preview_widget.winfo_height()
            
            # 如果Canvas还没有完全初始化，使用默认尺寸或延迟更新
            if canvas_width <= 1 or canvas_height <= 1:
                # 尝试更新Canvas并重新获取尺寸
                self.preview_widget.update_idletasks()
                canvas_width = self.preview_widget.winfo_width()
                canvas_height = self.preview_widget.winfo_height()
                
                # 如果仍然无效，使用默认尺寸
                if canvas_width <= 1:
                    canvas_width = 400
                if canvas_height <= 1:
                    canvas_height = 300
            
            # 计算缩放比例
            img_width, img_height = watermarked_image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # 不放大图片
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # 调整图片大小
            if scale < 1.0:
                try:
                    watermarked_image = watermarked_image.resize((new_width, new_height), Image.LANCZOS)
                except AttributeError:
                    watermarked_image = watermarked_image.resize((new_width, new_height), Image.LANCZOS)
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(watermarked_image)
            
            # 清空画布并显示图片
            self.preview_widget.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.preview_widget.create_image(x, y, anchor=tk.NW, image=photo)
            
            # 保持引用防止垃圾回收
            self.preview_widget.image = photo
            
        except Exception as e:
            print(f"Update preview failed: {e}")
            self._preview_update_pending = False
    
    # 水印设置相关方法
    def on_watermark_type_changed(self):
        """水印类型变化"""
        # 这里可以添加不同类型水印的UI切换逻辑
        pass
    
    def on_text_changed(self, event=None):
        """文本变化"""
        self.current_watermark.set_text(self.text_entry.get())
        self.update_preview()
    
    def on_font_size_changed(self, value):
        """字体大小变化"""
        self.current_watermark.set_font_size(int(value))
        self.update_preview()
    
    def choose_color(self):
        """选择颜色"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="选择颜色", color=self.color_var.get())
        if color[1]:
            self.color_var.set(color[1])
            self.current_watermark.set_color(color[1])
            self.update_preview()
    
    def on_transparency_changed(self, value):
        """透明度变化"""
        self.current_watermark.set_transparency(int(value))
        self.update_preview()
    
    def on_position_changed(self, event=None):
        """位置变化"""
        self.current_watermark.set_position(self.position_var.get())
        self.update_preview()
    
    def on_shadow_changed(self):
        """阴影效果变化"""
        self.current_watermark.set_shadow(self.shadow_var.get())
        self.update_preview()
    
    def on_outline_changed(self):
        """描边效果变化"""
        self.current_watermark.set_outline(self.outline_var.get())
        self.update_preview()
    
    def on_drag_toggle(self):
        """拖拽开关变化"""
        if self.watermark_drag_handler:
            if self.drag_enabled_var.get():
                self.watermark_drag_handler.setup_events()
            else:
                self.canvas.unbind('<Button-1>')
                self.canvas.unbind('<B1-Motion>')
                self.canvas.unbind('<ButtonRelease-1>')
                self.canvas.unbind('<Motion>')
    
    def calculate_scale_factor(self):
        """计算缩放因子"""
        if not hasattr(self, 'current_image_size') or not self.current_image_size:
            return 1.0
        
        canvas_width = self.preview_widget.winfo_width()
        canvas_height = self.preview_widget.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return 1.0
        
        img_width, img_height = self.current_image_size
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        return min(scale_x, scale_y, 1.0)
    
    def calculate_canvas_position(self, image_size, watermark):
        """计算画布上的水印位置"""
        if not image_size:
            return (0, 0)
        
        scale_factor = self.calculate_scale_factor()
        img_width, img_height = image_size
        
        # 计算画布上的图片尺寸
        canvas_img_width = int(img_width * scale_factor)
        canvas_img_height = int(img_height * scale_factor)
        
        # 计算画布上的图片偏移
        canvas_width = self.preview_widget.winfo_width()
        canvas_height = self.preview_widget.winfo_height()
        offset_x = (canvas_width - canvas_img_width) // 2
        offset_y = (canvas_height - canvas_img_height) // 2
        
        # 计算水印在画布上的位置
        if watermark.custom_position:
            # 使用自定义位置
            img_x, img_y = watermark.custom_position
        else:
            # 使用预设位置
            img_x, img_y = self.get_preset_position(image_size, watermark.position)
        
        # 转换为画布坐标
        canvas_x = offset_x + int(img_x * scale_factor)
        canvas_y = offset_y + int(img_y * scale_factor)
        
        return (canvas_x, canvas_y)
    
    def get_preset_position(self, image_size, position):
        """获取预设位置"""
        img_width, img_height = image_size
        margin = 20
        
        position_map = {
            "top_left": (margin, margin),
            "top_center": ((img_width - 100) // 2, margin),
            "top_right": (img_width - 100 - margin, margin),
            "center_left": (margin, (img_height - 30) // 2),
            "center": ((img_width - 100) // 2, (img_height - 30) // 2),
            "center_right": (img_width - 100 - margin, (img_height - 30) // 2),
            "bottom_left": (margin, img_height - 30 - margin),
            "bottom_center": ((img_width - 100) // 2, img_height - 30 - margin),
            "bottom_right": (img_width - 100 - margin, img_height - 30 - margin)
        }
        
        return position_map.get(position, position_map["bottom_right"])
    
    def preview_watermark(self):
        """预览水印效果"""
        try:
            current_image = self.image_list_manager.get_current_image()
            if not current_image:
                messagebox.showwarning("警告", "请先选择一张图片")
                return
            
            # 打开水印设置对话框
            dialog = TextWatermarkDialog(self.parent, self.current_watermark)
            result = dialog.show()
            
            if result:
                self.current_watermark = result
                self.update_watermark_ui()
                self.update_preview()
                
        except Exception as e:
            messagebox.showerror("错误", f"预览水印失败: {e}")
    
    def update_watermark_ui(self):
        """更新水印UI显示"""
        self.text_entry.delete(0, tk.END)
        self.text_entry.insert(0, self.current_watermark.text)
        
        self.font_size_var.set(self.current_watermark.font_size)
        self.color_var.set(self.current_watermark.color)
        self.transparency_var.set(self.current_watermark.transparency)
        self.position_var.set(self.current_watermark.position)
        self.shadow_var.set(self.current_watermark.shadow)
        self.outline_var.set(self.current_watermark.outline)
    
    def refresh_drag_hints(self):
        """刷新拖拽提示"""
        try:
            if hasattr(self, 'drag_drop_manager') and self.drag_drop_manager:
                self.drag_drop_manager.refresh_all_hints()
        except Exception as e:
            print(f"刷新拖拽提示失败: {e}")
