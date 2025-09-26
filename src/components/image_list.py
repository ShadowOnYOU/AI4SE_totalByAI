# -*- coding: utf-8 -*-
"""
图片列表管理模块
管理已导入图片的列表和缩略图
"""

import os
from typing import List, Dict, Optional, Callable
from PIL import Image
import threading
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import Config

class ImageListManager:
    """图片列表管理器"""
    
    def __init__(self):
        """初始化图片列表管理器"""
        self.image_list: List[Dict] = []
        self.thumbnail_cache: Dict[str, Image.Image] = {}
        self.current_index = 0
        self.callbacks: List[Callable] = []
    
    def add_image(self, file_path: str) -> bool:
        """添加图片到列表"""
        try:
            # 检查是否已存在
            if self._find_image_by_path(file_path) is not None:
                return False
            
            # 获取图片信息
            from components.file_manager import ImageFileManager
            file_manager = ImageFileManager()
            image_info = file_manager.get_image_info(file_path)
            
            if not image_info:
                return False
            
            # 添加到列表
            image_data = {
                'path': file_path,
                'filename': image_info['filename'],
                'size': image_info['size'],
                'mode': image_info['mode'],
                'format': image_info['format'],
                'file_size': image_info['file_size'],
                'thumbnail': None,
                'loaded': False
            }
            
            self.image_list.append(image_data)
            
            # 如果这是第一张图片，设置为当前图片
            if len(self.image_list) == 1:
                self.current_index = 0
            
            # 异步创建缩略图
            self._create_thumbnail_async(image_data)
            
            # 通知回调
            self._notify_callbacks('image_added', image_data)
            
            # 如果这是第一张图片，通知当前图片变化
            if len(self.image_list) == 1:
                self._notify_callbacks('current_changed', self.get_current_image())
            
            return True
            
        except Exception as e:
            print(f"添加图片失败: {e}")
            return False
    
    def remove_image(self, file_path: str) -> bool:
        """从列表移除图片"""
        try:
            index = self._find_image_by_path(file_path)
            if index is not None:
                image_data = self.image_list.pop(index)
                
                # 清理缩略图缓存
                if file_path in self.thumbnail_cache:
                    del self.thumbnail_cache[file_path]
                
                # 调整当前索引
                if self.current_index >= len(self.image_list):
                    self.current_index = max(0, len(self.image_list) - 1)
                
                # 通知回调
                self._notify_callbacks('image_removed', image_data)
                
                return True
            return False
            
        except Exception as e:
            print(f"移除图片失败: {e}")
            return False
    
    def clear_list(self):
        """清空图片列表"""
        try:
            self.image_list.clear()
            self.thumbnail_cache.clear()
            self.current_index = 0
            
            # 通知回调
            self._notify_callbacks('list_cleared', None)
            
        except Exception as e:
            print(f"清空列表失败: {e}")
    
    def get_image_list(self) -> List[Dict]:
        """获取图片列表"""
        return self.image_list.copy()
    
    def get_image_count(self) -> int:
        """获取图片数量"""
        return len(self.image_list)
    
    def get_current_image(self) -> Optional[Dict]:
        """获取当前选中的图片"""
        if 0 <= self.current_index < len(self.image_list):
            return self.image_list[self.current_index]
        return None
    
    def set_current_index(self, index: int) -> bool:
        """设置当前索引"""
        if 0 <= index < len(self.image_list):
            self.current_index = index
            self._notify_callbacks('current_changed', self.get_current_image())
            return True
        return False
    
    def get_next_image(self) -> Optional[Dict]:
        """获取下一张图片"""
        if len(self.image_list) == 0:
            return None
        
        self.current_index = (self.current_index + 1) % len(self.image_list)
        self._notify_callbacks('current_changed', self.get_current_image())
        return self.get_current_image()
    
    def get_previous_image(self) -> Optional[Dict]:
        """获取上一张图片"""
        if len(self.image_list) == 0:
            return None
        
        self.current_index = (self.current_index - 1) % len(self.image_list)
        self._notify_callbacks('current_changed', self.get_current_image())
        return self.get_current_image()
    
    def get_thumbnail(self, file_path: str) -> Optional[Image.Image]:
        """获取缩略图"""
        return self.thumbnail_cache.get(file_path)
    
    def load_image(self, file_path: str) -> Optional[Image.Image]:
        """加载完整图片"""
        try:
            image_index = self._find_image_by_path(file_path)
            if image_index is not None:
                image_data = self.image_list[image_index]
                if not image_data['loaded']:
                    with Image.open(file_path) as img:
                        image_data['loaded'] = True
                        return img.copy()
                else:
                    return Image.open(file_path)
            return None
            
        except Exception as e:
            print(f"Load image failed: {e}")
            return None
    
    def _find_image_by_path(self, file_path: str) -> Optional[int]:
        """根据路径查找图片索引"""
        for i, image_data in enumerate(self.image_list):
            if image_data['path'] == file_path:
                return i
        return None
    
    def _create_thumbnail_async(self, image_data: Dict):
        """异步创建缩略图"""
        def create_thumbnail():
            try:
                file_path = image_data['path']
                if file_path not in self.thumbnail_cache:
                    from components.file_manager import ImageFileManager
                    file_manager = ImageFileManager()
                    thumbnail = file_manager.create_thumbnail(file_path)
                    if thumbnail:
                        self.thumbnail_cache[file_path] = thumbnail
                        image_data['thumbnail'] = thumbnail
                        self._notify_callbacks('thumbnail_created', image_data)
            except Exception as e:
                print(f"Create thumbnail failed: {e}")
        
        # 在新线程中创建缩略图
        thread = threading.Thread(target=create_thumbnail)
        thread.daemon = True
        thread.start()
    
    def add_callback(self, callback: Callable):
        """添加回调函数"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """移除回调函数"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, event: str, data):
        """通知所有回调函数"""
        for callback in self.callbacks:
            try:
                callback(event, data)
            except Exception as e:
                print(f"回调函数执行失败: {e}")
    
    def get_image_by_index(self, index: int) -> Optional[Dict]:
        """根据索引获取图片"""
        if 0 <= index < len(self.image_list):
            return self.image_list[index]
        return None
    
    def get_image_info(self, file_path: str) -> Optional[Dict]:
        """获取图片信息"""
        image_data = self._find_image_by_path(file_path)
        if image_data is not None:
            return self.image_list[image_data]
        return None
    
    def update_image_info(self, file_path: str, info: Dict):
        """更新图片信息"""
        index = self._find_image_by_path(file_path)
        if index is not None:
            self.image_list[index].update(info)
            self._notify_callbacks('image_updated', self.image_list[index])
    
    def get_statistics(self) -> Dict:
        """获取列表统计信息"""
        total_size = sum(img['file_size'] for img in self.image_list)
        formats = {}
        for img in self.image_list:
            fmt = img['format'] or 'Unknown'
            formats[fmt] = formats.get(fmt, 0) + 1
        
        return {
            'count': len(self.image_list),
            'total_size': total_size,
            'formats': formats,
            'current_index': self.current_index
        }
