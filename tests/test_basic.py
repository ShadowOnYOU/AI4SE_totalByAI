# -*- coding: utf-8 -*-
"""
基础架构测试脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """测试配置模块"""
    print("Testing config module...")
    try:
        from config import Config
        
        # 测试默认配置
        default_config = Config.get_default_config()
        print(f"[OK] Default config loaded: {len(default_config)} items")
        
        # 测试图片格式验证
        valid_formats = ['.jpg', '.png', '.bmp']
        invalid_formats = ['.txt', '.doc', '.pdf']
        
        for fmt in valid_formats:
            assert Config.validate_image_format(f"test{fmt}"), f"Format {fmt} should be valid"
        print("[OK] Valid image format validation passed")
        
        for fmt in invalid_formats:
            assert not Config.validate_image_format(f"test{fmt}"), f"Format {fmt} should be invalid"
        print("[OK] Invalid image format validation passed")
        
        # 测试配置保存和加载
        test_config = {'test': 'value', 'number': 123}
        Config.save_config(test_config)
        loaded_config = Config.load_config()
        assert loaded_config['test'] == 'value', "Config save/load failed"
        print("[OK] Config save/load test passed")
        
        print("Config module test completed!\n")
        return True
        
    except Exception as e:
        print(f"[FAIL] Config module test failed: {e}")
        return False

def test_main_app():
    """测试主应用程序（不启动GUI）"""
    print("Testing main application...")
    try:
        from main import WatermarkApp
        
        # 创建应用实例（不运行GUI）
        app = WatermarkApp()
        assert app.root is not None, "Main window creation failed"
        assert app.config is not None, "Config loading failed"
        print("[OK] Main application initialization successful")
        
        # 测试状态更新
        app.update_status("Test status")
        print("[OK] Status update function working")
        
        # 关闭窗口
        app.root.destroy()
        print("[OK] Main application test completed")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Main application test failed: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 50)
    print("Watermark Tool - Basic Architecture Test")
    print("=" * 50)
    
    tests = [
        test_config,
        test_main_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    print("=" * 50)
    
    if passed == total:
        print("All basic architecture tests passed!")
        return True
    else:
        print("Some tests failed, please check the code")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
