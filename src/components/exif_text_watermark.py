# -*- coding: utf-8 -*-
"""
EXIF文本水印处理模块
从图片EXIF信息中提取日期并作为水印
"""

import os
import sys
from typing import Tuple, Optional, Dict, Any
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import Config

# 尝试导入EXIF处理库
try:
    import piexif
    PIEXIF_AVAILABLE = True
except ImportError:
    PIEXIF_AVAILABLE = False

try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    EXIFREAD_AVAILABLE = False

class ExifTextWatermark:
    """EXIF文本水印类"""
    
    def __init__(self):
        """初始化EXIF文本水印"""
        self.font_size = 24
        self.font_family = "STHeiti Medium.ttc"  # 使用支持中文的默认字体
        self.color = "#FFFFFF"
        self.transparency = 80  # 0-100
        self.position = "bottom_right"
        self.custom_position = None
        self.angle = 0
        self.shadow = True
        self.outline = False
        self.shadow_color = "#000000"
        self.outline_color = "#000000"
        self.outline_width = 1
        
        # EXIF特定设置
        self.date_format = "%Y-%m-%d"  # 日期格式
        self.fallback_to_file_time = True  # 如果没有EXIF日期，是否使用文件修改时间
        self.prefix_text = ""  # 前缀文本，如 "拍摄于: "
        self.suffix_text = ""  # 后缀文本
        
        # 字体缓存
        self._font_cache = {}
    
    def set_font_size(self, size: int):
        """设置字体大小"""
        self.font_size = max(8, min(200, size))
    
    def set_font_family(self, family: str):
        """设置字体族"""
        self.font_family = family
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
            self.custom_position = None
    
    def set_custom_position(self, position: Tuple[int, int]):
        """设置自定义位置"""
        self.custom_position = position
    
    def set_date_format(self, format_str: str):
        """设置日期格式"""
        self.date_format = format_str
    
    def set_prefix_suffix(self, prefix: str = "", suffix: str = ""):
        """设置前缀和后缀文本"""
        self.prefix_text = prefix
        self.suffix_text = suffix
    
    def extract_date_from_exif(self, image_path: str) -> Optional[str]:
        """从EXIF信息中提取日期"""
        try:
            # 优先使用piexif
            if PIEXIF_AVAILABLE:
                return self._extract_date_piexif(image_path)
            
            # 备用使用exifread
            if EXIFREAD_AVAILABLE:
                return self._extract_date_exifread(image_path)
            
            return None
            
        except Exception as e:
            print(f"Extract EXIF date failed: {e}")
            return None
    
    def _extract_date_piexif(self, image_path: str) -> Optional[str]:
        """使用piexif提取日期"""
        try:
            exif_data = piexif.load(image_path)
            
            # 尝试不同的日期字段
            date_fields = [
                ('Exif', piexif.ExifIFD.DateTimeOriginal),
                ('Exif', piexif.ExifIFD.DateTimeDigitized),
                ('0th', piexif.ImageIFD.DateTime)
            ]
            
            for group, field in date_fields:
                try:
                    if group in exif_data and field in exif_data[group]:
                        date_str = exif_data[group][field].decode('utf-8')
                        # 转换格式 "2023:01:15 12:30:45" -> "2023-01-15"
                        date_part = date_str.split(' ')[0]
                        formatted_date = date_part.replace(':', '-')
                        
                        # 验证日期格式
                        datetime.strptime(formatted_date, "%Y-%m-%d")
                        return formatted_date
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Extract date with piexif failed: {e}")
            return None
    
    def _extract_date_exifread(self, image_path: str) -> Optional[str]:
        """使用exifread提取日期"""
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f)
            
            # 尝试不同的日期标签
            date_tags = [
                'EXIF DateTimeOriginal',
                'EXIF DateTimeDigitized',
                'Image DateTime'
            ]
            
            for tag_name in date_tags:
                if tag_name in tags:
                    date_str = str(tags[tag_name])
                    # 转换格式
                    date_part = date_str.split(' ')[0]
                    formatted_date = date_part.replace(':', '-')
                    
                    # 验证日期格式
                    datetime.strptime(formatted_date, "%Y-%m-%d")
                    return formatted_date
            
            return None
            
        except Exception as e:
            print(f"Extract date with exifread failed: {e}")
            return None
    
    def get_file_modification_date(self, image_path: str) -> str:
        """获取文件修改日期作为备用"""
        try:
            mtime = os.path.getmtime(image_path)
            return datetime.fromtimestamp(mtime).strftime(self.date_format)
        except:
            return datetime.now().strftime(self.date_format)
    
    def generate_watermark_text(self, image_path: str) -> str:
        """生成水印文本"""
        # 尝试从EXIF获取日期
        exif_date = self.extract_date_from_exif(image_path)
        
        if exif_date:
            date_text = exif_date
        elif self.fallback_to_file_time:
            date_text = self.get_file_modification_date(image_path)
        else:
            return ""  # 如果不允许备用，返回空字符串
        
        # 格式化最终文本
        final_text = f"{self.prefix_text}{date_text}{self.suffix_text}"
        return final_text.strip()
    
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
        try:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return (r, g, b, alpha)
            else:
                return (255, 255, 255, alpha)  # 默认白色
        except:
            return (255, 255, 255, alpha)  # 默认白色
    
    def _calculate_position(self, image_size: Tuple[int, int], 
                          text_size: Tuple[int, int]) -> Tuple[int, int]:
        """计算文本位置"""
        img_width, img_height = image_size
        text_width, text_height = text_size
        
        # 如果有自定义位置，使用自定义位置
        if self.custom_position:
            return self.custom_position
        
        # 边距
        margin = min(img_width, img_height) // 20
        
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
            shadow_offset = max(1, self.font_size // 20)
            draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
        
        # 绘制描边
        if self.outline:
            outline_color = self._hex_to_rgba(self.outline_color, fill_color[3])
            for dx in range(-self.outline_width, self.outline_width + 1):
                for dy in range(-self.outline_width, self.outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        
        # 绘制主文本
        draw.text((x, y), text, font=font, fill=fill_color)
    
    def apply_to_image_with_path(self, image: Image.Image, image_path: str) -> Optional[Image.Image]:
        """将EXIF水印应用到图片上（需要图片路径来提取EXIF）"""
        try:
            # 生成水印文本
            watermark_text = self.generate_watermark_text(image_path)
            if not watermark_text:
                return image  # 如果没有日期信息，返回原图
            
            # 确保图片是RGBA模式
            if image.mode != 'RGBA':
                result_image = image.convert('RGBA')
            else:
                result_image = image.copy()
            
            # 创建绘制对象
            draw = ImageDraw.Draw(result_image)
            
            # 获取字体
            font = self._get_font()
            
            # 计算文本尺寸
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 计算位置
            position = self._calculate_position(image.size, (text_width, text_height))
            
            # 计算透明度
            alpha = int(255 * self.transparency / 100)
            fill_color = self._hex_to_rgba(self.color, alpha)
            
            # 绘制文本
            self._draw_text_with_effects(draw, position, watermark_text, font, fill_color)
            
            # 旋转处理
            if self.angle != 0:
                result_image = result_image.rotate(self.angle, expand=True, fillcolor=(0, 0, 0, 0))
            
            return result_image
            
        except Exception as e:
            print(f"Apply EXIF watermark failed: {e}")
            return image
    
    def get_watermark_info(self) -> Dict[str, Any]:
        """获取水印信息"""
        return {
            'font_size': self.font_size,
            'font_family': self.font_family,
            'color': self.color,
            'transparency': self.transparency,
            'position': self.position,
            'custom_position': self.custom_position,
            'angle': self.angle,
            'shadow': self.shadow,
            'outline': self.outline,
            'shadow_color': self.shadow_color,
            'outline_color': self.outline_color,
            'outline_width': self.outline_width,
            'date_format': self.date_format,
            'fallback_to_file_time': self.fallback_to_file_time,
            'prefix_text': self.prefix_text,
            'suffix_text': self.suffix_text
        }
    
    def load_from_dict(self, data: Dict[str, Any]):
        """从字典加载水印设置"""
        try:
            self.font_size = data.get('font_size', 24)
            self.font_family = data.get('font_family', 'Arial')
            self.color = data.get('color', '#FFFFFF')
            self.transparency = data.get('transparency', 80)
            self.position = data.get('position', 'bottom_right')
            self.custom_position = data.get('custom_position', None)
            self.angle = data.get('angle', 0)
            self.shadow = data.get('shadow', True)
            self.outline = data.get('outline', False)
            self.shadow_color = data.get('shadow_color', '#000000')
            self.outline_color = data.get('outline_color', '#000000')
            self.outline_width = data.get('outline_width', 1)
            self.date_format = data.get('date_format', '%Y-%m-%d')
            self.fallback_to_file_time = data.get('fallback_to_file_time', True)
            self.prefix_text = data.get('prefix_text', '')
            self.suffix_text = data.get('suffix_text', '')
            
            # 清除字体缓存
            self._font_cache.clear()
            
        except Exception as e:
            print(f"Load EXIF watermark from dict failed: {e}")


class ExifWatermarkDialog:
    """EXIF水印设置对话框"""
    
    def __init__(self, parent, watermark: ExifTextWatermark = None):
        """初始化对话框"""
        self.parent = parent
        self.watermark = watermark or ExifTextWatermark()
        self.result = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """创建对话框"""
        import tkinter as tk
        from tkinter import ttk, messagebox
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("EXIF时间水印设置")
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
        
        # EXIF设置
        exif_frame = tk.LabelFrame(main_frame, text="EXIF设置", padx=5, pady=5)
        exif_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(exif_frame, text="日期格式:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.date_format_var = tk.StringVar(value=self.watermark.date_format)
        date_format_combo = ttk.Combobox(exif_frame, textvariable=self.date_format_var, width=20)
        date_format_combo['values'] = ('%Y-%m-%d', '%Y年%m月%d日', '%m/%d/%Y', '%d-%m-%Y')
        date_format_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        self.fallback_var = tk.BooleanVar(value=self.watermark.fallback_to_file_time)
        fallback_check = tk.Checkbutton(exif_frame, text="无EXIF时使用文件时间", variable=self.fallback_var)
        fallback_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        tk.Label(exif_frame, text="前缀文本:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.prefix_var = tk.StringVar(value=self.watermark.prefix_text)
        prefix_entry = tk.Entry(exif_frame, textvariable=self.prefix_var, width=25)
        prefix_entry.grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        
        tk.Label(exif_frame, text="后缀文本:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.suffix_var = tk.StringVar(value=self.watermark.suffix_text)
        suffix_entry = tk.Entry(exif_frame, textvariable=self.suffix_var, width=25)
        suffix_entry.grid(row=3, column=1, sticky=tk.W, padx=(5, 0))
        
        # 字体设置
        font_frame = tk.LabelFrame(main_frame, text="字体设置", padx=5, pady=5)
        font_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(font_frame, text="字体大小:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.font_size_var = tk.IntVar(value=self.watermark.font_size)
        font_size_scale = tk.Scale(font_frame, from_=8, to=100, orient=tk.HORIZONTAL, 
                                  variable=self.font_size_var, length=200)
        font_size_scale.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
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
        position_combo = ttk.Combobox(position_frame, textvariable=self.position_var, width=20)
        position_combo['values'] = ('top_left', 'top_center', 'top_right',
                                   'center_left', 'center', 'center_right',
                                   'bottom_left', 'bottom_center', 'bottom_right')
        position_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # 效果设置
        effect_frame = tk.LabelFrame(main_frame, text="效果设置", padx=5, pady=5)
        effect_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.shadow_var = tk.BooleanVar(value=self.watermark.shadow)
        shadow_check = tk.Checkbutton(effect_frame, text="阴影效果", variable=self.shadow_var)
        shadow_check.pack(anchor=tk.W)
        
        self.outline_var = tk.BooleanVar(value=self.watermark.outline)
        outline_check = tk.Checkbutton(effect_frame, text="描边效果", variable=self.outline_var)
        outline_check.pack(anchor=tk.W)
        
        # 按钮
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.RIGHT)
    
    def choose_color(self):
        """选择颜色"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(color=self.color_var.get())
        if color[1]:
            self.color_var.set(color[1])
    
    def ok_clicked(self):
        """确定按钮点击"""
        try:
            # 更新水印设置
            self.watermark.set_font_size(self.font_size_var.get())
            self.watermark.set_color(self.color_var.get())
            self.watermark.set_transparency(self.transparency_var.get())
            self.watermark.set_position(self.position_var.get())
            self.watermark.set_date_format(self.date_format_var.get())
            self.watermark.fallback_to_file_time = self.fallback_var.get()
            self.watermark.set_prefix_suffix(self.prefix_var.get(), self.suffix_var.get())
            self.watermark.shadow = self.shadow_var.get()
            self.watermark.outline = self.outline_var.get()
            
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
