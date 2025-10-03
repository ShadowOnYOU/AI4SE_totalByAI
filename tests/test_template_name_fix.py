#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模板名称类型修复
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_template_name_types():
    """测试各种模板名称类型"""
    print("🧪 测试模板名称类型修复...")
    
    try:
        from src.components.template_manager import TemplateManager
        
        manager = TemplateManager()
        
        # 测试各种类型的模板名称
        test_cases = [
            ("字符串", "6"),
            ("整数", 6),
            ("浮点数", 6.0),
            ("None", None),
            ("列表", [6]),
            ("字典", {"name": 6})
        ]
        
        for case_name, template_name in test_cases:
            print(f"\n  测试 {case_name}: {template_name} ({type(template_name)})")
            
            try:
                # 测试get_template_file_path
                print(f"    测试 get_template_file_path...")
                if template_name is None:
                    print(f"      跳过None测试")
                    continue
                    
                file_path = manager.get_template_file_path(template_name)
                print(f"      ✅ 文件路径: {file_path}")
                
                # 测试load_template
                print(f"    测试 load_template...")
                template = manager.load_template(template_name)
                if template:
                    print(f"      ✅ 加载成功: {template.name}")
                else:
                    print(f"      ℹ️  模板不存在（正常）")
                    
            except Exception as e:
                print(f"      ❌ 测试失败: {e}")
        
        print(f"\n🎯 测试真实模板...")
        
        # 测试真实存在的模板
        real_templates = ["1", "2", "6"]  # 这些应该存在
        
        for template_name in real_templates:
            print(f"\n  测试真实模板: {template_name}")
            
            # 测试字符串类型
            try:
                template = manager.load_template(template_name)
                if template:
                    print(f"    ✅ 字符串加载成功")
                else:
                    print(f"    ℹ️  模板不存在")
            except Exception as e:
                print(f"    ❌ 字符串加载失败: {e}")
            
            # 测试整数类型（模拟错误情况）
            try:
                template = manager.load_template(int(template_name))
                if template:
                    print(f"    ✅ 整数加载成功（自动转换）")
                else:
                    print(f"    ℹ️  整数模板不存在")
            except Exception as e:
                print(f"    ❌ 整数加载失败: {e}")
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_template_name_types()