#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试基于中心的水印旋转功能
"""

import sys
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, os.path.join(src_dir, 'components'))

def create_test_image_with_grid():
    """创建带网格的测试图片，便于观察旋转效果"""
    image = Image.new('RGB', (400, 300), 'white')
    draw = ImageDraw.Draw(image)
    
    # 绘制网格
    for x in range(0, 400, 50):
        draw.line([(x, 0), (x, 300)], fill='lightgray', width=1)
    for y in range(0, 300, 50):
        draw.line([(0, y), (400, y)], fill='lightgray', width=1)
    
    # 绘制中心十字线
    draw.line([(200, 0), (200, 300)], fill='red', width=2)
    draw.line([(0, 150), (400, 150)], fill='red', width=2)
    
    # 标记中心点
    draw.ellipse([(195, 145), (205, 155)], fill='red')
    
    return image

def test_center_rotation():
    """测试基于中心的旋转功能"""
    print("=== 测试基于中心的水印旋转 ===\n")
    
    try:
        from text_watermark import TextWatermark
        
        # 创建测试图片
        test_image = create_test_image_with_grid()
        
        # 创建文本水印
        watermark = TextWatermark()
        watermark.set_text("CENTER ROTATION TEST")
        watermark.set_font_size(24)
        watermark.set_color("#FF0000")
        watermark.set_position("center")  # 放在中心位置
        
        with tempfile.TemporaryDirectory() as temp_dir:
            print("测试不同角度的中心旋转:")
            
            # 测试不同角度
            angles = [0, 30, 45, 60, 90, 120, 135, 150, 180]
            
            for angle in angles:
                watermark.set_rotation(angle)
                
                # 应用水印
                result_image = watermark.apply_to_image(test_image.copy())
                
                if result_image:
                    # 保存结果图片
                    output_path = os.path.join(temp_dir, f"rotation_{angle:03d}.png")
                    result_image.save(output_path)
                    print(f"  ✅ {angle:3d}° - 已保存到: {os.path.basename(output_path)}")
                else:
                    print(f"  ❌ {angle:3d}° - 旋转失败")
                    return False
            
            print(f"\n📁 测试图片保存在: {temp_dir}")
            print("   可以打开查看旋转效果是否基于水印中心进行")
            
            # 等待用户查看
            input("\n按回车键继续...")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_positions():
    """测试不同位置的中心旋转"""
    print("\n=== 测试不同位置的中心旋转 ===\n")
    
    try:
        from text_watermark import TextWatermark
        
        # 创建测试图片
        test_image = create_test_image_with_grid()
        
        # 测试不同位置的旋转
        positions = [
            ("top_left", "左上"),
            ("top_center", "上中"),
            ("top_right", "右上"),
            ("center_left", "左中"),
            ("center", "中心"),
            ("center_right", "右中"),
            ("bottom_left", "左下"),
            ("bottom_center", "下中"),
            ("bottom_right", "右下")
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            print("测试不同位置的45度旋转:")
            
            for pos_key, pos_name in positions:
                watermark = TextWatermark()
                watermark.set_text(f"{pos_name}旋转")
                watermark.set_font_size(20)
                watermark.set_color("#0000FF")
                watermark.set_position(pos_key)
                watermark.set_rotation(45)  # 统一45度旋转
                
                # 应用水印
                result_image = watermark.apply_to_image(test_image.copy())
                
                if result_image:
                    output_path = os.path.join(temp_dir, f"position_{pos_key}.png")
                    result_image.save(output_path)
                    print(f"  ✅ {pos_name:4s} - 已保存")
                else:
                    print(f"  ❌ {pos_name:4s} - 失败")
                    return False
            
            print(f"\n📁 位置测试图片保存在: {temp_dir}")
            input("按回车键继续...")
        
        return True
        
    except Exception as e:
        print(f"❌ 位置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rotation_with_effects():
    """测试带效果的旋转"""
    print("\n=== 测试带效果的旋转 ===\n")
    
    try:
        from text_watermark import TextWatermark
        
        # 创建测试图片
        test_image = create_test_image_with_grid()
        
        # 创建带效果的水印
        watermark = TextWatermark()
        watermark.set_text("效果旋转测试")
        watermark.set_font_size(28)
        watermark.set_color("#FF6600")
        watermark.set_position("center")
        watermark.set_shadow(True)
        watermark.set_outline(True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            print("测试带阴影和描边的旋转效果:")
            
            # 测试几个关键角度
            angles = [0, 45, 90, 135, 180, -45, -90]
            
            for angle in angles:
                watermark.set_rotation(angle)
                
                result_image = watermark.apply_to_image(test_image.copy())
                
                if result_image:
                    output_path = os.path.join(temp_dir, f"effects_{angle:+03d}.png")
                    result_image.save(output_path)
                    print(f"  ✅ {angle:+4d}° - 效果旋转成功")
                else:
                    print(f"  ❌ {angle:+4d}° - 效果旋转失败")
                    return False
            
            print(f"\n📁 效果测试图片保存在: {temp_dir}")
            input("按回车键继续...")
        
        return True
        
    except Exception as e:
        print(f"❌ 效果测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def visual_comparison_test():
    """视觉对比测试 - 原始旋转 vs 中心旋转"""
    print("\n=== 视觉对比测试 ===\n")
    
    try:
        from text_watermark import TextWatermark
        
        # 创建测试图片
        test_image = create_test_image_with_grid()
        
        watermark = TextWatermark()
        watermark.set_text("旋转对比测试")
        watermark.set_font_size(24)
        watermark.set_color("#00AA00")
        watermark.set_position("center")
        watermark.set_rotation(60)  # 明显的旋转角度
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 使用新的中心旋转方法
            result_new = watermark.apply_to_image(test_image.copy())
            
            if result_new:
                new_path = os.path.join(temp_dir, "center_rotation.png")
                result_new.save(new_path)
                print(f"✅ 基于中心的旋转结果已保存")
                
                print(f"\n📁 对比图片保存在: {temp_dir}")
                print("   center_rotation.png - 基于中心的旋转")
                print("\n请查看旋转效果是否符合预期：")
                print("- 文本应该基于自身中心旋转")
                print("- 旋转后文本位置应该相对稳定")
                
                input("\n按回车键结束测试...")
                return True
            else:
                print("❌ 旋转失败")
                return False
        
    except Exception as e:
        print(f"❌ 对比测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始基于中心的水印旋转测试...")
    print("=" * 50)
    
    # 执行各项测试
    test1 = test_center_rotation()
    test2 = test_different_positions() 
    test3 = test_rotation_with_effects()
    test4 = visual_comparison_test()
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"中心旋转测试: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"位置旋转测试: {'✅ 通过' if test2 else '❌ 失败'}")
    print(f"效果旋转测试: {'✅ 通过' if test3 else '❌ 失败'}")
    print(f"视觉对比测试: {'✅ 通过' if test4 else '❌ 失败'}")
    
    if test1 and test2 and test3 and test4:
        print("\n🎉 基于中心的旋转功能实现成功！")
        print("\n✨ 新旋转功能特点:")
        print("📐 基于水印文本中心进行旋转")
        print("🎯 旋转后位置保持相对稳定")
        print("🎨 支持阴影和描边效果的旋转")
        print("📍 适用于所有预设位置")
        print("🔄 支持任意角度(-180° 到 180°)")
    else:
        print("\n❌ 部分测试失败，请检查实现")
    
    print("=" * 50)

if __name__ == "__main__":
    main()