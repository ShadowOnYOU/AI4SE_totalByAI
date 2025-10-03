# -*- coding: utf-8 -*-
"""
水印模板管理模块
处理水印模板的保存、加载和管理
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import Config

class WatermarkTemplate:
    """水印模板类"""
    
    def __init__(self, name: str = "", description: str = ""):
        """初始化模板"""
        self.name = name
        self.description = description
        self.created_time = datetime.now().isoformat()
        self.watermark_type = "text"  # "text", "image", "exif"
        self.text_settings = {}
        self.image_settings = {}
        self.exif_settings = {}
        # 新增：高级功能设置
        self.export_settings = {}
        self.advanced_settings = {}
        self.position_settings = {}
    
    def set_text_watermark(self, text_watermark):
        """设置文本水印"""
        self.watermark_type = "text"
        self.text_settings = text_watermark.get_watermark_info()
    
    def set_image_watermark(self, image_watermark):
        """设置图片水印"""
        self.watermark_type = "image"
        self.image_settings = image_watermark.get_watermark_info()
    
    def set_mixed_watermark(self, text_watermark, image_watermark, watermark_type):
        """设置混合水印设置"""
        self.watermark_type = watermark_type
        self.text_settings = text_watermark.get_watermark_info()
        self.image_settings = image_watermark.get_watermark_info()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'description': self.description,
            'created_time': self.created_time,
            'watermark_type': self.watermark_type,
            'text_settings': self.text_settings,
            'image_settings': self.image_settings,
            'exif_settings': self.exif_settings,
            'position_settings': self.position_settings,
            # 新增：高级功能设置
            'export_settings': self.export_settings,
            'advanced_settings': self.advanced_settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WatermarkTemplate':
        """从字典创建模板"""
        template = cls()
        template.name = data.get('name', '')
        template.description = data.get('description', '')
        template.created_time = data.get('created_time', datetime.now().isoformat())
        template.watermark_type = data.get('watermark_type', 'text')
        template.text_settings = data.get('text_settings', {})
        template.image_settings = data.get('image_settings', {})
        template.exif_settings = data.get('exif_settings', {})
        template.position_settings = data.get('position_settings', {})
        # 新增：高级功能设置（兼容旧模板）
        template.export_settings = data.get('export_settings', {})
        template.advanced_settings = data.get('advanced_settings', {})
        return template


class TemplateManager:
    """模板管理器"""
    
    def __init__(self):
        """初始化模板管理器"""
        self.templates_dir = Config.TEMPLATES_DIR
        self.ensure_templates_dir()
        self.templates: Dict[str, WatermarkTemplate] = {}
        self.load_all_templates()
    
    def ensure_templates_dir(self):
        """确保模板目录存在"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
    
    def get_template_file_path(self, template_name) -> str:
        """获取模板文件路径（安全类型处理）"""
        # 安全转换为字符串，处理各种输入类型
        if isinstance(template_name, str):
            name_str = template_name
        elif isinstance(template_name, (int, float)):
            name_str = str(template_name)
        elif template_name is None:
            raise ValueError("模板名称不能为None")
        else:
            name_str = str(template_name)
        
        # 生成安全的文件名
        safe_name = "".join(c for c in name_str if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_name:
            raise ValueError(f"无效的模板名称: {template_name}")
        
        return os.path.join(self.templates_dir, f"{safe_name}.json")
    
    def save_template(self, template: WatermarkTemplate) -> bool:
        """保存模板"""
        try:
            if not template.name.strip():
                return False
            
            file_path = self.get_template_file_path(template.name)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template.to_dict(), f, ensure_ascii=False, indent=2)
            
            # 更新内存中的模板
            self.templates[template.name] = template
            
            return True
            
        except Exception as e:
            print(f"Save template failed: {e}")
            return False
    
    def load_template(self, template_name) -> Optional[WatermarkTemplate]:
        """加载模板（安全类型处理）"""
        try:
            # 类型安全转换
            if isinstance(template_name, str):
                name_key = template_name
            elif isinstance(template_name, (int, float)):
                name_key = str(template_name)
                print(f"[WARNING] 模板名称为数字类型，已转换为字符串: {template_name} -> '{name_key}'")
            elif template_name is None:
                print(f"[ERROR] 模板名称不能为None")
                return None
            else:
                name_key = str(template_name)
                print(f"[WARNING] 模板名称类型异常，已转换为字符串: {type(template_name)} -> '{name_key}'")
            
            # 检查缓存
            if name_key in self.templates:
                return self.templates[name_key]
            
            # 获取文件路径
            file_path = self.get_template_file_path(name_key)
            if not os.path.exists(file_path):
                print(f"[INFO] 模板文件不存在: {file_path}")
                return None
            
            # 读取和解析文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 创建模板对象
            template = WatermarkTemplate.from_dict(data)
            self.templates[name_key] = template
            
            return template
            
        except Exception as e:
            print(f"❌ Load template failed: {e}")
            print(f"   模板名称: {template_name} (类型: {type(template_name)})")
            import traceback
            traceback.print_exc()
            return None
    
    def delete_template(self, template_name: str) -> bool:
        """删除模板"""
        try:
            file_path = self.get_template_file_path(template_name)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 从内存中删除
            if template_name in self.templates:
                del self.templates[template_name]
            
            return True
            
        except Exception as e:
            print(f"Delete template failed: {e}")
            return False
    
    def get_template_list(self) -> List[str]:
        """获取模板列表"""
        return list(self.templates.keys())
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """获取模板信息"""
        template = self.load_template(template_name)
        if template:
            return {
                'name': template.name,
                'description': template.description,
                'created_time': template.created_time,
                'watermark_type': template.watermark_type
            }
        return None
    
    def load_all_templates(self):
        """加载所有模板"""
        try:
            if not os.path.exists(self.templates_dir):
                return
            
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.json'):
                    template_name = os.path.splitext(filename)[0]
                    self.load_template(template_name)
                    
        except Exception as e:
            print(f"Load all templates failed: {e}")
    
    def export_template(self, template_name: str, export_path: str) -> bool:
        """导出模板"""
        try:
            template = self.load_template(template_name)
            if not template:
                return False
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(template.to_dict(), f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Export template failed: {e}")
            return False
    
    def import_template(self, import_path: str) -> Optional[str]:
        """导入模板"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            template = WatermarkTemplate.from_dict(data)
            
            # 检查名称冲突
            original_name = template.name
            counter = 1
            while template.name in self.templates:
                template.name = f"{original_name}_{counter}"
                counter += 1
            
            if self.save_template(template):
                return template.name
            
            return None
            
        except Exception as e:
            print(f"Import template failed: {e}")
            return None
    
    def export_template(self, template_name: str, file_path: str) -> bool:
        """导出模板到文件"""
        try:
            template = self.load_template(template_name)
            if not template:
                return False
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template.to_dict(), f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Export template failed: {e}")
            return False


class TemplateDialog:
    """模板管理对话框"""
    
    def __init__(self, parent, template_manager: TemplateManager, mode: str = "load"):
        """
        初始化对话框
        mode: "load" - 加载模板, "save" - 保存模板, "manage" - 管理模板
        """
        self.parent = parent
        self.template_manager = template_manager
        self.mode = mode
        self.result = None
        self.selected_template = None
        
        self.create_dialog()
    
    def create_dialog(self):
        """创建对话框"""
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog
        
        self.dialog = tk.Toplevel(self.parent)
        
        if self.mode == "load":
            self.dialog.title("加载水印模板")
            self.dialog.geometry("500x400")
        elif self.mode == "save":
            self.dialog.title("保存水印模板")
            self.dialog.geometry("400x300")
        else:  # manage
            self.dialog.title("管理水印模板")
            self.dialog.geometry("600x500")
        
        self.dialog.resizable(True, True)
        
        # 使对话框模态
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 创建界面
        if self.mode == "load":
            self.create_load_interface()
        elif self.mode == "save":
            self.create_save_interface()
        else:
            self.create_manage_interface()
        
        # 居中显示
        self.center_dialog()
    
    def center_dialog(self):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_load_interface(self):
        """创建加载界面"""
        import tkinter as tk
        from tkinter import ttk
        
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 模板列表
        list_frame = tk.LabelFrame(main_frame, text="选择模板", padx=5, pady=5)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview
        columns = ("name", "type", "created")
        self.template_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # 设置列标题
        self.template_tree.heading("name", text="模板名称")
        self.template_tree.heading("type", text="类型")
        self.template_tree.heading("created", text="创建时间")
        
        # 设置列宽
        self.template_tree.column("name", width=200)
        self.template_tree.column("type", width=100)
        self.template_tree.column("created", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.template_tree.yview)
        self.template_tree.configure(yscrollcommand=scrollbar.set)
        
        self.template_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.template_tree.bind("<<TreeviewSelect>>", self.on_template_select)
        self.template_tree.bind("<Double-1>", self.on_template_double_click)
        
        # 描述区域
        desc_frame = tk.LabelFrame(main_frame, text="模板描述", padx=5, pady=5)
        desc_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.desc_text = tk.Text(desc_frame, height=3, wrap=tk.WORD, state=tk.DISABLED)
        self.desc_text.pack(fill=tk.X)
        
        # 按钮
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        tk.Button(button_frame, text="加载", command=self.load_selected_template).pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.RIGHT)
        tk.Button(button_frame, text="删除", command=self.delete_selected_template).pack(side=tk.LEFT)
        tk.Button(button_frame, text="导入", command=self.import_template).pack(side=tk.LEFT, padx=(5, 0))
        
        # 加载模板列表
        self.refresh_template_list()
    
    def create_save_interface(self):
        """创建保存界面"""
        import tkinter as tk
        
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 模板信息
        info_frame = tk.LabelFrame(main_frame, text="模板信息", padx=5, pady=5)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(info_frame, text="模板名称:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = tk.Entry(info_frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        tk.Label(info_frame, text="描述:").grid(row=1, column=0, sticky=tk.NW, pady=2)
        self.desc_entry = tk.Text(info_frame, width=30, height=4)
        self.desc_entry.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        # 按钮
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(button_frame, text="保存", command=self.save_template).pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.RIGHT)
    
    def create_manage_interface(self):
        """创建管理界面"""
        import tkinter as tk
        from tkinter import ttk
        
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 模板列表
        list_frame = tk.LabelFrame(main_frame, text="模板管理", padx=5, pady=5)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview
        columns = ("name", "type", "created", "default")
        self.template_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        
        # 设置列标题
        self.template_tree.heading("name", text="模板名称")
        self.template_tree.heading("type", text="类型")
        self.template_tree.heading("created", text="创建时间")
        self.template_tree.heading("default", text="默认模板")
        
        # 设置列宽
        self.template_tree.column("name", width=200)
        self.template_tree.column("type", width=100)
        self.template_tree.column("created", width=150)
        self.template_tree.column("default", width=80)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.template_tree.yview)
        self.template_tree.configure(yscrollcommand=scrollbar.set)
        
        self.template_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.template_tree.bind("<<TreeviewSelect>>", self.on_template_select)
        self.template_tree.bind("<Double-1>", self.on_template_double_click)
        
        # 描述区域
        desc_frame = tk.LabelFrame(main_frame, text="模板描述", padx=5, pady=5)
        desc_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.desc_text = tk.Text(desc_frame, height=3, wrap=tk.WORD, state=tk.DISABLED)
        self.desc_text.pack(fill=tk.X)
        
        # 按钮区域
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 左侧按钮
        left_buttons = tk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        tk.Button(left_buttons, text="删除", command=self.delete_selected_template).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(left_buttons, text="设为默认", command=self.set_as_default).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(left_buttons, text="取消默认", command=self.unset_default).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(left_buttons, text="导入", command=self.import_template).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(left_buttons, text="导出", command=self.export_template).pack(side=tk.LEFT)
        
        # 右侧按钮
        tk.Button(button_frame, text="关闭", command=self.cancel_clicked).pack(side=tk.RIGHT)
        
        # 加载模板列表
        self.refresh_template_list()
        
        # 保存主窗口引用用于设置默认模板
        if hasattr(self.parent, 'main_window'):
            self.main_window = self.parent.main_window
        else:
            self.main_window = self.parent
    
    def refresh_template_list(self):
        """刷新模板列表"""
        # 清空现有项目
        for item in self.template_tree.get_children():
            self.template_tree.delete(item)
        
        # 获取默认模板名称
        default_template = ""
        if hasattr(self, 'main_window') and self.main_window:
            default_template = self.main_window.config.get('default_template', '')
        
        # 添加模板项目
        template_names = self.template_manager.get_template_list()
        for name in template_names:
            info = self.template_manager.get_template_info(name)
            if info:
                # 格式化创建时间
                try:
                    created_time = datetime.fromisoformat(info['created_time']).strftime("%Y-%m-%d %H:%M")
                except:
                    created_time = info['created_time']
                
                # 是否为默认模板
                is_default = "是" if name == default_template else ""
                
                # 根据列数决定values
                if self.mode == "manage":
                    values = (info['name'], info['watermark_type'], created_time, is_default)
                else:
                    values = (info['name'], info['watermark_type'], created_time)
                
                self.template_tree.insert('', tk.END, values=values)
    
    def on_template_select(self, event):
        """模板选择事件"""
        selection = self.template_tree.selection()
        if selection:
            item = self.template_tree.item(selection[0])
            template_name = item['values'][0]
            self.selected_template = template_name
            
            # 显示描述
            info = self.template_manager.get_template_info(template_name)
            if info:
                self.desc_text.config(state=tk.NORMAL)
                self.desc_text.delete(1.0, tk.END)
                self.desc_text.insert(1.0, info.get('description', ''))
                self.desc_text.config(state=tk.DISABLED)
    
    def on_template_double_click(self, event):
        """模板双击事件"""
        if self.mode == "load":
            self.load_selected_template()
    
    def load_selected_template(self):
        """加载选中的模板"""
        if not self.selected_template:
            messagebox.showwarning("提示", "请先选择一个模板")
            return
        
        template = self.template_manager.load_template(self.selected_template)
        if template:
            self.result = template
            self.dialog.destroy()
        else:
            messagebox.showerror("错误", "加载模板失败")
    
    def delete_selected_template(self):
        """删除选中的模板"""
        if not self.selected_template:
            messagebox.showwarning("提示", "请先选择一个模板")
            return
        
        if messagebox.askyesno("确认", f"确定要删除模板 '{self.selected_template}' 吗？"):
            if self.template_manager.delete_template(self.selected_template):
                messagebox.showinfo("成功", "模板删除成功")
                self.refresh_template_list()
                self.selected_template = None
                self.desc_text.config(state=tk.NORMAL)
                self.desc_text.delete(1.0, tk.END)
                self.desc_text.config(state=tk.DISABLED)
            else:
                messagebox.showerror("错误", "删除模板失败")
    
    def import_template(self):
        """导入模板"""
        from tkinter import filedialog, messagebox
        
        file_path = filedialog.askopenfilename(
            title="导入模板",
            filetypes=[
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            template_name = self.template_manager.import_template(file_path)
            if template_name:
                messagebox.showinfo("成功", f"模板导入成功，名称: {template_name}")
                self.refresh_template_list()
            else:
                messagebox.showerror("错误", "导入模板失败")
    
    def export_template(self):
        """导出模板"""
        from tkinter import filedialog, messagebox
        
        if not self.selected_template:
            messagebox.showwarning("提示", "请先选择一个模板")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="导出模板",
            defaultextension=".json",
            filetypes=[
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ],
            initialvalue=f"{self.selected_template}.json"
        )
        
        if file_path:
            if self.template_manager.export_template(self.selected_template, file_path):
                messagebox.showinfo("成功", f"模板导出成功: {file_path}")
            else:
                messagebox.showerror("错误", "导出模板失败")
    
    def set_as_default(self):
        """设置为默认模板"""
        from tkinter import messagebox
        
        if not self.selected_template:
            messagebox.showwarning("提示", "请先选择一个模板")
            return
        
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.set_default_template(self.selected_template)
            messagebox.showinfo("成功", f"已将 '{self.selected_template}' 设为默认模板")
            self.refresh_template_list()
        else:
            messagebox.showerror("错误", "无法设置默认模板")
    
    def unset_default(self):
        """取消默认模板"""
        from tkinter import messagebox
        
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.set_default_template("")
            messagebox.showinfo("成功", "已取消默认模板设置")
            self.refresh_template_list()
        else:
            messagebox.showerror("错误", "无法取消默认模板")
    
    def save_template(self):
        """保存模板"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入模板名称")
            return
        
        description = self.desc_entry.get(1.0, tk.END).strip()
        
        # 这里需要从外部传入当前的水印设置
        # 在实际使用时，会通过回调函数获取当前设置
        if hasattr(self, 'get_current_watermark_callback'):
            template = self.get_current_watermark_callback(name, description)
            if template and self.template_manager.save_template(template):
                messagebox.showinfo("成功", "模板保存成功")
                self.result = template
                self.dialog.destroy()
            else:
                messagebox.showerror("错误", "保存模板失败")
        else:
            messagebox.showerror("错误", "无法获取当前水印设置")
    
    def cancel_clicked(self):
        """取消按钮点击"""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """显示对话框并返回结果"""
        self.dialog.wait_window()
        return self.result
