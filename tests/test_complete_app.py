# -*- coding: utf-8 -*-
"""
完整应用程序测试脚本
"""

import sys
import os
import tempfile
import time
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
            img = Image.new('RGB', (300, 200), color)
            img.save(img_path, 'JPEG')
            test_images.append(img_path)
    
    return test_images

def test_app_initialization():
    """测试应用程序初始化"""
    print("Testing app initialization...")
    try:
        from main import WatermarkApp
        
        # 创建应用实例
        app = WatermarkApp()
        assert app.root is not None, "Main window creation failed"
        assert app.config is not None, "Config loading failed"
        assert hasattr(app, 'main_window'), "Main window component missing"
        
        # 测试状态更新
        app.update_status("Test status")
        
        # 关闭应用
        app.root.destroy()
        
        print("[OK] App initialization test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] App initialization test failed: {e}")
        return False

def test_main_window_components():
    """测试主窗口组件"""
    print("Testing main window components...")
    try:
        from main import WatermarkApp
        
        app = WatermarkApp()
        main_window = app.main_window
        
        # 测试组件存在性
        assert main_window.main_frame is not None, "Main frame missing"
        assert main_window.image_list_widget is not None, "Image list widget missing"
        assert main_window.preview_widget is not None, "Preview widget missing"
        assert main_window.status_bar is not None, "Status bar missing"
        
        # 测试管理器实例
        assert main_window.file_manager is not None, "File manager missing"
        assert main_window.export_manager is not None, "Export manager missing"
        assert main_window.image_list_manager is not None, "Image list manager missing"
        assert main_window.current_watermark is not None, "Watermark instance missing"
        
        # 测试基本功能
        main_window.update_status("Test message")
        
        app.root.destroy()
        
        print("[OK] Main window components test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Main window components test failed: {e}")
        return False

def test_image_import_workflow():
    """测试图片导入工作流"""
    print("Testing image import workflow...")
    try:
        from main import WatermarkApp
        from file_manager import ImageFileManager
        
        app = WatermarkApp()
        main_window = app.main_window
        
        # 创建测试图片
        test_images = create_test_images()
        
        # 模拟导入图片
        for img_path in test_images:
            success = main_window.image_list_manager.add_image(img_path)
            assert success, f"Failed to add image: {img_path}"
        
        # 验证图片列表
        image_count = main_window.image_list_manager.get_image_count()
        assert image_count == len(test_images), f"Image count mismatch: {image_count} != {len(test_images)}"
        
        # 测试当前图片选择
        current_image = main_window.image_list_manager.get_current_image()
        assert current_image is not None, "No current image selected"
        
        # 测试图片导航
        next_image = main_window.image_list_manager.get_next_image()
        assert next_image is not None, "Next image navigation failed"
        
        prev_image = main_window.image_list_manager.get_previous_image()
        assert prev_image is not None, "Previous image navigation failed"
        
        app.root.destroy()
        
        print("[OK] Image import workflow test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Image import workflow test failed: {e}")
        return False

def test_watermark_application():
    """测试水印应用"""
    print("Testing watermark application...")
    try:
        from main import WatermarkApp
        from text_watermark import TextWatermark
        
        app = WatermarkApp()
        main_window = app.main_window
        
        # 创建测试图片
        test_images = create_test_images()
        main_window.image_list_manager.add_image(test_images[0])
        
        # 设置水印
        watermark = TextWatermark()
        watermark.set_text("Test Watermark")
        watermark.set_font_size(24)
        watermark.set_color("#FFFFFF")
        watermark.set_transparency(80)
        watermark.set_position("bottom_right")
        
        main_window.current_watermark = watermark
        
        # 加载图片
        current_image = main_window.image_list_manager.get_current_image()
        image = main_window.image_list_manager.load_image(current_image['path'])
        assert image is not None, "Failed to load test image"
        
        # 应用水印
        watermarked_image = watermark.apply_to_image(image)
        assert watermarked_image is not None, "Failed to apply watermark"
        assert watermarked_image.size == image.size, "Watermarked image size changed"
        
        app.root.destroy()
        
        print("[OK] Watermark application test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Watermark application test failed: {e}")
        return False

