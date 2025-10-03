#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际应用场景测试 - 模拟用户输入中文水印的问题
"""

import os
import sys
from PIL import Image

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_real_application_scenario():
    """测试真实应用场景"""
    print("=== Real Application Scenario Test ===")
    
    from components.text_watermark import TextWatermark
    
    # 创建一个测试图片（模拟用户选择的图片）
    test_img = Image.new('RGB', (800, 600), 'white')
    
    # 测试不同的中文输入场景
    test_cases = [
        "中文水印",
        "版权所有",
        "摄影作品",
        "未经授权禁止使用",
        "Copyright © 2024",
        "Test测试",
        "水印Watermark",
        "拍摄于北京",
        "©️ 张三 2024"
    ]
    
    success_count = 0
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{test_text}'")
        
        try:
            # 创建水印实例
            watermark = TextWatermark()
            
            # 模拟用户在UI中的操作
            watermark.set_text(test_text)
            watermark.set_font_size(24)
            watermark.set_color("#FF0000")  # 红色便于识别
            watermark.set_position("center")
            watermark.set_transparency(80)
            
            # 应用水印
            result = watermark.apply_to_image(test_img.copy())
            
            if result:
                # 保存结果
                output_path = os.path.join(current_dir, f'real_test_{i}_{test_text.replace("/", "_").replace("©", "c")}.png')
                result.save(output_path)
                print(f"✓ Success: {output_path}")
                success_count += 1
            else:
                print("✗ Failed: Watermark application failed")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n=== Results ===")
    print(f"Success: {success_count}/{len(test_cases)}")
    print(f"Success Rate: {success_count/len(test_cases)*100:.1f}%")
    
    return success_count == len(test_cases)

def test_font_family_settings():
    """测试不同字体族设置"""
    print("\n=== Font Family Settings Test ===")
    
    from components.text_watermark import TextWatermark
    
    test_img = Image.new('RGB', (400, 200), 'white')
    test_text = "中文字体测试"
    
    # 测试不同字体设置
    font_tests = [
        ("默认", "Arial"),
        ("黑体", "STHeiti Medium.ttc"),
        ("冬青黑体", "Hiragino Sans GB.ttc"),
        ("不存在字体", "NonExistentFont123")
    ]
    
    for font_name, font_family in font_tests:
        print(f"\nTesting {font_name} ({font_family}):")
        
        try:
            watermark = TextWatermark()
            watermark.set_text(test_text)
            watermark.set_font_family(font_family)
            watermark.set_font_size(20)
            watermark.set_color("#000000")
            watermark.set_position("center")
            
            # 获取实际使用的字体
            font_obj = watermark._get_font()
            print(f"  Font object: {font_obj}")
            
            result = watermark.apply_to_image(test_img.copy())
            
            if result:
                output_path = os.path.join(current_dir, f'font_test_{font_name}.png')
                result.save(output_path)
                print(f"  ✓ Saved: {output_path}")
            else:
                print(f"  ✗ Failed to apply watermark")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")

def test_ui_encoding():
    """测试UI编码问题"""
    print("\n=== UI Encoding Test ===")
    
    # 模拟从UI Entry获取的文本可能存在的编码问题
    test_inputs = [
        "中文水印",  # 直接字符串
        "中文水印".encode('utf-8').decode('utf-8'),  # UTF-8编码后解码
        # 其他可能的编码问题...
    ]
    
    from components.text_watermark import TextWatermark
    
    test_img = Image.new('RGB', (300, 200), 'white')
    
    for i, text_input in enumerate(test_inputs, 1):
        print(f"\nTest {i}: type={type(text_input)}, repr={repr(text_input)}")
        
        try:
            watermark = TextWatermark()
            watermark.set_text(text_input)
            watermark.set_font_size(24)
            watermark.set_position("center")
            
            result = watermark.apply_to_image(test_img.copy())
            
            if result:
                output_path = os.path.join(current_dir, f'encoding_test_{i}.png')
                result.save(output_path)
                print(f"  ✓ Success: {output_path}")
            else:
                print(f"  ✗ Failed")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")

if __name__ == "__main__":
    print("Testing Chinese watermark in real application scenarios...")
    
    # 测试真实应用场景
    scenario_success = test_real_application_scenario()
    
    # 测试字体设置
    test_font_family_settings()
    
    # 测试编码问题
    test_ui_encoding()
    
    print(f"\n=== Overall Result ===")
    if scenario_success:
        print("✓ All tests passed! The Chinese watermark issue should be fixed.")
        print("Key improvements made:")
        print("  1. Enhanced font fallback mechanism")
        print("  2. Prioritized Chinese-compatible fonts")
        print("  3. Added better error handling and logging")
    else:
        print("✗ Some tests failed. Further investigation needed.")
    
    print(f"\nGenerated test images are saved in: {current_dir}")