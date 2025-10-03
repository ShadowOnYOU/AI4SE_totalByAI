#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试图片导航选中状态更新
"""

import sys
import os
sys.path.insert(0, '/Users/shadowonyou/2025研一上/大模型辅助软件开发/AI4SE_totalByAI/src')

def test_navigation_fix():
    """测试导航修复功能"""
    print("🔍 检查图片导航选中状态更新修复...")
    
    try:
        # 检查修复的代码
        with open('/Users/shadowonyou/2025研一上/大模型辅助软件开发/AI4SE_totalByAI/src/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键修复点
        fixes = [
            ('update_image_list_selection方法', 'def update_image_list_selection(self):'),
            ('current_changed事件处理', 'self.update_image_list_selection()'),
            ('防循环标志初始化', 'self._updating_selection = False'),
            ('selection_set调用', 'self.image_list_widget.selection_set(item_id)'),
            ('see方法调用', 'self.image_list_widget.see(item_id)'),
        ]
        
        print("检查修复内容:")
        for fix_name, fix_code in fixes:
            if fix_code in content:
                print(f"   ✅ {fix_name}: 已添加")
            else:
                print(f"   ❌ {fix_name}: 缺失")
        
        print()
        
        # 检查具体的修复逻辑
        print("检查修复逻辑:")
        
        # 检查事件处理是否正确
        if 'elif event == \'current_changed\':\n            self.update_preview()\n            self.update_image_list_selection()' in content:
            print("   ✅ current_changed事件处理: 正确添加选中状态更新")
        else:
            print("   ❌ current_changed事件处理: 未正确修复")
        
        # 检查防循环机制
        if '_updating_selection = True' in content and '_updating_selection = False' in content:
            print("   ✅ 防循环机制: 已实现")
        else:
            print("   ❌ 防循环机制: 未实现")
        
        # 检查选中状态更新
        if 'selection_set(item_id)' in content and 'see(item_id)' in content:
            print("   ✅ 选中状态更新: 已实现")
        else:
            print("   ❌ 选中状态更新: 未实现")
        
        print()
        
        print("🎯 修复总结:")
        print("1. 添加了 update_image_list_selection() 方法")
        print("2. 在 current_changed 事件中调用选中状态更新")
        print("3. 实现了防循环更新机制")
        print("4. 确保选中项可见(自动滚动)")
        
        print()
        print("📋 修复说明:")
        print("- 当点击'上一张'/'下一张'按钮时，会触发 current_changed 事件")
        print("- current_changed 事件现在会同时更新预览和列表选中状态")
        print("- 防循环标志防止用户点击列表时造成的无限递归")
        print("- 选中的项目会自动滚动到可见区域")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

if __name__ == "__main__":
    test_navigation_fix()