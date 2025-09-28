#!/usr/bin/env python3
"""
Test script for the watermark tool.
Creates sample images and tests the watermarking functionality.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS

def create_test_image_with_exif(filename: str, date_str: str):
    """Create a test image with EXIF date information."""
    # Create a simple test image
    img = Image.new('RGB', (800, 600), color='lightblue')
    
    # Add some content
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except (OSError, IOError):
        font = ImageFont.load_default()
    
    draw.text((50, 50), "Test Image", fill='black', font=font)
    draw.text((50, 100), f"Created: {date_str}", fill='darkblue', font=font)
    
    # Save with EXIF data
    img.save(filename, 'JPEG', quality=95)
    
    # Note: PIL doesn't easily support writing EXIF data
    # For a real test, you would need images with actual EXIF data
    print(f"Created test image: {filename}")

def create_test_images():
    """Create a set of test images in a temporary directory."""
    # Create temporary directory
    test_dir = Path("test_images")
    test_dir.mkdir(exist_ok=True)
    
    # Create test images with different dates
    test_dates = [
        "2023-01-15",
        "2023-06-20", 
        "2023-12-25",
        "2024-03-10"
    ]
    
    for i, date in enumerate(test_dates):
        filename = test_dir / f"test_image_{i+1}.jpg"
        create_test_image_with_exif(str(filename), date)
    
    print(f"Created {len(test_dates)} test images in {test_dir}")
    return str(test_dir)

def test_watermark_tool():
    """Test the watermark tool with sample images."""
    print("Creating test images...")
    test_dir = create_test_images()
    
    print("\nTesting watermark tool...")
    print("=" * 50)
    
    # Test different configurations
    test_configs = [
        {
            "name": "Default settings",
            "args": [test_dir]
        },
        {
            "name": "Center position, large font",
            "args": [test_dir, "--position", "center", "--font-size", "32"]
        },
        {
            "name": "Top-left, red color",
            "args": [test_dir, "--position", "top-left", "--color", "red", "--font-size", "20"]
        }
    ]
    
    for config in test_configs:
        print(f"\nTesting: {config['name']}")
        print(f"Command: python watermark_tool.py {' '.join(config['args'])}")
        
        # Import and run the watermark tool
        import sys
        sys.argv = ['watermark_tool.py'] + config['args']
        
        try:
            from watermark_tool import main
            main()
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print(f"Check the output in: {test_dir}_watermark/")

if __name__ == "__main__":
    test_watermark_tool()




