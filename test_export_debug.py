#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug export functionality
"""

import sys
import os
import tempfile
from PIL import Image

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_export_step_by_step():
    """Step by step export test"""
    print("=== Export Debug Test ===")
    
    try:
        from file_manager import ExportManager
        from text_watermark import TextWatermark
        from image_list import ImageListManager
        
        # Create test image
        test_img = Image.new('RGB', (400, 300), 'lightblue')
        
        # Create watermark
        watermark = TextWatermark()
        watermark.set_text("Test Watermark")
        print(f"1. Created watermark: {watermark.text}")
        
        # Apply watermark
        watermarked_img = watermark.apply_to_image(test_img)
        if watermarked_img:
            print("2. ✅ Watermark applied successfully")
        else:
            print("2. ❌ Watermark application failed")
            return False
        
        # Test export manager
        export_manager = ExportManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            export_manager.output_folder = temp_dir
            print(f"3. Set output folder: {temp_dir}")
            
            # Test filename generation
            test_path = "/Users/test/sample.jpg"
            output_path = export_manager.generate_filename(test_path)
            print(f"4. Generated filename: {os.path.basename(output_path)}")
            
            # Test export
            success = export_manager.export_single_image(test_path, watermarked_img)
            if success:
                files = os.listdir(temp_dir)
                print(f"5. ✅ Export successful, created: {files}")
                return True
            else:
                print("5. ❌ Export failed")
                return False
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chinese_filename():
    """Test Chinese filename handling"""
    print("\n=== Chinese Filename Test ===")
    
    try:
        from file_manager import ExportManager
        
        export_manager = ExportManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            export_manager.output_folder = temp_dir
            
            # Test Chinese filename
            chinese_path = "/Users/test/研究生校园卡.jpg"
            output_path = export_manager.generate_filename(chinese_path)
            
            print(f"Input: {os.path.basename(chinese_path)}")
            print(f"Output: {os.path.basename(output_path)}")
            
            # Test if path is valid
            if os.path.dirname(output_path) == temp_dir:
                print("✅ Chinese filename handled correctly")
                return True
            else:
                print("❌ Chinese filename handling failed")
                return False
                
    except Exception as e:
        print(f"❌ Chinese filename test failed: {e}")
        return False

def main():
    print("Starting export functionality debug...")
    
    # Test basic export
    basic_test = test_export_step_by_step()
    
    # Test Chinese filename
    chinese_test = test_chinese_filename()
    
    print("\n" + "=" * 40)
    if basic_test and chinese_test:
        print("🎉 All tests passed! Export should work now.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    print("=" * 40)

if __name__ == "__main__":
    main()
