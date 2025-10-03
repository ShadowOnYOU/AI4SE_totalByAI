#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件命名规则功能
"""

import sys
import os
import tempfile
from PIL import Image

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, os.path.join(src_dir, 'components'))

def test_naming_rules():
    """测试文件命名规则"""
    print("=== 测试文件命名规则 ===\n")
    
    try:
        # 导入组件
        from file_manager import ExportManager
        from main_window import MainWindow
        
        # 创建导出管理器实例
        export_manager = ExportManager()
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            export_manager.output_folder = temp_dir
            print(f"输出目录: {temp_dir}")
            
            # 测试原始图片路径
            test_paths = [
                "/Users/test/vacation.jpg",
                "/Users/test/研究生校园卡.png",
                "/Users/test/family_photo.jpeg"
            ]
            
            # 测试不同的命名规则
            naming_tests = [
                {
                    "name": "保留原文件名",
                    "settings": {
                        'format': 'jpg',
                        'filename_prefix': '',
                        'filename_suffix': ''
                    },
                    "expected_pattern": "原文件名.jpg"
                },
                {
                    "name": "添加前缀",
                    "settings": {
                        'format': 'jpg',
                        'filename_prefix': 'wm_',
                        'filename_suffix': ''
                    },
                    "expected_pattern": "wm_原文件名.jpg"
                },
                {
                    "name": "添加后缀",
                    "settings": {
                        'format': 'png',
                        'filename_prefix': '',
                        'filename_suffix': '_watermarked'
                    },
                    "expected_pattern": "原文件名_watermarked.png"
                },
                {
                    "name": "前缀+后缀",
                    "settings": {
                        'format': 'jpg',
                        'filename_prefix': 'processed_',
                        'filename_suffix': '_final'
                    },
                    "expected_pattern": "processed_原文件名_final.jpg"
                }
            ]
            
            # 执行测试
            for test in naming_tests:
                print(f"\n--- 测试: {test['name']} ---")
                print(f"预期格式: {test['expected_pattern']}")
                
                # 更新导出设置
                export_manager.update_export_settings(test['settings'])
                
                # 测试每个文件路径
                for test_path in test_paths:
                    original_name = os.path.splitext(os.path.basename(test_path))[0]
                    
                    # 生成输出文件名
                    output_path = export_manager.generate_filename(test_path)
                    output_filename = os.path.basename(output_path)
                    
                    print(f"  输入: {os.path.basename(test_path)}")
                    print(f"  输出: {output_filename}")
                    
                    # 验证命名规则
                    prefix = test['settings']['filename_prefix']
                    suffix = test['settings']['filename_suffix']
                    ext = f".{test['settings']['format']}"
                    
                    expected_name = f"{prefix}{original_name}{suffix}{ext}"
                    
                    if output_filename == expected_name:
                        print(f"  ✅ 命名正确")
                    else:
                        print(f"  ❌ 命名错误，期望: {expected_name}")
                        return False
            
            print("\n🎉 所有命名规则测试通过！")
            return True
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_conflict_handling():
    """测试文件冲突处理"""
    print("\n=== 测试文件冲突处理 ===\n")
    
    try:
        from file_manager import ExportManager
        
        export_manager = ExportManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            export_manager.output_folder = temp_dir
            
            # 设置命名规则
            export_manager.update_export_settings({
                'format': 'jpg',
                'filename_prefix': 'test_',
                'filename_suffix': '_output'
            })
            
            # 创建一个已存在的文件
            existing_file = os.path.join(temp_dir, "test_sample_output.jpg")
            with open(existing_file, 'w') as f:
                f.write("existing content")
            
            print(f"已存在文件: {os.path.basename(existing_file)}")
            
            # 测试冲突处理
            test_path = "/path/to/sample.jpg"
            new_path = export_manager.generate_filename(test_path)
            new_filename = os.path.basename(new_path)
            
            print(f"生成新文件名: {new_filename}")
            
            # 验证新文件名与原文件不同
            if new_filename != "test_sample_output.jpg":
                print("✅ 文件冲突处理正确，生成了不同的文件名")
                return True
            else:
                print("❌ 文件冲突处理失败，生成了相同的文件名")
                return False
                
    except Exception as e:
        print(f"❌ 文件冲突测试失败: {e}")
        return False

def test_full_export_process():
    """测试完整导出流程"""
    print("\n=== 测试完整导出流程 ===\n")
    
    try:
        from file_manager import ExportManager
        
        export_manager = ExportManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            export_manager.output_folder = temp_dir
            
            # 设置导出参数
            export_manager.update_export_settings({
                'format': 'png',
                'quality': 95,
                'filename_prefix': 'exported_',
                'filename_suffix': '_final'
            })
            
            # 创建测试图片
            test_image = Image.new('RGB', (300, 200), 'lightgreen')
            
            # 模拟原始文件路径
            original_path = "/Users/test/demo_image.jpg"
            
            # 执行导出
            print(f"导出图片: {os.path.basename(original_path)}")
            success = export_manager.export_single_image(original_path, test_image)
            
            if success:
                # 检查导出的文件
                files = os.listdir(temp_dir)
                if files:
                    exported_file = files[0]
                    print(f"✅ 导出成功: {exported_file}")
                    
                    # 验证文件名格式
                    expected_name = "exported_demo_image_final.png"
                    if exported_file == expected_name:
                        print("✅ 文件名格式正确")
                        return True
                    else:
                        print(f"❌ 文件名格式错误，期望: {expected_name}")
                        return False
                else:
                    print("❌ 没有找到导出的文件")
                    return False
            else:
                print("❌ 导出失败")
                return False
                
    except Exception as e:
        print(f"❌ 完整导出测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试文件命名规则功能...")
    print("=" * 50)
    
    # 执行各项测试
    test1 = test_naming_rules()
    test2 = test_file_conflict_handling()
    test3 = test_full_export_process()
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"文件命名规则测试: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"文件冲突处理测试: {'✅ 通过' if test2 else '❌ 失败'}")
    print(f"完整导出流程测试: {'✅ 通过' if test3 else '❌ 失败'}")
    
    if test1 and test2 and test3:
        print("\n🎉 所有测试通过！文件命名规则功能实现成功")
        print("\n现在可以使用的功能:")
        print("1. 保留原文件名")
        print("2. 添加自定义前缀（如 wm_）")
        print("3. 添加自定义后缀（如 _watermarked）")
        print("4. 同时使用前缀和后缀")
        print("5. 自动处理文件名冲突")
        print("6. 支持中文文件名")
    else:
        print("\n❌ 部分测试失败，请检查代码")
    
    print("=" * 50)

if __name__ == "__main__":
    main()