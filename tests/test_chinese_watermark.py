#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文水印测试脚本
用于诊断中文字符水印显示问题
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_fonts_for_chinese():
    """测试系统字体对中文支持"""
    print("Testing font support for Chinese characters...")
    
    # 创建测试图片
    test_img = Image.new('RGB', (400, 300), 'white')
    draw = ImageDraw.Draw(test_img)
    
    # 测试文本
    test_texts = [
        "Hello World",  # 英文
        "中文测试",      # 中文
        "Test水印",     # 混合
        "测试Watermark" # 混合
    ]
    
    # 常见字体列表 (macOS)
    fonts_to_test = [
        "Arial.ttf",
        "Helvetica.ttc", 
        "PingFang.ttc",
        "STHeiti Medium.ttc",
        "STSong.ttc",
        "Hiragino Sans GB.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode MS.ttf",
        "/Library/Fonts/Arial Unicode MS.ttf",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc"
    ]
    
    working_fonts = []
    
    for font_path in fonts_to_test:
        print(f"\nTesting font: {font_path}")
        try:
            font = ImageFont.truetype(font_path, 20)
            
            for text in test_texts:
                try:
                    # 尝试测量文本大小
                    bbox = draw.textbbox((0, 0), text, font=font)
                    width = bbox[2] - bbox[0]
                    height = bbox[3] - bbox[1]
                    
                    if width > 0 and height > 0:
                        print(f"  ✓ '{text}' - Size: {width}x{height}")
                        if text == "中文测试" and font_path not in working_fonts:
                            working_fonts.append(font_path)
                    else:
                        print(f"  ✗ '{text}' - Zero size (font doesn't support)")
                except Exception as e:
                    print(f"  ✗ '{text}' - Error: {e}")
                    
        except Exception as e:
            print(f"  Font load failed: {e}")
    
    print(f"\nFonts that support Chinese characters:")
    for font in working_fonts:
        print(f"  ✓ {font}")
    
    return working_fonts

def test_default_font_chinese():
    """测试默认字体的中文支持"""
    print("\nTesting default font for Chinese...")
    
    try:
        font = ImageFont.load_default()
        test_img = Image.new('RGB', (200, 100), 'white')
        draw = ImageDraw.Draw(test_img)
        
        test_text = "中文测试"
        bbox = draw.textbbox((0, 0), test_text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        print(f"Default font - '{test_text}': {width}x{height}")
        
        if width > 0 and height > 0:
            print("✓ Default font supports Chinese")
            return True
        else:
            print("✗ Default font doesn't support Chinese")
            return False
            
    except Exception as e:
        print(f"✗ Default font test failed: {e}")
        return False

def test_current_watermark():
    """测试当前水印实现"""
    print("\nTesting current watermark implementation...")
    
    try:
        from components.text_watermark import TextWatermark
        
        # 创建测试图片
        test_img = Image.new('RGB', (400, 300), 'white')
        
        # 创建水印
        watermark = TextWatermark()
        watermark.set_text("中文水印测试")
        watermark.set_font_size(24)
        watermark.set_position("center")
        
        # 应用水印
        result = watermark.apply_to_image(test_img)
        
        if result:
            # 保存结果用于检查
            output_path = os.path.join(current_dir, 'chinese_watermark_test.png')
            result.save(output_path)
            print(f"✓ Watermark applied successfully, saved to: {output_path}")
            return True
        else:
            print("✗ Watermark application failed")
            return False
            
    except Exception as e:
        print(f"✗ Watermark test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Chinese Watermark Diagnosis ===\n")
    
    # 测试字体支持
    working_fonts = test_fonts_for_chinese()
    
    # 测试默认字体
    default_supports_chinese = test_default_font_chinese()
    
    # 测试当前水印实现
    watermark_works = test_current_watermark()
    
    print("\n=== Summary ===")
    print(f"Fonts supporting Chinese: {len(working_fonts)}")
    print(f"Default font supports Chinese: {default_supports_chinese}")
    print(f"Current watermark works: {watermark_works}")
    
    if working_fonts:
        print(f"\nRecommended font for Chinese: {working_fonts[0]}")
    else:
        print("\n⚠️  No fonts found that support Chinese characters!")
        print("This is likely the cause of the issue.")