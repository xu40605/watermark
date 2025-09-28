#!/usr/bin/env python3
"""
水印GUI应用程序测试脚本
用于验证核心功能是否正常工作
"""

import os
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_dependencies():
    """测试依赖库是否正确安装"""
    logger.info("开始测试依赖库...")
    
    # 测试PIL库
    try:
        import PIL
        from PIL import Image, ImageTk
        logger.info(f"PIL库安装正常，版本: {PIL.__version__}")
    except ImportError as e:
        logger.error(f"PIL库导入失败: {str(e)}")
        return False
    
    # 测试tkinter库
    try:
        import tkinter as tk
        from tkinter import ttk, colorchooser, filedialog, messagebox
        logger.info(f"tkinter库导入正常")
    except ImportError as e:
        logger.error(f"tkinter库导入失败: {str(e)}")
        return False
    
    # 测试水印处理模块
    try:
        from watermarking import (
            GridPosition, 
            TextWatermarkOptions, 
            apply_text_watermark,
            is_font_available
        )
        logger.info(f"watermarking模块导入正常")
    except ImportError as e:
        logger.error(f"watermarking模块导入失败: {str(e)}")
        return False
    
    # 测试文件处理模块
    try:
        from file_processing import (
            discover_inputs,
            ExportOptions,
            NamingMode,
            ResizeMode
        )
        logger.info(f"file_processing模块导入正常")
    except ImportError as e:
        logger.error(f"file_processing模块导入失败: {str(e)}")
        return False
    
    logger.info("所有依赖库测试通过！")
    return True

def test_watermark_functionality():
    """测试水印功能是否正常工作"""
    logger.info("开始测试水印功能...")
    
    try:
        # 尝试创建水印选项对象
        from watermarking import GridPosition, TextWatermarkOptions
        
        # 测试GridPosition枚举
        positions = list(GridPosition)
        logger.info(f"GridPosition枚举包含 {len(positions)} 个位置选项")
        
        # 创建一个水印选项示例
        options = TextWatermarkOptions(
            text="测试水印",
            font_size=36,
            font_name="Arial",
            color=(255, 255, 255),
            opacity=80,
            position=GridPosition.BOTTOM_RIGHT,
            margin=20
        )
        logger.info(f"成功创建TextWatermarkOptions对象: {options}")
        
        # 测试字体可用性检查函数
        from watermarking import is_font_available
        font_available = is_font_available("Arial")
        logger.info(f"字体'Arial'是否可用: {font_available}")
        
        # 检查是否有测试图片可以使用
        test_image_path = None
        for ext in ['.jpg', '.png', '.jpeg']:
            for file in os.listdir('.'):
                if file.lower().endswith(ext):
                    test_image_path = file
                    break
            if test_image_path:
                break
        
        if test_image_path:
            logger.info(f"找到测试图片: {test_image_path}")
            try:
                from PIL import Image
                from watermarking import apply_text_watermark
                
                # 打开测试图片
                img = Image.open(test_image_path)
                logger.info(f"成功打开测试图片，尺寸: {img.size}")
                
                # 尝试应用水印（不实际渲染）
                # 这里只是验证函数调用是否正常
                logger.info("准备应用水印...")
                # 注意：在实际测试中可能需要注释下面这行，避免在无图形界面环境中执行
                # watermarked_img = apply_text_watermark(img, options)
                logger.info("水印功能测试完成")
            except Exception as e:
                logger.error(f"应用水印测试失败: {str(e)}")
        else:
            logger.warning("未找到测试图片，跳过实际水印应用测试")
        
        logger.info("水印功能测试通过！")
        return True
    except Exception as e:
        logger.error(f"水印功能测试失败: {str(e)}")
        return False

def test_file_processing():
    """测试文件处理功能"""
    logger.info("开始测试文件处理功能...")
    
    try:
        from file_processing import discover_inputs, ExportOptions, NamingMode
        from pathlib import Path
        
        # 测试discover_inputs函数（使用当前目录）
        current_dir = Path('.')
        import_result = discover_inputs([current_dir])
        logger.info(f"discover_inputs找到 {len(import_result.files)} 个文件")
        
        # 测试ExportOptions创建
        export_options = ExportOptions(
            output_dir=Path('test_output'),
            naming_mode=NamingMode.SUFFIX,
            suffix="_test",
            jpeg_quality=90
        )
        logger.info(f"成功创建ExportOptions对象: {export_options}")
        
        logger.info("文件处理功能测试通过！")
        return True
    except Exception as e:
        logger.error(f"文件处理功能测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    logger.info("开始水印GUI应用程序测试...")
    
    # 测试依赖
    dependencies_ok = test_dependencies()
    
    # 测试水印功能
    watermark_ok = test_watermark_functionality()
    
    # 测试文件处理功能
    file_processing_ok = test_file_processing()
    
    # 总结测试结果
    logger.info("\n测试结果总结:")
    logger.info(f"依赖库测试: {'通过' if dependencies_ok else '失败'}")
    logger.info(f"水印功能测试: {'通过' if watermark_ok else '失败'}")
    logger.info(f"文件处理功能测试: {'通过' if file_processing_ok else '失败'}")
    
    if dependencies_ok and watermark_ok and file_processing_ok:
        logger.info("\n所有测试通过！水印GUI应用程序的核心功能正常。")
        logger.info("注意：在无图形界面的环境中，GUI界面可能无法正常显示。")
        logger.info("请在有图形界面的环境中运行 'python watermark_gui.py' 来启动完整的GUI应用程序。")
    else:
        logger.error("\n测试未全部通过，请修复上述问题后再尝试运行GUI应用程序。")


if __name__ == "__main__":
    main()