# 图片水印添加工具

一个简单易用的Java应用程序，可以从图片的EXIF信息中提取拍摄日期，并将其作为水印添加到图片上。

## 功能特点

- 自动读取图片EXIF信息中的拍摄时间
- 支持自定义水印字体大小、颜色和位置
- 批量处理图片文件
- 处理后的图片保存在原目录的子目录中

## 系统要求

- Java 11或更高版本
- 支持Windows、macOS和Linux操作系统

## 安装说明

1. 确保您的系统已安装Java 11或更高版本
2. 下载最新的发布版本
3. 解压缩下载的文件

## 使用方法

1. 运行程序：
   ```
   java -jar ImageWatermark.jar
   ```

2. 在程序界面中：
   - 点击"选择文件夹"按钮，选择包含图片的文件夹
   - 设置水印字体大小（小、中、大）
   - 选择水印颜色
   - 选择水印位置（左上角、居中、右下角等）
   - 点击"添加水印"按钮开始处理

3. 处理完成后，水印图片将保存在原目录下的"原目录名_watermark"子文件夹中

## 项目结构

```
src/
├── main/
│   ├── java/
│   │   └── com/
│   │       └── imagewatermark/
│   │           ├── Main.java                 # 程序入口
│   │           ├── ui/
│   │           │   └── WatermarkUI.java      # 用户界面
│   │           ├── core/
│   │           │   ├── ExifReader.java       # EXIF信息读取
│   │           │   ├── WatermarkProcessor.java # 水印处理
│   │           │   └── ImageSaver.java       # 图片保存
│   │           └── util/
│   │               └── FileUtils.java        # 文件工具类
│   └── resources/
│       └── icons/                            # 图标资源
└── test/                                     # 测试代码
```

## 依赖库

- [metadata-extractor](https://github.com/drewnoakes/metadata-extractor) - 用于读取图片EXIF信息
- [Swing/AWT](https://docs.oracle.com/javase/tutorial/uiswing/) - 用于构建用户界面

## 开发

### 构建项目

使用Maven构建项目：

```
mvn clean package
```

### 运行测试

```
mvn test
```

## 许可证

本项目采用MIT许可证 - 详见LICENSE文件

## 贡献

欢迎提交问题和拉取请求！