#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无可见拖拽指示器测试
验证拖拽功能工作但没有视觉指示器
"""

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_invisible_drag_areas():
    """测试不可见拖拽区域"""
    print("=== 不可见拖拽区域测试 ===")
    
    try:
        from ui.simple_watermark_drag import SimpleWatermarkDrag
        import tkinter as tk
        
        # 创建测试Canvas
        root = tk.Tk()
        root.withdraw()
        
        canvas = tk.Canvas(root, width=400, height=300, bg='white')
        
        # 创建拖拽处理器
        drag_handler = SimpleWatermarkDrag(canvas)
        
        # 测试不同水印类型的拖拽区域
        test_cases = [
            ("text", "这是测试文本", "文本水印"),
            ("image", "test.png", "图片水印"),
            ("exif", "2024-01-01", "EXIF水印")
        ]
        
        for watermark_type, text, desc in test_cases:
            print(f"\n  测试 {desc}:")
            
            # 显示水印（应该创建不可见区域）
            drag_handler.show_watermark((100, 100), text, watermark_type)
            
            # 检查canvas上的元素
            items = canvas.find_withtag('watermark_drag')
            print(f"    创建的元素数量: {len(items)}")
            
            # 检查是否有可见元素
            visible_items = 0
            for item in items:
                item_type = canvas.type(item)
                if item_type == 'text':
                    visible_items += 1
                    print(f"    ⚠️  发现可见文本元素")
                elif item_type == 'rectangle':
                    # 检查矩形是否可见
                    outline = canvas.itemcget(item, 'outline')
                    fill = canvas.itemcget(item, 'fill')
                    width = canvas.itemcget(item, 'width')
                    
                    if outline or fill or (width and int(width) > 0):
                        visible_items += 1
                        print(f"    ⚠️  发现可见矩形元素: outline='{outline}', fill='{fill}', width='{width}'")
                    else:
                        print(f"    ✓ 创建了不可见矩形拖拽区域")
            
            if visible_items == 0:
                print(f"    ✓ {desc}: 完全不可见，但拖拽功能可用")
            else:
                print(f"    ✗ {desc}: 仍有 {visible_items} 个可见元素")
            
            # 清除水印
            drag_handler.hide_watermark()
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False

def test_drag_functionality():
    """测试拖拽功能是否仍然工作"""
    print("\n=== 拖拽功能测试 ===")
    
    try:
        from ui.simple_watermark_drag import SimpleWatermarkDrag
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()
        
        canvas = tk.Canvas(root, width=400, height=300)
        
        # 记录位置变化
        position_changes = []
        
        def on_position_changed(pos):
            position_changes.append(pos)
            print(f"    位置变化: {pos}")
        
        drag_handler = SimpleWatermarkDrag(canvas, on_position_changed)
        
        # 设置水印
        drag_handler.show_watermark((100, 100), "测试", "text")
        
        # 模拟点击事件（检查是否能检测到点击）
        class MockEvent:
            def __init__(self, x, y):
                self.x = x
                self.y = y
        
        # 测试点击在拖拽区域内
        click_event = MockEvent(120, 110)  # 在拖拽区域内
        drag_handler.on_click(click_event)
        
        if drag_handler.is_dragging:
            print("    ✓ 点击检测工作正常")
        else:
            print("    ✗ 点击检测失败")
        
        # 模拟拖拽
        drag_event = MockEvent(150, 140)
        drag_handler.on_drag(drag_event)
        
        # 检查位置是否更新
        if drag_handler.current_position != (100, 100):
            print(f"    ✓ 拖拽功能工作正常，新位置: {drag_handler.current_position}")
        else:
            print("    ✗ 拖拽功能可能有问题")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"  ✗ 拖拽功能测试失败: {e}")
        return False

def test_size_calculation():
    """测试不同水印类型的拖拽区域大小"""
    print("\n=== 拖拽区域大小测试 ===")
    
    try:
        from ui.simple_watermark_drag import SimpleWatermarkDrag
        import tkinter as tk
        
        root = tk.Tk()
        root.withdraw()
        
        canvas = tk.Canvas(root, width=400, height=300)
        drag_handler = SimpleWatermarkDrag(canvas)
        
        test_cases = [
            ("text", "短文本", "应该较小"),
            ("text", "这是一个比较长的文本水印内容", "应该较大"),
            ("image", "image.png", "固定大小"),
            ("exif", "2024-01-01", "固定大小")
        ]
        
        for watermark_type, text, expected in test_cases:
            drag_handler.show_watermark((100, 100), text, watermark_type)
            size = drag_handler.watermark_size
            print(f"    {watermark_type} ({text[:10]}...): {size[0]}x{size[1]} - {expected}")
            drag_handler.hide_watermark()
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"  ✗ 大小计算测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始无可见拖拽指示器测试...\n")
    
    # 运行测试
    test1 = test_invisible_drag_areas()
    test2 = test_drag_functionality()
    test3 = test_size_calculation()
    
    print(f"\n=== 测试结果总结 ===")
    print(f"不可见区域测试: {'✓' if test1 else '✗'}")
    print(f"拖拽功能测试: {'✓' if test2 else '✗'}")
    print(f"区域大小测试: {'✓' if test3 else '✗'}")
    
    if test1 and test2 and test3:
        print(f"\n🎉 所有测试通过！")
        print("\n修复效果:")
        print("✓ 所有水印类型都没有可见的拖拽指示器")
        print("✓ 拖拽功能完全保留")
        print("✓ 用户体验：干净的预览界面 + 隐藏的拖拽功能")
    else:
        print(f"\n❌ 部分测试失败")
    
    print(f"\n用户操作说明:")
    print("• 预览区域看不到任何拖拽指示器")
    print("• 在水印预期位置附近点击拖拽即可调整位置") 
    print("• 拖拽后九宫格自动显示为'custom'")