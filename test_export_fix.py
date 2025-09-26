#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试导出功能修复
"""

import sys
import os
import tempfile
from PIL import Image

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_file_conflict_handling():
    """测试文件冲突处理"""
    print("测试文件冲突处理...")
    try:
        from file_manager import ExportManager
        
        export_manager = ExportManager()
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            export_manager.output_folder = temp_dir
            
            # 创建一个已存在的测试文件
            existing_file = os.path.join(temp_dir, 'wm_test.jpg')
            img = Image.new('RGB', (100, 100), 'red')
            img.save(existing_file)
            
            print(f"创建已存在文件: {os.path.basename(existing_file)}")
            
            # 测试生成新文件名（应该避免冲突）
            new_path1 = export_manager.generate_filename('/path/to/test.jpg')
            new_path2 = export_manager.generate_filename('/path/to/test.jpg')
            new_path3 = export_manager.generate_filename('/path/to/test.jpg')
            
            print(f"第一次生成: {os.path.basename(new_path1)}")
            print(f"第二次生成: {os.path.basename(new_path2)}")
            print(f"第三次生成: {os.path.basename(new_path3)}")
            
            # 验证文件名不同
            names = [os.path.basename(p) for p in [new_path1, new_path2, new_path3]]
            if len(set(names)) == len(names):
                print("✅ 文件冲突处理正常工作")
                return True
            else:
                print("❌ 文件冲突处理失败")
                return False
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_export_functionality():
    """测试导出功能"""
    print("\n测试导出功能...")
    try:
        from file_manager import ExportManager
        
        export_manager = ExportManager()
        
        # 创建临时目录和测试图片
        with tempfile.TemporaryDirectory() as temp_dir:
            export_manager.output_folder = temp_dir
            
            # 创建测试图片
            test_img = Image.new('RGB', (200, 200), 'blue')
            
            # 模拟原始文件路径
            original_path = "/path/to/test_image.jpg"
            
            # 测试导出
            success = export_manager.export_single_image(original_path, test_img)
            
            if success:
                # 检查文件是否创建
                files = os.listdir(temp_dir)
                if files:
                    print(f"✅ 成功导出文件: {files[0]}")
                    return True
                else:
                    print("❌ 导出失败：没有创建文件")
                    return False
            else:
                print("❌ 导出函数返回失败")
                return False
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("导出功能修复验证")
    print("=" * 50)
    
    # 测试文件冲突处理
    conflict_test = test_file_conflict_handling()
    
    # 测试导出功能
    export_test = test_export_functionality()
    
    print("\n" + "=" * 50)
    if conflict_test and export_test:
        print("🎉 所有测试通过！导出功能修复成功")
        print("\n现在可以正常使用导出功能了：")
        print("1. 选择输出文件夹")
        print("2. 点击'导出图片'按钮")
        print("3. 如果文件已存在，会自动添加数字后缀避免冲突")
    else:
        print("❌ 部分测试失败，请检查代码")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
