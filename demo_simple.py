#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的拖拽功能演示
"""

import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_demo():
    """创建演示程序"""
    root = tk.Tk()
    root.title("图片水印工具 - 拖拽功能演示")
    root.geometry("800x600")
    
    # 创建主框架
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 创建左侧面板（模拟图片列表）
    left_frame = tk.LabelFrame(main_frame, text="图片列表", width=200)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
    left_frame.pack_propagate(False)
    
    # 创建图片列表
    listbox = tk.Listbox(left_frame)
    listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # 创建中间面板（预览区域）
    preview_frame = tk.LabelFrame(main_frame, text="预览区域")
    preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    # 创建预览Canvas
    canvas = tk.Canvas(preview_frame, bg='lightblue', width=400, height=300)
    canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # 添加提示文本
    canvas.create_text(200, 120, text="点击选择图片文件", 
                      font=("Arial", 14), fill="gray", justify=tk.CENTER)
    canvas.create_text(200, 150, text="或拖拽图片到此处", 
                      font=("Arial", 12), fill="lightgray", justify=tk.CENTER)
    
    # 创建右侧面板（控制面板）
    control_frame = tk.LabelFrame(main_frame, text="控制面板", width=200)
    control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
    control_frame.pack_propagate(False)
    
    # 添加控制按钮
    tk.Button(control_frame, text="导入图片", command=lambda: select_files(listbox, canvas)).pack(pady=5)
    tk.Button(control_frame, text="清空列表", command=lambda: clear_list(listbox, canvas)).pack(pady=5)
    tk.Button(control_frame, text="退出", command=root.quit).pack(pady=5)
    
    # 拖拽功能
    setup_drag_drop(canvas, listbox)
    setup_drag_drop(listbox, listbox)
    
    # 状态栏
    status_frame = tk.Frame(root)
    status_frame.pack(side=tk.BOTTOM, fill=tk.X)
    status_label = tk.Label(status_frame, text="就绪 - 点击或拖拽选择图片文件", 
                           relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(fill=tk.X)
    
    return root, listbox, canvas, status_label

def setup_drag_drop(widget, listbox):
    """设置拖拽功能"""
    def on_click(event):
        select_files(listbox, None)
    
    def on_drag_motion(event):
        if not hasattr(widget, '_drag_start'):
            widget._drag_start = (event.x, event.y)
            widget._is_dragging = False
            return
        
        dx = abs(event.x - widget._drag_start[0])
        dy = abs(event.y - widget._drag_start[1])
        
        if dx > 10 or dy > 10:
            widget._is_dragging = True
            try:
                widget.configure(bg='lightgreen')
            except:
                pass
    
    def on_drag_release(event):
        if hasattr(widget, '_is_dragging') and widget._is_dragging:
            select_files(listbox, None)
            try:
                widget.configure(bg='lightblue')
            except:
                pass
        widget._is_dragging = False
    
    # 绑定事件
    widget.bind('<Button-1>', on_click)
    widget.bind('<B1-Motion>', on_drag_motion)
    widget.bind('<ButtonRelease-1>', on_drag_release)

def select_files(listbox, canvas):
    """选择文件"""
    files = filedialog.askopenfilenames(
        title="选择图片文件",
        filetypes=[
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("所有文件", "*.*")
        ]
    )
    
    if files:
        # 添加到列表
        for file_path in files:
            filename = os.path.basename(file_path)
            listbox.insert(tk.END, filename)
        
        # 更新Canvas
        if canvas:
            canvas.delete("all")
            canvas.create_text(200, 120, text=f"已选择 {len(files)} 个文件", 
                              font=("Arial", 14), fill="green", justify=tk.CENTER)
            if len(files) == 1:
                filename = os.path.basename(files[0])
                canvas.create_text(200, 150, text=filename, 
                                  font=("Arial", 12), fill="darkgreen", justify=tk.CENTER)

def clear_list(listbox, canvas):
    """清空列表"""
    listbox.delete(0, tk.END)
    if canvas:
        canvas.delete("all")
        canvas.create_text(200, 120, text="点击选择图片文件", 
                          font=("Arial", 14), fill="gray", justify=tk.CENTER)
        canvas.create_text(200, 150, text="或拖拽图片到此处", 
                          font=("Arial", 12), fill="lightgray", justify=tk.CENTER)

def main():
    """主函数"""
    print("=" * 60)
    print("图片水印工具 - 拖拽功能演示")
    print("=" * 60)
    print()
    print("功能说明：")
    print("1. 点击蓝色预览区域选择图片文件")
    print("2. 在预览区域上拖拽鼠标也会触发文件选择")
    print("3. 点击左侧列表区域也可以选择文件")
    print("4. 使用右侧按钮进行其他操作")
    print()
    print("请尝试以下操作：")
    print("- 点击预览区域选择文件")
    print("- 在预览区域上拖拽鼠标")
    print("- 点击'导入图片'按钮")
    print()
    
    root, listbox, canvas, status_label = create_demo()
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n演示结束")
    finally:
        root.destroy()

if __name__ == "__main__":
    main()

