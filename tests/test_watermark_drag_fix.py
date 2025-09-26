#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test watermark drag functionality
"""

import sys
import os
import tkinter as tk
from PIL import Image, ImageTk

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_watermark_drag():
    """Test watermark drag functionality"""
    print("Testing watermark drag functionality...")
    
    try:
        from simple_watermark_drag import SimpleWatermarkDrag
        
        # Create test window
        root = tk.Tk()
        root.title("Watermark Drag Test")
        root.geometry("600x400")
        
        # Create canvas
        canvas = tk.Canvas(root, bg='lightgray', width=500, height=300)
        canvas.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create test image background
        test_img = Image.new('RGB', (400, 250), 'lightblue')
        photo = ImageTk.PhotoImage(test_img)
        canvas.create_image(250, 150, image=photo)
        
        # Drag state tracking
        drag_states = []
        
        def on_drag_start():
            drag_states.append("drag_started")
            print("Drag started!")
        
        def on_drag_end():
            drag_states.append("drag_ended")
            print("Drag ended!")
        
        def on_position_changed(position):
            print(f"Position changed to: {position}")
        
        # Create watermark drag handler
        drag_handler = SimpleWatermarkDrag(canvas, on_position_changed)
        drag_handler.set_drag_callbacks(on_start=on_drag_start, on_end=on_drag_end)
        
        # Show initial watermark
        drag_handler.show_watermark((100, 50), "Test Watermark")
        
        # Add instructions
        canvas.create_text(250, 350, text="Click and drag the red watermark rectangle", 
                          font=("Arial", 12), fill="black")
        
        # Add close button
        close_btn = tk.Button(root, text="Close Test", command=root.destroy)
        close_btn.pack(pady=10)
        
        # Keep reference to prevent garbage collection
        root.photo = photo
        
        print("Watermark drag test window created")
        print("Try dragging the red watermark rectangle")
        
        # Run test window
        root.mainloop()
        
        print(f"Drag events recorded: {drag_states}")
        return True
        
    except Exception as e:
        print(f"Watermark drag test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("WATERMARK DRAG FUNCTIONALITY TEST")
    print("=" * 50)
    
    success = test_watermark_drag()
    
    print("\n" + "=" * 50)
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed - check errors above")
    print("=" * 50)

if __name__ == "__main__":
    main()

