# 图片EXIF水印命令行工具

## 功能简介
- 批量读取图片EXIF拍摄时间，自动添加日期水印。
- 支持自定义字体大小、颜色和水印位置。
- 新图片自动保存到 _watermark 子目录。

## 使用方法
1. 安装依赖：
   ```
   pip install pillow piexif
   ```
2. 命令行运行：
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
- 新图片保存在原目录的 `_watermark` 子目录。
- 无EXIF拍摄时间的图片会被跳过并提示。

## 兼容性
- 支持 JPG、JPEG、PNG 格式。
- 兼容 Windows/macOS/Linux。

## 其他
- 如需扩展功能或遇到问题，请提交 issue。
