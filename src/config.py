# -*- coding: utf-8 -*-
"""
配置管理模块
管理应用配置和常量
"""

import os
import json
from typing import Dict, List, Any

class Config:
    """应用配置类"""
    
    # 支持的图片格式
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    
    # 输出格式
    OUTPUT_FORMATS = ['.jpg', '.png']
    
    # 默认水印参数
    DEFAULT_WATERMARK = {
        'text': 'Watermark',
        'font_size': 24,
        'color': '#FFFFFF',
        'transparency': 80,
        'position': 'bottom_right',
        'font_family': 'Arial'
    }
    
    # 文件路径常量
    TEMPLATES_DIR = 'templates'
    CONFIG_FILE = 'config.json'
    LOG_FILE = 'watermark_tool.log'
    
    # 窗口设置
    WINDOW_TITLE = 'Image Watermark Tool'
    WINDOW_SIZE = '1200x800'
    MIN_WINDOW_SIZE = (800, 600)
    
    # 图片处理设置
    MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB
    THUMBNAIL_SIZE = (150, 150)
    PREVIEW_MAX_SIZE = (600, 400)
    
    # 性能设置
    MAX_MEMORY_USAGE = 500 * 1024 * 1024  # 500MB
    BATCH_SIZE = 10
    
    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return cls.get_default_config()
        return cls.get_default_config()
    
    @classmethod
    def save_config(cls, config: Dict[str, Any]) -> bool:
        """保存配置文件"""
        try:
            with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'watermark': cls.DEFAULT_WATERMARK.copy(),
            'output_folder': '',
            'last_import_folder': '',
            'window_geometry': cls.WINDOW_SIZE,
            'recent_templates': [],
            'export_settings': {
                'format': 'jpg',
                'quality': 95,
                'filename_prefix': 'wm_',
                'filename_suffix': ''
            }
        }
    
    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        if not os.path.exists(cls.TEMPLATES_DIR):
            os.makedirs(cls.TEMPLATES_DIR)
    
    @classmethod
    def validate_image_format(cls, filename: str) -> bool:
        """验证图片格式是否支持"""
        if not filename:
            return False
        ext = os.path.splitext(filename.lower())[1]
        return ext in cls.SUPPORTED_FORMATS
