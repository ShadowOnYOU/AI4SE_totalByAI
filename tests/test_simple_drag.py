# -*- coding: utf-8 -*-
"""
简化的拖拽功能测试
"""

import sys
import os
import tkinter as tk
from tkinter import filedialog

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple_drag():
    """测试简化的拖拽功能"""
    print("Testing simple drag functionality...")
    
    root = tk.Tk()
    root.title("拖拽测试")
    root.geometry("600x400")
    
    # 创建Canvas作为拖拽目标
    canvas = tk.Canvas(root, bg='lightblue', width=400, height=300)
    canvas.pack(pady=20)
    
    # 添加提示文本
    canvas.create_text(200, 150, text="拖拽图片文件到此处\n或点击选择文件", 
                      font=("Arial", 14), fill="gray", justify=tk.CENTER)
    
    def on_click(event):
        """点击事件处理"""
        print("Canvas clicked, opening file dialog...")
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("所有文件", "*.*")
            ]
        )
        if files:
            print(f"Selected files: {files}")
            # 更新提示文本
            canvas.delete("all")
            canvas.create_text(200, 150, text=f"已选择 {len(files)} 个文件\n{os.path.basename(files[0]) if files else ''}", 
                              font=("Arial", 14), fill="green", justify=tk.CENTER)
    
    def on_drag_start(event):
        """拖拽开始"""
        print(f"Drag start at ({event.x}, {event.y})")
        canvas.configure(bg='lightgreen')
    
    def on_drag_motion(event):
        """拖拽移动"""
        print(f"Drag motion to ({event.x}, {event.y})")
    
    def on_drag_end(event):
        """拖拽结束"""
        print(f"Drag end at ({event.x}, {event.y})")
        canvas.configure(bg='lightblue')
        # 模拟文件选择
        on_click(event)
    
    # 绑定事件
    canvas.bind('<Button-1>', on_click)
    canvas.bind('<B1-Motion>', on_drag_motion)
    canvas.bind('<ButtonRelease-1>', on_drag_end)
    
    print("拖拽测试窗口已打开，请尝试：")
    print("1. 点击Canvas区域选择文件")
    print("2. 在Canvas上拖拽鼠标")
    print("3. 关闭窗口结束测试")
    
    root.mainloop()

if __name__ == "__main__":
    test_simple_drag()

