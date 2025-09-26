#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Watermark Tool - Main Entry Point
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from main import main

if __name__ == "__main__":
    main()
