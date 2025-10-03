#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强模板系统
验证新的高级功能模板是否正常工作
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.template_manager import TemplateManager, WatermarkTemplate

def test_enhanced_templates():
    """测试增强的模板系统"""
    print("🚀 开始测试增强模板系统...")
    
    # 初始化模板管理器
    template_manager = TemplateManager()
    print(f"✅ 模板管理器初始化完成，模板目录: {template_manager.templates_dir}")
    
    # 测试加载新模板
    test_templates = [
        "高级功能演示",
        "专业输出", 
        "社交媒体优化"
    ]
    
    for template_name in test_templates:
        print(f"\n📋 测试模板: {template_name}")
        
        # 加载模板
        template = template_manager.load_template(template_name)
        if template:
            print(f"  ✅ 模板加载成功")
            print(f"  📝 描述: {template.description}")
            print(f"  🔧 水印类型: {template.watermark_type}")
            
            # 检查导出设置
            if hasattr(template, 'export_settings') and template.export_settings:
                export_settings = template.export_settings
                print(f"  📤 导出设置:")
                print(f"    - 格式: {export_settings.get('format', 'N/A')}")
                print(f"    - 质量: {export_settings.get('quality', 'N/A')}%")
                print(f"    - 命名方式: {export_settings.get('naming', 'N/A')}")
                
                resize_settings = export_settings.get('resize_settings', {})
                if resize_settings:
                    resize_option = resize_settings.get('resize_option', 'none')
                    print(f"    - 尺寸调整: {resize_option}")
                    if resize_option == 'width':
                        print(f"      宽度: {resize_settings.get('width')}px")
                    elif resize_option == 'height':
                        print(f"      高度: {resize_settings.get('height')}px")
                    elif resize_option == 'percent':
                        print(f"      缩放: {resize_settings.get('percent')}%")
            else:
                print(f"  ⚠️  未找到导出设置")
            
            # 检查高级设置
            if hasattr(template, 'advanced_settings') and template.advanced_settings:
                advanced_settings = template.advanced_settings
                print(f"  ⚙️  高级设置:")
                print(f"    - 旋转角度: {advanced_settings.get('rotation_angle', 0)}°")
                print(f"    - 模板版本: {advanced_settings.get('version', '1.0')}")
                
                feature_flags = advanced_settings.get('feature_flags', {})
                if feature_flags:
                    enabled_features = [k for k, v in feature_flags.items() if v]
                    print(f"    - 支持功能: {', '.join(enabled_features)}")
            else:
                print(f"  ⚠️  未找到高级设置")
            
            # 检查文本设置中的旋转角度
            if template.text_settings and 'angle' in template.text_settings:
                text_angle = template.text_settings['angle']
                print(f"  🔄 文本旋转角度: {text_angle}°")
            
        else:
            print(f"  ❌ 模板加载失败")

def test_template_compatibility():
    """测试模板兼容性"""
    print(f"\n🔄 测试模板向后兼容性...")
    
    template_manager = TemplateManager()
    
    # 测试旧版模板
    old_templates = ["1", "2", "粉色"]
    
    for template_name in old_templates:
        print(f"\n📋 测试旧模板: {template_name}")
        
        template = template_manager.load_template(template_name)
        if template:
            print(f"  ✅ 旧模板加载成功")
            
            # 检查是否自动添加了默认的高级设置
            if hasattr(template, 'export_settings'):
                if template.export_settings:
                    print(f"  📤 已有导出设置")
                else:
                    print(f"  📤 导出设置为空（正常，旧模板）")
            
            if hasattr(template, 'advanced_settings'):
                if template.advanced_settings:
                    print(f"  ⚙️  已有高级设置")
                else:
                    print(f"  ⚙️  高级设置为空（正常，旧模板）")
        else:
            print(f"  ❌ 旧模板加载失败")

def test_create_template_with_advanced_features():
    """测试创建包含高级功能的新模板"""
    print(f"\n🆕 测试创建新的高级功能模板...")
    
    # 创建一个包含所有新功能的模板
    template = WatermarkTemplate("测试高级模板", "程序创建的测试模板")
    
    # 设置基本水印属性
    template.watermark_type = "text"
    template.text_settings = {
        "text": "测试水印",
        "font_size": 36,
        "color": "#FF0000",
        "transparency": 80,
        "position": "center",
        "angle": 30,
        "shadow": True,
        "outline": True
    }
    
    # 设置导出功能
    template.export_settings = {
        "format": "jpg",
        "naming": "add_prefix",
        "prefix": "TEST_",
        "suffix": "",
        "quality": 90,
        "resize_settings": {
            "resize_option": "percent",
            "width": 1920,
            "height": 1080, 
            "percent": 75
        }
    }
    
    # 设置高级功能
    template.advanced_settings = {
        "rotation_angle": 30,
        "version": "1.1",
        "feature_flags": {
            "quality_control": True,
            "resize_options": True,
            "rotation_support": True
        }
    }
    
    # 保存模板
    template_manager = TemplateManager()
    success = template_manager.save_template(template)
    
    if success:
        print(f"  ✅ 新模板创建成功")
        
        # 重新加载验证
        loaded_template = template_manager.load_template("测试高级模板")
        if loaded_template:
            print(f"  ✅ 新模板重新加载成功")
            
            # 验证数据完整性
            if (loaded_template.export_settings.get('quality') == 90 and
                loaded_template.advanced_settings.get('rotation_angle') == 30):
                print(f"  ✅ 高级功能数据完整")
            else:
                print(f"  ❌ 高级功能数据不完整")
        else:
            print(f"  ❌ 新模板重新加载失败")
    else:
        print(f"  ❌ 新模板创建失败")

def print_summary():
    """打印测试总结"""
    print(f"\n" + "="*50)
    print(f"📊 模板系统升级总结")
    print(f"="*50)
    print(f"✨ 新增功能:")
    print(f"  1. 📤 导出设置 (export_settings)")
    print(f"     - JPEG质量控制 (0-100%)")
    print(f"     - 文件命名规则")
    print(f"     - 图片尺寸调整选项")
    print(f"  2. ⚙️  高级设置 (advanced_settings)")
    print(f"     - 水印旋转角度")
    print(f"     - 功能标志位")
    print(f"     - 版本兼容性标识")
    print(f"  3. 🔄 向后兼容性")
    print(f"     - 旧模板正常加载")
    print(f"     - 新功能自动初始化")
    print(f"\n💡 使用建议:")
    print(f"  - 使用'高级功能演示'模板体验所有新功能")
    print(f"  - 使用'专业输出'模板获得最佳质量")
    print(f"  - 使用'社交媒体优化'模板快速发布")
    print(f"\n🎯 模板文件位置: templates/ 目录")

if __name__ == "__main__":
    try:
        test_enhanced_templates()
        test_template_compatibility()
        test_create_template_with_advanced_features()
        print_summary()
        
        print(f"\n🎉 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()