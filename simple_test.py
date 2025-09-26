#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple drag drop test
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test module imports"""
    print("Testing module imports...")
    try:
        from real_drag_drop import RealDragDrop, RealDragDropManager, create_dnd_root, DRAG_DROP_AVAILABLE
        from config import Config
        from file_manager import ImageFileManager
        from main import WatermarkApp
        
        print("SUCCESS: All modules imported successfully")
        print(f"Drag drop available: {DRAG_DROP_AVAILABLE}")
        return True
        
    except Exception as e:
        print(f"FAILED: Module import error: {e}")
        return False

def test_app_creation():
    """Test app creation"""
    print("Testing app creation...")
    try:
        # Test root window creation
        from real_drag_drop import create_dnd_root
        root = create_dnd_root()
        root.title("Test Window")
        root.withdraw()  # Hide the window
        root.destroy()   # Clean up
        
        print("SUCCESS: DnD root window created and destroyed")
        return True
        
    except Exception as e:
        print(f"FAILED: App creation error: {e}")
        return False

def main():
    print("=" * 50)
    print("DRAG DROP FUNCTIONALITY TEST")
    print("=" * 50)
    
    # Test imports
    import_success = test_imports()
    
    # Test app creation
    app_success = test_app_creation()
    
    if import_success and app_success:
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
        print("\nYou can now run the main application:")
        print("python3 main.py")
    else:
        print("\nSome tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
