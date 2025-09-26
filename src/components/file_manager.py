# -*- coding: utf-8 -*-
"""
文件管理模块
处理图片导入、验证和导出功能
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import List, Optional, Tuple
from PIL import Image
import shutil

from config import Config

class ImageFileManager:
    """图片文件管理器"""
    
    def __init__(self):
        """初始化文件管理器"""
        self.supported_formats = Config.SUPPORTED_FORMATS
        self.max_file_size = Config.MAX_IMAGE_SIZE
    
    def import_single_image(self, parent_window=None) -> Optional[str]:
        """导入单张图片"""
        try:
            file_path = filedialog.askopenfilename(
                parent=parent_window,
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
            
            if file_path and self.validate_image_file(file_path):
                return file_path
            elif file_path:
                messagebox.showerror("错误", f"不支持的文件格式: {os.path.basename(file_path)}")
            
            return None
            
        except Exception as e:
            messagebox.showerror("错误", f"导入图片失败: {e}")
            return None
    
    def import_multiple_images(self, parent_window=None) -> List[str]:
        """批量导入图片"""
        try:
            file_paths = filedialog.askopenfilenames(
                parent=parent_window,
                title="选择多张图片文件",
                filetypes=[
                    ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                    ("所有文件", "*.*")
                ]
            )
            
            valid_files = []
            invalid_files = []
            
            for file_path in file_paths:
                if self.validate_image_file(file_path):
                    valid_files.append(file_path)
                else:
                    invalid_files.append(os.path.basename(file_path))
            
            if invalid_files:
                messagebox.showwarning(
                    "警告", 
                    f"以下文件格式不支持，已跳过:\n{', '.join(invalid_files)}"
                )
            
            return valid_files
            
        except Exception as e:
            messagebox.showerror("错误", f"批量导入图片失败: {e}")
            return []
    
    def import_folder(self, parent_window=None) -> List[str]:
        """导入整个文件夹"""
        try:
            folder_path = filedialog.askdirectory(
                parent=parent_window,
                title="选择图片文件夹"
            )
            
            if not folder_path:
                return []
            
            image_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.validate_image_file(file_path):
                        image_files.append(file_path)
            
            if not image_files:
                messagebox.showinfo("提示", "所选文件夹中没有找到支持的图片文件")
            
            return image_files
            
        except Exception as e:
            messagebox.showerror("错误", f"导入文件夹失败: {e}")
            return []
    
    def validate_image_file(self, file_path: str) -> bool:
        """验证图片文件"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False
            
            # 检查文件扩展名
            if not Config.validate_image_format(file_path):
                return False
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return False
            
            # 尝试打开图片验证格式
            with Image.open(file_path) as img:
                img.verify()
            
            return True
            
        except Exception:
            return False
    
    def get_image_info(self, file_path: str) -> Optional[dict]:
        """获取图片信息"""
        try:
            with Image.open(file_path) as img:
                return {
                    'path': file_path,
                    'filename': os.path.basename(file_path),
                    'size': img.size,
                    'mode': img.mode,
                    'format': img.format,
                    'file_size': os.path.getsize(file_path)
                }
        except Exception as e:
            print(f"获取图片信息失败: {e}")
            return None
    
    def create_thumbnail(self, file_path: str, size: Tuple[int, int] = None) -> Optional[Image.Image]:
        """创建缩略图"""
        try:
            if size is None:
                size = Config.THUMBNAIL_SIZE
            
            with Image.open(file_path) as img:
                # 保持宽高比
                # 兼容不同PIL版本
                try:
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                except AttributeError:
                    # 较老版本的PIL使用LANCZOS
                    img.thumbnail(size, Image.LANCZOS)
                return img.copy()
        except Exception as e:
            print(f"Create thumbnail failed: {e}")
            return None

