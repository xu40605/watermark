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

from PIL import Image
import exifread

# 导入我们实现的水印模块
from watermarking import (
    GridPosition,
    TextWatermarkOptions,
    apply_text_watermark
)
from file_processing import is_supported_input


class WatermarkTool:
    """Main class for watermarking images with EXIF data."""
    
    def __init__(self, font_size=24, color='white', position='bottom-right', font_name=None):
        """Initialize the WatermarkTool with the specified settings.
        
        Args:
            font_size: Font size for the watermark text
            color: Color for the watermark text
            position: Position of the watermark on the image
            font_name: Name of the font to use for the watermark text (optional)
        """
        # 使用file_processing模块中的支持格式列表
        from file_processing import SUPPORTED_INPUT_EXTS
        self.supported_formats = SUPPORTED_INPUT_EXTS
        
        # 保存水印设置作为实例变量
        self.font_size = font_size
        self.color = color
        self.position = position
        self.font_name = font_name
        
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
    
    def _convert_position_str_to_enum(self, position_str: str) -> GridPosition:
        """将字符串位置转换为GridPosition枚举值"""
        position_map = {
            'top-left': GridPosition.TOP_LEFT,
            'top-center': GridPosition.TOP_CENTER,
            'top-right': GridPosition.TOP_RIGHT,
            'middle-left': GridPosition.MIDDLE_LEFT,
            'center': GridPosition.CENTER,
            'middle-right': GridPosition.MIDDLE_RIGHT,
            'bottom-left': GridPosition.BOTTOM_LEFT,
            'bottom-center': GridPosition.BOTTOM_CENTER,
            'bottom-right': GridPosition.BOTTOM_RIGHT
        }
        # 查找映射
        if position_str in position_map:
            return position_map[position_str]
        
        # 尝试直接转换（例如对于枚举名称）
        try:
            return GridPosition(position_str)
        except ValueError:
            # 默认使用右下角
            return GridPosition.BOTTOM_RIGHT
    
    def _convert_color_str_to_tuple(self, color_str: str) -> Tuple[int, int, int]:
        """将颜色字符串转换为RGB元组"""
        # 处理颜色名称
        color_names = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'purple': (128, 0, 128),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
            'gray': (128, 128, 128),
            'grey': (128, 128, 128)
        }
        
        if color_str.lower() in color_names:
            return color_names[color_str.lower()]
        
        # 尝试解析RGB格式，如 "255,0,0"
        try:
            parts = [int(x.strip()) for x in color_str.split(',')]
            if len(parts) == 3:
                # 确保值在有效范围内
                return (max(0, min(255, parts[0])),
                        max(0, min(255, parts[1])),
                        max(0, min(255, parts[2])))
        except ValueError:
            pass
        
        # 默认返回白色
        return (255, 255, 255)
    
    def add_watermark(self, image_path: str, output_path: str, watermark_text: str):
        """Add watermark to an image using our watermarking module."""
        try:
            # Open the image
            with Image.open(image_path) as img:
                # 转换位置字符串为枚举值
                grid_position = self._convert_position_str_to_enum(self.position)
                
                # 转换颜色字符串为RGB元组
                rgb_color = self._convert_color_str_to_tuple(self.color)
                
                # 创建水印选项
                options = TextWatermarkOptions(
                    text=watermark_text,
                    font_size=self.font_size,
                    color=rgb_color,
                    opacity=100,  # 默认完全不透明
                    position=grid_position,
                    margin=20,    # 默认边距
                    font_name=self.font_name  # 使用字体名称
                )
                
                # 应用水印
                watermarked_img = apply_text_watermark(img, options)
                
                # 如果是JPEG格式，需要转换为RGB
                if img.format == 'JPEG' and watermarked_img.mode == 'RGBA':
                    watermarked_img = watermarked_img.convert('RGB')
                
                # Save the watermarked image
                watermarked_img.save(output_path, quality=95)
                print(f"✓ Watermarked: {output_path}")
                
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
    
    def process_directory(self, input_path: str):
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
        print(f"Watermark settings - Font size: {self.font_size}, Color: {self.color}, Position: {self.position}")
        if self.font_name:
            print(f"Font name: {self.font_name}")
        
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
            self.add_watermark(str(image_file), str(output_file), watermark_text)
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
        """)
    
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
        choices=['top-left', 'top-center', 'top-right', 'middle-left', 'center', 'middle-right', 'bottom-left', 'bottom-center', 'bottom-right'],
        default='bottom-right',
        help='Position of watermark on image (default: bottom-right)'
    )
    
    parser.add_argument(
        '--font-name', '-f',
        default=None,
        help='Font name for watermark text (optional)'
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
