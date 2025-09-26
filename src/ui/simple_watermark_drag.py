# -*- coding: utf-8 -*-
"""
简化的水印拖拽功能模块
"""

import tkinter as tk
from typing import Tuple, Optional, Callable

class SimpleWatermarkDrag:
    """简化的水印拖拽处理器"""
    
    def __init__(self, canvas, on_position_changed: Optional[Callable] = None):
        """初始化拖拽处理器"""
        self.canvas = canvas
        self.on_position_changed = on_position_changed
        
        # 拖拽状态
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # 水印相关
        self.watermark_rect = None
        self.watermark_text = None
        self.current_position = (0, 0)
        self.watermark_size = (100, 30)
        
        # 状态回调
        self.on_drag_start_callback = None
        self.on_drag_end_callback = None
        
        # 设置事件
        self.setup_events()
    
    def setup_events(self):
        """设置事件"""
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.canvas.bind('<Motion>', self.on_motion)
    
    def show_watermark(self, position: Tuple[int, int], text: str = "水印"):
        """显示水印预览"""
        self.hide_watermark()
        
        x, y = position
        w, h = self.watermark_size
        
        # 创建水印矩形
        self.watermark_rect = self.canvas.create_rectangle(
            x, y, x + w, y + h,
            outline='red',
            width=2,
            fill='',
            tags='watermark_drag'
        )
        
        # 创建水印文本
        self.watermark_text = self.canvas.create_text(
            x + w//2, y + h//2,
            text=text,
            font=("Arial", 12),
            fill='red',
            tags='watermark_drag'
        )
        
        self.current_position = position
        # print(f"Watermark shown at {position}")  # 减少日志输出
    
    def hide_watermark(self):
        """隐藏水印"""
        self.canvas.delete('watermark_drag')
        self.watermark_rect = None
        self.watermark_text = None
    
    def on_click(self, event):
        """点击事件"""
        print(f"Click at ({event.x}, {event.y})")
        
        # 检查是否点击在水印区域
        if self.is_in_watermark(event.x, event.y):
            self.is_dragging = True
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.canvas.configure(cursor='hand2')
            print("Started dragging watermark")
            
            # 通知开始拖拽
            if self.on_drag_start_callback:
                self.on_drag_start_callback()
        else:
            self.is_dragging = False
            print("Not on watermark")
    
    def on_drag(self, event):
        """拖拽事件"""
        if not self.is_dragging:
            return
        
        # print(f"Dragging to ({event.x}, {event.y})")  # 减少日志输出
        
        # 计算移动距离
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        # 移动水印
        self.canvas.move('watermark_drag', dx, dy)
        
        # 更新位置
        self.current_position = (
            self.current_position[0] + dx,
            self.current_position[1] + dy
        )
        
        # 更新起始点
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def on_release(self, event):
        """释放事件"""
        if self.is_dragging:
            print(f"Released at ({event.x}, {event.y})")
            self.is_dragging = False
            self.canvas.configure(cursor='')
            
            # 通知结束拖拽
            if self.on_drag_end_callback:
                self.on_drag_end_callback()
            
            # 通知位置改变
            if self.on_position_changed:
                self.on_position_changed(self.current_position)
    
    def on_motion(self, event):
        """鼠标移动事件"""
        if self.is_in_watermark(event.x, event.y):
            self.canvas.configure(cursor='hand2')
        else:
            self.canvas.configure(cursor='')
    
    def is_in_watermark(self, x: int, y: int) -> bool:
        """检查点是否在水印区域内"""
        if not self.watermark_rect:
            return False
        
        wx, wy = self.current_position
        ww, wh = self.watermark_size
        
        return wx <= x <= wx + ww and wy <= y <= wy + wh
    
    def set_drag_callbacks(self, on_start: Optional[Callable] = None, on_end: Optional[Callable] = None):
        """设置拖拽状态回调"""
        self.on_drag_start_callback = on_start
        self.on_drag_end_callback = on_end
    
    def set_position(self, position: Tuple[int, int]):
        """设置水印位置"""
        self.current_position = position
        if self.watermark_rect:
            x, y = position
            w, h = self.watermark_size
            
            # 更新矩形位置
            self.canvas.coords(self.watermark_rect, x, y, x + w, y + h)
            
            # 更新文本位置
            self.canvas.coords(self.watermark_text, x + w//2, y + h//2)
    
    def get_position(self) -> Tuple[int, int]:
        """获取当前位置"""
        return self.current_position

