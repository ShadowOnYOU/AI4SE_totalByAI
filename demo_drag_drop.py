#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拖拽上传功能演示脚本
"""

import sys
import os
import tempfile
from PIL import Image

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_demo_images():
    """创建演示图片"""
    demo_images = []
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建不同颜色的演示图片
        colors = [
            ('red', '红色'),
            ('green', '绿色'), 
            ('blue', '蓝色'),
            ('yellow', '黄色'),
            ('purple', '紫色')
        ]
        
        for i, (color, name) in enumerate(colors):
            img_path = os.path.join(temp_dir, f"demo_{i+1}_{name}.jpg")
            img = Image.new('RGB', (200, 150), color)
            img.save(img_path, 'JPEG')
            demo_images.append(img_path)
            print(f"创建演示图片: {img_path}")
    
    return demo_images

def demo_drag_drop():
    """演示拖拽功能"""
    print("=" * 60)
    print("图片水印工具 - 拖拽上传功能演示")
    print("=" * 60)
    
    try:
        from main import WatermarkApp
        
        print("1. 启动应用程序...")
        app = WatermarkApp()
        
        print("2. 应用程序已启动，现在您可以：")
        print("   - 将图片文件拖拽到预览区域（中间蓝色区域）")
        print("   - 将图片文件拖拽到图片列表区域（左侧区域）")
        print("   - 或者点击'导入图片'按钮选择文件")
        print()
        print("3. 创建了以下演示图片供您测试：")
        
        # 创建演示图片
        demo_images = create_demo_images()
        
        print()
        print("4. 拖拽功能说明：")
        print("   - 拖拽区域会显示'拖拽图片文件到此处'提示")
        print("   - 拖拽时区域会变成绿色")
        print("   - 支持同时拖拽多个文件")
        print("   - 自动验证文件格式")
        print("   - 无效文件会显示警告")
        print()
        print("5. 演示图片位置：")
        for img_path in demo_images:
            print(f"   {img_path}")
        print()
        print("请将上述图片文件拖拽到应用程序中进行测试！")
        print("按 Ctrl+C 退出演示")
        
        # 运行应用程序
        app.run()
        
    except KeyboardInterrupt:
        print("\n演示结束")
    except Exception as e:
        print(f"演示过程中出现错误: {e}")

if __name__ == "__main__":
    demo_drag_drop()

