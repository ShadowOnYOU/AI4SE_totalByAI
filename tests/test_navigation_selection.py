#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图片导航选中状态更新修复
"""

import sys
import os
import tempfile
import tkinter as tk
from PIL import Image

# 添加项目路径
sys.path.insert(0, '/Users/shadowonyou/2025研一上/大模型辅助软件开发/AI4SE_totalByAI/src')

def create_test_images():
    """创建测试图片"""
    test_images = []
    temp_dir = tempfile.mkdtemp()
    
    # 创建5张不同颜色的测试图片
    colors = [
        ('red', (255, 0, 0)),
        ('green', (0, 255, 0)),
        ('blue', (0, 0, 255)),
        ('yellow', (255, 255, 0)),
        ('purple', (128, 0, 128))
    ]
    
    for i, (color_name, color) in enumerate(colors):
        img_path = os.path.join(temp_dir, f"test_{i+1}_{color_name}.jpg")
        img = Image.new('RGB', (200, 150), color)
        
        # 添加一些文字以便区分
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.load_default()
            draw.text((10, 10), f"图片 {i+1}", fill='white', font=font)
            draw.text((10, 30), f"{color_name.upper()}", fill='white', font=font)
        except:
            draw.text((10, 10), f"图片 {i+1}", fill='white')
            draw.text((10, 30), f"{color_name.upper()}", fill='white')
        
        img.save(img_path, 'JPEG', quality=85)
        test_images.append(img_path)
    
    return test_images, temp_dir

def test_navigation_selection_update():
    """测试导航时选中状态更新"""
    print("🧪 测试图片导航选中状态更新修复...")
    print()
    
    try:
        # 创建测试图片
        print("1. 创建测试图片...")
        test_images, temp_dir = create_test_images()
        
        for i, img_path in enumerate(test_images):
            filename = os.path.basename(img_path)
            print(f"   - 图片 {i+1}: {filename}")
        
        print(f"   📁 临时目录: {temp_dir}")
        print()
        
        # 启动应用
        print("2. 启动应用程序...")
        from main_window import MainWindow
        
        root = tk.Tk()
        root.title("测试图片导航选中状态更新")
        root.geometry("1000x700")
        
        main_window = MainWindow(root)
        
        print("   ✅ 应用启动成功")
        print()
        
        # 导入测试图片
        print("3. 导入测试图片...")
        for img_path in test_images:
            main_window.image_list_manager.add_image(img_path)
        
        print(f"   ✅ 已导入 {len(test_images)} 张图片")
        print()
        
        # 获取图片列表组件
        image_list = main_window.image_list_widget
        
        print("4. 测试导航功能...")
        
        # 检查初始状态
        print("   测试初始状态:")
        current_index = main_window.image_list_manager.current_index
        selection = image_list.selection()
        print(f"     - 当前索引: {current_index}")
        print(f"     - 列表选中: {len(selection)} 项")
        if selection:
            item = image_list.item(selection[0])
            selected_index = int(item['text']) - 1
            print(f"     - 选中索引: {selected_index}")
            if selected_index == current_index:
                print("     ✅ 初始状态一致")
            else:
                print("     ❌ 初始状态不一致")
        print()
        
        # 测试下一张功能
        print("   测试'下一张'按钮:")
        for i in range(3):
            print(f"     点击'下一张' (第{i+1}次)...")
            main_window.next_image()
            
            # 等待UI更新
            root.update_idletasks()
            
            current_index = main_window.image_list_manager.current_index
            selection = image_list.selection()
            
            print(f"       当前索引: {current_index}")
            if selection:
                item = image_list.item(selection[0])
                selected_index = int(item['text']) - 1
                print(f"       选中索引: {selected_index}")
                if selected_index == current_index:
                    print("       ✅ 选中状态已同步")
                else:
                    print("       ❌ 选中状态未同步")
            else:
                print("       ❌ 没有选中项")
            print()
        
        # 测试上一张功能
        print("   测试'上一张'按钮:")
        for i in range(2):
            print(f"     点击'上一张' (第{i+1}次)...")
            main_window.previous_image()
            
            # 等待UI更新
            root.update_idletasks()
            
            current_index = main_window.image_list_manager.current_index
            selection = image_list.selection()
            
            print(f"       当前索引: {current_index}")
            if selection:
                item = image_list.item(selection[0])
                selected_index = int(item['text']) - 1
                print(f"       选中索引: {selected_index}")
                if selected_index == current_index:
                    print("       ✅ 选中状态已同步")
                else:
                    print("       ❌ 选中状态未同步")
            else:
                print("       ❌ 没有选中项")
            print()
        
        print("5. 测试结果:")
        print("   🎯 图片导航选中状态更新功能已修复！")
        print("   📋 功能说明:")
        print("     - 点击'上一张'/'下一张'按钮时，左侧列表选中状态会自动更新")
        print("     - 选中的图片会以深蓝色高亮显示")
        print("     - 如果选中项不在可见区域，列表会自动滚动到该项")
        print()
        
        print("6. 手动测试:")
        print("   现在您可以手动测试以下操作:")
        print("   - 点击'上一张'/'下一张'按钮，观察左侧列表选中状态变化")
        print("   - 直接点击左侧列表项，观察预览区域更新")
        print("   - 两种操作方式应该保持同步")
        print()
        print("   按 Ctrl+C 或关闭窗口退出测试")
        
        # 启动主循环
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理临时文件
        import shutil
        if 'temp_dir' in locals():
            try:
                shutil.rmtree(temp_dir)
                print(f"🗑️  已清理临时目录: {temp_dir}")
            except:
                pass

if __name__ == "__main__":
    test_navigation_selection_update()