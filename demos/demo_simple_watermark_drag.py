#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的水印拖拽功能演示程序
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
        colors = [
            ('red', '红色'),
            ('green', '绿色'), 
            ('blue', '蓝色'),
            ('yellow', '黄色'),
            ('purple', '紫色')
        ]
        
        for i, (color, name) in enumerate(colors):
            img_path = os.path.join(temp_dir, f"demo_{i+1}_{name}.jpg")
            img = Image.new('RGB', (400, 300), color)
            img.save(img_path, 'JPEG')
            demo_images.append(img_path)
            print(f"创建演示图片: {img_path}")
    
    return demo_images

def main():
    """主函数"""
    print("=" * 70)
    print("图片水印工具 - 简化水印拖拽功能演示")
    print("=" * 70)
    print()
    print("🎯 水印拖拽功能：")
    print("1. 导入图片后，水印会显示红色边框")
    print("2. 鼠标悬停在水印上时，光标变成手型")
    print("3. 点击并拖拽红色边框调整水印位置")
    print("4. 支持9种预设位置 + 手动拖拽调整")
    print("5. 可以开关拖拽功能")
    print()
    print("🎨 使用步骤：")
    print("1. 点击'导入图片'按钮选择图片")
    print("2. 在控制面板设置水印文本（如：'测试水印'）")
    print("3. 在预览区域拖拽红色水印框调整位置")
    print("4. 使用'启用拖拽调整'开关控制功能")
    print("5. 点击'导出图片'保存结果")
    print()
    
    # 创建演示图片
    demo_images = create_demo_images()
    
    print("📁 演示图片已创建，位置：")
    for img_path in demo_images:
        print(f"   {img_path}")
    print()
    print("🚀 启动应用程序...")
    print("请尝试水印拖拽功能！")
    print()
    
    try:
        from main import WatermarkApp
        app = WatermarkApp()
        
        print("✅ 应用程序已启动！")
        print("现在您可以：")
        print("- 导入图片查看水印预览")
        print("- 拖拽红色边框调整水印位置")
        print("- 使用控制面板开关拖拽功能")
        print("- 设置不同的水印样式和效果")
        print()
        print("💡 提示：")
        print("- 水印会显示红色边框，这是正常现象")
        print("- 鼠标悬停在水印上时，光标会变成手型")
        print("- 可以随时开关拖拽功能")
        print()
        print("按 Ctrl+C 退出程序")
        
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 演示结束，感谢使用！")
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")

if __name__ == "__main__":
    main()



