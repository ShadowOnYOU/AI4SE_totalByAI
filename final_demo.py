#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终功能演示程序
展示所有导入图片的方式
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
            img = Image.new('RGB', (200, 150), color)
            img.save(img_path, 'JPEG')
            demo_images.append(img_path)
            print(f"创建演示图片: {img_path}")
    
    return demo_images

def main():
    """主函数"""
    print("=" * 70)
    print("图片水印工具 - 完整功能演示")
    print("=" * 70)
    print()
    print("🎯 图片导入方式：")
    print("1. 点击'导入图片'按钮 - 选择单张或多张图片")
    print("2. 点击'导入文件夹'按钮 - 导入整个文件夹")
    print("3. 双击预览区域 - 快速选择图片文件")
    print("4. 拖拽图片文件到预览区域 - 拖拽上传")
    print("5. 拖拽图片文件到图片列表区域 - 拖拽上传")
    print()
    print("🎨 水印功能：")
    print("- 文本水印：自定义文本、字体、颜色、位置")
    print("- 9种预设位置：左上、中上、右上等")
    print("- 效果设置：阴影、描边、透明度")
    print("- 实时预览：即时查看水印效果")
    print()
    print("📤 导出功能：")
    print("- 支持JPEG和PNG格式")
    print("- 自定义输出文件夹")
    print("- 文件命名规则（前缀/后缀）")
    print("- 批量导出处理")
    print()
    
    # 创建演示图片
    demo_images = create_demo_images()
    
    print("📁 演示图片已创建，位置：")
    for img_path in demo_images:
        print(f"   {img_path}")
    print()
    print("🚀 启动应用程序...")
    print("请尝试上述各种导入方式！")
    print()
    
    try:
        from main import WatermarkApp
        app = WatermarkApp()
        
        print("✅ 应用程序已启动！")
        print("现在您可以：")
        print("- 点击'导入图片'按钮选择文件")
        print("- 双击预览区域选择文件")
        print("- 将演示图片拖拽到预览区域")
        print("- 设置水印参数并预览效果")
        print("- 导出处理后的图片")
        print()
        print("按 Ctrl+C 退出程序")
        
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 演示结束，感谢使用！")
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")

if __name__ == "__main__":
    main()

