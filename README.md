# 图片水印工具

## 功能简介
- 图形界面工具，支持批量为图片添加自定义水印
- 支持文本水印和图片水印，可自定义样式、位置和透明度
- 支持从EXIF中提取拍摄日期作为水印内容
- 实时预览水印效果，所见即所得
- 支持保存和加载水印模板，提高工作效率

## 主要功能

### 文件处理
- **导入方式**：支持拖拽导入、文件选择器导入单张或多张图片、导入整个文件夹
- **支持格式**：JPEG、PNG、BMP、TIFF，支持PNG透明通道
- **导出选项**：自定义输出文件夹、文件命名规则（前缀/后缀）、图片质量和尺寸调整

### 水印设置
- **文本水印**：自定义文本内容、字体、大小、颜色、透明度、阴影/描边效果
- **图片水印**：支持导入Logo等图片作为水印，可调整大小和透明度
- **位置控制**：九宫格预设位置或自由拖拽定位
- **旋转功能**：可任意角度旋转水印

### 配置管理
- **水印模板**：保存、加载和管理水印设置模板
- **自动加载**：程序启动时自动加载上次设置或默认模板

## 系统要求
- 支持 Windows/macOS/Linux 操作系统
- Python 3.6 或更高版本
- 依赖库：Pillow, piexif (图像处理)，tkinter (GUI界面)

## 安装方法
```
# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

## 使用方法
1. 启动程序：
   ```
   python watermark_app.py
   ```
2. 通过界面导入图片（拖拽或文件选择器）
3. 设置水印类型、内容和样式
4. 实时预览效果并调整
5. 设置输出选项并导出处理后的图片

## 命令行模式
除了图形界面外，也提供命令行模式用于批处理：
```
python exif_watermark.py <图片路径或目录> --size <small|medium|large> --color <white|black|red|blue|green> --pos <top-left|center|bottom-right>
```

示例：
```
python exif_watermark.py ./images --size large --color red --pos center
```

## 参数说明
- `--size`：水印字体大小（默认 medium）
- `--color`：水印颜色（默认 white）
- `--pos`：水印位置（默认 bottom-right）

## 结果说明
- 新图片保存在用户指定的输出目录，默认命名规则为原文件名加后缀
- 无EXIF拍摄时间的图片会提示用户并提供替代选项

## 兼容性
- 支持 JPG、JPEG、PNG、BMP、TIFF 格式
- 兼容 Windows/macOS/Linux

## 其他
- 如需扩展功能或遇到问题，请提交 issue
- 欢迎贡献代码，提交 pull request
