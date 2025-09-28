#!/usr/bin/env python3
"""
测试水印布局与样式功能的脚本

运行方式：
    python test_watermark_layout.py

此脚本会在test_output目录下生成测试图片，展示不同位置和样式的水印效果。
"""

import os
from pathlib import Path
from PIL import Image

# 导入我们实现的水印模块
from watermarking import (
    GridPosition,
    TextWatermarkOptions,
    apply_text_watermark,
    get_position_name,
    is_font_available
)


def create_test_image(width: int = 800, height: int = 600) -> Image.Image:
    """创建一个简单的测试图像"""
    # 创建白色背景图像
    image = Image.new('RGB', (width, height), color='white')
    
    # 在图像中心绘制一个彩色方块作为标记
    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)
    square_size = min(width, height) // 2
    square_x = (width - square_size) // 2
    square_y = (height - square_size) // 2
    draw.rectangle(
        [(square_x, square_y), (square_x + square_size, square_y + square_size)],
        fill=(240, 240, 240),
        outline=(200, 200, 200),
        width=2
    )
    
    # 绘制一些参考线
    draw.line([(0, height//2), (width, height//2)], fill=(220, 220, 220), width=1)
    draw.line([(width//2, 0), (width//2, height)], fill=(220, 220, 220), width=1)
    
    return image


def test_watermark_positions():
    """测试不同位置的水印"""
    # 创建输出目录
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # 创建测试图像
    test_image = create_test_image()
    
    # 测试所有九宫格位置
    for position in GridPosition:
        # 创建水印选项
        options = TextWatermarkOptions(
            text=f"水印测试 - {get_position_name(position)}",
            font_size=32,
            color=(255, 0, 0),  # 红色水印
            opacity=80,
            position=position,
            margin=20
        )
        
        # 应用水印
        watermarked_image = apply_text_watermark(test_image, options)
        
        # 保存结果
        output_path = output_dir / f"watermark_{position.value}.png"
        watermarked_image.save(output_path)
        print(f"已保存位置测试图像: {output_path}")


def test_watermark_styles():
    """测试不同样式的水印"""
    # 创建输出目录
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # 创建测试图像
    test_image = create_test_image()
    
    # 测试不同字体大小
    for size in [20, 32, 48]:
        options = TextWatermarkOptions(
            text=f"字体大小测试 - {size}px",
            font_size=size,
            color=(0, 0, 255),  # 蓝色水印
            opacity=100,
            position=GridPosition.CENTER,
            margin=20
        )
        watermarked_image = apply_text_watermark(test_image, options)
        output_path = output_dir / f"watermark_fontsize_{size}.png"
        watermarked_image.save(output_path)
        print(f"已保存字体大小测试图像: {output_path}")
    
    # 测试不同透明度
    for opacity in [25, 50, 75, 100]:
        options = TextWatermarkOptions(
            text=f"透明度测试 - {opacity}%",
            font_size=32,
            color=(0, 128, 0),  # 绿色水印
            opacity=opacity,
            position=GridPosition.CENTER,
            margin=20
        )
        watermarked_image = apply_text_watermark(test_image, options)
        output_path = output_dir / f"watermark_opacity_{opacity}.png"
        watermarked_image.save(output_path)
        print(f"已保存透明度测试图像: {output_path}")
    
    # 测试不同颜色
    colors = [
        (255, 0, 0),    # 红色
        (0, 255, 0),    # 绿色
        (0, 0, 255),    # 蓝色
        (255, 255, 0),  # 黄色
        (255, 0, 255),  # 洋红色
    ]
    color_names = ["red", "green", "blue", "yellow", "magenta"]
    
    for i, (color, name) in enumerate(zip(colors, color_names)):
        options = TextWatermarkOptions(
            text=f"颜色测试 - {name}",
            font_size=32,
            color=color,
            opacity=100,
            position=GridPosition.CENTER,
            margin=20
        )
        watermarked_image = apply_text_watermark(test_image, options)
        output_path = output_dir / f"watermark_color_{name}.png"
        watermarked_image.save(output_path)
        print(f"已保存颜色测试图像: {output_path}")
    
    # 测试不同边距
    for margin in [10, 30, 50]:
        options = TextWatermarkOptions(
            text=f"边距测试 - {margin}px",
            font_size=24,
            color=(128, 128, 128),  # 灰色水印
            opacity=100,
            position=GridPosition.BOTTOM_RIGHT,
            margin=margin
        )
        watermarked_image = apply_text_watermark(test_image, options)
        output_path = output_dir / f"watermark_margin_{margin}.png"
        watermarked_image.save(output_path)
        print(f"已保存边距测试图像: {output_path}")


def test_font_selection():
    """测试字体选择功能"""
    # 创建输出目录
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    # 创建测试图像
    test_image = create_test_image()
    
    # 测试一些常见字体
    fonts_to_test = [
        "Arial",
        "SimHei",      # 黑体
        "SimSun",      # 宋体
        "Microsoft YaHei",  # 微软雅黑
    ]
    
    for font_name in fonts_to_test:
        if is_font_available(font_name):
            options = TextWatermarkOptions(
                text=f"字体测试 - {font_name}",
                font_name=font_name,
                font_size=32,
                color=(0, 0, 0),  # 黑色水印
                opacity=100,
                position=GridPosition.CENTER,
                margin=20
            )
            watermarked_image = apply_text_watermark(test_image, options)
            # 替换字体名称中的空格以便文件名有效
            safe_font_name = font_name.replace(" ", "_")
            output_path = output_dir / f"watermark_font_{safe_font_name}.png"
            watermarked_image.save(output_path)
            print(f"已保存字体测试图像: {output_path}")
        else:
            print(f"警告: 字体 '{font_name}' 在系统上不可用，跳过此测试")


def main():
    """运行所有测试"""
    print("开始测试水印布局与样式功能...")
    
    print("\n测试1: 九宫格位置测试")
    test_watermark_positions()
    
    print("\n测试2: 水印样式测试 (字体大小、透明度、颜色、边距)")
    test_watermark_styles()
    
    print("\n测试3: 字体选择测试")
    test_font_selection()
    
    print("\n所有测试完成! 测试结果保存在 'test_output' 目录中")


if __name__ == "__main__":
    main()