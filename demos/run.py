#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片水印工具启动脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查依赖包"""
    try:
        import tkinter
        from PIL import Image
        import exifread
        print("✓ 所有依赖包已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("图片水印工具 v1.0")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    try:
        # 导入并运行主程序
        from main import WatermarkApp
        app = WatermarkApp()
        print("✓ 应用程序启动成功")
        app.run()
        return 0
    except Exception as e:
        print(f"✗ 程序启动失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
