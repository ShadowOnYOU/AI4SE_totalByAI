#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板系统安全性测试
测试在没有初始化高级功能UI的情况下保存模板
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.template_manager import WatermarkTemplate, TemplateManager
from src.components.text_watermark import TextWatermark
from src.components.image_watermark import ImageWatermark
from src.components.exif_text_watermark import ExifTextWatermark

class SimpleMainWindow:
    """简化版主窗口，用于测试模板系统"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("模板系统安全性测试")
        self.root.geometry("600x400")
        
        # 初始化水印组件
        self.current_watermark = TextWatermark()
        self.current_image_watermark = ImageWatermark()
        self.current_exif_watermark = ExifTextWatermark()
        
        # 设置水印类型（但不初始化高级功能UI变量）
        self.watermark_type = "text"
        
        # 初始化模板管理器
        self.template_manager = TemplateManager()
        
        self.create_ui()
    
    def create_ui(self):
        """创建简单的UI"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="模板系统安全性测试", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 说明文本
        info_text = """
此测试验证在没有初始化高级功能UI变量的情况下：
1. 保存模板是否会出错
2. 加载模板是否会出错
3. 模板系统是否具有向后兼容性
        """
        info_label = ttk.Label(main_frame, text=info_text, justify='left')
        info_label.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky='w')
        
        # 测试按钮
        test1_btn = ttk.Button(main_frame, text="测试1: 保存基础模板", 
                              command=self.test_save_basic_template)
        test1_btn.grid(row=2, column=0, padx=(0, 10), pady=5, sticky='ew')
        
        test2_btn = ttk.Button(main_frame, text="测试2: 加载高级模板", 
                              command=self.test_load_advanced_template)
        test2_btn.grid(row=2, column=1, padx=(10, 0), pady=5, sticky='ew')
        
        test3_btn = ttk.Button(main_frame, text="测试3: 模板列表", 
                              command=self.test_template_list)
        test3_btn.grid(row=3, column=0, pady=5, sticky='ew')
        
        test4_btn = ttk.Button(main_frame, text="测试4: 清理测试模板", 
                              command=self.test_cleanup)
        test4_btn.grid(row=3, column=1, padx=(10, 0), pady=5, sticky='ew')
        
        # 结果显示区域
        self.result_text = tk.Text(main_frame, height=15, width=70)
        self.result_text.grid(row=4, column=0, columnspan=2, pady=(20, 0), sticky='nsew')
        
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.grid(row=4, column=2, sticky='ns', pady=(20, 0))
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # 配置网格权重
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def log(self, message):
        """记录日志"""
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.root.update()
    
    def test_save_basic_template(self):
        """测试保存基础模板（没有高级功能UI变量）"""
        self.log("=== 测试1: 保存基础模板 ===")
        
        try:
            # 创建模板（模拟保存模板对话框的回调）
            def get_current_watermark_callback(name, description):
                template = WatermarkTemplate(name, description)
                template.watermark_type = self.watermark_type
                template.text_settings = self.current_watermark.get_watermark_info()
                template.image_settings = self.current_image_watermark.get_watermark_info()
                template.exif_settings = self.current_exif_watermark.get_watermark_info()
                
                # 新增：保存高级功能设置（安全访问）
                template.export_settings = {
                    'format': getattr(self, 'format_var', tk.StringVar()).get() if hasattr(self, 'format_var') else 'jpg',
                    'naming': getattr(self, 'naming_var', tk.StringVar()).get() if hasattr(self, 'naming_var') else 'original',
                    'prefix': getattr(self, 'prefix_var', tk.StringVar()).get() if hasattr(self, 'prefix_var') else '',
                    'suffix': getattr(self, 'suffix_var', tk.StringVar()).get() if hasattr(self, 'suffix_var') else '',
                    'quality': getattr(self, 'quality_var', tk.IntVar()).get() if hasattr(self, 'quality_var') else 95,
                    'resize_settings': {
                        'resize_option': getattr(self, 'resize_var', tk.StringVar()).get() if hasattr(self, 'resize_var') else 'none',
                        'width': getattr(self, 'width_var', tk.IntVar()).get() if hasattr(self, 'width_var') and getattr(self, 'width_var', tk.IntVar()).get() else 800,
                        'height': getattr(self, 'height_var', tk.IntVar()).get() if hasattr(self, 'height_var') and getattr(self, 'height_var', tk.IntVar()).get() else 600,
                        'percent': getattr(self, 'percent_var', tk.IntVar()).get() if hasattr(self, 'percent_var') and getattr(self, 'percent_var', tk.IntVar()).get() else 100
                    }
                }
                
                template.advanced_settings = {
                    'rotation_angle': getattr(self, 'rotation_var', tk.IntVar()).get() if hasattr(self, 'rotation_var') else 0,
                    'version': '1.1',  # 版本标识，便于后续升级
                    'feature_flags': {
                        'quality_control': hasattr(self, 'quality_var'),
                        'resize_options': hasattr(self, 'resize_var'),
                        'rotation_support': hasattr(self, 'rotation_var')
                    }
                }
                
                return template
            
            # 创建并保存测试模板
            template = get_current_watermark_callback("安全性测试模板", "测试在没有高级UI的情况下保存模板")
            
            success = self.template_manager.save_template(template)
            if success:
                self.log("✅ 成功保存基础模板")
                self.log(f"   - 模板名: {template.name}")
                self.log(f"   - 导出设置: {template.export_settings}")
                self.log(f"   - 高级设置: {template.advanced_settings}")
            else:
                self.log("❌ 保存基础模板失败")
                
        except Exception as e:
            self.log(f"❌ 保存基础模板时发生异常: {e}")
            import traceback
            self.log(traceback.format_exc())
    
    def test_load_advanced_template(self):
        """测试加载高级模板"""
        self.log("\n=== 测试2: 加载高级模板 ===")
        
        try:
            # 尝试加载高级功能演示模板
            template = self.template_manager.load_template("高级功能演示")
            
            if template:
                self.log("✅ 成功加载高级模板")
                self.log(f"   - 模板名: {template.name}")
                self.log(f"   - 水印类型: {template.watermark_type}")
                
                # 检查高级设置
                if hasattr(template, 'export_settings'):
                    self.log(f"   - 导出格式: {template.export_settings.get('format', 'N/A')}")
                    self.log(f"   - 质量设置: {template.export_settings.get('quality', 'N/A')}")
                
                if hasattr(template, 'advanced_settings'):
                    self.log(f"   - 旋转角度: {template.advanced_settings.get('rotation_angle', 'N/A')}")
                    self.log(f"   - 模板版本: {template.advanced_settings.get('version', 'N/A')}")
                
                # 测试应用模板设置（模拟）
                self.apply_template_safe(template)
                self.log("✅ 成功应用模板设置")
            else:
                self.log("❌ 加载高级模板失败")
                
        except Exception as e:
            self.log(f"❌ 加载高级模板时发生异常: {e}")
            import traceback
            self.log(traceback.format_exc())
    
    def apply_template_safe(self, template):
        """安全地应用模板设置"""
        try:
            # 应用基础设置
            if template.text_settings:
                self.current_watermark.load_from_dict(template.text_settings)
            
            if template.image_settings:
                self.current_image_watermark.load_from_dict(template.image_settings)
            
            if template.exif_settings:
                self.current_exif_watermark.load_from_dict(template.exif_settings)
            
            # 安全地应用高级设置
            if hasattr(template, 'export_settings') and template.export_settings:
                self.log("   - 尝试应用导出设置（跳过，UI未初始化）")
            
            if hasattr(template, 'advanced_settings') and template.advanced_settings:
                self.log("   - 尝试应用高级设置（跳过，UI未初始化）")
            
        except Exception as e:
            self.log(f"   应用模板设置时出错: {e}")
    
    def test_template_list(self):
        """测试获取模板列表"""
        self.log("\n=== 测试3: 模板列表 ===")
        
        try:
            templates = self.template_manager.get_template_list()
            self.log(f"✅ 找到 {len(templates)} 个模板:")
            
            for template_name in templates:
                info = self.template_manager.get_template_info(template_name)
                if info:
                    self.log(f"   - {template_name}: {info.get('watermark_type', 'unknown')}")
                else:
                    self.log(f"   - {template_name}: 信息获取失败")
                    
        except Exception as e:
            self.log(f"❌ 获取模板列表时发生异常: {e}")
    
    def test_cleanup(self):
        """清理测试模板"""
        self.log("\n=== 测试4: 清理测试模板 ===")
        
        try:
            success = self.template_manager.delete_template("安全性测试模板")
            if success:
                self.log("✅ 成功删除测试模板")
            else:
                self.log("❌ 删除测试模板失败（可能不存在）")
                
        except Exception as e:
            self.log(f"❌ 删除测试模板时发生异常: {e}")
    
    def run(self):
        """运行测试"""
        self.log("模板系统安全性测试启动")
        self.log("测试目标：验证在没有高级功能UI的情况下模板系统的稳定性")
        self.log("点击测试按钮开始测试...\n")
        
        self.root.mainloop()

if __name__ == "__main__":
    print("启动模板系统安全性测试...")
    app = SimpleMainWindow()
    app.run()