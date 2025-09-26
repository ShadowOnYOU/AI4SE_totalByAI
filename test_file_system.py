# -*- coding: utf-8 -*-
"""
文件处理系统测试脚本
"""

import sys
import os
import tempfile
from PIL import Image

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_image(filename: str, size=(100, 100), format='JPEG'):
    """创建测试图片"""
    try:
        # 创建一个简单的测试图片
        img = Image.new('RGB', size, color='red')
        img.save(filename, format)
        return True
    except Exception as e:
        print(f"创建测试图片失败: {e}")
        return False

def test_file_manager():
    """测试文件管理器"""
    print("Testing file manager...")
    try:
        from file_manager import ImageFileManager, ExportManager
        
        # 测试文件管理器
        file_manager = ImageFileManager()
        
        # 创建临时测试图片
        with tempfile.TemporaryDirectory() as temp_dir:
            test_jpg = os.path.join(temp_dir, "test.jpg")
            test_png = os.path.join(temp_dir, "test.png")
            test_txt = os.path.join(temp_dir, "test.txt")
            
            # 创建测试文件
            assert create_test_image(test_jpg), "创建JPG测试文件失败"
            assert create_test_image(test_png, format='PNG'), "创建PNG测试文件失败"
            
            # 创建非图片文件
            with open(test_txt, 'w') as f:
                f.write("test")
            
            # 测试文件验证
            assert file_manager.validate_image_file(test_jpg), "JPG文件验证失败"
            assert file_manager.validate_image_file(test_png), "PNG文件验证失败"
            assert not file_manager.validate_image_file(test_txt), "TXT文件应该验证失败"
            
            # 测试图片信息获取
            jpg_info = file_manager.get_image_info(test_jpg)
            assert jpg_info is not None, "获取JPG图片信息失败"
            assert jpg_info['format'] == 'JPEG', "JPG格式识别失败"
            
            png_info = file_manager.get_image_info(test_png)
            assert png_info is not None, "获取PNG图片信息失败"
            assert png_info['format'] == 'PNG', "PNG格式识别失败"
            
            # 测试缩略图创建
            thumbnail = file_manager.create_thumbnail(test_jpg)
            assert thumbnail is not None, "创建缩略图失败"
            assert thumbnail.size[0] <= 150 and thumbnail.size[1] <= 150, "缩略图尺寸错误"
        
        print("[OK] File manager tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] File manager test failed: {e}")
        return False

def test_export_manager():
    """测试导出管理器"""
    print("Testing export manager...")
    try:
        from file_manager import ExportManager
        
        export_manager = ExportManager()
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 设置输出文件夹
            export_manager.output_folder = temp_dir
            
            # 测试文件名生成
            test_path = "/path/to/test.jpg"
            filename = export_manager.generate_filename(test_path, "wm_", "_test")
            expected = os.path.join(temp_dir, "wm_test_test.jpg")
            assert filename == expected, f"文件名生成错误: {filename} != {expected}"
            
            # 测试文件名清理
            dirty_name = "test<>:\"/\\|?*.jpg"
            clean_name = export_manager._sanitize_filename(dirty_name)
            assert "<" not in clean_name, "文件名清理失败"
            
            # 测试导出设置
            settings = {'format': 'png', 'quality': 80}
            export_manager.update_export_settings(settings)
            current_settings = export_manager.get_export_settings()
            assert current_settings['format'] == 'png', "导出设置更新失败"
            assert current_settings['quality'] == 80, "导出设置更新失败"
        
        print("[OK] Export manager tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Export manager test failed: {e}")
        return False

def test_image_list_manager():
    """测试图片列表管理器"""
    print("Testing image list manager...")
    try:
        from image_list import ImageListManager
        
        list_manager = ImageListManager()
        
        # 创建临时测试图片
        with tempfile.TemporaryDirectory() as temp_dir:
            test_jpg = os.path.join(temp_dir, "test1.jpg")
            test_png = os.path.join(temp_dir, "test2.png")
            
            assert create_test_image(test_jpg), "创建测试JPG失败"
            assert create_test_image(test_png, format='PNG'), "创建测试PNG失败"
            
            # 测试添加图片
            assert list_manager.add_image(test_jpg), "添加JPG图片失败"
            assert list_manager.add_image(test_png), "添加PNG图片失败"
            assert not list_manager.add_image(test_jpg), "重复添加应该失败"
            
            # 测试列表操作
            assert list_manager.get_image_count() == 2, "图片数量错误"
            assert list_manager.get_current_image() is not None, "当前图片获取失败"
            
            # 测试索引操作
            assert list_manager.set_current_index(1), "设置索引失败"
            assert list_manager.get_current_image()['filename'] == "test2.png", "索引设置错误"
            
            # 测试导航
            next_img = list_manager.get_next_image()
            assert next_img['filename'] == "test1.jpg", "下一张图片错误"
            
            prev_img = list_manager.get_previous_image()
            assert prev_img['filename'] == "test2.png", "上一张图片错误"
            
            # 测试移除图片
            assert list_manager.remove_image(test_jpg), "移除图片失败"
            assert list_manager.get_image_count() == 1, "移除后图片数量错误"
            
            # 测试清空列表
            list_manager.clear_list()
            assert list_manager.get_image_count() == 0, "清空列表失败"
            assert list_manager.current_index == 0, "清空后索引错误"
        
        print("[OK] Image list manager tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Image list manager test failed: {e}")
        return False

def test_integration():
    """测试集成功能"""
    print("Testing integration...")
    try:
        from file_manager import ImageFileManager, ExportManager
        from image_list import ImageListManager
        
        # 创建管理器实例
        file_manager = ImageFileManager()
        export_manager = ExportManager()
        list_manager = ImageListManager()
        
        # 创建临时测试图片
        with tempfile.TemporaryDirectory() as temp_dir:
            test_jpg = os.path.join(temp_dir, "integration_test.jpg")
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            assert create_test_image(test_jpg), "创建集成测试图片失败"
            
            # 验证并添加图片
            assert file_manager.validate_image_file(test_jpg), "图片验证失败"
            assert list_manager.add_image(test_jpg), "添加图片到列表失败"
            
            # 设置导出
            export_manager.output_folder = output_dir
            export_manager.update_export_settings({'format': 'jpg', 'quality': 90})
            
            # 等待缩略图创建完成
            import time
            time.sleep(0.5)
            
            # 加载图片并导出
            image = list_manager.load_image(test_jpg)
            if image is None:
                print(f"Failed to load image: {test_jpg}")
                print(f"Image list: {[img['path'] for img in list_manager.get_image_list()]}")
            assert image is not None, "Load image failed"
            
            # 测试导出
            assert export_manager.export_single_image(test_jpg, image), "Export image failed"
            
            # 验证导出文件
            exported_files = os.listdir(output_dir)
            assert len(exported_files) == 1, "Exported file count error"
            assert exported_files[0].startswith("wm_"), "Exported filename error"
        
        print("[OK] Integration tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Integration test failed: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("File Processing System Test")
    print("=" * 60)
    
    tests = [
        test_file_manager,
        test_export_manager,
        test_image_list_manager,
        test_integration
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
        print("All file processing system tests passed!")
        return True
    else:
        print("Some tests failed, please check the code")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