def test_export_functionality():
    """测试导出功能"""
    print("Testing export functionality...")
    try:
        from main import WatermarkApp
        from text_watermark import TextWatermark
        
        app = WatermarkApp()
        main_window = app.main_window
        
        # 创建测试图片
        test_images = create_test_images()
        main_window.image_list_manager.add_image(test_images[0])
        
        # 设置水印
        watermark = TextWatermark()
        watermark.set_text("Export Test")
        main_window.current_watermark = watermark
        
        # 设置导出参数
        with tempfile.TemporaryDirectory() as temp_dir:
            main_window.export_manager.output_folder = temp_dir
            main_window.export_manager.update_export_settings({
                'format': 'jpg',
                'quality': 95
            })
            
            # 测试单张图片导出
            current_image = main_window.image_list_manager.get_current_image()
            image = main_window.image_list_manager.load_image(current_image['path'])
            watermarked_image = watermark.apply_to_image(image)
            
            success = main_window.export_manager.export_single_image(
                current_image['path'], watermarked_image
            )
            assert success, "Single image export failed"
            
            # 验证导出文件
            exported_files = os.listdir(temp_dir)
            assert len(exported_files) == 1, "Export file count mismatch"
            assert exported_files[0].startswith("wm_"), "Export filename format wrong"
        
        app.root.destroy()
        
        print("[OK] Export functionality test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Export functionality test failed: {e}")
        return False

def test_ui_interaction():
    """测试UI交互"""
    print("Testing UI interaction...")
    try:
        from main import WatermarkApp
        
        app = WatermarkApp()
        main_window = app.main_window
        
        # 测试状态更新
        main_window.update_status("UI Test")
        
        # 测试进度条
        main_window.show_progress(True)
        main_window.update_progress(50.0)
        main_window.show_progress(False)
        
        # 测试水印设置更新
        main_window.current_watermark.set_text("UI Test Watermark")
        main_window.current_watermark.set_font_size(20)
        main_window.current_watermark.set_color("#FF0000")
        
        # 验证设置
        assert main_window.current_watermark.text == "UI Test Watermark", "Watermark text not updated"
        assert main_window.current_watermark.font_size == 20, "Font size not updated"
        assert main_window.current_watermark.color == "#FF0000", "Color not updated"
        
        app.root.destroy()
        
        print("[OK] UI interaction test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] UI interaction test failed: {e}")
        return False

def test_error_handling():
    """测试错误处理"""
    print("Testing error handling...")
    try:
        from main import WatermarkApp
        
        app = WatermarkApp()
        main_window = app.main_window
        
        # 测试无效图片路径
        invalid_path = "/nonexistent/path/image.jpg"
        success = main_window.image_list_manager.add_image(invalid_path)
        assert not success, "Should fail to add invalid image path"
        
        # 测试空图片列表操作
        main_window.image_list_manager.clear_list()
        current_image = main_window.image_list_manager.get_current_image()
        assert current_image is None, "Current image should be None after clear"
        
        # 测试无效水印设置
        main_window.current_watermark.set_font_size(-10)  # 无效值
        assert main_window.current_watermark.font_size == 8, "Font size should be clamped to minimum"
        
        main_window.current_watermark.set_transparency(150)  # 无效值
        assert main_window.current_watermark.transparency == 100, "Transparency should be clamped to maximum"
        
        app.root.destroy()
        
        print("[OK] Error handling test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Error handling test failed: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("Complete Application Test")
    print("=" * 60)
    
    tests = [
        test_app_initialization,
        test_main_window_components,
        test_image_import_workflow,
        test_watermark_application,
        test_export_functionality,
        test_ui_interaction,
        test_error_handling
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
        print("All complete application tests passed!")
        return True
    else:
        print("Some tests failed, please check the code")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
