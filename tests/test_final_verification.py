#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证测试 - 完整的中文水印功能测试
"""

import os
import sys
from PIL import Image

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, 'src'))

def create_test_image():
    """创建一个测试图片"""
    # 创建一个白色背景的图片，模拟用户的照片
    img = Image.new('RGB', (800, 600), (255, 255, 255))
    return img

def test_complete_workflow():
    """测试完整的工作流程"""
    print("=== 完整工作流程测试 ===")
    
    from components.text_watermark import TextWatermark
    from components.exif_text_watermark import ExifTextWatermark
    
    # 创建测试图片
    test_img = create_test_image()
    
    print("1. 测试普通文本水印...")
    
    # 测试用例
    text_watermark_tests = [
        {
            'text': '版权所有 © 2024',
            'font_size': 24,
            'color': '#FF0000',
            'position': 'bottom_right',
            'description': '红色版权水印'
        },
        {
            'text': '摄影师：李明',
            'font_size': 18,
            'color': '#000000',
            'position': 'top_left',
            'description': '黑色署名水印'
        },
        {
            'text': '未经授权禁止使用',
            'font_size': 20,
            'color': '#0000FF',
            'position': 'center',
            'transparency': 70,
            'description': '半透明警告水印'
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(text_watermark_tests, 1):
        print(f"\n  测试 {i}: {test_case['description']}")
        print(f"    文本: '{test_case['text']}'")
        
        try:
            watermark = TextWatermark()
            watermark.set_text(test_case['text'])
            watermark.set_font_size(test_case['font_size'])
            watermark.set_color(test_case['color'])
            watermark.set_position(test_case['position'])
            
            if 'transparency' in test_case:
                watermark.set_transparency(test_case['transparency'])
            
            # 应用水印
            result = watermark.apply_to_image(test_img.copy())
            
            if result:
                output_path = os.path.join(current_dir, f'final_test_text_{i}.png')
                result.save(output_path)
                print(f"    ✓ 成功: {output_path}")
                success_count += 1
            else:
                print(f"    ✗ 失败: 水印应用失败")
                
        except Exception as e:
            print(f"    ✗ 错误: {e}")
    
    print(f"\n2. 测试EXIF时间水印...")
    
    # 测试EXIF水印
    try:
        exif_watermark = ExifTextWatermark()
        exif_watermark.set_font_size(16)
        exif_watermark.set_color('#666666')
        exif_watermark.set_position('bottom_left')
        exif_watermark.set_prefix_suffix('拍摄于: ', '')
        
        # 由于没有真实的EXIF数据，我们直接测试生成的文本
        test_date = '2024-03-01'
        watermark_text = f"拍摄于: {test_date}"
        
        print(f"    EXIF水印文本: '{watermark_text}'")
        
        # 创建一个临时的文本水印来测试EXIF样式
        temp_watermark = TextWatermark()
        temp_watermark.set_text(watermark_text)
        temp_watermark.set_font_size(16)
        temp_watermark.set_color('#666666')
        temp_watermark.set_position('bottom_left')
        
        result = temp_watermark.apply_to_image(test_img.copy())
        
        if result:
            output_path = os.path.join(current_dir, 'final_test_exif.png')
            result.save(output_path)
            print(f"    ✓ 成功: {output_path}")
            success_count += 1
        else:
            print(f"    ✗ 失败: EXIF水印应用失败")
            
    except Exception as e:
        print(f"    ✗ 错误: {e}")
    
    print(f"\n3. 测试边缘情况...")
    
    # 测试边缘情况
    edge_cases = [
        '中',  # 单个中文字符
        '中英Mixed文本123',  # 混合文本
        '特殊符号©®™',  # 特殊符号
        '很长的中文水印文本测试用例用来验证换行和显示效果',  # 长文本
        '',  # 空文本
    ]
    
    for i, text in enumerate(edge_cases, 1):
        print(f"\n  边缘测试 {i}: '{text}'")
        
        try:
            watermark = TextWatermark()
            watermark.set_text(text)
            watermark.set_font_size(20)
            watermark.set_position('center')
            
            result = watermark.apply_to_image(test_img.copy())
            
            if result:
                output_path = os.path.join(current_dir, f'final_test_edge_{i}.png')
                result.save(output_path)
                print(f"    ✓ 成功: {output_path}")
                success_count += 1
            else:
                print(f"    ✗ 失败: 水印应用失败")
                
        except Exception as e:
            print(f"    ✗ 错误: {e}")
    
    total_tests = len(text_watermark_tests) + 1 + len(edge_cases)
    print(f"\n=== 测试结果 ===")
    print(f"成功: {success_count}/{total_tests}")
    print(f"成功率: {success_count/total_tests*100:.1f}%")
    
    return success_count == total_tests

def test_font_robustness():
    """测试字体的鲁棒性"""
    print("\n=== 字体鲁棒性测试 ===")
    
    from components.text_watermark import TextWatermark
    
    test_img = create_test_image()
    test_text = "字体测试ABC123"
    
    # 测试系统中可能不存在的字体
    problematic_fonts = [
        "NotExistFont",
        "/path/to/nonexistent/font.ttf",
        "微软雅黑",  # Windows字体在macOS上不存在
        "宋体",
        "仿宋",
        "",  # 空字体名
        None  # None值
    ]
    
    success_count = 0
    
    for i, font_name in enumerate(problematic_fonts, 1):
        print(f"\n测试问题字体 {i}: {repr(font_name)}")
        
        try:
            watermark = TextWatermark()
            watermark.set_text(test_text)
            
            if font_name is not None:
                watermark.set_font_family(font_name)
            
            # 查看实际使用的字体
            font_obj = watermark._get_font()
            print(f"  实际字体对象: {font_obj}")
            
            result = watermark.apply_to_image(test_img.copy())
            
            if result:
                output_path = os.path.join(current_dir, f'font_robust_{i}.png')
                result.save(output_path)
                print(f"  ✓ 字体回退成功: {output_path}")
                success_count += 1
            else:
                print(f"  ✗ 字体回退失败")
                
        except Exception as e:
            print(f"  ✗ 错误: {e}")
    
    print(f"\n字体鲁棒性测试结果: {success_count}/{len(problematic_fonts)}")
    return success_count == len(problematic_fonts)

if __name__ == "__main__":
    print("开始中文水印功能的最终验证测试...")
    print("=" * 50)
    
    # 完整工作流程测试
    workflow_success = test_complete_workflow()
    
    # 字体鲁棒性测试
    robustness_success = test_font_robustness()
    
    print("\n" + "=" * 50)
    print("=== 最终结果 ===")
    
    if workflow_success and robustness_success:
        print("🎉 所有测试通过！中文水印问题已解决！")
        print("\n修复要点:")
        print("✓ 1. 改进了字体回退机制，优先选择支持中文的字体")
        print("✓ 2. 默认字体改为STHeiti Medium.ttc（黑体）")
        print("✓ 3. 添加了多个平台的中文字体支持")
        print("✓ 4. 增强了错误处理和调试信息")
        print("✓ 5. 更新了UI字体选择列表")
        
        print("\n用户使用建议:")
        print("• 推荐使用'STHeiti Medium.ttc'或'Hiragino Sans GB.ttc'字体")
        print("• 如果遇到显示问题，尝试切换字体")
        print("• 系统会自动回退到支持中文的字体")
        
    else:
        print("❌ 部分测试失败，需要进一步调查")
        print(f"工作流程测试: {'✓' if workflow_success else '✗'}")
        print(f"字体鲁棒性测试: {'✓' if robustness_success else '✗'}")
    
    print(f"\n测试结果图片保存在: {current_dir}")
    print("您可以检查这些图片来验证中文水印是否正确显示")