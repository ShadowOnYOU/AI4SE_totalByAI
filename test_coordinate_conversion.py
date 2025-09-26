#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test coordinate conversion accuracy
"""

import sys
import os
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_image_with_grid():
    """创建带网格的测试图片"""
    width, height = 400, 300
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # 绘制网格
    grid_size = 50
    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill='lightgray', width=1)
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill='lightgray', width=1)
    
    # 标记关键点
    points = [
        (50, 50, "A(50,50)"),
        (150, 100, "B(150,100)"),
        (300, 200, "C(300,200)"),
        (350, 250, "D(350,250)")
    ]
    
    for x, y, label in points:
        # 绘制红点
        draw.ellipse([x-3, y-3, x+3, y+3], fill='red')
        # 绘制标签
        draw.text((x+5, y-15), label, fill='red')
    
    return img

def test_coordinate_conversion():
    """测试坐标转换准确性"""
    print("Testing coordinate conversion accuracy...")
    
    try:
        from text_watermark import TextWatermark
        
        # Create test window
        root = tk.Tk()
        root.title("Coordinate Conversion Test")
        root.geometry("800x600")
        
        # Create canvas
        canvas = tk.Canvas(root, bg='lightgray', width=700, height=500)
        canvas.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create test image
        test_img = create_test_image_with_grid()
        
        # Mock image size and scale calculation
        image_size = test_img.size
        canvas_width = 700
        canvas_height = 500
        
        # Calculate scale factor
        img_width, img_height = image_size
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        scale_factor = min(scale_x, scale_y, 1.0)
        
        # Calculate display size and offset
        canvas_img_width = int(img_width * scale_factor)
        canvas_img_height = int(img_height * scale_factor)
        offset_x = (canvas_width - canvas_img_width) // 2
        offset_y = (canvas_height - canvas_img_height) // 2
        
        print(f"Image size: {image_size}")
        print(f"Canvas size: ({canvas_width}, {canvas_height})")
        print(f"Scale factor: {scale_factor:.3f}")
        print(f"Display size: ({canvas_img_width}, {canvas_img_height})")
        print(f"Offset: ({offset_x}, {offset_y})")
        
        # Display image
        try:
            # Try new PIL version
            display_img = test_img.resize((canvas_img_width, canvas_img_height), Image.Resampling.LANCZOS)
        except AttributeError:
            # Fallback for older PIL versions
            display_img = test_img.resize((canvas_img_width, canvas_img_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(display_img)
        canvas.create_image(offset_x + canvas_img_width//2, offset_y + canvas_img_height//2, image=photo)
        
        # Test coordinate conversion functions
        def canvas_to_image(canvas_x, canvas_y):
            """Canvas coordinates to image coordinates"""
            image_x = int((canvas_x - offset_x) / scale_factor)
            image_y = int((canvas_y - offset_y) / scale_factor)
            image_x = max(0, min(image_x, img_width))
            image_y = max(0, min(image_y, img_height))
            return (image_x, image_y)
        
        def image_to_canvas(image_x, image_y):
            """Image coordinates to canvas coordinates"""
            canvas_x = offset_x + int(image_x * scale_factor)
            canvas_y = offset_y + int(image_y * scale_factor)
            return (canvas_x, canvas_y)
        
        # Test known points
        test_points = [(50, 50), (150, 100), (300, 200), (350, 250)]
        
        print("\nTesting coordinate conversion:")
        for img_x, img_y in test_points:
            canvas_x, canvas_y = image_to_canvas(img_x, img_y)
            back_img_x, back_img_y = canvas_to_image(canvas_x, canvas_y)
            
            print(f"Image({img_x}, {img_y}) -> Canvas({canvas_x}, {canvas_y}) -> Image({back_img_x}, {back_img_y})")
            
            # Draw test markers on canvas
            canvas.create_oval(canvas_x-3, canvas_y-3, canvas_x+3, canvas_y+3, 
                             fill='blue', outline='blue')
            canvas.create_text(canvas_x+10, canvas_y-10, 
                             text=f"({img_x},{img_y})", fill='blue', font=("Arial", 8))
        
        # Click handler for interactive testing
        def on_canvas_click(event):
            canvas_pos = (event.x, event.y)
            image_pos = canvas_to_image(event.x, event.y)
            back_canvas_pos = image_to_canvas(image_pos[0], image_pos[1])
            
            print(f"Click: Canvas{canvas_pos} -> Image{image_pos} -> Canvas{back_canvas_pos}")
            
            # Draw click marker
            canvas.create_oval(event.x-2, event.y-2, event.x+2, event.y+2, 
                             fill='green', outline='green')
            canvas.create_text(event.x+5, event.y-5, 
                             text=f"{image_pos}", fill='green', font=("Arial", 8))
        
        canvas.bind("<Button-1>", on_canvas_click)
        
        # Add instructions
        instructions = tk.Label(root, 
                               text="Blue dots show test points. Click anywhere to test coordinate conversion.",
                               font=("Arial", 10))
        instructions.pack(pady=5)
        
        # Keep reference to prevent garbage collection
        root.photo = photo
        
        print("\nCoordinate conversion test window created")
        print("Click on the image to test coordinate conversion")
        
        # Run test window
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"Coordinate conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("COORDINATE CONVERSION ACCURACY TEST")
    print("=" * 60)
    
    success = test_coordinate_conversion()
    
    print("\n" + "=" * 60)
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed - check errors above")
    print("=" * 60)

if __name__ == "__main__":
    main()
