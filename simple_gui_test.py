#!/usr/bin/env python3
"""
简单的水印GUI应用程序测试脚本
仅验证GUI是否能正常启动
"""

import os
import sys
import logging
import time

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """简单测试GUI是否能正常启动"""
    logger.info("开始简单的GUI启动测试...")
    
    try:
        # 导入必要的库
        import tkinter as tk
        logger.info("tkinter库导入成功")
        
        # 尝试创建一个简单的窗口
        logger.info("尝试创建测试窗口...")
        root = tk.Tk()
        root.title("测试窗口")
        root.geometry("300x200")
        
        # 添加标签
        label = tk.Label(root, text="Tkinter窗口创建成功！")
        label.pack(pady=20)
        
        # 启动窗口的同时设置一个定时器，在3秒后自动关闭
        def close_window():
            logger.info("测试窗口即将关闭...")
            root.destroy()
            logger.info("测试完成！")
            sys.exit(0)
        
        # 3秒后关闭窗口
        root.after(3000, close_window)
        
        logger.info("测试窗口已创建，3秒后自动关闭")
        logger.info("如果您能看到一个标题为'测试窗口'的小窗口，说明GUI功能正常")
        
        # 启动主循环
        root.mainloop()
        
    except ImportError as e:
        logger.error(f"导入库失败: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"创建GUI窗口失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()