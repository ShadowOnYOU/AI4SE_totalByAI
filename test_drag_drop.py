# -*- coding: utf-8 -*-
"""
拖拽上传功能测试脚本
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
        # 创建不同颜色的测试图片
        colors = ['red', 'green', 'blue', 'yellow', 'purple']
        for i, color in enumerate(colors):
            img_path = os.path.join(temp_dir, f"test_{i+1}_{color}.jpg")
            img = Image.new('RGB', (100, 100), color)
            img.save(img_path, 'JPEG')
            test_images.append(img_path)
    
    return test_images

def test_drag_drop_module():
    """测试拖拽模块导入"""
    print("Testing drag drop module import...")
    try:
        from drag_drop import DragDropHandler, FileDropHandler, AdvancedDragDrop, DragDropManager
        print("[OK] Drag drop module imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Drag drop module import failed: {e}")
        return False

def test_drag_drop_creation():
    """测试拖拽处理器创建"""
    print("Testing drag drop handler creation...")
    try:
        import tkinter as tk
        from drag_drop import AdvancedDragDrop
        
        # 创建测试窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 创建Canvas控件
        canvas = tk.Canvas(root, width=400, height=300, bg='lightgray')
        canvas.pack()
        
        # 创建拖拽处理器
        def test_callback(files):
            print(f"Files dropped: {files}")
        
        handler = AdvancedDragDrop(canvas, test_callback)
        
        # 验证处理器创建成功
        assert handler is not None, "Drag drop handler creation failed"
        assert handler.target_widget == canvas, "Target widget not set correctly"
        assert handler.callback == test_callback, "Callback not set correctly"
        
        root.destroy()
        print("[OK] Drag drop handler creation test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Drag drop handler creation test failed: {e}")
        return False

def test_drag_drop_manager():
    """测试拖拽管理器"""
    print("Testing drag drop manager...")
    try:
        import tkinter as tk
        from drag_drop import DragDropManager
        
        # 创建测试窗口
        root = tk.Tk()
        root.withdraw()
        
        # 创建模拟主窗口
        class MockMainWindow:
            pass
        
        main_window = MockMainWindow()
        manager = DragDropManager(main_window)
        
        # 创建测试控件
        canvas = tk.Canvas(root, width=400, height=300)
        
        def test_callback(files):
            print(f"Manager callback: {files}")
        
        # 添加拖拽目标
        handler = manager.add_drop_target(canvas, "test_target", test_callback)
        assert handler is not None, "Add drop target failed"
        assert "test_target" in manager.drop_handlers, "Drop target not registered"
        
        # 测试移除拖拽目标
        manager.remove_drop_target("test_target")
        assert "test_target" not in manager.drop_handlers, "Remove drop target failed"
        
        root.destroy()
        print("[OK] Drag drop manager test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Drag drop manager test failed: {e}")
        return False

def test_file_validation():
    """测试文件验证功能"""
    print("Testing file validation...")
    try:
        from drag_drop import AdvancedDragDrop
        from file_manager import ImageFileManager
        
        # 创建测试文件
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建有效图片
            valid_image = os.path.join(temp_dir, "valid.jpg")
            img = Image.new('RGB', (100, 100), 'red')
            img.save(valid_image, 'JPEG')
            
            # 创建无效文件
            invalid_file = os.path.join(temp_dir, "invalid.txt")
            with open(invalid_file, 'w') as f:
                f.write("not an image")
            
            file_manager = ImageFileManager()
            
            # 测试文件验证
            assert file_manager.validate_image_file(valid_image), "Valid image should pass validation"
            assert not file_manager.validate_image_file(invalid_file), "Invalid file should fail validation"
            
            # 测试文件处理
            handler = AdvancedDragDrop(None, None)
            handler.file_manager = file_manager
            
            # 模拟处理文件
            test_files = [valid_image, invalid_file]
            valid_files = []
            invalid_files = []
            
            for file_path in test_files:
                if file_manager.validate_image_file(file_path):
                    valid_files.append(file_path)
                else:
                    invalid_files.append(os.path.basename(file_path))
            
            assert len(valid_files) == 1, "Should have 1 valid file"
            assert len(invalid_files) == 1, "Should have 1 invalid file"
            assert valid_files[0] == valid_image, "Valid file should be the image"
            assert invalid_files[0] == "invalid.txt", "Invalid file should be the text file"
        
        print("[OK] File validation test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] File validation test failed: {e}")
        return False

def test_main_window_integration():
    """测试主窗口集成"""
    print("Testing main window integration...")
    try:
        from main import WatermarkApp
        
        # 创建应用实例
        app = WatermarkApp()
        
        # 验证拖拽管理器存在
        assert hasattr(app.main_window, 'drag_drop_manager'), "Drag drop manager not found"
        assert hasattr(app.main_window, 'setup_drag_drop'), "Setup drag drop method not found"
        assert hasattr(app.main_window, 'on_files_dropped'), "Files dropped handler not found"
        
        # 验证拖拽目标已设置
        drop_handlers = app.main_window.drag_drop_manager.drop_handlers
        assert "preview_area" in drop_handlers, "Preview area drop target not set"
        assert "image_list_area" in drop_handlers, "Image list area drop target not set"
        
        app.root.destroy()
        print("[OK] Main window integration test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Main window integration test failed: {e}")
        return False

def test_drag_drop_workflow():
    """测试拖拽工作流"""
    print("Testing drag drop workflow...")
    try:
        from main import WatermarkApp
        
        app = WatermarkApp()
        main_window = app.main_window
        
        # 创建测试图片
        test_images = create_test_images()
        
        # 模拟拖拽文件处理
        main_window.on_files_dropped(test_images)
        
        # 验证图片已添加到列表
        image_count = main_window.image_list_manager.get_image_count()
        assert image_count == len(test_images), f"Expected {len(test_images)} images, got {image_count}"
        
        # 验证图片列表显示已更新
        # 这里可以添加更多验证逻辑
        
        app.root.destroy()
        print("[OK] Drag drop workflow test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Drag drop workflow test failed: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("Drag Drop Functionality Test")
    print("=" * 60)
    
    tests = [
        test_drag_drop_module,
        test_drag_drop_creation,
        test_drag_drop_manager,
        test_file_validation,
        test_main_window_integration,
        test_drag_drop_workflow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # 空行分隔
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} passed")
    print("=" * 60)
    
    if passed == total:
        print("All drag drop tests passed!")
        return True
    else:
        print("Some tests failed, please check the code")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