class ExportManager:
    """导出管理器"""
    
    def __init__(self):
        """初始化导出管理器"""
        self.output_folder = ""
        self.export_settings = {
            'format': 'jpg',
            'quality': 95,
            'filename_prefix': 'wm_',
            'filename_suffix': ''
        }
    
    def set_output_folder(self, parent_window=None) -> bool:
        """设置输出文件夹"""
        try:
            folder = filedialog.askdirectory(
                parent=parent_window,
                title="选择输出文件夹"
            )
            
            if folder:
                self.output_folder = folder
                return True
            return False
            
        except Exception as e:
            messagebox.showerror("错误", f"设置输出文件夹失败: {e}")
            return False
    
    def generate_filename(self, original_path: str, prefix: str = "", suffix: str = "") -> str:
        """生成输出文件名"""
        try:
            base_name = os.path.splitext(os.path.basename(original_path))[0]
            extension = f".{self.export_settings['format']}"
            
            # 使用配置中的前缀和后缀，如果没有提供参数的话
            if not prefix:
                prefix = self.export_settings.get('filename_prefix', '')
            if not suffix:
                suffix = self.export_settings.get('filename_suffix', '')
            
            filename = f"{prefix}{base_name}{suffix}{extension}"
            
            # 确保文件名安全
            filename = self._sanitize_filename(filename)
            
            # 处理文件冲突
            output_path = os.path.join(self.output_folder, filename)
            output_path = self._handle_file_conflict(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"生成文件名失败: {e}")
            return original_path
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除非法字符"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def _handle_file_conflict(self, file_path: str) -> str:
        """处理文件冲突，如果文件已存在则添加数字后缀"""
        original_path = file_path
        
        if not os.path.exists(file_path):
            return file_path
        
        # 分离路径、文件名和扩展名
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        
        # 生成新的文件名，添加数字后缀
        counter = 1
        while True:
            new_filename = f"{name}_{counter}{ext}"
            new_path = os.path.join(directory, new_filename)
            
            if not os.path.exists(new_path):
                return new_path
            
            counter += 1
            
            # 防止无限循环
            if counter > 9999:
                import time
                timestamp = int(time.time())
                new_filename = f"{name}_{timestamp}{ext}"
                return os.path.join(directory, new_filename)
    
    def export_single_image(self, image_path: str, watermarked_image: Image.Image) -> bool:
        """导出单张图片"""
        try:
            if not self.output_folder:
                messagebox.showerror("错误", "请先设置输出文件夹")
                return False
            
            # 生成输出文件名
            output_path = self.generate_filename(
                image_path,
                self.export_settings['filename_prefix'],
                self.export_settings['filename_suffix']
            )
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存图片
            if self.export_settings['format'].lower() == 'jpg':
                # JPEG格式需要转换为RGB模式
                if watermarked_image.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', watermarked_image.size, (255, 255, 255))
                    if watermarked_image.mode == 'P':
                        watermarked_image = watermarked_image.convert('RGBA')
                    background.paste(watermarked_image, mask=watermarked_image.split()[-1] if watermarked_image.mode == 'RGBA' else None)
                    watermarked_image = background
                elif watermarked_image.mode != 'RGB':
                    watermarked_image = watermarked_image.convert('RGB')
                
                watermarked_image.save(
                    output_path,
                    'JPEG',
                    quality=self.export_settings['quality'],
                    optimize=True
                )
            else:
                # PNG格式
                watermarked_image.save(output_path, 'PNG', optimize=True)
            
            return True
            
        except Exception as e:
            messagebox.showerror("错误", f"导出图片失败: {e}")
            return False
    
    def export_batch(self, image_data: List[Tuple[str, Image.Image]], progress_callback=None) -> Tuple[int, int]:
        """批量导出图片"""
        try:
            if not self.output_folder:
                messagebox.showerror("错误", "请先设置输出文件夹")
                return 0, 0
            
            success_count = 0
            total_count = len(image_data)
            
            for i, (image_path, watermarked_image) in enumerate(image_data):
                try:
                    if self.export_single_image(image_path, watermarked_image):
                        success_count += 1
                    
                    # 更新进度
                    if progress_callback:
                        progress_callback(i + 1, total_count)
                        
                except Exception as e:
                    print(f"导出图片失败 {image_path}: {e}")
                    continue
            
            return success_count, total_count
            
        except Exception as e:
            messagebox.showerror("错误", f"批量导出失败: {e}")
            return 0, 0
    
    def update_export_settings(self, settings: dict):
        """更新导出设置"""
        self.export_settings.update(settings)
    
    def get_export_settings(self) -> dict:
        """获取导出设置"""
        return self.export_settings.copy()
