# -*- coding: utf-8 -*-
"""
改进的拖拽功能测试
"""

import sys
import os
import tempfile
from PIL import Image

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_images():
    """创建测试图片"""
    test_images = []
    with tempfile.TemporaryDirectory() as temp_dir:
        colors = ['red', 'green', 'blue', 'yellow', 'purple']
        for i, color in enumerate(colors):
            img_path = os.path.join(temp_dir, f"test_{i+1}_{color}.jpg")
            img = Image.new('RGB', (100, 100), color)
            img.save(img_path, 'JPEG')
            test_images.append(img_path)
            print(f"Created test image: {img_path}")
    return test_images

def test_improved_drag():
    """测试改进的拖拽功能"""
    print("Testing improved drag functionality...")
    
    try:
        from improved_drag_drop import SimpleDragDrop, DragDropManager
        import tkinter as tk
        
        # 创建测试窗口
        root = tk.Tk()
        root.title("改进的拖拽功能测试")
        root.geometry("500x400")
        
        # 创建Canvas
        canvas = tk.Canvas(root, bg='lightblue', width=400, height=300)
        canvas.pack(pady=20)
        
        # 创建拖拽处理器
        def on_files_selected(files):
            print(f"Files selected: {files}")
            # 更新Canvas显示
            canvas.delete("all")
            canvas.create_text(200, 120, text=f"已选择 {len(files)} 个文件", 
                              font=("Arial", 14), fill="green", justify=tk.CENTER)
            if files:
                filename = os.path.basename(files[0])
                canvas.create_text(200, 150, text=filename, 
                                  font=("Arial", 12), fill="darkgreen", justify=tk.CENTER)
        
        handler = SimpleDragDrop(canvas, on_files_selected)
        
        # 添加说明文本
        info_text = tk.Label(root, text="点击蓝色区域或拖拽鼠标来选择图片文件", 
                            font=("Arial", 12), fg="blue")
        info_text.pack(pady=10)
        
        print("测试窗口已打开，请尝试：")
        print("1. 点击蓝色区域选择文件")
        print("2. 在蓝色区域上拖拽鼠标")
        print("3. 关闭窗口结束测试")
        
        root.mainloop()
        
    except Exception as e:
        print(f"Test failed: {e}")

def test_main_app_drag():
    """测试主应用的拖拽功能"""
    print("Testing main app drag functionality...")
    
    try:
        from main import WatermarkApp
        
        app = WatermarkApp()
        
        # 验证拖拽管理器存在
        assert hasattr(app.main_window, 'drag_drop_manager'), "Drag drop manager not found"
        assert hasattr(app.main_window, 'on_files_dropped'), "Files dropped handler not found"
        
        # 验证拖拽目标已设置
        drop_handlers = app.main_window.drag_drop_manager.drop_handlers
        assert "preview_area" in drop_handlers, "Preview area drop target not set"
        assert "image_list_area" in drop_handlers, "Image list area drop target not set"
        
        print("Main app drag functionality test passed")
        app.root.destroy()
        return True
        
    except Exception as e:
        print(f"Main app drag test failed: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("Improved Drag Drop Functionality Test")
    print("=" * 60)
    
    # 测试改进的拖拽功能
    test_improved_drag()
    
    print("\n" + "=" * 60)
    print("Testing main app integration...")
    
    # 测试主应用集成
    success = test_main_app_drag()
    
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed")

if __name__ == "__main__":
    main()

