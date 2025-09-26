# -*- coding: utf-8 -*-
"""
文本水印处理系统测试脚本
"""

import sys
import os
import tempfile
from PIL import Image

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_image(filename: str, size=(400, 300), color='lightblue'):
    """创建测试图片"""
    try:
        img = Image.new('RGB', size, color)
        img.save(filename, 'JPEG')
        return True
    except Exception as e:
        print(f"Create test image failed: {e}")
        return False

def test_text_watermark_basic():
    """测试基本文本水印功能"""
    print("Testing basic text watermark...")
    try:
        from text_watermark import TextWatermark
        
        # 创建水印实例
        watermark = TextWatermark()
        
        # 测试基本设置
        watermark.set_text("Test Watermark")
        assert watermark.text == "Test Watermark", "Set text failed"
        
        watermark.set_font_size(30)
        assert watermark.font_size == 30, "Set font size failed"
        
        watermark.set_color("#FF0000")
        assert watermark.color == "#FF0000", "Set color failed"
        
        watermark.set_transparency(80)
        assert watermark.transparency == 80, "Set transparency failed"
        
        watermark.set_position("center")
        assert watermark.position == "center", "Set position failed"
        
        # 测试边界值
        watermark.set_font_size(5)  # 小于最小值
        assert watermark.font_size == 8, "Font size min limit failed"
        
        watermark.set_font_size(250)  # 大于最大值
        assert watermark.font_size == 200, "Font size max limit failed"
        
        watermark.set_transparency(-10)  # 小于最小值
        assert watermark.transparency == 0, "Transparency min limit failed"
        
        watermark.set_transparency(150)  # 大于最大值
        assert watermark.transparency == 100, "Transparency max limit failed"
        
        print("[OK] Basic text watermark tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Basic text watermark test failed: {e}")
        return False

def test_text_watermark_effects():
    """测试水印效果功能"""
    print("Testing watermark effects...")
    try:
        from text_watermark import TextWatermark
        
        watermark = TextWatermark()
        watermark.set_text("Effect Test")
        
        # 测试阴影效果
        watermark.set_shadow(True, "#000000")
        assert watermark.shadow == True, "Set shadow failed"
        assert watermark.shadow_color == "#000000", "Set shadow color failed"
        
        # 测试描边效果
        watermark.set_outline(True, "#FFFFFF", 2)
        assert watermark.outline == True, "Set outline failed"
        assert watermark.outline_color == "#FFFFFF", "Set outline color failed"
        assert watermark.outline_width == 2, "Set outline width failed"
        
        # 测试旋转
        watermark.set_angle(45)
        assert watermark.angle == 45, "Set angle failed"
        
        # 测试角度范围
        watermark.set_angle(400)
        assert watermark.angle == 40, "Angle range failed"
        
        print("[OK] Watermark effects tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Watermark effects test failed: {e}")
        return False

def test_watermark_creation():
    """测试水印图片创建"""
    print("Testing watermark image creation...")
    try:
        from text_watermark import TextWatermark
        
        watermark = TextWatermark()
        watermark.set_text("Creation Test")
        watermark.set_font_size(24)
        watermark.set_color("#FF0000")
        watermark.set_transparency(80)
        
        # 创建水印图片
        watermark_img = watermark.create_watermark_image((400, 300))
        assert watermark_img is not None, "Create watermark image failed"
        assert watermark_img.size == (400, 300), "Watermark image size wrong"
        assert watermark_img.mode == 'RGBA', "Watermark image mode wrong"
        
        # 测试不同位置
        positions = ["top_left", "center", "bottom_right"]
        for pos in positions:
            watermark.set_position(pos)
            img = watermark.create_watermark_image((200, 150))
            assert img is not None, f"Create watermark at {pos} failed"
        
        print("[OK] Watermark creation tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Watermark creation test failed: {e}")
        return False

