#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板系统增强功能演示
展示新的高级功能模板的使用方法
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def demo_template_features():
    """演示模板功能"""
    print("🎯 模板系统增强功能演示")
    print("=" * 50)
    
    from src.components.template_manager import TemplateManager
    
    # 初始化管理器
    manager = TemplateManager()
    
    print("\n📋 可用的增强模板:")
    templates = manager.get_template_list()
    enhanced_templates = []
    
    for template_name in templates:
        template = manager.load_template(template_name)
        if template and hasattr(template, 'advanced_settings') and template.advanced_settings:
            enhanced_templates.append(template_name)
            print(f"  ✨ {template_name}")
            print(f"     {template.description}")
    
    if not enhanced_templates:
        print("  ⚠️  未找到增强模板")
        return
    
    print(f"\n🔍 详细功能对比:")
    print(f"{'模板名称':<15} {'质量':<6} {'尺寸调整':<12} {'旋转角度':<8} {'命名方式'}")
    print("-" * 70)
    
    for template_name in enhanced_templates:
        template = manager.load_template(template_name)
        if template:
            # 获取导出设置
            export_settings = getattr(template, 'export_settings', {})
            advanced_settings = getattr(template, 'advanced_settings', {})
            
            quality = export_settings.get('quality', 'N/A')
            resize_option = export_settings.get('resize_settings', {}).get('resize_option', 'none')
            rotation = advanced_settings.get('rotation_angle', 0)
            naming = export_settings.get('naming', 'original')
            
            print(f"{template_name:<15} {quality!s:<6} {resize_option:<12} {rotation!s:>6}° {naming}")
    
    print(f"\n🎨 使用场景推荐:")
    scenarios = [
        ("高级功能演示", "🔬 功能测试", "体验所有新功能，学习使用方法"),
        ("专业输出", "📸 专业摄影", "需要最高质量的专业用途"),
        ("社交媒体优化", "📱 社交分享", "快速优化用于社交媒体发布")
    ]
    
    for template_name, icon_desc, usage in scenarios:
        if template_name in enhanced_templates:
            print(f"  {icon_desc}: {template_name}")
            print(f"    💡 {usage}")

def demo_template_comparison():
    """对比新旧模板功能"""
    print(f"\n📊 新旧模板功能对比:")
    print("=" * 50)
    
    from src.components.template_manager import TemplateManager
    manager = TemplateManager()
    
    # 分类模板
    all_templates = manager.get_template_list()
    enhanced_templates = []
    legacy_templates = []
    
    for template_name in all_templates:
        template = manager.load_template(template_name)
        if template:
            if hasattr(template, 'advanced_settings') and template.advanced_settings:
                enhanced_templates.append(template_name)
            else:
                legacy_templates.append(template_name)
    
    print(f"\n📈 增强模板 ({len(enhanced_templates)}个):")
    for template_name in enhanced_templates:
        template = manager.load_template(template_name)
        version = getattr(template, 'advanced_settings', {}).get('version', '1.0')
        features = list(getattr(template, 'advanced_settings', {}).get('feature_flags', {}).keys())
        print(f"  ✨ {template_name} (v{version}) - 功能: {', '.join(features)}")
    
    print(f"\n📜 传统模板 ({len(legacy_templates)}个):")
    for template_name in legacy_templates:
        print(f"  📋 {template_name} - 基础功能")
    
    print(f"\n🆙 升级建议:")
    if legacy_templates:
        print(f"  1. 加载传统模板 → 调整高级设置 → 另存为新模板")
        print(f"  2. 参考增强模板的设置，升级现有工作流程")
        print(f"  3. 根据使用场景选择合适的预设模板")
    else:
        print(f"  🎉 所有模板都已升级到最新版本！")

def demo_migration_guide():
    """迁移指南"""
    print(f"\n🚀 模板升级迁移指南:")
    print("=" * 50)
    
    steps = [
        ("1. 备份现有模板", "确保数据安全，建议备份 templates/ 目录"),
        ("2. 测试新功能", "使用'高级功能演示'模板熟悉新界面"),
        ("3. 更新工作流程", "根据需求调整质量、尺寸、旋转设置"),
        ("4. 创建新模板", "将常用设置保存为新的增强模板"),
        ("5. 设置默认模板", "选择最常用的模板作为默认加载")
    ]
    
    for step, description in steps:
        print(f"  {step}")
        print(f"    💡 {description}")
        print()

def demo_best_practices():
    """最佳实践"""
    print(f"\n💎 模板使用最佳实践:")
    print("=" * 50)
    
    practices = [
        ("🎯 针对性创建", "为不同用途创建专门的模板（打印、网络、社交媒体）"),
        ("📝 详细命名", "使用清晰的模板名称和描述，便于识别"),
        ("⚡ 质量平衡", "根据用途选择合适的JPEG质量（网络78-85%，打印90-98%）"),
        ("📐 尺寸优化", "根据目标平台选择合适的尺寸调整方式"),
        ("🔄 角度统一", "在同一批次处理中使用一致的旋转角度"),
        ("🔄 定期更新", "根据使用反馈定期优化模板设置"),
        ("📋 模板文档", "为重要模板创建使用说明")
    ]
    
    for title, description in practices:
        print(f"  {title}")
        print(f"    {description}")
        print()

if __name__ == "__main__":
    try:
        demo_template_features()
        demo_template_comparison()
        demo_migration_guide()
        demo_best_practices()
        
        print(f"\n" + "="*50)
        print(f"🎉 模板系统演示完成！")
        print(f"💡 提示: 启动主程序后可在界面中体验这些新功能")
        print(f"="*50)
        
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()