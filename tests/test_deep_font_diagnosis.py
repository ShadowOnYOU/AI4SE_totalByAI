#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入诊断文本水印字体问题
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_font_fallback():
    """测试字体回退机制"""
    print("Testing font fallback mechanism...")
    
    from components.text_watermark import TextWatermark
    
    # 创建水印实例
    watermark = TextWatermark()
    
    # 测试不同字体设置
    font_tests = [
        ("Arial", "Arial字体测试"),
        ("NonExistentFont", "不存在字体测试"),
        ("Times New Roman", "Times字体测试"),
        ("Helvetica", "Helvetica字体测试")
    ]
    
    test_img = Image.new('RGB', (400, 200), 'white')
    
    for font_name, test_text in font_tests:
        print(f"\nTesting font: {font_name}")
        print(f"Test text: {test_text}")
        
        # 设置字体
        watermark.set_font_family(font_name)
        watermark.set_text(test_text)
        
        # 获取字体对象
        font_obj = watermark._get_font()
        print(f"Font object: {font_obj}")
        
        # 测试文本渲染
        draw = ImageDraw.Draw(test_img)
        try:
            bbox = draw.textbbox((0, 0), test_text, font=font_obj)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            print(f"Text size: {width}x{height}")
            
            if width > 0 and height > 0:
                print("✓ Text renders successfully")
            else:
                print("✗ Text has zero size")
                
        except Exception as e:
            print(f"✗ Text rendering failed: {e}")

def test_specific_chinese_fonts():
    """测试特定的中文字体"""
    print("\nTesting specific Chinese fonts...")
    
    from components.text_watermark import TextWatermark
    
    # 推荐的中文字体列表
    chinese_fonts = [
        "STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "Hiragino Sans GB.ttc", 
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc"
    ]
    
    test_text = "中文水印测试"
    test_img = Image.new('RGB', (400, 100), 'white')
    
    for font_name in chinese_fonts:
        print(f"\nTesting Chinese font: {font_name}")
        
        watermark = TextWatermark()
        watermark.set_font_family(font_name)
        watermark.set_text(test_text)
        watermark.set_font_size(24)
        watermark.set_color("#FF0000")  # 红色，便于识别
        
        # 应用水印
        result = watermark.apply_to_image(test_img)
        
        if result:
            output_path = os.path.join(current_dir, f'test_font_{font_name.replace("/", "_").replace(" ", "_")}.png')
            result.save(output_path)
            print(f"✓ Saved to: {output_path}")
        else:
            print("✗ Watermark application failed")

def test_font_cache_issue():
    """测试字体缓存问题"""
    print("\nTesting font cache...")
    
    from components.text_watermark import TextWatermark
    
    watermark = TextWatermark()
    
    # 清空字体缓存
    watermark._font_cache.clear()
    print("Font cache cleared")
    
    # 设置中文字体
    watermark.set_font_family("STHeiti Medium.ttc")
    print("Font family set to STHeiti Medium.ttc")
    
    # 获取字体
    font1 = watermark._get_font(24)
    print(f"Font 1: {font1}")
    print(f"Cache contents: {list(watermark._font_cache.keys())}")
    
    # 再次获取相同字体
    font2 = watermark._get_font(24)
    print(f"Font 2: {font2}")
    print(f"Same font object: {font1 is font2}")

def test_ui_integration():
    """测试UI集成问题"""
    print("\nTesting UI integration...")
    
    # 模拟UI中的字体设置
    from components.text_watermark import TextWatermark
    
    watermark = TextWatermark()
    
    # 模拟用户在UI中设置中文文本
    chinese_text = "中文水印"
    print(f"Setting Chinese text: {chinese_text}")
    
    watermark.set_text(chinese_text)
    watermark.set_font_size(30)
    watermark.set_font_family("Arial")  # 默认字体
    watermark.set_color("#000000")  # 黑色
    watermark.set_position("center")
    
    # 创建测试图片
    test_img = Image.new('RGB', (300, 200), 'white')
    
    # 应用水印
    result = watermark.apply_to_image(test_img)
    
    if result:
        output_path = os.path.join(current_dir, 'ui_integration_test.png')
        result.save(output_path)
        print(f"✓ UI integration test passed, saved to: {output_path}")
        return True
    else:
        print("✗ UI integration test failed")
        return False

if __name__ == "__main__":
    print("=== Deep Font Diagnosis ===")
    
    # 测试字体回退机制
    test_font_fallback()
    
    # 测试中文字体
    test_specific_chinese_fonts()
    
    # 测试字体缓存
    test_font_cache_issue()
    
    # 测试UI集成
    ui_works = test_ui_integration()
    
    print(f"\n=== Conclusion ===")
    print(f"UI integration works: {ui_works}")
    print("\nIf the issue persists in the actual application, it might be:")
    print("1. Font loading path differences")
    print("2. UI encoding issues")
    print("3. Different Python environment")
    print("4. Image display/export problems")