# -*- coding: utf-8 -*-
"""
文本水印处理模块
处理文本水印的创建、样式设置和应用
"""

import os
import math
from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import colorchooser

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import Config

class TextWatermark:
    """文本水印类"""
    
    def __init__(self):
        """初始化文本水印"""
        self.text = "Watermark"
        self.font_size = 24
        self.font_family = "STHeiti Medium.ttc"  # 使用支持中文的默认字体
        self.color = "#FFFFFF"
        self.transparency = 80  # 0-100
        self.position = "bottom_right"
        self.angle = 0
        self.shadow = False
        self.outline = False
        self.shadow_color = "#000000"
        self.outline_color = "#000000"
        self.outline_width = 1
        
        # 自定义位置
        self.custom_position = None
        
        # 字体缓存
        self._font_cache = {}
    
    def set_text(self, text: str):
        """设置水印文本"""
        self.text = text
    
    def set_font_size(self, size: int):
        """设置字体大小"""
        self.font_size = max(8, min(200, size))  # 限制字体大小范围
    
    def set_font_family(self, family: str):
        """设置字体族"""
        self.font_family = family
        # 清除字体缓存
        self._font_cache.clear()
    
    def set_color(self, color: str):
        """设置颜色"""
        self.color = color
    
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
    
    def set_angle(self, angle: float):
        """设置旋转角度"""
        self.angle = angle % 360
    
    def set_shadow(self, enabled: bool, color: str = "#000000"):
        """设置阴影效果"""
        self.shadow = enabled
        self.shadow_color = color
    
    def set_outline(self, enabled: bool, color: str = "#000000", width: int = 1):
        """设置描边效果"""
        self.outline = enabled
        self.outline_color = color
        self.outline_width = max(1, width)
    
    def _get_font(self, size: int = None) -> ImageFont.ImageFont:
        """获取字体对象，优先选择支持中文的字体"""
        if size is None:
            size = self.font_size
        
        cache_key = f"{self.font_family}_{size}"
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        font = None
        
        # 首先尝试用户指定的字体
        try:
            font = ImageFont.truetype(self.font_family, size)
        except (OSError, IOError):
            # 如果用户指定字体失败，尝试支持中文的系统字体
            chinese_fonts = [
                # macOS 中文字体
                "/System/Library/Fonts/STHeiti Medium.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc", 
                "/System/Library/Fonts/Supplemental/Songti.ttc",
                "STHeiti Medium.ttc",
                "Hiragino Sans GB.ttc",
                # 通用字体（也支持中文）
                "Arial.ttf",
                "Helvetica.ttc",
                # Windows 中文字体（如果在Windows上运行）
                "C:/Windows/Fonts/simsun.ttc",
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/msyh.ttc",
                # Linux 中文字体
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
            ]
            
            for font_path in chinese_fonts:
                try:
                    font = ImageFont.truetype(font_path, size)
                    print(f"Using fallback Chinese font: {font_path}")
                    break
                except (OSError, IOError):
                    continue
            
            # 如果所有中文字体都失败，使用默认字体
            if font is None:
                try:
                    font = ImageFont.load_default()
                    print("Warning: Using default font, Chinese characters may not display correctly")
                except:
                    font = ImageFont.load_default()
        
        self._font_cache[cache_key] = font
        return font
    
    def _hex_to_rgba(self, hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
        """将十六进制颜色转换为RGBA"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        else:
            r = g = b = 0
        
        # 应用透明度
        alpha = int(alpha * self.transparency / 100)
        return (r, g, b, alpha)
    
    def _calculate_position(self, image_size: Tuple[int, int], text_size: Tuple[int, int]) -> Tuple[int, int]:
        """计算文本位置"""
        # 如果有自定义位置，优先使用
        if self.custom_position:
            return self.custom_position
        
        img_width, img_height = image_size
        text_width, text_height = text_size
        
        # 边距
        margin = 20
        
        position_map = {
            "top_left": (margin, margin),
            "top_center": ((img_width - text_width) // 2, margin),
            "top_right": (img_width - text_width - margin, margin),
            "center_left": (margin, (img_height - text_height) // 2),
            "center": ((img_width - text_width) // 2, (img_height - text_height) // 2),
            "center_right": (img_width - text_width - margin, (img_height - text_height) // 2),
            "bottom_left": (margin, img_height - text_height - margin),
            "bottom_center": ((img_width - text_width) // 2, img_height - text_height - margin),
            "bottom_right": (img_width - text_width - margin, img_height - text_height - margin)
        }
        
        return position_map.get(self.position, position_map["bottom_right"])
    
    def _draw_text_with_effects(self, draw: ImageDraw.Draw, position: Tuple[int, int], 
                               text: str, font: ImageFont.ImageFont, 
                               fill_color: Tuple[int, int, int, int]):
        """绘制带效果的文本"""
        x, y = position
        
        # 绘制阴影
        if self.shadow:
            shadow_color = self._hex_to_rgba(self.shadow_color, fill_color[3])
            shadow_offset = 2
            draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
        
        # 绘制描边
        if self.outline and self.outline_width > 0:
            outline_color = self._hex_to_rgba(self.outline_color, fill_color[3])
            for dx in range(-self.outline_width, self.outline_width + 1):
                for dy in range(-self.outline_width, self.outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        
        # 绘制主文本
        draw.text((x, y), text, font=font, fill=fill_color)
    
    def create_watermark_image(self, size: Tuple[int, int]) -> Optional[Image.Image]:
        """创建水印图片"""
        try:
            # 创建透明背景
            watermark = Image.new('RGBA', size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # 获取字体
            font = self._get_font()
            
            # 计算文本尺寸
            bbox = draw.textbbox((0, 0), self.text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 计算位置
            position = self._calculate_position(size, (text_width, text_height))
            
            # 获取颜色
            fill_color = self._hex_to_rgba(self.color)
            
            # 绘制文本
            self._draw_text_with_effects(draw, position, self.text, font, fill_color)
            
            # 旋转处理
            if self.angle != 0:
                watermark = watermark.rotate(self.angle, expand=True, fillcolor=(0, 0, 0, 0))
            
            return watermark
            
        except Exception as e:
            print(f"Create watermark image failed: {e}")
            return None
    
    def apply_to_image(self, image: Image.Image) -> Optional[Image.Image]:
        """将水印应用到图片上"""
        try:
            # 创建水印图片
            watermark = self.create_watermark_image(image.size)
            if not watermark:
                return None
            
            # 确保图片是RGBA模式
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # 调整水印大小以匹配图片
            if watermark.size != image.size:
                # 兼容不同PIL版本
                try:
                    watermark = watermark.resize(image.size, Image.Resampling.LANCZOS)
                except AttributeError:
                    watermark = watermark.resize(image.size, Image.LANCZOS)
            
            # 合成水印
            result = Image.alpha_composite(image, watermark)
            
            return result
            
        except Exception as e:
            print(f"Apply watermark failed: {e}")
            return None
    
    def get_watermark_info(self) -> Dict[str, Any]:
        """获取水印信息"""
        return {
            'text': self.text,
            'font_size': self.font_size,
            'font_family': self.font_family,
            'color': self.color,
            'transparency': self.transparency,
            'position': self.position,
            'angle': self.angle,
            'shadow': self.shadow,
            'outline': self.outline,
            'shadow_color': self.shadow_color,
            'outline_color': self.outline_color,
            'outline_width': self.outline_width
        }
    
    def load_from_dict(self, data: Dict[str, Any]):
        """从字典加载水印设置"""
        self.text = data.get('text', self.text)
        self.font_size = data.get('font_size', self.font_size)
        self.font_family = data.get('font_family', self.font_family)
        self.color = data.get('color', self.color)
        self.transparency = data.get('transparency', self.transparency)
        self.position = data.get('position', self.position)
        self.angle = data.get('angle', self.angle)
        self.shadow = data.get('shadow', self.shadow)
        self.outline = data.get('outline', self.outline)
        self.shadow_color = data.get('shadow_color', self.shadow_color)
        self.outline_color = data.get('outline_color', self.outline_color)
        self.outline_width = data.get('outline_width', self.outline_width)
    
    def preview_watermark(self, image: Image.Image, preview_size: Tuple[int, int] = None) -> Optional[Image.Image]:
        """预览水印效果"""
        try:
            if preview_size:
                # 创建预览图片
                preview = image.copy()
                # 兼容不同PIL版本
                try:
                    preview.thumbnail(preview_size, Image.Resampling.LANCZOS)
                except AttributeError:
                    preview.thumbnail(preview_size, Image.LANCZOS)
                return self.apply_to_image(preview)
            else:
                return self.apply_to_image(image)
        except Exception as e:
            print(f"Preview watermark failed: {e}")
            return None

class TextWatermarkDialog:
    """文本水印设置对话框"""
    
    def __init__(self, parent, watermark: TextWatermark = None):
        """初始化对话框"""
        self.parent = parent
        self.watermark = watermark or TextWatermark()
        self.result = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """创建对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("文本水印设置")
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)
        
        # 使对话框模态
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_widgets()
        
        # 居中显示
        self.center_dialog()
    
    def create_widgets(self):
        """创建控件"""
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 文本设置
        text_frame = tk.LabelFrame(main_frame, text="文本设置", padx=5, pady=5)
        text_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(text_frame, text="水印文本:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.text_entry = tk.Entry(text_frame, width=30)
        self.text_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        self.text_entry.insert(0, self.watermark.text)
        
        # 字体设置
        font_frame = tk.LabelFrame(main_frame, text="字体设置", padx=5, pady=5)
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(font_frame, text="字体大小:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.font_size_var = tk.IntVar(value=self.watermark.font_size)
        font_size_scale = tk.Scale(font_frame, from_=8, to=100, orient=tk.HORIZONTAL, 
                                 variable=self.font_size_var, length=200)
        font_size_scale.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        tk.Label(font_frame, text="字体族:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.font_family_var = tk.StringVar(value=self.watermark.font_family)
        font_family_combo = tk.ttk.Combobox(font_frame, textvariable=self.font_family_var, width=20)
        font_family_combo['values'] = (
            'STHeiti Medium.ttc',  # 黑体（推荐中文）
            'Hiragino Sans GB.ttc',  # 冬青黑体（推荐中文）
            'Arial',  # Arial（支持中文）
            'Helvetica',  # Helvetica（支持中文）
            'Times New Roman', 
            'Courier New'
        )
        font_family_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        # 颜色设置
        color_frame = tk.LabelFrame(main_frame, text="颜色设置", padx=5, pady=5)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(color_frame, text="文本颜色:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.color_var = tk.StringVar(value=self.watermark.color)
        color_entry = tk.Entry(color_frame, textvariable=self.color_var, width=15)
        color_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        color_button = tk.Button(color_frame, text="选择", command=self.choose_color)
        color_button.grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        
        tk.Label(color_frame, text="透明度:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.transparency_var = tk.IntVar(value=self.watermark.transparency)
        transparency_scale = tk.Scale(color_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                    variable=self.transparency_var, length=200)
        transparency_scale.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
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
        
        # 效果设置
        effect_frame = tk.LabelFrame(main_frame, text="效果设置", padx=5, pady=5)
        effect_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.shadow_var = tk.BooleanVar(value=self.watermark.shadow)
        shadow_check = tk.Checkbutton(effect_frame, text="阴影效果", variable=self.shadow_var)
        shadow_check.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.outline_var = tk.BooleanVar(value=self.watermark.outline)
        outline_check = tk.Checkbutton(effect_frame, text="描边效果", variable=self.outline_var)
        outline_check.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # 按钮
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(button_frame, text="确定", command=self.ok_clicked, width=10).pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(button_frame, text="取消", command=self.cancel_clicked, width=10).pack(side=tk.RIGHT)
    
    def choose_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(title="选择颜色", color=self.color_var.get())
        if color[1]:
            self.color_var.set(color[1])
    
    def center_dialog(self):
        """对话框居中"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def ok_clicked(self):
        """确定按钮点击"""
        # 更新水印设置
        self.watermark.set_text(self.text_entry.get())
        self.watermark.set_font_size(self.font_size_var.get())
        self.watermark.set_font_family(self.font_family_var.get())
        self.watermark.set_color(self.color_var.get())
        self.watermark.set_transparency(self.transparency_var.get())
        self.watermark.set_position(self.position_var.get())
        self.watermark.set_shadow(self.shadow_var.get())
        self.watermark.set_outline(self.outline_var.get())
        
        self.result = self.watermark
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """取消按钮点击"""
        self.result = None
        self.dialog.destroy()
    
    def show(self) -> Optional[TextWatermark]:
        """显示对话框并返回结果"""
        self.dialog.wait_window()
        return self.result
