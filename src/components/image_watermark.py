# -*- coding: utf-8 -*-
"""
图片水印处理模块
处理图片水印的创建、样式设置和应用
"""

import os
import sys
from typing import Tuple, Optional, Dict, Any
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import Config

class ImageWatermark:
    """图片水印类"""
    
    def __init__(self):
        """初始化图片水印"""
        self.watermark_path = None
        self.watermark_image = None
        self.scale_factor = 0.2  # 水印相对于原图的缩放比例 (0.1-1.0)
        self.transparency = 80  # 透明度 (0-100)
        self.position = "bottom_right"
        self.custom_position = None
        self.maintain_aspect_ratio = True
        self.max_size_percent = 30  # 水印最大尺寸占原图的百分比
        
    def load_watermark_image(self, file_path: str) -> bool:
        """加载水印图片"""
        try:
            if not os.path.exists(file_path):
                return False
            
            # 验证文件格式
            if not Config.validate_image_format(file_path):
                return False
            
            # 加载图片
            watermark = Image.open(file_path)
            
            # 确保有透明通道支持
            if watermark.mode != 'RGBA':
                watermark = watermark.convert('RGBA')
            
            self.watermark_image = watermark
            self.watermark_path = file_path
            
            return True
            
        except Exception as e:
            print(f"Load watermark image failed: {e}")
            return False
    
    def set_scale_factor(self, scale: float):
        """设置缩放因子 (0.1-1.0)"""
        self.scale_factor = max(0.1, min(1.0, scale))
    
    def set_transparency(self, transparency: int):
        """设置透明度 (0-100)"""
        self.transparency = max(0, min(100, transparency))
    
    def set_position(self, position: str):
        """设置位置"""
        valid_positions = [
            "top_left", "top_center", "top_right",
            "center_left", "center", "center_right",
            "bottom_left", "bottom_center", "bottom_right"
        ]
        if position in valid_positions:
            self.position = position
            # 清除自定义位置
            self.custom_position = None
    
    def set_custom_position(self, position: Tuple[int, int]):
        """设置自定义位置"""
        self.custom_position = position
    
    def set_maintain_aspect_ratio(self, maintain: bool):
        """设置是否保持宽高比"""
        self.maintain_aspect_ratio = maintain
    
    def set_max_size_percent(self, percent: int):
        """设置水印最大尺寸百分比 (10-50)"""
        self.max_size_percent = max(10, min(50, percent))
    
    def _calculate_watermark_size(self, target_size: Tuple[int, int]) -> Tuple[int, int]:
        """计算水印尺寸"""
        if not self.watermark_image:
            return (0, 0)
        
        target_width, target_height = target_size
        watermark_width, watermark_height = self.watermark_image.size
        
        # 基于缩放因子计算尺寸
        new_width = int(target_width * self.scale_factor)
        new_height = int(target_height * self.scale_factor)
        
        if self.maintain_aspect_ratio:
            # 保持宽高比，以较小的缩放比为准
            ratio = min(new_width / watermark_width, new_height / watermark_height)
            new_width = int(watermark_width * ratio)
            new_height = int(watermark_height * ratio)
        
        # 限制最大尺寸
        max_width = int(target_width * self.max_size_percent / 100)
        max_height = int(target_height * self.max_size_percent / 100)
        
        if new_width > max_width or new_height > max_height:
            ratio = min(max_width / new_width, max_height / new_height)
            new_width = int(new_width * ratio)
            new_height = int(new_height * ratio)
        
        return (new_width, new_height)
    
    def _calculate_position(self, image_size: Tuple[int, int], 
                          watermark_size: Tuple[int, int]) -> Tuple[int, int]:
        """计算水印位置"""
        img_width, img_height = image_size
        wm_width, wm_height = watermark_size
        
        # 如果有自定义位置，使用自定义位置
        if self.custom_position:
            return self.custom_position
        
        # 边距
        margin = min(img_width, img_height) // 20  # 动态边距
        
        position_map = {
            "top_left": (margin, margin),
            "top_center": ((img_width - wm_width) // 2, margin),
            "top_right": (img_width - wm_width - margin, margin),
            "center_left": (margin, (img_height - wm_height) // 2),
            "center": ((img_width - wm_width) // 2, (img_height - wm_height) // 2),
            "center_right": (img_width - wm_width - margin, (img_height - wm_height) // 2),
            "bottom_left": (margin, img_height - wm_height - margin),
            "bottom_center": ((img_width - wm_width) // 2, img_height - wm_height - margin),
            "bottom_right": (img_width - wm_width - margin, img_height - wm_height - margin)
        }
        
        return position_map.get(self.position, position_map["bottom_right"])
    
    def apply_to_image(self, image: Image.Image) -> Optional[Image.Image]:
        """将图片水印应用到图片上"""
        try:
            if not self.watermark_image:
                return None
            
            # 确保目标图片是RGBA模式
            if image.mode != 'RGBA':
                result_image = image.convert('RGBA')
            else:
                result_image = image.copy()
            
            # 计算水印尺寸
            watermark_size = self._calculate_watermark_size(image.size)
            if watermark_size[0] <= 0 or watermark_size[1] <= 0:
                return result_image
            
            # 缩放水印图片
            try:
                # 兼容不同PIL版本
                scaled_watermark = self.watermark_image.resize(watermark_size, Image.Resampling.LANCZOS)
            except AttributeError:
                scaled_watermark = self.watermark_image.resize(watermark_size, Image.LANCZOS)
            
            # 调整透明度
            if self.transparency < 100:
                alpha = int(255 * self.transparency / 100)
                # 创建透明度遮罩
                alpha_mask = scaled_watermark.split()[-1]  # 获取alpha通道
                alpha_mask = alpha_mask.point(lambda x: int(x * alpha / 255))
                scaled_watermark.putalpha(alpha_mask)
            
            # 计算位置
            position = self._calculate_position(image.size, watermark_size)
            
            # 粘贴水印
            result_image.paste(scaled_watermark, position, scaled_watermark)
            
            return result_image
            
        except Exception as e:
            print(f"Apply image watermark failed: {e}")
            return None
    
    def get_watermark_info(self) -> Dict[str, Any]:
        """获取水印信息"""
        return {
            'watermark_path': self.watermark_path,
            'scale_factor': self.scale_factor,
            'transparency': self.transparency,
            'position': self.position,
            'custom_position': self.custom_position,
            'maintain_aspect_ratio': self.maintain_aspect_ratio,
            'max_size_percent': self.max_size_percent
        }
    
    def load_from_dict(self, data: Dict[str, Any]):
        """从字典加载水印设置"""
        try:
            if 'watermark_path' in data and data['watermark_path']:
                self.load_watermark_image(data['watermark_path'])
            
            self.scale_factor = data.get('scale_factor', 0.2)
            self.transparency = data.get('transparency', 80)
            self.position = data.get('position', 'bottom_right')
            self.custom_position = data.get('custom_position', None)
            self.maintain_aspect_ratio = data.get('maintain_aspect_ratio', True)
            self.max_size_percent = data.get('max_size_percent', 30)
            
        except Exception as e:
            print(f"Load image watermark from dict failed: {e}")


class ImageWatermarkDialog:
    """图片水印设置对话框"""
    
    def __init__(self, parent, watermark: ImageWatermark = None):
        """初始化对话框"""
        self.parent = parent
        self.watermark = watermark or ImageWatermark()
        self.result = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """创建对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("图片水印设置")
        self.dialog.geometry("450x600")
        self.dialog.resizable(False, False)
        
        # 使对话框模态
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_widgets()
        
        # 居中显示
        self.center_dialog()
    
    def center_dialog(self):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """创建控件"""
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 图片选择
        image_frame = tk.LabelFrame(main_frame, text="水印图片", padx=5, pady=5)
        image_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.image_path_var = tk.StringVar(value=self.watermark.watermark_path or "")
        tk.Label(image_frame, text="图片路径:").grid(row=0, column=0, sticky=tk.W, pady=2)
        path_entry = tk.Entry(image_frame, textvariable=self.image_path_var, width=30, state="readonly")
        path_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 5))
        select_btn = tk.Button(image_frame, text="选择图片", command=self.select_watermark_image)
        select_btn.grid(row=0, column=2, sticky=tk.W)
        
        # 预览区域
        preview_frame = tk.LabelFrame(main_frame, text="预览", padx=5, pady=5)
        preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_label = tk.Label(preview_frame, text="请选择水印图片", 
                                    width=40, height=8, bg="lightgray", relief="sunken")
        self.preview_label.pack()
        
        # 尺寸设置
        size_frame = tk.LabelFrame(main_frame, text="尺寸设置", padx=5, pady=5)
        size_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(size_frame, text="缩放比例:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.scale_var = tk.DoubleVar(value=self.watermark.scale_factor)
        scale_scale = tk.Scale(size_frame, from_=0.1, to=1.0, resolution=0.05, 
                              orient=tk.HORIZONTAL, variable=self.scale_var, length=200)
        scale_scale.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        tk.Label(size_frame, text="最大尺寸(%):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.max_size_var = tk.IntVar(value=self.watermark.max_size_percent)
        max_size_scale = tk.Scale(size_frame, from_=10, to=50, orient=tk.HORIZONTAL,
                                 variable=self.max_size_var, length=200)
        max_size_scale.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        self.aspect_var = tk.BooleanVar(value=self.watermark.maintain_aspect_ratio)
        aspect_check = tk.Checkbutton(size_frame, text="保持宽高比", variable=self.aspect_var)
        aspect_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # 透明度设置
        transparency_frame = tk.LabelFrame(main_frame, text="透明度设置", padx=5, pady=5)
        transparency_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(transparency_frame, text="透明度:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.transparency_var = tk.IntVar(value=self.watermark.transparency)
        transparency_scale = tk.Scale(transparency_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                    variable=self.transparency_var, length=200)
        transparency_scale.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # 位置设置
        position_frame = tk.LabelFrame(main_frame, text="位置设置", padx=5, pady=5)
        position_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(position_frame, text="位置:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.position_var = tk.StringVar(value=self.watermark.position)
        position_combo = tk.ttk.Combobox(position_frame, textvariable=self.position_var, width=20)
        position_combo['values'] = ('top_left', 'top_center', 'top_right',
                                   'center_left', 'center', 'center_right',
                                   'bottom_left', 'bottom_center', 'bottom_right')
        position_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # 按钮
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.RIGHT)
        
        # 更新预览
        if self.watermark.watermark_path:
            self.update_preview()
    
    def select_watermark_image(self):
        """选择水印图片"""
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
            if self.watermark.load_watermark_image(file_path):
                self.image_path_var.set(file_path)
                self.update_preview()
            else:
                messagebox.showerror("错误", "无法加载图片，请选择有效的图片文件")
    
    def update_preview(self):
        """更新预览"""
        if not self.watermark.watermark_image:
            return
        
        try:
            # 创建预览图片
            preview_size = (150, 100)
            preview_img = self.watermark.watermark_image.copy()
            
            # 缩放到预览尺寸
            try:
                preview_img = preview_img.resize(preview_size, Image.Resampling.LANCZOS)
            except AttributeError:
                preview_img = preview_img.resize(preview_size, Image.LANCZOS)
            
            # 转换为tkinter可用的格式
            from PIL import ImageTk
            photo = ImageTk.PhotoImage(preview_img)
            
            # 更新预览标签
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # 保持引用
            
        except Exception as e:
            print(f"Update preview failed: {e}")
    
    def ok_clicked(self):
        """确定按钮点击"""
        try:
            # 更新水印设置
            self.watermark.set_scale_factor(self.scale_var.get())
            self.watermark.set_transparency(self.transparency_var.get())
            self.watermark.set_position(self.position_var.get())
            self.watermark.set_maintain_aspect_ratio(self.aspect_var.get())
            self.watermark.set_max_size_percent(self.max_size_var.get())
            
            self.result = self.watermark
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {e}")
    
    def cancel_clicked(self):
        """取消按钮点击"""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """显示对话框并返回结果"""
        self.dialog.wait_window()
        return self.result
