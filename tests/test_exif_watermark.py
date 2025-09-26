#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXIF水印功能测试
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PIL import Image
import tempfile
from components.exif_text_watermark import ExifTextWatermark

def test_exif_watermark():
    """测试EXIF水印功能"""
    print("=" * 50)
    print("EXIF水印功能测试")
    print("=" * 50)
    
    # 创建测试图片
    test_image = Image.new('RGB', (400, 300), color='lightblue')
    
    # 创建EXIF水印实例
    exif_watermark = ExifTextWatermark()
    
    # 设置水印属性
    exif_watermark.set_font_size(24)
    exif_watermark.set_color('#FFFFFF')
    exif_watermark.set_transparency(80)
    exif_watermark.set_position('bottom_right')
    exif_watermark.set_prefix_suffix("拍摄于 ", "")
    
    # 测试1：无EXIF数据，使用文件时间
    print("\n测试1：无EXIF数据，使用文件时间")
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        test_image.save(temp_file.name)
        temp_path = temp_file.name
    
    try:
        watermark_text = exif_watermark.generate_watermark_text(temp_path)
        print(f"生成的水印文本: {watermark_text}")
        
        # 应用水印
        result_image = exif_watermark.apply_to_image_with_path(test_image, temp_path)
        print(f"水印应用结果: {'成功' if result_image else '失败'}")
        
        if result_image:
            print(f"结果图片尺寸: {result_image.size}")
            print(f"结果图片模式: {result_image.mode}")
            
    except Exception as e:
        print(f"测试失败: {e}")
    
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    # 测试2：测试不同的日期格式
    print("\n测试2：测试不同的日期格式")
    formats = ['%Y-%m-%d', '%Y年%m月%d日', '%m/%d/%Y', '%d-%m-%Y']
    
    for fmt in formats:
        exif_watermark.set_date_format(fmt)
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            test_image.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            watermark_text = exif_watermark.generate_watermark_text(temp_path)
            print(f"格式 {fmt}: {watermark_text}")
        except Exception as e:
            print(f"格式 {fmt} 失败: {e}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    # 测试3：测试前缀后缀
    print("\n测试3：测试前缀后缀")
    exif_watermark.set_date_format('%Y-%m-%d')
    exif_watermark.set_prefix_suffix("📷 ", " 摄")
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        test_image.save(temp_file.name)
        temp_path = temp_file.name
    
    try:
        watermark_text = exif_watermark.generate_watermark_text(temp_path)
        print(f"带前缀后缀: {watermark_text}")
    except Exception as e:
        print(f"前缀后缀测试失败: {e}")
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    print("\n=" * 50)
    print("EXIF水印测试完成")
    print("=" * 50)

if __name__ == "__main__":
    test_exif_watermark()
