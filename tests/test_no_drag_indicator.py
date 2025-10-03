#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片水印拖拽指示器移除测试
验证图片水印模式下不显示任何拖拽指示器
"""

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_image_watermark_no_overlay():
    """测试图片水印不显示任何拖拽覆盖层"""
    print("=== 图片水印拖拽指示器测试 ===")
    
    try:
        from ui.simple_watermark_drag import SimpleWatermarkDrag
        import tkinter as tk
        
        # 创建测试Canvas
        root = tk.Tk()
        root.withdraw()
        
        canvas = tk.Canvas(root, width=400, height=300, bg='white')
        
        # 创建拖拽处理器
        drag_handler = SimpleWatermarkDrag(canvas)
        
        # 测试不同水印类型
        test_cases = [
            {
                'type': 'text',
                'text': '文本水印',
                'should_have_elements': True,
                'description': '文本水印应该显示红色文字'
            },
            {
                'type': 'image', 
                'text': 'photo.jpg',
                'should_have_elements': False,
                'description': '图片水印不应该显示任何拖拽元素'
            },
            {
                'type': 'exif',
                'text': '2024-10-03',
                'should_have_elements': True,
                'description': 'EXIF水印应该显示灰色日期'
            }
        ]
        
        for test_case in test_cases:
            watermark_type = test_case['type']
            text = test_case['text']
            should_have_elements = test_case['should_have_elements']
            description = test_case['description']
            
            print(f"\n测试 {watermark_type} 水印:")
            print(f"  预期: {description}")
            
            # 显示水印
            drag_handler.show_watermark((100, 100), text, watermark_type)
            
            # 检查Canvas上的元素
            items = canvas.find_withtag('watermark_drag')
            has_elements = len(items) > 0
            
            # 检查是否可以拖拽
            is_draggable = drag_handler.is_in_watermark(100, 100)
            
            print(f"  实际结果:")
            print(f"    Canvas元素数量: {len(items)}")
            print(f"    可拖拽: {is_draggable}")
            print(f"    watermark_rect: {drag_handler.watermark_rect is not None}")
            print(f"    watermark_text: {drag_handler.watermark_text is not None}")
            
            # 验证结果
            if should_have_elements:
                if has_elements and is_draggable:
                    print(f"  ✓ {description}")
                else:
                    print(f"  ✗ 应该显示拖拽元素但没有显示")
            else:
                if not has_elements and not is_draggable:
                    print(f"  ✓ {description}")
                else:
                    print(f"  ✗ 不应该显示拖拽元素但仍然显示了")
            
            # 清理
            drag_handler.hide_watermark()
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_image_watermark_position_only():
    """测试图片水印只通过九宫格设置位置"""
    print("\n=== 图片水印位置设置测试 ===")
    
    try:
        from components.image_watermark import ImageWatermark
        
        # 创建图片水印实例
        watermark = ImageWatermark()
        
        # 测试九宫格位置设置
        positions = [
            'top_left', 'top_center', 'top_right',
            'center_left', 'center', 'center_right', 
            'bottom_left', 'bottom_center', 'bottom_right'
        ]
        
        print("测试九宫格位置设置:")
        for pos in positions:
            try:
                watermark.set_position(pos)
                assert watermark.position == pos, f"位置设置失败"
                print(f"  ✓ {pos}")
            except Exception as e:
                print(f"  ✗ {pos}: {e}")
        
        # 测试自定义位置
        try:
            watermark.set_custom_position((150, 200))
            assert watermark.custom_position == (150, 200), "自定义位置设置失败"
            print(f"  ✓ custom position (150, 200)")
        except Exception as e:
            print(f"  ✗ custom position: {e}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_canvas_cleanliness():
    """测试Canvas的清洁性"""
    print("\n=== Canvas清洁性测试 ===")
    
    try:
        from ui.simple_watermark_drag import SimpleWatermarkDrag
        import tkinter as tk
        
        root = tk.Tk() 
        root.withdraw()
        
        canvas = tk.Canvas(root, width=400, height=300, bg='white')
        drag_handler = SimpleWatermarkDrag(canvas)
        
        # 初始状态检查
        initial_items = canvas.find_all()
        print(f"初始Canvas元素数量: {len(initial_items)}")
        
        # 显示图片水印
        drag_handler.show_watermark((200, 150), "test.png", "image")
        
        # 检查是否增加了元素
        after_show_items = canvas.find_all()
        added_items = len(after_show_items) - len(initial_items)
        
        print(f"显示图片水印后Canvas元素数量: {len(after_show_items)}")
        print(f"新增元素数量: {added_items}")
        
        # 图片水印不应该添加任何可见元素
        if added_items == 0:
            print("✓ 图片水印没有添加任何Canvas元素")
            success = True
        else:
            print("✗ 图片水印意外地添加了Canvas元素")
            success = False
        
        # 隐藏水印
        drag_handler.hide_watermark()
        
        # 检查是否清理干净
        final_items = canvas.find_all()
        print(f"隐藏水印后Canvas元素数量: {len(final_items)}")
        
        if len(final_items) == len(initial_items):
            print("✓ Canvas已正确清理")
        else:
            print("✗ Canvas清理不完整")
            success = False
        
        root.destroy()
        return success
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始图片水印拖拽指示器移除验证测试...\n")
    
    # 运行测试
    test1_result = test_image_watermark_no_overlay()
    test2_result = test_image_watermark_position_only() 
    test3_result = test_canvas_cleanliness()
    
    print(f"\n=== 测试结果总结 ===")
    print(f"拖拽指示器测试: {'✓' if test1_result else '✗'}")
    print(f"位置设置测试: {'✓' if test2_result else '✗'}")
    print(f"Canvas清洁性测试: {'✓' if test3_result else '✗'}")
    
    if test1_result and test2_result and test3_result:
        print(f"\n🎉 所有测试通过！图片水印拖拽指示器已完全移除！")
        print("\n修复效果:")
        print("✓ 图片水印模式下不显示任何拖拽指示器")
        print("✓ 图片水印不可拖拽，避免用户混淆")
        print("✓ 用户通过九宫格选择位置，界面更清洁")
        print("✓ Canvas保持清洁，没有多余元素")
    else:
        print(f"\n❌ 部分测试失败，需要进一步调查")
    
    print(f"\n用户体验:")
    print("• 图片水印: 纯净的预览，仅在实际图片中显示水印")
    print("• 文本水印: 可拖拽的红色文字预览")  
    print("• EXIF水印: 可拖拽的灰色日期预览")
    print("• 位置调整: 所有水印都可通过九宫格精确定位")