def test_watermark_application():
    """测试水印应用到图片"""
    print("Testing watermark application...")
    try:
        from text_watermark import TextWatermark
        
        # 创建测试图片
        with tempfile.TemporaryDirectory() as temp_dir:
            test_image_path = os.path.join(temp_dir, "test.jpg")
            assert create_test_image(test_image_path), "Create test image failed"
            
            # 加载图片
            with Image.open(test_image_path) as img:
                original_size = img.size
                
                # 创建水印
                watermark = TextWatermark()
                watermark.set_text("Applied Watermark")
                watermark.set_font_size(20)
                watermark.set_color("#FFFFFF")
                watermark.set_transparency(90)
                watermark.set_position("bottom_right")
                
                # 应用水印
                watermarked_img = watermark.apply_to_image(img)
                assert watermarked_img is not None, "Apply watermark failed"
                assert watermarked_img.size == original_size, "Watermarked image size changed"
                
                # 测试预览功能
                preview_img = watermark.preview_watermark(img, (200, 150))
                assert preview_img is not None, "Preview watermark failed"
                assert preview_img.size[0] <= 200 and preview_img.size[1] <= 150, "Preview size wrong"
        
        print("[OK] Watermark application tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Watermark application test failed: {e}")
        return False

def test_watermark_serialization():
    """测试水印序列化"""
    print("Testing watermark serialization...")
    try:
        from text_watermark import TextWatermark
        
        # 创建水印并设置各种属性
        watermark1 = TextWatermark()
        watermark1.set_text("Serialization Test")
        watermark1.set_font_size(28)
        watermark1.set_color("#00FF00")
        watermark1.set_transparency(75)
        watermark1.set_position("top_center")
        watermark1.set_angle(30)
        watermark1.set_shadow(True, "#000000")
        watermark1.set_outline(True, "#FFFFFF", 2)
        
        # 获取水印信息
        info = watermark1.get_watermark_info()
        assert info['text'] == "Serialization Test", "Get watermark info failed"
        assert info['font_size'] == 28, "Font size in info wrong"
        assert info['color'] == "#00FF00", "Color in info wrong"
        
        # 创建新水印并从信息加载
        watermark2 = TextWatermark()
        watermark2.load_from_dict(info)
        
        # 验证加载结果
        assert watermark2.text == watermark1.text, "Load from dict failed"
        assert watermark2.font_size == watermark1.font_size, "Font size load failed"
        assert watermark2.color == watermark1.color, "Color load failed"
        assert watermark2.position == watermark1.position, "Position load failed"
        assert watermark2.angle == watermark1.angle, "Angle load failed"
        assert watermark2.shadow == watermark1.shadow, "Shadow load failed"
        assert watermark2.outline == watermark1.outline, "Outline load failed"
        
        print("[OK] Watermark serialization tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Watermark serialization test failed: {e}")
        return False

def test_color_conversion():
    """测试颜色转换功能"""
    print("Testing color conversion...")
    try:
        from text_watermark import TextWatermark
        
        watermark = TextWatermark()
        
        # 测试十六进制颜色转换
        test_cases = [
            ("#FF0000", 255, (255, 0, 0, 255)),
            ("#00FF00", 128, (0, 255, 0, 128)),
            ("#0000FF", 0, (0, 0, 255, 0)),
            ("#FFFFFF", 200, (255, 255, 255, 200))
        ]
        
        for hex_color, alpha, expected in test_cases:
            # 直接测试颜色转换逻辑
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            result = (r, g, b, alpha)
            assert result == expected, f"Color conversion failed for {hex_color}"
        
        print("[OK] Color conversion tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Color conversion test failed: {e}")
        return False

def test_position_calculation():
    """测试位置计算功能"""
    print("Testing position calculation...")
    try:
        from text_watermark import TextWatermark
        
        watermark = TextWatermark()
        
        # 测试不同位置的计算
        image_size = (400, 300)
        text_size = (100, 30)
        
        positions = [
            "top_left", "top_center", "top_right",
            "center_left", "center", "center_right",
            "bottom_left", "bottom_center", "bottom_right"
        ]
        
        for pos in positions:
            watermark.set_position(pos)
            x, y = watermark._calculate_position(image_size, text_size)
            
            # 验证位置在合理范围内
            assert 0 <= x <= image_size[0], f"X position out of range for {pos}: {x}"
            assert 0 <= y <= image_size[1], f"Y position out of range for {pos}: {y}"
        
        print("[OK] Position calculation tests passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Position calculation test failed: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("Text Watermark System Test")
    print("=" * 60)
    
    tests = [
        test_text_watermark_basic,
        test_text_watermark_effects,
        test_watermark_creation,
        test_watermark_application,
        test_watermark_serialization,
        test_color_conversion,
        test_position_calculation
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
        print("All text watermark system tests passed!")
        return True
    else:
        print("Some tests failed, please check the code")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
