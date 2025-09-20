#!/usr/bin/env python3
"""
Image Watermark Tool
A command-line tool to add watermarks to images based on EXIF data.
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
import exifread


class WatermarkTool:
    """Main class for watermarking images with EXIF data."""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
        
    def extract_exif_date(self, image_path: str) -> Optional[str]:
        """Extract date from EXIF data of an image."""
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                
                # Try different date fields
                date_fields = ['EXIF DateTimeOriginal', 'EXIF DateTime', 'Image DateTime']
                
                for field in date_fields:
                    if field in tags:
                        date_str = str(tags[field])
                        # Parse and format the date
                        try:
                            # Handle different date formats
                            if ':' in date_str:
                                if ' ' in date_str:
                                    # Format: "2023:12:25 14:30:00"
                                    dt = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                                else:
                                    # Format: "2023:12:25"
                                    dt = datetime.strptime(date_str, '%Y:%m:%d')
                                return dt.strftime('%Y-%m-%d')
                        except ValueError:
                            continue
                            
        except Exception as e:
            print(f"Warning: Could not extract EXIF data from {image_path}: {e}")
            
        return None
    
    def get_watermark_position(self, img_width: int, img_height: int, 
                             text_width: int, text_height: int, 
                             position: str) -> Tuple[int, int]:
        """Calculate watermark position based on user preference."""
        margin = 20
        
        # Ensure watermark fits within image bounds
        max_x = max(0, img_width - text_width - margin)
        max_y = max(0, img_height - text_height - margin)
        min_x = margin
        min_y = margin
        
        if position == 'top-left':
            x = min_x
            y = min_y
        elif position == 'top-right':
            x = max_x
            y = min_y
        elif position == 'bottom-left':
            x = min_x
            y = max_y
        elif position == 'bottom-right':
            x = max_x
            y = max_y
        elif position == 'center':
            x = max(min_x, min(max_x, (img_width - text_width) // 2))
            y = max(min_y, min(max_y, (img_height - text_height) // 2))
        else:
            # Default to bottom-right
            x = max_x
            y = max_y
        
        # Final bounds check to ensure watermark is completely within image
        x = max(0, min(x, img_width - text_width))
        y = max(0, min(y, img_height - text_height))
        
        return (x, y)
    
    def add_watermark(self, image_path: str, output_path: str, 
                     watermark_text: str, font_size: int = 24, 
                     color: str = 'white', position: str = 'bottom-right'):
        """Add watermark to an image."""
        try:
            # Open the image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create a copy for drawing
                watermarked_img = img.copy()
                draw = ImageDraw.Draw(watermarked_img)
                
                # Try to load a font, fallback to default if not available
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except (OSError, IOError):
                    try:
                        # Try system fonts
                        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                    except (OSError, IOError):
                        # Fallback to default font
                        font = ImageFont.load_default()
                
                # Get text dimensions
                bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Check if text is too large for the image
                if text_width > img.width or text_height > img.height:
                    print(f"Warning: Font size {font_size} is too large for image {image_path} ({img.width}x{img.height}). Text size: {text_width}x{text_height}")
                
                # Calculate position
                x, y = self.get_watermark_position(
                    img.width, img.height, text_width, text_height, position
                )
                
                # Add the watermark text without background
                draw.text((x, y), watermark_text, font=font, fill=color)
                
                # Save the watermarked image
                watermarked_img.save(output_path, quality=95)
                print(f"✓ Watermarked: {output_path}")
                
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
    
    def process_directory(self, input_path: str, font_size: int = 24, 
                         color: str = 'white', position: str = 'bottom-right'):
        """Process all images in a directory."""
        input_dir = Path(input_path)
        
        if not input_dir.exists():
            print(f"Error: Directory '{input_path}' does not exist.")
            return
        
        if not input_dir.is_dir():
            print(f"Error: '{input_path}' is not a directory.")
            return
        
        # Create output directory as a subdirectory of the input directory
        output_dir = input_dir / f"{input_dir.name}_watermark"
        output_dir.mkdir(exist_ok=True)
        
        # Find all image files
        image_files = []
        for ext in self.supported_formats:
            image_files.extend(input_dir.glob(f"*{ext}"))
            image_files.extend(input_dir.glob(f"*{ext.upper()}"))
        
        if not image_files:
            print(f"No supported image files found in '{input_path}'")
            return
        
        print(f"Found {len(image_files)} image files to process...")
        print(f"Output directory: {output_dir}")
        
        processed_count = 0
        
        for image_file in image_files:
            # Extract date from EXIF
            date_str = self.extract_exif_date(str(image_file))
            
            if date_str:
                watermark_text = date_str
                print(f"Using EXIF date for {image_file.name}: {date_str}")
            else:
                # Fallback to file modification date
                mod_time = datetime.fromtimestamp(image_file.stat().st_mtime)
                watermark_text = mod_time.strftime('%Y-%m-%d')
                print(f"Using file date for {image_file.name}: {watermark_text}")
            
            # Create output filename
            output_file = output_dir / image_file.name
            
            # Add watermark
            self.add_watermark(
                str(image_file), str(output_file), watermark_text,
                font_size, color, position
            )
            processed_count += 1
        
        print(f"\n✓ Successfully processed {processed_count} images")
        print(f"Watermarked images saved to: {output_dir}")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Add watermarks to images based on EXIF data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python watermark_tool.py /path/to/images
  python watermark_tool.py /path/to/images --font-size 32 --color red --position center
  python watermark_tool.py /path/to/images --position top-left --font-size 20
        """
    )
    
    parser.add_argument(
        'input_path',
        help='Path to directory containing images to watermark'
    )
    
    parser.add_argument(
        '--font-size', '-s',
        type=int,
        default=24,
        help='Font size for watermark text (default: 24)'
    )
    
    parser.add_argument(
        '--color', '-c',
        default='white',
        help='Color for watermark text (default: white)'
    )
    
    parser.add_argument(
        '--position', '-p',
        choices=['top-left', 'top-right', 'center', 'bottom-left', 'bottom-right'],
        default='bottom-right',
        help='Position of watermark on image (default: bottom-right)'
    )
    
    args = parser.parse_args()
    
    # Create watermark tool instance
    tool = WatermarkTool()
    
    # Process the directory
    tool.process_directory(
        args.input_path,
        font_size=args.font_size,
        color=args.color,
        position=args.position
    )


if __name__ == "__main__":
    main()
