# -*- coding: utf-8 -*-
"""
最终测试脚本 - 验证核心功能
"""

import sys
import os
import tempfile
from PIL import Image

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_core_modules():
    """测试核心模块导入"""
    print("Testing core module imports...")
    try:
        from config import Config
        from file_manager import ImageFileManager, ExportManager
        from image_list import ImageListManager
        from text_watermark import TextWatermark
        from main_window import MainWindow
        from main import WatermarkApp
        
        print("[OK] All core modules imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Module import failed: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("Testing basic functionality...")
    try:
        # 测试配置
        from config import Config
        config = Config.load_config()
        assert isinstance(config, dict), "Config should be a dictionary"
        
        # 测试文件管理器
        from file_manager import ImageFileManager
        file_manager = ImageFileManager()
        
        # 创建测试图片
        with tempfile.TemporaryDirectory() as temp_dir:
            test_image = os.path.join(temp_dir, "test.jpg")
            img = Image.new('RGB', (100, 100), 'red')
            img.save(test_image, 'JPEG')
            
            # 验证图片
            assert file_manager.validate_image_file(test_image), "Image validation failed"
            
            # 获取图片信息
            info = file_manager.get_image_info(test_image)
            assert info is not None, "Image info retrieval failed"
            assert info['format'] == 'JPEG', "Image format detection failed"
        
        # 测试图片列表管理器
        from image_list import ImageListManager
        list_manager = ImageListManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_image = os.path.join(temp_dir, "test.jpg")
            img = Image.new('RGB', (100, 100), 'blue')
            img.save(test_image, 'JPEG')
            
            # 添加图片到列表
            success = list_manager.add_image(test_image)
            assert success, "Add image to list failed"
            assert list_manager.get_image_count() == 1, "Image count wrong"
            
            # 获取当前图片
            current = list_manager.get_current_image()
            assert current is not None, "Current image should not be None"
        
        # 测试文本水印
        from text_watermark import TextWatermark
        watermark = TextWatermark()
        watermark.set_text("Test")
        watermark.set_font_size(20)
        watermark.set_color("#FFFFFF")
        
        # 创建水印图片
        watermark_img = watermark.create_watermark_image((200, 100))
        assert watermark_img is not None, "Watermark creation failed"
        assert watermark_img.size == (200, 100), "Watermark size wrong"
        
        print("[OK] Basic functionality tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Basic functionality test failed: {e}")
        return False

def test_app_creation():
    """测试应用程序创建"""
    print("Testing app creation...")
    try:
        from main import WatermarkApp
        
        # 创建应用实例
        app = WatermarkApp()
        assert app.root is not None, "Main window not created"
        assert app.config is not None, "Config not loaded"
        assert hasattr(app, 'main_window'), "Main window component missing"
        
        # 测试状态更新
        app.update_status("Test message")
        
        # 关闭应用
        app.root.destroy()
        
        print("[OK] App creation test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] App creation test failed: {e}")
        return False

def test_watermark_workflow():
    """测试水印工作流"""
    print("Testing watermark workflow...")
    try:
        from text_watermark import TextWatermark
        from file_manager import ImageFileManager
        from image_list import ImageListManager
        
        # 创建测试图片
        with tempfile.TemporaryDirectory() as temp_dir:
            test_image = os.path.join(temp_dir, "test.jpg")
            img = Image.new('RGB', (300, 200), 'lightblue')
            img.save(test_image, 'JPEG')
            
            # 创建水印
            watermark = TextWatermark()
            watermark.set_text("Workflow Test")
            watermark.set_font_size(24)
            watermark.set_color("#FF0000")
            watermark.set_transparency(80)
            watermark.set_position("center")
            
            # 应用水印
            watermarked_img = watermark.apply_to_image(img)
            assert watermarked_img is not None, "Watermark application failed"
            assert watermarked_img.size == img.size, "Size should not change"
            
            # 测试导出
            from file_manager import ExportManager
            export_manager = ExportManager()
            export_manager.output_folder = temp_dir
            export_manager.update_export_settings({'format': 'jpg', 'quality': 95})
            
            success = export_manager.export_single_image(test_image, watermarked_img)
            assert success, "Export failed"
            
            # 验证导出文件
            exported_files = [f for f in os.listdir(temp_dir) if f.startswith('wm_')]
            assert len(exported_files) == 1, "Export file not created"
        
        print("[OK] Watermark workflow test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Watermark workflow test failed: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("Final Application Test")
    print("=" * 60)
    
    tests = [
        test_core_modules,
        test_basic_functionality,
        test_app_creation,
        test_watermark_workflow
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
        print("All tests passed! Application is ready for use.")
        return True
    else:
        print("Some tests failed, please check the code")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
