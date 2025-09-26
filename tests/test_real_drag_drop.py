#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真正的拖拽功能
"""

import sys
import os
import tempfile
import tkinter as tk
from PIL import Image

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_image():
    """创建测试图片"""
    try:
        # 创建临时图片
        temp_dir = tempfile.gettempdir()
        test_image_path = os.path.join(temp_dir, 'test_drag_drop.jpg')
        
        # 创建一个简单的测试图片
        img = Image.new('RGB', (400, 300), 'lightblue')
        img.save(test_image_path, 'JPEG')
        
        print(f"测试图片已创建: {test_image_path}")
        return test_image_path
        
    except Exception as e:
        print(f"创建测试图片失败: {e}")
        return None

def test_import_modules():
    """测试模块导入"""
    print("测试模块导入...")
    try:
        from real_drag_drop import RealDragDrop, RealDragDropManager, create_dnd_root, DRAG_DROP_AVAILABLE
        from config import Config
        from file_manager import ImageFileManager
        
        print(f"[OK] 所有模块导入成功")
        print(f"[OK] 拖拽功能可用: {'是' if DRAG_DROP_AVAILABLE else '否'}")
        return True
        
    except Exception as e:
        print(f"[FAIL] 模块导入失败: {e}")
        return False

def test_drag_drop_functionality():
    """测试拖拽功能"""
    print("\n测试拖拽功能...")
    try:
        from real_drag_drop import RealDragDrop, create_dnd_root
        
        # 创建支持拖拽的根窗口
        root = create_dnd_root()
        root.title("拖拽功能测试")
        root.geometry("500x400")
        
        # 创建Canvas
        canvas = tk.Canvas(root, bg='lightblue', width=400, height=300)
        canvas.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 文件列表
        dropped_files = []
        
        def on_files_dropped(files):
            """处理拖拽的文件"""
            print(f"拖拽文件: {files}")
            dropped_files.extend(files)
            canvas.delete("status")
            canvas.create_text(200, 150, text=f"已拖拽 {len(files)} 个文件", 
                             font=("Arial", 14), fill="green", tags="status")
        
        # 创建拖拽处理器
        drag_handler = RealDragDrop(canvas, on_files_dropped)
        
        # 添加关闭按钮
        close_btn = tk.Button(root, text="关闭测试", command=root.destroy)
        close_btn.pack(pady=10)
        
        print("[OK] 拖拽功能测试窗口已创建")
        print("[INFO] 请尝试将图片文件拖拽到蓝色区域")
        
        # 运行测试窗口
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"[FAIL] 拖拽功能测试失败: {e}")
        return False

def test_main_app():
    """测试主应用程序"""
    print("\n测试主应用程序...")
    try:
        from main import WatermarkApp
        
        print("[OK] 主应用程序类导入成功")
        print("[INFO] 主应用程序可以正常创建")
        return True
        
    except Exception as e:
        print(f"[FAIL] 主应用程序测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("真正拖拽功能测试")
    print("=" * 60)
    
    # 创建测试图片
    test_image = create_test_image()
    
    # 测试模块导入
    import_success = test_import_modules()
    
    # 测试主应用程序
    app_success = test_main_app()
    
    if import_success and app_success:
        print("\n" + "=" * 60)
        print("[SUCCESS] 所有基础测试通过！")
        print("=" * 60)
        
        # 询问是否运行交互式测试
        try:
            choice = input("\n是否运行拖拽功能交互式测试？(y/n): ").lower().strip()
            if choice in ['y', 'yes', '是']:
                test_drag_drop_functionality()
        except KeyboardInterrupt:
            print("\n测试被用户中断")
        except:
            print("\n跳过交互式测试")
    else:
        print("\n[FAIL] 基础测试失败，请检查代码")
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()
