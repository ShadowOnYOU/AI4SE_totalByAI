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
from components.image_watermark import ImageWatermark, ImageWatermarkDialog
from components.template_manager import TemplateManager, WatermarkTemplate, TemplateDialog
from components.exif_text_watermark import ExifTextWatermark, ExifWatermarkDialog
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
        self.current_image_watermark = ImageWatermark()
        self.current_exif_watermark = ExifTextWatermark()
        self.watermark_type = "text"  # "text", "image", or "exif"
        self.template_manager = TemplateManager()
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
        
        # 自动加载上次设置
        self.parent.after(200, self.auto_load_last_settings)
    
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
        self.main_frame.grid_columnconfigure(1, weight=2)  # 增加中间预览区域权重
        self.main_frame.grid_columnconfigure(2, weight=1)  # 右侧控制面板权重
        self.main_frame.grid_rowconfigure(0, weight=1)
    
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
        # 控制面板框架（增加宽度）
        control_frame = tk.LabelFrame(self.main_frame, text="水印设置", width=420)
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
        
        self.watermark_type_var = tk.StringVar(value="text")
        text_radio = tk.Radiobutton(type_frame, text="文本水印", variable=self.watermark_type_var, 
                                   value="text", command=self.on_watermark_type_changed)
        text_radio.pack(anchor=tk.W)
        
        image_radio = tk.Radiobutton(type_frame, text="图片水印", variable=self.watermark_type_var, 
                                    value="image", command=self.on_watermark_type_changed)
        image_radio.pack(anchor=tk.W)
        
        exif_radio = tk.Radiobutton(type_frame, text="EXIF时间水印", variable=self.watermark_type_var, 
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
                                  'bottom_left', 'bottom_center', 'bottom_right', 'custom')
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
        
        # 图片水印设置
        self.image_frame = tk.LabelFrame(scrollable_frame, text="图片设置", padx=5, pady=5)
        self.image_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 图片选择
        image_select_frame = tk.Frame(self.image_frame)
        image_select_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(image_select_frame, text="水印图片:").pack(side=tk.LEFT)
        self.image_path_var = tk.StringVar(value="")
        image_path_entry = tk.Entry(image_select_frame, textvariable=self.image_path_var, 
                                   width=20, state="readonly")
        image_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        select_image_btn = tk.Button(image_select_frame, text="选择", 
                                    command=self.select_watermark_image, width=6)
        select_image_btn.pack(side=tk.RIGHT)
        
        # 图片缩放
        scale_frame = tk.Frame(self.image_frame)
        scale_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(scale_frame, text="缩放比例:").pack(side=tk.LEFT)
        self.image_scale_var = tk.DoubleVar(value=self.current_image_watermark.scale_factor)
        image_scale = tk.Scale(scale_frame, from_=0.1, to=1.0, resolution=0.05, orient=tk.HORIZONTAL,
                              variable=self.image_scale_var, command=self.on_image_scale_changed)
        image_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 图片透明度
        image_transparency_frame = tk.Frame(self.image_frame)
        image_transparency_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(image_transparency_frame, text="透明度:").pack(side=tk.LEFT)
        self.image_transparency_var = tk.IntVar(value=self.current_image_watermark.transparency)
        image_transparency_scale = tk.Scale(image_transparency_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                           variable=self.image_transparency_var, command=self.on_image_transparency_changed)
        image_transparency_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 保持宽高比
        self.maintain_aspect_var = tk.BooleanVar(value=self.current_image_watermark.maintain_aspect_ratio)
        aspect_check = tk.Checkbutton(self.image_frame, text="保持宽高比", variable=self.maintain_aspect_var,
                                     command=self.on_maintain_aspect_changed)
        aspect_check.pack(anchor=tk.W)
        
        # 图片水印位置设置
        image_position_frame = tk.Frame(self.image_frame)
        image_position_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Label(image_position_frame, text="位置:").pack(side=tk.LEFT)
        self.image_position_var = tk.StringVar(value=self.current_image_watermark.position)
        image_position_combo = ttk.Combobox(image_position_frame, textvariable=self.image_position_var, width=15)
        image_position_combo['values'] = ('top_left', 'top_center', 'top_right',
                                         'center_left', 'center', 'center_right',
                                         'bottom_left', 'bottom_center', 'bottom_right', 'custom')
        image_position_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        image_position_combo.bind('<<ComboboxSelected>>', self.on_image_position_changed)
        
        # EXIF水印设置
        self.exif_frame = tk.LabelFrame(scrollable_frame, text="EXIF设置", padx=5, pady=5)
        self.exif_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 日期格式
        date_format_frame = tk.Frame(self.exif_frame)
        date_format_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(date_format_frame, text="日期格式:").pack(side=tk.LEFT)
        self.date_format_var = tk.StringVar(value=self.current_exif_watermark.date_format)
        date_format_combo = ttk.Combobox(date_format_frame, textvariable=self.date_format_var, 
                                        values=('%Y-%m-%d', '%Y年%m月%d日', '%m/%d/%Y', '%d-%m-%Y'),
                                        width=15, state="readonly")
        date_format_combo.pack(side=tk.LEFT, padx=(5, 0))
        date_format_combo.bind('<<ComboboxSelected>>', self.on_exif_date_format_changed)
        
        # 前缀后缀
        prefix_frame = tk.Frame(self.exif_frame)
        prefix_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(prefix_frame, text="前缀:").pack(side=tk.LEFT)
        self.exif_prefix_var = tk.StringVar(value=self.current_exif_watermark.prefix_text)
        prefix_entry = tk.Entry(prefix_frame, textvariable=self.exif_prefix_var, width=12)
        prefix_entry.pack(side=tk.LEFT, padx=(5, 5))
        prefix_entry.bind('<KeyRelease>', self.on_exif_prefix_changed)
        
        tk.Label(prefix_frame, text="后缀:").pack(side=tk.LEFT)
        self.exif_suffix_var = tk.StringVar(value=self.current_exif_watermark.suffix_text)
        suffix_entry = tk.Entry(prefix_frame, textvariable=self.exif_suffix_var, width=12)
        suffix_entry.pack(side=tk.LEFT, padx=(5, 0))
        suffix_entry.bind('<KeyRelease>', self.on_exif_suffix_changed)
        
        # EXIF字体大小
        exif_font_frame = tk.Frame(self.exif_frame)
        exif_font_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(exif_font_frame, text="字体大小:").pack(side=tk.LEFT)
        self.exif_font_size_var = tk.IntVar(value=self.current_exif_watermark.font_size)
        exif_font_scale = tk.Scale(exif_font_frame, from_=8, to=100, orient=tk.HORIZONTAL,
                                  variable=self.exif_font_size_var, command=self.on_exif_font_size_changed)
        exif_font_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # EXIF透明度
        exif_transparency_frame = tk.Frame(self.exif_frame)
        exif_transparency_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(exif_transparency_frame, text="透明度:").pack(side=tk.LEFT)
        self.exif_transparency_var = tk.IntVar(value=self.current_exif_watermark.transparency)
        exif_transparency_scale = tk.Scale(exif_transparency_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                          variable=self.exif_transparency_var, command=self.on_exif_transparency_changed)
        exif_transparency_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 备用选项
        self.exif_fallback_var = tk.BooleanVar(value=self.current_exif_watermark.fallback_to_file_time)
        fallback_check = tk.Checkbutton(self.exif_frame, text="无EXIF时使用文件时间", 
                                       variable=self.exif_fallback_var, command=self.on_exif_fallback_changed)
        fallback_check.pack(anchor=tk.W)
        
        # EXIF水印位置设置
        exif_position_frame = tk.Frame(self.exif_frame)
        exif_position_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Label(exif_position_frame, text="位置:").pack(side=tk.LEFT)
        self.exif_position_var = tk.StringVar(value=self.current_exif_watermark.position)
        exif_position_combo = ttk.Combobox(exif_position_frame, textvariable=self.exif_position_var, width=15)
        exif_position_combo['values'] = ('top_left', 'top_center', 'top_right',
                                        'center_left', 'center', 'center_right',
                                        'bottom_left', 'bottom_center', 'bottom_right', 'custom')
        exif_position_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        exif_position_combo.bind('<<ComboboxSelected>>', self.on_exif_position_changed)
        
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
        
        # 模板管理区域
        template_frame = tk.LabelFrame(scrollable_frame, text="模板管理", padx=5, pady=5)
        template_frame.pack(fill=tk.X, padx=5, pady=(10, 5))
        
        # 模板管理按钮（横向排列）
        template_button_frame = tk.Frame(template_frame)
        template_button_frame.pack(fill=tk.X, pady=5)
        
        save_template_btn = tk.Button(template_button_frame, text="保存模板", 
                                    command=self.save_current_template, 
                                    width=12, bg="#e8f5e8")
        save_template_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        load_template_btn = tk.Button(template_button_frame, text="加载模板", 
                                    command=self.load_template, 
                                    width=12, bg="#e8f0ff")
        load_template_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        manage_template_btn = tk.Button(template_button_frame, text="管理模板", 
                                      command=self.manage_templates, 
                                      width=12, bg="#fff8e8")
        manage_template_btn.pack(side=tk.LEFT)
        
        # 模板状态显示
        self.template_status_label = tk.Label(template_frame, text="", fg="gray", font=("Arial", 9))
        self.template_status_label.pack(pady=(5, 0))
        
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
                
                # 根据当前水印类型设置位置
                if self.watermark_type == "text":
                    self.current_watermark.set_custom_position((image_x, image_y))
                    # 清除预设位置选择，显示为自定义
                    if hasattr(self, 'position_var'):
                        self.position_var.set("custom")
                elif self.watermark_type == "image":
                    self.current_image_watermark.set_custom_position((image_x, image_y))
                    # 清除预设位置选择，显示为自定义
                    if hasattr(self, 'image_position_var'):
                        self.image_position_var.set("custom")
                elif self.watermark_type == "exif":
                    self.current_exif_watermark.set_custom_position((image_x, image_y))
                    # 清除预设位置选择，显示为自定义
                    if hasattr(self, 'exif_position_var'):
                        self.exif_position_var.set("custom")
                
                print(f"Watermark position updated ({self.watermark_type}): canvas({position[0]}, {position[1]}) -> image({image_x}, {image_y}) [offset: ({offset_x}, {offset_y}), scale: {scale_factor:.3f}]")
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
                    
                    # 应用当前选择的水印类型
                    if self.watermark_type == "exif":
                        # EXIF水印需要图片路径
                        watermarked_image = self.current_exif_watermark.apply_to_image_with_path(image, image_data['path'])
                    else:
                        watermarked_image = self.apply_current_watermark(image)
                    
                    if not watermarked_image:
                        print("Failed to apply watermark")
                        watermarked_image = image  # 如果应用失败，使用原图
                    
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
            watermarked_image = self.apply_current_watermark(image)
            if not watermarked_image:
                watermarked_image = image
            
            # 保存图片尺寸用于坐标转换
            self.current_image_size = image.size
            
            # 显示水印拖拽预览（只在非拖拽状态下）
            if self.watermark_drag_handler and not self._watermark_dragging:
                # 计算画布上的水印位置并显示相应类型的水印
                if self.watermark_type == "text":
                    canvas_pos = self.calculate_canvas_position(image.size, self.current_watermark)
                    watermark_text = self.current_watermark.text if self.current_watermark.text else "Sample Text"
                    self.watermark_drag_handler.show_watermark(canvas_pos, watermark_text, "text")
                elif self.watermark_type == "image":
                    canvas_pos = self.calculate_canvas_position(image.size, self.current_image_watermark)
                    if self.current_image_watermark.watermark_path:
                        watermark_name = os.path.basename(self.current_image_watermark.watermark_path)
                    else:
                        watermark_name = "Select Image"
                    self.watermark_drag_handler.show_watermark(canvas_pos, watermark_name, "image")
                    print(f"Showing image watermark: {watermark_name} at {canvas_pos}")
                elif self.watermark_type == "exif":
                    canvas_pos = self.calculate_canvas_position(image.size, self.current_exif_watermark)
                    current_image_data = self.image_list_manager.get_current_image()
                    if current_image_data and current_image_data.get('path'):
                        exif_text = self.current_exif_watermark.generate_watermark_text(current_image_data['path'])
                    else:
                        exif_text = "2024-01-15"
                    self.watermark_drag_handler.show_watermark(canvas_pos, exif_text, "exif")
                    print(f"Showing EXIF watermark: {exif_text} at {canvas_pos}")
            
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
    
    def apply_current_watermark(self, image: Image.Image) -> Optional[Image.Image]:
        """应用当前选择的水印类型"""
        try:
            if self.watermark_type == "text":
                return self.current_watermark.apply_to_image(image)
            elif self.watermark_type == "image":
                return self.current_image_watermark.apply_to_image(image)
            elif self.watermark_type == "exif":
                # EXIF水印需要图片路径
                current_image = self.image_list_manager.get_current_image()
                if current_image and current_image.get('path'):
                    return self.current_exif_watermark.apply_to_image_with_path(image, current_image['path'])
                else:
                    return image
            else:
                return image
        except Exception as e:
            print(f"Apply watermark failed: {e}")
            return image
    
    # 水印设置相关方法
    def on_watermark_type_changed(self):
        """水印类型变化"""
        watermark_type = self.watermark_type_var.get()
        self.watermark_type = watermark_type
        
        print(f"Watermark type changed to: {watermark_type}")
        
        # 显示/隐藏相应的设置面板
        if watermark_type == "text":
            self.text_frame.pack(fill=tk.X, padx=5, pady=5)
            self.image_frame.pack_forget()
            self.exif_frame.pack_forget()
        elif watermark_type == "image":
            self.text_frame.pack_forget()
            self.image_frame.pack(fill=tk.X, padx=5, pady=5)
            self.exif_frame.pack_forget()
        else:  # exif
            self.text_frame.pack_forget()
            self.image_frame.pack_forget()
            self.exif_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 立即更新预览以显示新的水印类型
        self.update_preview()
        
        # 强制刷新拖拽显示
        if hasattr(self, 'watermark_drag_handler') and self.watermark_drag_handler:
            self.parent.after(100, self._force_refresh_drag_display)
    
    def _force_refresh_drag_display(self):
        """强制刷新拖拽显示"""
        try:
            current_image = self.image_list_manager.get_current_image()
            if not current_image:
                return
                
            image = self.image_list_manager.load_image(current_image['path'])
            if not image or not hasattr(self, 'current_image_size'):
                return
            
            print(f"Force refreshing drag display for watermark type: {self.watermark_type}")
            
            # 根据当前水印类型显示拖拽预览
            if self.watermark_type == "text":
                canvas_pos = self.calculate_canvas_position(image.size, self.current_watermark)
                watermark_text = self.current_watermark.text if self.current_watermark.text else "Sample Text"
                self.watermark_drag_handler.show_watermark(canvas_pos, watermark_text, "text")
                print(f"Refreshed text watermark at {canvas_pos}")
                
            elif self.watermark_type == "image":
                canvas_pos = self.calculate_canvas_position(image.size, self.current_image_watermark)
                if self.current_image_watermark.watermark_path:
                    watermark_name = os.path.basename(self.current_image_watermark.watermark_path)
                else:
                    watermark_name = "Select Image"
                self.watermark_drag_handler.show_watermark(canvas_pos, watermark_name, "image")
                print(f"Refreshed image watermark: {watermark_name} at {canvas_pos}")
                
            elif self.watermark_type == "exif":
                canvas_pos = self.calculate_canvas_position(image.size, self.current_exif_watermark)
                if current_image and current_image.get('path'):
                    exif_text = self.current_exif_watermark.generate_watermark_text(current_image['path'])
                else:
                    exif_text = "2024-01-15"
                self.watermark_drag_handler.show_watermark(canvas_pos, exif_text, "exif")
                print(f"Refreshed EXIF watermark: {exif_text} at {canvas_pos}")
                
        except Exception as e:
            print(f"Force refresh drag display failed: {e}")
    
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
        position = self.position_var.get()
        if position != "custom":  # 只有非自定义位置才设置预设位置
            self.current_watermark.set_position(position)
        self.update_preview()
        if self.watermark_type == "text":
            self._schedule_drag_refresh()
    
    def on_shadow_changed(self):
        """阴影效果变化"""
        self.current_watermark.set_shadow(self.shadow_var.get())
        self.update_preview()
    
    def on_outline_changed(self):
        """描边效果变化"""
        self.current_watermark.set_outline(self.outline_var.get())
        self.update_preview()
    
    def select_watermark_image(self):
        """选择水印图片"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("PNG文件", "*.png"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            if self.current_image_watermark.load_watermark_image(file_path):
                self.image_path_var.set(os.path.basename(file_path))
                self.update_preview()
                # 立即更新拖拽显示
                if hasattr(self, 'watermark_drag_handler') and self.watermark_drag_handler and self.watermark_type == "image":
                    self.parent.after(50, self._force_refresh_drag_display)
            else:
                messagebox.showerror("错误", "无法加载图片，请选择有效的图片文件")
    
    def on_image_scale_changed(self, value):
        """图片缩放变化"""
        self.current_image_watermark.set_scale_factor(float(value))
        self.update_preview()
        if self.watermark_type == "image":
            self._schedule_drag_refresh()
    
    def on_image_transparency_changed(self, value):
        """图片透明度变化"""
        self.current_image_watermark.set_transparency(int(float(value)))
        self.update_preview()
        if self.watermark_type == "image":
            self._schedule_drag_refresh()
    
    def on_maintain_aspect_changed(self):
        """保持宽高比变化"""
        self.current_image_watermark.set_maintain_aspect_ratio(self.maintain_aspect_var.get())
        self.update_preview()
        if self.watermark_type == "image":
            self._schedule_drag_refresh()
    
    def on_image_position_changed(self, event=None):
        """图片水印位置变化"""
        position = self.image_position_var.get()
        if position != "custom":  # 只有非自定义位置才设置预设位置
            self.current_image_watermark.set_position(position)
        self.update_preview()
        if self.watermark_type == "image":
            self._schedule_drag_refresh()
    
    def _schedule_drag_refresh(self):
        """调度拖拽显示刷新"""
        if hasattr(self, 'watermark_drag_handler') and self.watermark_drag_handler:
            self.parent.after(50, self._force_refresh_drag_display)
    
    # EXIF水印事件处理方法
    def on_exif_date_format_changed(self, event=None):
        """EXIF日期格式变化"""
        self.current_exif_watermark.set_date_format(self.date_format_var.get())
        self.update_preview()
        if self.watermark_type == "exif":
            self._schedule_drag_refresh()
    
    def on_exif_prefix_changed(self, event=None):
        """EXIF前缀变化"""
        self.current_exif_watermark.set_prefix_suffix(
            self.exif_prefix_var.get(),
            self.current_exif_watermark.suffix_text
        )
        self.update_preview()
        if self.watermark_type == "exif":
            self._schedule_drag_refresh()
    
    def on_exif_suffix_changed(self, event=None):
        """EXIF后缀变化"""
        self.current_exif_watermark.set_prefix_suffix(
            self.current_exif_watermark.prefix_text,
            self.exif_suffix_var.get()
        )
        self.update_preview()
        if self.watermark_type == "exif":
            self._schedule_drag_refresh()
    
    def on_exif_font_size_changed(self, value):
        """EXIF字体大小变化"""
        self.current_exif_watermark.set_font_size(int(float(value)))
        self.update_preview()
        if self.watermark_type == "exif":
            self._schedule_drag_refresh()
    
    def on_exif_transparency_changed(self, value):
        """EXIF透明度变化"""
        self.current_exif_watermark.set_transparency(int(float(value)))
        self.update_preview()
        if self.watermark_type == "exif":
            self._schedule_drag_refresh()
    
    def on_exif_fallback_changed(self):
        """EXIF备用选项变化"""
        self.current_exif_watermark.fallback_to_file_time = self.exif_fallback_var.get()
        self.update_preview()
        if self.watermark_type == "exif":
            self._schedule_drag_refresh()
    
    def on_exif_position_changed(self, event=None):
        """EXIF水印位置变化"""
        position = self.exif_position_var.get()
        if position != "custom":  # 只有非自定义位置才设置预设位置
            self.current_exif_watermark.set_position(position)
        self.update_preview()
        if self.watermark_type == "exif":
            self._schedule_drag_refresh()
    
    # 模板管理相关方法
    def save_current_template(self):
        """保存当前水印设置为模板"""
        try:
            dialog = TemplateDialog(self.parent, self.template_manager, mode="save")
            
            # 设置获取当前水印设置的回调
            def get_current_watermark_callback(name, description):
                template = WatermarkTemplate(name, description)
                template.watermark_type = self.watermark_type
                template.text_settings = self.current_watermark.get_watermark_info()
                template.image_settings = self.current_image_watermark.get_watermark_info()
                template.exif_settings = self.current_exif_watermark.get_watermark_info()
                return template
            
            dialog.get_current_watermark_callback = get_current_watermark_callback
            
            result = dialog.show()
            if result:
                messagebox.showinfo("成功", f"模板 '{result.name}' 保存成功！\n\n模板包含以下设置：\n- 水印类型: {self.watermark_type}\n- 模板文件: templates/{result.name}.json")
                self.update_status(f"模板 '{result.name}' 已保存")
                self.update_template_status(f"已保存: {result.name}")
                
        except Exception as e:
            messagebox.showerror("错误", f"保存模板失败: {e}")
    
    def load_template(self):
        """加载水印模板"""
        try:
            dialog = TemplateDialog(self.parent, self.template_manager, mode="load")
            result = dialog.show()
            
            if result:
                self.apply_template(result)
                messagebox.showinfo("成功", f"模板 '{result.name}' 加载成功！\n\n已应用以下设置：\n- 水印类型: {result.watermark_type}")
                self.update_status(f"模板 '{result.name}' 已加载")
                self.update_template_status(f"已加载: {result.name}")
                
        except Exception as e:
            messagebox.showerror("错误", f"加载模板失败: {e}")
    
    def apply_template(self, template: WatermarkTemplate):
        """应用模板设置"""
        try:
            print(f"Applying template: {template.name}, type: {template.watermark_type}")
            
            # 1. 应用文本水印设置
            if template.text_settings:
                print("Loading text settings...")
                self.current_watermark.load_from_dict(template.text_settings)
                self.update_text_ui_from_watermark()
            
            # 2. 应用图片水印设置
            if template.image_settings:
                print("Loading image settings...")
                self.current_image_watermark.load_from_dict(template.image_settings)
                self.update_image_ui_from_watermark()
            
            # 3. 应用EXIF水印设置
            if template.exif_settings:
                print("Loading EXIF settings...")
                self.current_exif_watermark.load_from_dict(template.exif_settings)
                self.update_exif_ui_from_watermark()
            
            # 4. 设置水印类型（放在最后，这样UI会正确切换）
            self.watermark_type = template.watermark_type
            self.watermark_type_var.set(template.watermark_type)
            
            # 5. 触发UI更新
            self.on_watermark_type_changed()
            
            # 6. 强制刷新预览
            self.parent.after(100, self.update_preview)
            
            print("Template applied successfully")
            
        except Exception as e:
            print(f"Apply template failed: {e}")
            import traceback
            traceback.print_exc()
    
    def update_text_ui_from_watermark(self):
        """从水印设置更新文本UI"""
        try:
            print("Updating text UI from watermark...")
            
            # 更新文本输入框
            if hasattr(self, 'text_entry'):
                self.text_entry.delete(0, tk.END)
                self.text_entry.insert(0, self.current_watermark.text)
                print(f"  Text updated: {self.current_watermark.text}")
            
            # 更新字体大小
            if hasattr(self, 'font_size_var'):
                self.font_size_var.set(self.current_watermark.font_size)
                print(f"  Font size updated: {self.current_watermark.font_size}")
            
            # 更新颜色
            if hasattr(self, 'color_var'):
                self.color_var.set(self.current_watermark.color)
                print(f"  Color updated: {self.current_watermark.color}")
            
            # 更新透明度
            if hasattr(self, 'transparency_var'):
                self.transparency_var.set(self.current_watermark.transparency)
                print(f"  Transparency updated: {self.current_watermark.transparency}")
            
            # 更新位置
            if hasattr(self, 'position_var'):
                self.position_var.set(self.current_watermark.position)
                print(f"  Position updated: {self.current_watermark.position}")
            
            # 更新阴影和描边设置
            if hasattr(self, 'shadow_var'):
                self.shadow_var.set(self.current_watermark.shadow)
                print(f"  Shadow updated: {self.current_watermark.shadow}")
            
            if hasattr(self, 'outline_var'):
                self.outline_var.set(self.current_watermark.outline)
                print(f"  Outline updated: {self.current_watermark.outline}")
                
        except Exception as e:
            print(f"Update text UI failed: {e}")
    
    def update_image_ui_from_watermark(self):
        """从水印设置更新图片UI"""
        try:
            if hasattr(self, 'image_path_var') and self.current_image_watermark.watermark_path:
                self.image_path_var.set(os.path.basename(self.current_image_watermark.watermark_path))
            
            if hasattr(self, 'image_scale_var'):
                self.image_scale_var.set(self.current_image_watermark.scale_factor)
            
            if hasattr(self, 'image_transparency_var'):
                self.image_transparency_var.set(self.current_image_watermark.transparency)
            
            if hasattr(self, 'maintain_aspect_var'):
                self.maintain_aspect_var.set(self.current_image_watermark.maintain_aspect_ratio)
            
            if hasattr(self, 'image_position_var'):
                self.image_position_var.set(self.current_image_watermark.position)
                
        except Exception as e:
            print(f"Update image UI failed: {e}")
    
    def update_exif_ui_from_watermark(self):
        """从水印设置更新EXIF UI"""
        try:
            if hasattr(self, 'date_format_var'):
                self.date_format_var.set(self.current_exif_watermark.date_format)
            
            if hasattr(self, 'exif_prefix_var'):
                self.exif_prefix_var.set(self.current_exif_watermark.prefix_text)
            
            if hasattr(self, 'exif_suffix_var'):
                self.exif_suffix_var.set(self.current_exif_watermark.suffix_text)
            
            if hasattr(self, 'exif_font_size_var'):
                self.exif_font_size_var.set(self.current_exif_watermark.font_size)
            
            if hasattr(self, 'exif_transparency_var'):
                self.exif_transparency_var.set(self.current_exif_watermark.transparency)
            
            if hasattr(self, 'exif_fallback_var'):
                self.exif_fallback_var.set(self.current_exif_watermark.fallback_to_file_time)
            
            if hasattr(self, 'exif_position_var'):
                self.exif_position_var.set(self.current_exif_watermark.position)
                
        except Exception as e:
            print(f"Update EXIF UI failed: {e}")
    
    def manage_templates(self):
        """管理模板"""
        try:
            dialog = TemplateDialog(self.parent, self.template_manager, mode="manage")
            dialog.show()
            
        except Exception as e:
            messagebox.showerror("错误", f"管理模板失败: {e}")
    
    def on_drag_toggle(self):
        """拖拽开关变化"""
        if self.watermark_drag_handler:
            if self.drag_enabled_var.get():
                self.watermark_drag_handler.setup_events()
            else:
                self.preview_widget.unbind('<Button-1>')
                self.preview_widget.unbind('<B1-Motion>')
                self.preview_widget.unbind('<ButtonRelease-1>')
                self.preview_widget.unbind('<Motion>')
    
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
    
    def auto_load_last_settings(self):
        """自动加载上次的设置"""
        try:
            # 检查是否启用自动加载
            if not self.config.get('auto_load_last_settings', True):
                return
            
            # 首先尝试加载默认模板
            default_template = self.config.get('default_template', '')
            if default_template and self.template_manager:
                template = self.template_manager.load_template(default_template)
                if template:
                    self.apply_template(template)
                    print(f"Loaded default template: {default_template}")
                    return
            
            # 如果没有默认模板，加载上次的设置
            last_settings = self.config.get('last_settings', {})
            if last_settings:
                self.load_settings_from_config(last_settings)
                print("Loaded last settings from config")
                
        except Exception as e:
            print(f"Auto load settings failed: {e}")
    
    def load_settings_from_config(self, settings):
        """从配置中加载设置"""
        try:
            # 设置水印类型
            watermark_type = settings.get('watermark_type', 'text')
            self.watermark_type = watermark_type
            self.watermark_type_var.set(watermark_type)
            
            # 加载文本水印设置
            text_settings = settings.get('text_watermark', {})
            if text_settings:
                self.current_watermark.load_from_dict(text_settings)
                self.update_text_ui_from_watermark()
            
            # 加载图片水印设置
            image_settings = settings.get('image_watermark', {})
            if image_settings:
                self.current_image_watermark.load_from_dict(image_settings)
                self.update_image_ui_from_watermark()
            
            # 加载EXIF水印设置
            exif_settings = settings.get('exif_watermark', {})
            if exif_settings:
                self.current_exif_watermark.load_from_dict(exif_settings)
                self.update_exif_ui_from_watermark()
            
            # 更新界面显示
            self.on_watermark_type_changed()
            
        except Exception as e:
            print(f"Load settings from config failed: {e}")
    
    def save_current_settings_to_config(self):
        """保存当前设置到配置文件"""
        try:
            # 收集当前所有设置
            current_settings = {
                'watermark_type': self.watermark_type,
                'text_watermark': self.current_watermark.get_watermark_info(),
                'image_watermark': self.current_image_watermark.get_watermark_info(),
                'exif_watermark': self.current_exif_watermark.get_watermark_info()
            }
            
            # 更新配置
            self.config['last_settings'] = current_settings
            
            # 保存配置文件
            Config.save_config(self.config)
            print("Current settings saved to config")
            
        except Exception as e:
            print(f"Save current settings to config failed: {e}")
    
    def set_default_template(self, template_name):
        """设置默认模板"""
        try:
            self.config['default_template'] = template_name
            Config.save_config(self.config)
            print(f"Default template set to: {template_name}")
            self.update_template_status(f"默认模板: {template_name}" if template_name else "")
            
        except Exception as e:
            print(f"Set default template failed: {e}")
    
    def update_template_status(self, message):
        """更新模板状态显示"""
        if hasattr(self, 'template_status_label'):
            self.template_status_label.config(text=message)
