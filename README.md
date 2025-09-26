# 图片水印工具 (Image Watermark Tool)

一个功能完整的图形界面水印工具，支持批量为图片添加自定义水印。

## ✨ 主要特性

- 🖼️ **多种水印类型**：文本水印、图片水印、EXIF日期水印
- 🎨 **丰富的自定义选项**：字体、颜色、大小、透明度、阴影效果
- 📍 **灵活的位置控制**：九宫格预设位置 + 自由拖拽定位
- 👀 **实时预览**：所见即所得的水印效果预览
- 📁 **批量处理**：支持单张/多张/文件夹批量导入处理
- 💾 **模板系统**：保存和加载水印模板，提高工作效率
- 🚀 **拖拽导入**：直接拖拽图片文件到程序界面

## 🏗️ 项目结构

```
AI4SE_totalByAI/
├── README.md                    # 项目说明
├── requirements.txt             # 依赖列表
├── setup.py                     # 安装配置
├── main.py                      # 程序入口
├── config.json                  # 配置文件
│
├── src/                         # 源代码
│   ├── main.py                  # 主程序
│   ├── main_window.py           # 主窗口
│   ├── config.py                # 配置管理
│   ├── components/              # 核心组件
│   │   ├── text_watermark.py    # 文本水印
│   │   ├── image_list.py        # 图片列表管理
│   │   ├── file_manager.py      # 文件管理
│   │   └── exif_watermark.py    # EXIF水印
│   ├── ui/                      # 用户界面
│   │   ├── real_drag_drop.py    # 拖拽功能
│   │   ├── simple_watermark_drag.py # 水印拖拽
│   │   └── watermark_gui.py     # 水印GUI
│   └── utils/                   # 工具模块
│
├── tests/                       # 测试文件
├── demos/                       # 演示脚本
├── docs/                        # 项目文档
└── assets/                      # 静态资源
```

## 🚀 快速开始

### 环境要求

- Python 3.6+
- tkinter (通常随Python安装)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python main.py
```

或者使用UTF-8编码运行（推荐）：

```bash
PYTHONIOENCODING=utf-8 python main.py
```

## 📖 使用指南

### 基本操作流程

1. **导入图片**
   - 拖拽图片文件到程序界面
   - 或点击"导入图片"按钮选择文件

2. **设置水印**
   - 在右侧面板设置水印文本、样式
   - 选择水印位置或拖拽调整

3. **预览效果**
   - 在中央预览区域查看水印效果
   - 实时调整参数直到满意

4. **批量导出**
   - 选择输出文件夹
   - 点击"导出所有图片"完成处理

### 高级功能

- **模板管理**：保存常用水印设置为模板
- **EXIF水印**：自动从照片中提取拍摄日期
- **精确定位**：拖拽水印到任意位置
- **批量处理**：一次处理多张图片

## 🛠️ 开发

### 项目结构说明

- `src/`: 主要源代码，按功能模块组织
- `tests/`: 单元测试和功能测试
- `demos/`: 演示脚本和示例
- `docs/`: 详细的项目文档
- `assets/`: 静态资源文件

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python tests/test_coordinate_conversion.py
```

### 运行演示

```bash
# 基本功能演示
python demos/demo_simple.py

# 拖拽功能演示
python demos/demo_drag_drop.py
```

## 📚 文档

详细文档位于 `docs/` 目录：

- [产品需求文档](docs/PRD.md)
- [使用说明](docs/使用说明.md)
- [功能点拆解文档](docs/功能点拆解文档.md)
- [项目总结](docs/项目总结.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！
