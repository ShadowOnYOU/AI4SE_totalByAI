#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试高级功能：JPEG质量、图片尺寸调整、水印旋转
"""

import sys
import os
import tempfile
from PIL import Image

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, os.path.join(src_dir, 'components'))

def test_watermark_rotation():
    """测试水印旋转功能"""
    print("=== 测试水印旋转功能 ===\n")
    
    try:
        from text_watermark import TextWatermark
        
        # 创建文本水印
        watermark = TextWatermark()
        watermark.set_text("旋转测试 ROTATION TEST")
        watermark.set_font_size(36)
        watermark.set_color("#FF0000")
        
        # 创建测试图片
        test_image = Image.new('RGB', (400, 300), 'lightblue')
        
        # 测试不同角度的旋转
        angles = [0, 45, 90, 135, 180, -45]
        
        print("测试旋转角度:")
        for angle in angles:
            watermark.set_rotation(angle)
            print(f"  设置角度: {angle}°, 实际角度: {watermark.angle}°")
            
            # 应用水印
            watermarked_image = watermark.apply_to_image(test_image)
            if watermarked_image:
                print(f"  ✅ {angle}° 旋转成功")
            else:
                print(f"  ❌ {angle}° 旋转失败")
                return False
        
        print("\n🎉 水印旋转功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 水印旋转测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_jpeg_quality():
    """测试JPEG质量调整功能"""
    print("\n=== 测试JPEG质量调整功能 ===\n")
    
    try:
        from file_manager import ExportManager
        from text_watermark import TextWatermark
        
        # 创建导出管理器
        export_manager = ExportManager()
        
        # 创建测试图片
        test_image = Image.new('RGB', (300, 200), 'lightgreen')
        
        # 创建水印
        watermark = TextWatermark()
        watermark.set_text("质量测试")
        watermarked_image = watermark.apply_to_image(test_image)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            export_manager.output_folder = temp_dir
            
            # 测试不同的质量设置
            qualities = [10, 50, 75, 95, 100]
            
            print("测试不同JPEG质量:")
            for quality in qualities:
                export_manager.update_export_settings({
                    'format': 'jpg',
                    'quality': quality,
                    'filename_prefix': f'quality_{quality}_',
                    'filename_suffix': ''
                })
                
                # 模拟导出
                test_path = f"/test/image_{quality}.jpg"
                success = export_manager.export_single_image(test_path, watermarked_image)
                
                if success:
                    # 检查文件是否创建
                    files = [f for f in os.listdir(temp_dir) if f.startswith(f'quality_{quality}_')]
                    if files:
                        file_size = os.path.getsize(os.path.join(temp_dir, files[0]))
                        print(f"  质量 {quality}%: ✅ 成功，文件大小: {file_size} bytes")
                    else:
                        print(f"  质量 {quality}%: ❌ 文件未创建")
                        return False
                else:
                    print(f"  质量 {quality}%: ❌ 导出失败")
                    return False
        
        print("\n🎉 JPEG质量调整功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ JPEG质量测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_image_resize():
    """测试图片尺寸调整功能"""
    print("\n=== 测试图片尺寸调整功能 ===\n")
    
    try:
        from file_manager import ExportManager
        from text_watermark import TextWatermark
        
        # 创建导出管理器
        export_manager = ExportManager()
        
        # 创建测试图片 (800x600)
        test_image = Image.new('RGB', (800, 600), 'lightcoral')
        
        # 创建水印
        watermark = TextWatermark()
        watermark.set_text("尺寸测试")
        watermarked_image = watermark.apply_to_image(test_image)
        
        original_size = watermarked_image.size
        print(f"原始图片尺寸: {original_size[0]} x {original_size[1]}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            export_manager.output_folder = temp_dir
            
            # 测试不同的尺寸调整选项
            resize_tests = [
                {
                    "name": "保持原尺寸",
                    "settings": {
                        'resize_option': 'none'
                    },
                    "expected_size": (800, 600)
                },
                {
                    "name": "按宽度调整到400px",
                    "settings": {
                        'resize_option': 'width',
                        'width': 400
                    },
                    "expected_size": (400, 300)
                },
                {
                    "name": "按高度调整到200px", 
                    "settings": {
                        'resize_option': 'height',
                        'height': 200
                    },
                    "expected_size": (267, 200)  # 约267，保持比例
                },
                {
                    "name": "按50%缩放",
                    "settings": {
                        'resize_option': 'percent',
                        'percent': 0.5
                    },
                    "expected_size": (400, 300)
                }
            ]
            
            print("\n测试不同尺寸调整方式:")
            for test in resize_tests:
                print(f"\n--- {test['name']} ---")
                
                export_manager.update_export_settings({
                    'format': 'png',
                    'quality': 95,
                    'filename_prefix': 'resize_test_',
                    'filename_suffix': '',
                    'resize_settings': test['settings']
                })
                
                # 测试内部的尺寸调整方法
                resized_image = export_manager._apply_resize(watermarked_image)
                actual_size = resized_image.size
                expected_size = test['expected_size']
                
                print(f"  预期尺寸: {expected_size[0]} x {expected_size[1]}")
                print(f"  实际尺寸: {actual_size[0]} x {actual_size[1]}")
                
                # 允许一定的误差（特别是对于保持比例的调整）
                width_diff = abs(actual_size[0] - expected_size[0])
                height_diff = abs(actual_size[1] - expected_size[1])
                
                if width_diff <= 2 and height_diff <= 2:  # 允许2像素误差
                    print(f"  ✅ 尺寸调整正确")
                else:
                    print(f"  ❌ 尺寸调整错误，误差: ({width_diff}, {height_diff})")
                    return False
        
        print("\n🎉 图片尺寸调整功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 图片尺寸调整测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_integration():
    """测试UI集成"""
    print("\n=== 测试UI集成 ===\n")
    
    try:
        import tkinter as tk
        from main_window import MainWindow
        
        # 创建临时的root窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 创建主窗口实例
        main_window = MainWindow(root)
        
        # 测试新添加的UI组件是否存在
        ui_tests = [
            ("quality_var", "JPEG质量滑块变量"),
            ("quality_scale", "JPEG质量滑块"),
            ("resize_option", "尺寸调整选项变量"),
            ("width_var", "宽度输入变量"),
            ("height_var", "高度输入变量"),
            ("percent_var", "百分比输入变量"),
            ("rotation_var", "旋转角度变量"),
            ("rotation_label", "旋转角度标签")
        ]
        
        print("检查UI组件:")
        for attr_name, description in ui_tests:
            if hasattr(main_window, attr_name):
                print(f"  ✅ {description}: 已添加")
            else:
                print(f"  ❌ {description}: 缺失")
                root.destroy()
                return False
        
        # 测试回调函数是否存在
        callback_tests = [
            ("on_quality_changed", "JPEG质量变化回调"),
            ("on_rotation_changed", "旋转角度变化回调")
        ]
        
        print("\n检查回调函数:")
        for method_name, description in callback_tests:
            if hasattr(main_window, method_name):
                print(f"  ✅ {description}: 已实现")
            else:
                print(f"  ❌ {description}: 缺失")
                root.destroy()
                return False
        
        root.destroy()
        print("\n🎉 UI集成测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ UI集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试高级功能实现...")
    print("=" * 60)
    
    # 执行各项测试
    test1 = test_watermark_rotation()
    test2 = test_jpeg_quality()
    test3 = test_image_resize()
    test4 = test_ui_integration()
    
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print(f"水印旋转功能: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"JPEG质量调整: {'✅ 通过' if test2 else '❌ 失败'}")
    print(f"图片尺寸调整: {'✅ 通过' if test3 else '❌ 失败'}")
    print(f"UI集成测试: {'✅ 通过' if test4 else '❌ 失败'}")
    
    if test1 and test2 and test3 and test4:
        print("\n🎉 所有高级功能测试通过！")
        print("\n新增功能说明:")
        print("1. 📐 水印旋转: 支持-180°到180°任意角度旋转")
        print("2. 🎚️  JPEG质量: 可调节0-100%压缩质量") 
        print("3. 📏 图片尺寸: 支持按宽度、高度、百分比调整")
        print("4. 🎛️  完整UI: 所有功能都有对应的界面控制")
        print("\n这些功能完全符合PRD文档的高级功能要求！")
    else:
        print("\n❌ 部分测试失败，请检查实现")
    
    print("=" * 60)

if __name__ == "__main__":
    main()