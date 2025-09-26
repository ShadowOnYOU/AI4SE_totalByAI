# -*- coding: utf-8 -*-
"""
简单的 EXIF 日期水印脚本
用法:
  python exif_watermark.py <图片或目录> --size medium --color white --pos bottom-right
"""
import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont
import piexif
import datetime

SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png')
COLOR_MAP = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'blue': (0, 0, 255),
    'green': (0, 128, 0)
}
SIZE_MAP = {'small': 24, 'medium': 36, 'large': 48}
POS_MAP = ['top-left', 'center', 'bottom-right']


def extract_date(img_path):
    # 尝试用 piexif 读取常见字段
    try:
        exif = piexif.load(img_path)
    except Exception:
        exif = None
    if exif:
        try:
            v = exif.get('Exif', {}).get(piexif.ExifIFD.DateTimeOriginal)
            if v:
                return v.decode().split(' ')[0].replace(':', '-')
            v = exif.get('Exif', {}).get(piexif.ExifIFD.DateTimeDigitized)
            if v:
                return v.decode().split(' ')[0].replace(':', '-')
            v = exif.get('0th', {}).get(piexif.ImageIFD.DateTime)
            if v:
                return v.decode().split(' ')[0].replace(':', '-')
        except Exception:
            pass
    return None


def add_watermark(img, text, font_size, color, pos):
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
    # 计算文字尺寸
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except Exception:
        try:
            text_w, text_h = font.getsize(text)
        except Exception:
            text_w, text_h = (len(text) * font_size // 2, font_size)
    w, h = img.size
    margin = 12
    if pos == 'top-left':
        x, y = margin, margin
    elif pos == 'center':
        x, y = (w - text_w) // 2, (h - text_h) // 2
    else:
        x, y = w - text_w - margin, h - text_h - margin
    # 绘制半透明背景矩形以提高可读性
    rect_pad = 6
    rect_x0 = x - rect_pad
    rect_y0 = y - rect_pad
    rect_x1 = x + text_w + rect_pad
    rect_y1 = y + text_h + rect_pad
    try:
        # 复制一层 RGBA
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        odraw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=(0, 0, 0, 120))
        # 合并
        img = img.convert('RGBA')
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)
        draw.text((x, y), text, font=font, fill=color + (255,) if isinstance(color, tuple) else color)
        return img.convert('RGB')
    except Exception:
        draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=(0, 0, 0))
        draw.text((x, y), text, font=font, fill=color)
        return img


def process_file(path, out_dir, font_size, color, pos, fallback='filetime'):
    date = extract_date(path)
    if not date and fallback == 'filetime':
        try:
            ts = os.path.getmtime(path)
            date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        except Exception:
            date = None
    if not date:
        print('跳过：未找到日期 -', os.path.basename(path))
        return
    try:
        img = Image.open(path).convert('RGB')
        img = add_watermark(img, date, font_size, color, pos)
        out_path = os.path.join(out_dir, os.path.basename(path))
        img.save(out_path)
        print('已处理：', os.path.basename(path))
    except Exception as e:
        print('处理失败：', os.path.basename(path), e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('--size', choices=SIZE_MAP.keys(), default='medium')
    parser.add_argument('--color', choices=COLOR_MAP.keys(), default='white')
    parser.add_argument('--pos', choices=POS_MAP, default='bottom-right')
    parser.add_argument('--fallback', choices=['none', 'filetime'], default='filetime')
    args = parser.parse_args()
    input_path = args.input
    font_size = SIZE_MAP[args.size]
    color = COLOR_MAP[args.color]
    pos = args.pos
    fallback = args.fallback
    if not os.path.exists(input_path):
        print('路径不存在')
        sys.exit(1)
    if os.path.isfile(input_path):
        files = [input_path] if input_path.lower().endswith(SUPPORTED_FORMATS) else []
        parent = os.path.dirname(input_path) or '.'
    else:
        files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.lower().endswith(SUPPORTED_FORMATS)]
        parent = input_path
    out_dir = os.path.join(parent, '_watermark')
    os.makedirs(out_dir, exist_ok=True)
    if not files:
        print('未找到图片')
        sys.exit(1)
    for f in files:
        process_file(f, out_dir, font_size, color, pos, fallback)

if __name__ == '__main__':
    main()
