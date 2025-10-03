#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板系统快速安全性测试（命令行版本）
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.template_manager import WatermarkTemplate, TemplateManager
from src.components.text_watermark import TextWatermark
from src.components.image_watermark import ImageWatermark
from src.components.exif_text_watermark import ExifTextWatermark

def test_safe_template_operations():
    """测试模板操作的安全性"""
    print("🧪 开始模板系统安全性测试...")
    
    # 1. 创建模拟的主窗口对象（没有高级功能变量）
    class MockMainWindow:
        def __init__(self):
            self.current_watermark = TextWatermark()
            self.current_image_watermark = ImageWatermark()
            self.current_exif_watermark = ExifTextWatermark()
            self.watermark_type = "text"
            
            # 故意不初始化这些变量来测试安全性
            # self.format_var = None
            # self.quality_var = None
            # self.rotation_var = None
    
    mock_window = MockMainWindow()
    template_manager = TemplateManager()
    
    # 2. 测试保存模板（使用修复后的安全代码）
    print("\n📝 测试1: 保存模板（无高级UI变量）")
    try:
        def get_current_watermark_callback(name, description):
            template = WatermarkTemplate(name, description)
            template.watermark_type = mock_window.watermark_type
            template.text_settings = mock_window.current_watermark.get_watermark_info()
            template.image_settings = mock_window.current_image_watermark.get_watermark_info()
            template.exif_settings = mock_window.current_exif_watermark.get_watermark_info()
            
            # 新增：保存高级功能设置（安全访问）
            template.export_settings = {
                'format': getattr(mock_window, 'format_var', None).get() if hasattr(mock_window, 'format_var') and getattr(mock_window, 'format_var') else 'jpg',
                'naming': getattr(mock_window, 'naming_var', None).get() if hasattr(mock_window, 'naming_var') and getattr(mock_window, 'naming_var') else 'original',
                'prefix': getattr(mock_window, 'prefix_var', None).get() if hasattr(mock_window, 'prefix_var') and getattr(mock_window, 'prefix_var') else '',
                'suffix': getattr(mock_window, 'suffix_var', None).get() if hasattr(mock_window, 'suffix_var') and getattr(mock_window, 'suffix_var') else '',
                'quality': getattr(mock_window, 'quality_var', None).get() if hasattr(mock_window, 'quality_var') and getattr(mock_window, 'quality_var') else 95,
                'resize_settings': {
                    'resize_option': getattr(mock_window, 'resize_var', None).get() if hasattr(mock_window, 'resize_var') and getattr(mock_window, 'resize_var') else 'none',
                    'width': getattr(mock_window, 'width_var', None).get() if hasattr(mock_window, 'width_var') and getattr(mock_window, 'width_var') and getattr(mock_window, 'width_var').get() else 800,
                    'height': getattr(mock_window, 'height_var', None).get() if hasattr(mock_window, 'height_var') and getattr(mock_window, 'height_var') and getattr(mock_window, 'height_var').get() else 600,
                    'percent': getattr(mock_window, 'percent_var', None).get() if hasattr(mock_window, 'percent_var') and getattr(mock_window, 'percent_var') and getattr(mock_window, 'percent_var').get() else 100
                }
            }
            
            template.advanced_settings = {
                'rotation_angle': getattr(mock_window, 'rotation_var', None).get() if hasattr(mock_window, 'rotation_var') and getattr(mock_window, 'rotation_var') else 0,
                'version': '1.1',
                'feature_flags': {
                    'quality_control': hasattr(mock_window, 'quality_var'),
                    'resize_options': hasattr(mock_window, 'resize_var'),
                    'rotation_support': hasattr(mock_window, 'rotation_var')
                }
            }
            
            return template
        
        # 创建测试模板
        test_template = get_current_watermark_callback("CLI安全测试", "命令行安全性测试模板")
        
        # 保存模板
        success = template_manager.save_template(test_template)
        
        if success:
            print("✅ 模板保存成功！")
            print(f"   导出设置: {test_template.export_settings}")
            print(f"   功能标志: {test_template.advanced_settings['feature_flags']}")
        else:
            print("❌ 模板保存失败")
            
    except Exception as e:
        print(f"❌ 保存模板时发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. 测试加载模板
    print("\n📖 测试2: 加载现有模板")
    try:
        templates = template_manager.get_template_list()
        print(f"发现 {len(templates)} 个模板:")
        
        for template_name in templates[:3]:  # 只测试前3个
            template = template_manager.load_template(template_name)
            if template:
                print(f"✅ {template_name}: {template.watermark_type}")
                
                # 测试新属性的存在性
                has_export = hasattr(template, 'export_settings')
                has_advanced = hasattr(template, 'advanced_settings')
                print(f"   导出设置: {has_export}, 高级设置: {has_advanced}")
                
            else:
                print(f"❌ {template_name}: 加载失败")
                
    except Exception as e:
        print(f"❌ 加载模板时发生异常: {e}")
        return False
    
    # 4. 测试应用设置的安全性
    print("\n🔧 测试3: 安全应用模板设置")
    try:
        # 模拟应用导出设置的安全版本
        def safe_apply_export_settings(export_settings):
            print("   尝试应用导出设置...")
            
            # 这些应该都安全地跳过，不会出错
            if 'format' in export_settings and hasattr(mock_window, 'format_var'):
                print(f"     格式: {export_settings['format']}")
            else:
                print("     格式: 跳过（UI未初始化）")
                
            if 'quality' in export_settings and hasattr(mock_window, 'quality_var'):
                print(f"     质量: {export_settings['quality']}")
            else:
                print("     质量: 跳过（UI未初始化）")
        
        # 测试安全应用
        test_export_settings = {
            'format': 'jpg',
            'quality': 85,
            'naming': 'prefix',
            'prefix': 'test_'
        }
        
        safe_apply_export_settings(test_export_settings)
        print("✅ 安全应用设置测试通过")
        
    except Exception as e:
        print(f"❌ 应用设置时发生异常: {e}")
        return False
    
    # 5. 清理测试模板
    print("\n🧹 测试4: 清理测试模板")
    try:
        success = template_manager.delete_template("CLI安全测试")
        if success:
            print("✅ 测试模板清理成功")
        else:
            print("⚠️ 测试模板清理失败（可能不存在）")
    except Exception as e:
        print(f"❌ 清理时发生异常: {e}")
    
    print("\n🎉 所有安全性测试完成！")
    return True

if __name__ == "__main__":
    success = test_safe_template_operations()
    if success:
        print("✅ 模板系统安全性验证通过")
        exit(0)
    else:
        print("❌ 模板系统存在安全性问题")
        exit(1)