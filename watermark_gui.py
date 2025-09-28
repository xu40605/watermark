#!/usr/bin/env python3
"""
图片水印桌面应用程序
提供图形界面，支持导入图片、设置水印参数、预览和保存处理后的图片。
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, colorchooser, messagebox
from pathlib import Path
from typing import List, Optional
import glob
import platform

from PIL import Image, ImageTk

# 导入tkinterdnd2库用于拖拽功能
tkinterdnd2_available = False
tkinterdnd = None
DND_FILES = None

# 尝试导入tkinterdnd2库以支持拖拽文件
try:
    import tkinterdnd2 as tkinterdnd
    from tkinterdnd2 import DND_FILES
    tkinterdnd2_available = True
    print("tkinterdnd2库已成功导入")
except ImportError:
    print("警告: tkinterdnd2库未找到，请运行pip install tkinterdnd2以启用完整的拖拽功能")
    # 设置默认值，以便代码能够正常运行
    DND_FILES = 1

# 导入水印处理模块
from watermarking import (
    GridPosition, 
    TextWatermarkOptions, 
    apply_text_watermark,
    is_font_available
)
from file_processing import (
    discover_inputs,
    ExportOptions,
    NamingMode,
    ResizeMode,
    export_images
)

class ImportDialog(tk.Toplevel):
    """导入图片对话框，支持拖拽和文件选择器导入"""
    
    def __init__(self, parent, callback):
        """初始化导入对话框
        
        Args:
            parent: 父窗口
            callback: 导入完成后的回调函数，接收文件路径列表
        """
        super().__init__(parent)
        self.parent = parent
        self.callback = callback
        
        # 如果tkinterdnd可用，导入对话框类已继承了必要的功能，无需额外添加支持
        
        # 设置窗口属性
        self.title("导入图片")
        self.geometry("600x500")  # 增大窗口尺寸
        self.resizable(True, True)
        
        # 确保对话框模态
        self.transient(parent)
        self.grab_set()
        
        # 存储已拖拽的文件路径，用于显示
        self.dropped_files = []
        
        # 初始化拖拽状态变量
        self.drag_active = False
        
        # 设置中文字体
        self._setup_fonts()
        
        # 创建界面
        self._create_widgets()
        
        # 启用拖拽支持
        self._enable_drag_and_drop()
        
        # 居中显示
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.parent.winfo_width() // 2) - (width // 2) + self.parent.winfo_x()
        y = (self.parent.winfo_height() // 2) - (height // 2) + self.parent.winfo_y()
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _setup_fonts(self):
        """设置中文字体支持"""
        # 尝试设置中文字体
        if sys.platform.startswith('win'):
            # Windows系统
            self.default_font = ('Microsoft YaHei UI', 10)
            self.button_font = ('Microsoft YaHei UI', 11, 'bold')
            self.title_font = ('Microsoft YaHei UI', 16, 'bold')
        elif sys.platform.startswith('darwin'):
            # macOS系统
            self.default_font = ('Heiti TC', 10)
            self.button_font = ('Heiti TC', 11, 'bold')
            self.title_font = ('Heiti TC', 16, 'bold')
        else:
            # Linux系统
            self.default_font = ('WenQuanYi Micro Hei', 10)
            self.button_font = ('WenQuanYi Micro Hei', 11, 'bold')
            self.title_font = ('WenQuanYi Micro Hei', 16, 'bold')
        
        # 配置Tkinter字体
        self.style = ttk.Style()
        self.style.configure('.', font=self.default_font)
        self.style.configure('TButton', font=self.button_font)
        
        # 创建拖拽样式
        self.style.configure('Drag.TFrame', background='#e0e0ff', relief='solid', borderwidth=2)
    
    def _create_widgets(self):
        """创建对话框界面元素"""
        # 创建主框架
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(
            main_frame, 
            text="导入图片", 
            font=self.title_font
        )
        title_label.pack(pady=(0, 20))
        
        # 创建拖拽区域
        self.drag_frame = ttk.LabelFrame(
            main_frame, 
            text="拖拽文件到此处", 
            padding="20"
        )
        self.drag_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 拖拽区域提示文本
        self.drag_hint = ttk.Label(
            self.drag_frame, 
            text="请将图片文件或文件夹拖拽到此处\n\n或\n\n点击下方按钮选择文件", 
            justify=tk.CENTER, 
            font=self.default_font
        )
        self.drag_hint.pack(fill=tk.BOTH, expand=True)
        
        # 创建文件列表区域，用于显示已拖拽的文件
        self.files_frame = ttk.LabelFrame(main_frame, text="已选择的文件")
        self.files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 创建滚动区域
        list_frame = ttk.Frame(self.files_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建水平滚动条
        x_scroll = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建垂直滚动条
        y_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建文本框用于显示文件列表
        self.files_text = tk.Text(
            list_frame, 
            wrap=tk.NONE, 
            yscrollcommand=y_scroll.set, 
            xscrollcommand=x_scroll.set, 
            height=6, 
            font=self.default_font
        )
        self.files_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        x_scroll.config(command=self.files_text.xview)
        y_scroll.config(command=self.files_text.yview)
        
        # 禁用文本编辑
        self.files_text.config(state=tk.DISABLED)
        
        # 创建按钮区域
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        # 选择文件按钮
        self.btn_select_files = ttk.Button(
            buttons_frame, 
            text="选择图片文件", 
            command=self._select_files,
            padding=10  # 增加内边距使按钮更大
        )
        self.btn_select_files.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        # 选择文件夹按钮
        self.btn_select_folder = ttk.Button(
            buttons_frame, 
            text="选择文件夹", 
            command=self._select_folder,
            padding=10  # 增加内边距使按钮更大
        )
        self.btn_select_folder.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        
        # 取消按钮
        self.btn_cancel = ttk.Button(
            buttons_frame, 
            text="取消", 
            command=self.destroy,
            padding=10  # 增加内边距使按钮更大
        )
        self.btn_cancel.pack(side=tk.RIGHT, padx=(10, 0), fill=tk.X, expand=True)
    
    def _enable_drag_and_drop(self):
        """启用拖拽功能"""
        try:
            # 使用tkinterdnd2库的方法实现拖拽功能
            # 注册拖拽区域为文件拖放目标
            self.drag_frame.drop_target_register(DND_FILES)
            
            # 绑定拖放事件
            self.drag_frame.dnd_bind('<<Drop>>', self._on_drop)
            
            # 绑定进入和离开事件，提供视觉反馈
            self.drag_frame.dnd_bind('<<DragEnter>>', self._on_drag_enter)
            self.drag_frame.dnd_bind('<<DragLeave>>', self._on_drag_leave)
            
            print("使用tkinterdnd2库实现的拖拽功能已启用")
        except Exception as e:
            print(f"tkinterdnd2拖拽支持初始化失败: {e}")
            # 启用回退方案
            self._setup_alternative_drag_support()
        
        # 保留视觉反馈功能
        self._setup_visual_feedback()
        
    def _handle_dropped_files(self, file_paths):
        """处理拖拽的文件"""
        try:
            # 验证文件存在
            valid_files = [path for path in file_paths if os.path.exists(path)]
            
            if not valid_files:
                print("没有找到有效的文件")
                # 显示错误消息
                self.drag_hint.config(text="未找到有效的文件，请重新尝试")
                return
            
            print(f"有效文件数量: {len(valid_files)}")
            # 显示拖拽的文件
            self._display_dropped_files(valid_files)
            
        except Exception as e:
            print(f"处理拖拽文件时出错: {e}")
            self.drag_hint.config(text=f"处理文件时出错: {str(e)}")
    
    def _setup_alternative_drag_support(self):
        """设置替代的拖拽支持方法，提供视觉反馈"""
        # 使用Tkinter支持的拖拽事件类型，直接绑定事件处理函数
        self.bind('<Enter>', lambda e: self.drag_frame.config(style="Drag.TFrame"))
        self.bind('<Leave>', lambda e: self.drag_frame.config(style="TFrame"))
        # 添加剪贴板回退支持
        self._setup_fallback_drag_support()
        
    def _on_drop(self, event):
        """处理拖放事件"""
        try:
            # 获取拖拽的文件路径
            data = event.data
            print(f"接收到拖拽数据: {data}")
            
            file_paths = []
            
            # 处理Windows上tkinterdnd2的特殊格式
            # 格式1: 每个文件路径都被单独的大括号包围
            if '{' in data and '}' in data:
                # 将字符串分割成单独的大括号部分
                import re
                # 使用正则表达式提取大括号内的内容
                path_pattern = r'{([^{}]*)}'
                matches = re.findall(path_pattern, data)
                
                for match in matches:
                    path = match.strip()
                    # 标准化路径分隔符
                    path = path.replace('/', '\\')  # 转换为Windows风格的路径
                    
                    if os.path.exists(path):
                        print(f"找到有效文件路径: {path}")
                        file_paths.append(path)
                    else:
                        print(f"路径不存在: {path}")
            # 格式2: 大括号包围的路径，多个路径用空格分隔
            elif data.startswith('{') and data.endswith('}'):
                # 移除大括号
                data = data[1:-1]
                # 处理多个文件的情况
                # 检查是否有引号分隔的路径
                if '"' in data:
                    # 使用shlex解析带引号的路径
                    import shlex
                    paths = shlex.split(data)
                    for path in paths:
                        if os.path.exists(path):
                            file_paths.append(path)
                else:
                    # 尝试用空格分割，但要注意这可能会把长路径分开
                    # 所以我们需要检查每个分割后的部分是否为有效的文件路径
                    potential_paths = []
                    current_path = ""
                    parts = data.split(' ')
                    
                    for part in parts:
                        current_path = current_path + " " + part if current_path else part
                        if os.path.exists(current_path):
                            potential_paths.append(current_path)
                            current_path = ""
                    
                    # 如果没有找到有效的文件路径，尝试另一种方法
                    if not potential_paths:
                        # 检查整个data是否为一个文件路径
                        if os.path.exists(data):
                            file_paths.append(data)
                        # 或者检查是否包含多个用;分隔的路径（Windows资源管理器的标准格式）
                        elif ';' in data:
                            paths = data.split(';')
                            for path in paths:
                                path = path.strip()
                                if os.path.exists(path):
                                    file_paths.append(path)
                    else:
                        file_paths.extend(potential_paths)
            # 格式3: 直接的路径字符串
            else:
                # 检查是否有引号分隔的路径
                if '"' in data:
                    import shlex
                    paths = shlex.split(data)
                    for path in paths:
                        if os.path.exists(path):
                            file_paths.append(path)
                # 检查是否包含多个用;分隔的路径
                elif ';' in data:
                    paths = data.split(';')
                    for path in paths:
                        path = path.strip()
                        if os.path.exists(path):
                            file_paths.append(path)
                # 检查是否为单个文件
                elif os.path.exists(data):
                    file_paths.append(data)
                # 最后尝试用空格分割
                else:
                    paths = data.split()
                    for path in paths:
                        if os.path.exists(path):
                            file_paths.append(path)
            
            # 确保文件路径是唯一的
            file_paths = list(set(file_paths))
            
            if file_paths:
                print(f"成功解析{len(file_paths)}个文件路径")
                self._handle_dropped_files(file_paths)
            else:
                print("未找到有效的文件路径")
                self.drag_hint.config(text="未找到有效的文件路径，请重新尝试")
        except Exception as e:
            print(f"处理拖放事件时出错: {e}")
            self.drag_hint.config(text=f"处理拖放事件时出错: {str(e)}")
            
    def _on_drag_enter(self, event):
        """拖拽进入时的视觉反馈"""
        try:
            self.style.configure('Drag.TFrame', background='#e0e0ff', relief='solid', borderwidth=3)
            self.drag_frame.config(style="Drag.TFrame")
            self.drag_hint.config(text="释放鼠标以导入文件")
        except Exception as e:
            print(f"拖拽进入事件处理出错: {e}")
            
    def _on_drag_leave(self, event):
        """拖拽离开时的视觉反馈"""
        try:
            self.style.configure('Drag.TFrame', background='#ffffff', relief='solid', borderwidth=2)
            self.drag_frame.config(style="Drag.TFrame")
            self.drag_hint.config(text="请将图片文件或文件夹拖拽到此处\n\n或\n\n点击下方按钮选择文件")
        except Exception as e:
            print(f"拖拽离开事件处理出错: {e}")
            
    def _setup_fallback_drag_support(self):
        """设置拖拽支持失败时的回退方案"""
        print("启用剪贴板回退方案")
        self.bind('<ButtonRelease-1>', self._check_clipboard_for_files)
        
    def _setup_visual_feedback(self):
        """设置视觉反馈"""
        # 为整个对话框添加进入和离开事件，提供视觉反馈
        self.bind('<Enter>', lambda e: self.drag_frame.config(style="Drag.TFrame"))
        self.bind('<Leave>', lambda e: self.drag_frame.config(style="TFrame"))
    
    def _check_clipboard_for_files(self, event=None):
        """检查剪贴板中是否有文件路径"""
        print("检查剪贴板中的文件...")
        file_paths = []
        
        try:
            # 尝试使用tkinter的剪贴板方法
            try:
                clipboard_text = self.clipboard_get()
                print(f"通过tkinter获取剪贴板内容: {clipboard_text}")
                file_paths = self._process_clipboard_text(clipboard_text)
            except Exception as tk_error:
                print(f"tkinter剪贴板访问失败: {tk_error}")
                
                # 如果tkinter方法失败，尝试使用win32clipboard库（如果可用）
                try:
                    import win32clipboard
                    win32clipboard.OpenClipboard()
                    try:
                        # 检查是否有CF_HDROP格式的数据
                        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HDROP):
                            print("检测到CF_HDROP格式数据")
                            drop_data = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
                            # drop_data是一个元组，包含拖入的文件路径
                            for file_path in drop_data:
                                print(f"通过CF_HDROP获取文件: {file_path}")
                                if os.path.exists(file_path):
                                    file_paths.append(file_path)
                    finally:
                        win32clipboard.CloseClipboard()
                except ImportError:
                    print("win32clipboard库不可用，请安装pywin32以获得更好的Windows拖拽支持")
                except Exception as win_error:
                    print(f"win32clipboard操作失败: {win_error}")
            
            # 如果找到了文件路径，处理这些文件
            if file_paths:
                print(f"成功获取{len(file_paths)}个文件路径")
                self._display_dropped_files(file_paths)
                # 延迟处理，让用户有时间看到反馈
                self.after(500, self._process_dropped_files, file_paths)
        except Exception as e:
            print(f"检查剪贴板时发生错误: {e}")
            
    def _process_clipboard_text(self, clipboard_text):
        """处理剪贴板文本，提取文件路径"""
        file_paths = []
        
        try:
            # 检查是否直接是文件路径
            if os.path.exists(clipboard_text):
                print(f"剪贴板内容是单个文件路径: {clipboard_text}")
                file_paths.append(clipboard_text)
                return file_paths
            
            # 处理分号分隔的多个文件路径
            if ';' in clipboard_text:
                paths = clipboard_text.split(';')
                for path in paths:
                    path = path.strip()
                    if os.path.exists(path):
                        file_paths.append(path)
                        print(f"从分号分隔中提取文件: {path}")
                if file_paths:
                    return file_paths
            
            # 处理被引号包围的路径
            if clipboard_text.startswith('"') and clipboard_text.endswith('"'):
                unquoted_path = clipboard_text[1:-1]
                if os.path.exists(unquoted_path):
                    print(f"从引号中提取文件: {unquoted_path}")
                    file_paths.append(unquoted_path)
                    return file_paths
            
            # 处理路径中的换行符
            if '\n' in clipboard_text:
                paths = clipboard_text.split('\n')
                for path in paths:
                    path = path.strip()
                    if path and os.path.exists(path):
                        file_paths.append(path)
                        print(f"从换行分隔中提取文件: {path}")
                if file_paths:
                    return file_paths
            
            # 尝试清理路径并检查
            cleaned_path = clipboard_text.strip()
            if os.path.exists(cleaned_path):
                print(f"清理后找到文件: {cleaned_path}")
                file_paths.append(cleaned_path)
        except Exception as e:
            print(f"处理剪贴板文本时出错: {e}")
            
        return file_paths
    
    def _display_dropped_files(self, file_paths):
        """显示已拖拽的文件路径"""
        # 初始化dropped_files（如果不存在）或追加新文件
        if not hasattr(self, 'dropped_files'):
            self.dropped_files = []
        
        # 确保不添加重复文件
        for file_path in file_paths:
            if file_path not in self.dropped_files:
                self.dropped_files.append(file_path)
        
        # 启用文本框并清空内容
        self.files_text.config(state=tk.NORMAL)
        self.files_text.delete(1.0, tk.END)
        
        # 添加文件路径到文本框
        for file_path in self.dropped_files:
            self.files_text.insert(tk.END, f"{file_path}\n")
        
        # 禁用文本框
        self.files_text.config(state=tk.DISABLED)
        
        # 更新提示文本
        self.drag_hint.config(text=f"当前已添加 {len(self.dropped_files)} 个文件！\n\n点击确认继续或继续拖拽添加更多文件")
        
        # 更改拖拽区域样式以提供成功反馈
        self.style.configure('Drag.TFrame', background='#e0ffe0')  # 绿色背景表示成功
        self.drag_frame.config(style="Drag.TFrame")
        
        # 添加确认按钮（如果还没有）
        if not hasattr(self, 'btn_confirm'):
            self.btn_confirm = ttk.Button(
                self.btn_cancel.master,  # 与取消按钮在同一个框架
                text="确认", 
                command=lambda: self._process_dropped_files(self.dropped_files),
                padding=10
            )
            # 插入到取消按钮前面
            self.btn_confirm.pack(side=tk.RIGHT, padx=(10, 10), fill=tk.X, expand=True)
    
    def _process_dropped_files(self, file_paths):
        """处理拖拽的文件路径"""
        # 调用回调函数处理文件
        self.callback(file_paths)
        # 关闭对话框
        self.destroy()
    
    def _select_files(self):
        """打开文件选择器选择图片文件"""
        file_types = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("所有文件", "*.*")
        ]
        
        # 打开文件选择对话框，允许选择多个文件
        file_paths = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=file_types
        )
        
        if file_paths:
            # 处理选择的文件
            self.callback(file_paths)
            # 关闭对话框
            self.destroy()
    
    def _select_folder(self):
        """打开文件夹选择器选择图片文件夹"""
        folder_path = filedialog.askdirectory(title="选择图片文件夹")
        
        if folder_path:
            # 处理选择的文件夹
            self.callback([folder_path])
            # 关闭对话框
            self.destroy()
            
    def destroy(self):
        """销毁对话框"""
        # 确保清理任何资源
        # 使用tkinterdnd2库时，不再需要手动恢复窗口过程
        print("正在销毁对话框，清理资源...")
        
        # 移除所有绑定的事件
        try:
            self.unbind('<Enter>')
            self.unbind('<Leave>')
            self.unbind('<ButtonRelease-1>')
        except Exception as e:
            print(f"移除事件绑定时出错: {e}")
        
        super().destroy()


class WatermarkGUI:
    """水印工具的主界面"""
    
    def __init__(self, root):
        """初始化主界面
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title("图片水印工具")
        self.root.geometry("1024x768")  # 增大窗口尺寸以适应更好的布局
        
        # 图片列表
        self.image_paths = []
        self.current_image_index = -1
        self.current_image = None
        self.thumbnail_width = 100
        self.thumbnail_height = 180  # 进一步增加高度，确保有足够空间显示完整文件名
        
        # 水印参数
        self.watermark_text = "水印文字"
        self.watermark_color = "white"
        self.watermark_opacity = 0.5
        self.watermark_font = ("Arial", 36)
        self.watermark_position = "center"
        self.watermark_margin = 20
        
        # 支持的图片格式
        self.supported_formats = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]
        
        # 设置中文字体
        self._setup_fonts()
        
        # 创建界面
        self._create_widgets()
    
    def _setup_fonts(self):
        """设置中文字体支持"""
        # 尝试设置中文字体
        if sys.platform.startswith('win'):
            # Windows系统
            self.default_font = ('Microsoft YaHei UI', 10)
            self.button_font = ('Microsoft YaHei UI', 11, 'bold')
            self.title_font = ('Microsoft YaHei UI', 14, 'bold')
            self.watermark_default_font = ('Microsoft YaHei UI', 36)
        elif sys.platform.startswith('darwin'):
            # macOS系统
            self.default_font = ('Heiti TC', 10)
            self.button_font = ('Heiti TC', 11, 'bold')
            self.title_font = ('Heiti TC', 14, 'bold')
            self.watermark_default_font = ('Heiti TC', 36)
        else:
            # Linux系统
            self.default_font = ('WenQuanYi Micro Hei', 10)
            self.button_font = ('WenQuanYi Micro Hei', 11, 'bold')
            self.title_font = ('WenQuanYi Micro Hei', 14, 'bold')
            self.watermark_default_font = ('WenQuanYi Micro Hei', 36)
        
        # 配置Tkinter字体
        self.style = ttk.Style()
        self.style.configure('.', font=self.default_font)
        self.style.configure('TButton', font=self.button_font)
        
        # 更新水印字体设置
        self.watermark_font = self.watermark_default_font
    
    def _create_widgets(self):
        """创建主界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建顶部工具栏
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 添加图片按钮
        self.btn_add_images = ttk.Button(
            toolbar_frame, 
            text="添加图片", 
            command=self._show_import_dialog,
            padding=10
        )
        self.btn_add_images.pack(side=tk.LEFT, padx=(0, 10))
        
        # 应用水印按钮
        self.btn_apply_watermark = ttk.Button(
            toolbar_frame, 
            text="应用水印", 
            command=self._apply_watermark,
            padding=10
        )
        self.btn_apply_watermark.pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存图片按钮
        self.btn_save_image = ttk.Button(
            toolbar_frame, 
            text="保存图片", 
            command=self._save_image,
            padding=10
        )
        self.btn_save_image.pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存全部按钮
        self.btn_save_all = ttk.Button(
            toolbar_frame, 
            text="保存全部", 
            command=self._save_all_images,
            padding=10
        )
        self.btn_save_all.pack(side=tk.LEFT, padx=(0, 10))
        
        # 创建左侧控制面板和右侧预览区域
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(content_frame, text="水印设置", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 水印文本输入
        ttk.Label(control_frame, text="水印文字:", font=self.default_font).pack(anchor=tk.W, pady=(0, 5))
        self.watermark_entry = ttk.Entry(control_frame, font=self.default_font)
        self.watermark_entry.pack(fill=tk.X, pady=(0, 10))
        self.watermark_entry.insert(0, self.watermark_text)
        self.watermark_entry.bind('<KeyRelease>', self._on_watermark_change)
        
        # 水印颜色选择
        color_frame = ttk.Frame(control_frame)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(color_frame, text="水印颜色:", font=self.default_font).pack(side=tk.LEFT)
        self.color_button = ttk.Button(
            color_frame, 
            text="选择颜色", 
            command=self._choose_color,
            padding=5
        )
        self.color_button.pack(side=tk.RIGHT, padx=(10, 0))
        self.color_label = ttk.Label(
            color_frame, 
            text=self.watermark_color, 
            font=self.default_font, 
            width=10
        )
        self.color_label.pack(side=tk.RIGHT)
        
        # 水印透明度
        ttk.Label(control_frame, text="透明度:", font=self.default_font).pack(anchor=tk.W, pady=(0, 5))
        self.opacity_scale = ttk.Scale(
            control_frame, 
            from_=0.1, 
            to=1.0, 
            orient=tk.HORIZONTAL, 
            value=self.watermark_opacity,
            length=200,  # 增加滑块长度
            command=self._on_opacity_change
        )
        self.opacity_scale.pack(fill=tk.X, pady=(0, 10))
        self.opacity_label = ttk.Label(
            control_frame, 
            text=f"{int(self.watermark_opacity * 100)}%", 
            font=self.default_font
        )
        self.opacity_label.pack()
        
        # 水印位置选择
        ttk.Label(control_frame, text="水印位置:", font=self.default_font).pack(anchor=tk.W, pady=(0, 5))
        position_frame = ttk.Frame(control_frame)
        position_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建3x3的位置选择网格
        positions = [
            ("top-left", 0, 0), ("top-center", 0, 1), ("top-right", 0, 2),
            ("center-left", 1, 0), ("center", 1, 1), ("center-right", 1, 2),
            ("bottom-left", 2, 0), ("bottom-center", 2, 1), ("bottom-right", 2, 2)
        ]
        
        for pos, row, col in positions:
            btn = ttk.Button(
                position_frame, 
                text=pos.replace('-', '\n'), 
                command=lambda p=pos: self._set_watermark_position(p),
                padding=8,  # 增加按钮内边距
                width=8  # 增加按钮宽度
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky=tk.NSEW)
            position_frame.grid_columnconfigure(col, weight=1)
            position_frame.grid_rowconfigure(row, weight=1)
            
            # 默认选中中心位置
            if pos == self.watermark_position:
                btn.state(['pressed'])
            
            # 存储按钮引用
            setattr(self, f"pos_{pos.replace('-', '_')}", btn)
        
        # 水印边距
        ttk.Label(control_frame, text="水印边距:", font=self.default_font).pack(anchor=tk.W, pady=(0, 5))
        margin_frame = ttk.Frame(control_frame)
        margin_frame.pack(fill=tk.X, pady=(0, 10))
        self.margin_scale = ttk.Scale(
            margin_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL, 
            value=self.watermark_margin,
            length=200,  # 增加滑块长度
            command=self._on_margin_change
        )
        self.margin_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.margin_label = ttk.Label(
            margin_frame, 
            text=f"{self.watermark_margin}px", 
            font=self.default_font, 
            width=6
        )
        self.margin_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 右侧预览区域
        preview_frame = ttk.LabelFrame(content_frame, text="图片预览", padding="10")
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 画布容器
        canvas_container = ttk.Frame(preview_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建画布用于显示图片
        self.canvas = tk.Canvas(canvas_container, bg="#f0f0f0")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定画布大小变化事件
        self.canvas.bind('<Configure>', self._on_canvas_resize)
        
        # 预览导航按钮
        nav_frame = ttk.Frame(preview_frame)
        nav_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.btn_prev = ttk.Button(
            nav_frame, 
            text="上一张", 
            command=self._prev_image,
            padding=8
        )
        self.btn_prev.pack(side=tk.LEFT, padx=(0, 10))
        
        self.image_counter = ttk.Label(
            nav_frame, 
            text="0/0", 
            font=self.default_font,
            width=10
        )
        self.image_counter.pack(side=tk.LEFT, padx=(10, 10))
        
        self.btn_next = ttk.Button(
            nav_frame, 
            text="下一张", 
            command=self._next_image,
            padding=8
        )
        self.btn_next.pack(side=tk.LEFT, padx=(10, 0))
        
        # 图片列表区域
        list_frame = ttk.LabelFrame(main_frame, text="已添加图片", padding="10")
        list_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 创建图片列表
        self.scroll_frame = ttk.Frame(list_frame)
        self.scroll_frame.pack(fill=tk.X, expand=True)
        
        self.scroll_canvas = tk.Canvas(self.scroll_frame, height=200, bg="white")  # 增加画布高度，确保能显示完整的缩略图和文件名
        self.scroll_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.scrollbar = ttk.Scrollbar(
            self.scroll_frame, 
            orient=tk.HORIZONTAL, 
            command=self.scroll_canvas.xview
        )
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.scroll_canvas.configure(xscrollcommand=self.scrollbar.set)
        
        self.list_container = ttk.Frame(self.scroll_canvas)
        self.scroll_canvas_window = self.scroll_canvas.create_window(
            (0, 0), 
            window=self.list_container, 
            anchor="nw"
        )
        
        # 绑定滚动事件
        self.list_container.bind(
            "<Configure>", 
            lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        )
        
        # 初始化禁用状态
        self._update_ui_state()
    
    def _update_image_list(self):
        """更新图片列表显示"""
        # 清空当前列表
        for widget in self.list_container.winfo_children():
            widget.destroy()
        
        # 显示每个图片的缩略图
        for i, image_path in enumerate(self.image_paths):
            # 创建图片项框架
            item_frame = ttk.Frame(self.list_container)
            item_frame.grid(row=0, column=i, padx=5, pady=5)
            
            try:
                # 加载图片并创建缩略图
                pil_image = Image.open(image_path)
                pil_image.thumbnail((self.thumbnail_width, self.thumbnail_height), Image.Resampling.LANCZOS)
                
                # 转换为Tkinter可用的图像格式
                thumbnail = ImageTk.PhotoImage(pil_image)
                
                # 创建标签显示缩略图
                img_label = ttk.Label(item_frame, image=thumbnail)
                img_label.image = thumbnail  # 保存引用以防止被垃圾回收
                img_label.pack()
                
                # 获取文件名（不包含路径）
                filename = os.path.basename(image_path)
                
                # 增加允许显示的文件名长度，并添加悬停提示
                max_display_length = 25
                if len(filename) > max_display_length:
                    display_name = filename[:max_display_length-3] + "..."
                else:
                    display_name = filename
                
                # 创建标签显示文件名，并设置tooltip显示完整文件名
                name_label = ttk.Label(item_frame, text=display_name, font=self.default_font, wraplength=self.thumbnail_width)
                name_label.pack(pady=(5, 0))
                
                # 添加悬停提示功能以显示完整文件名
                def on_enter(event, full_name=filename):
                    # 创建临时提示窗口
                    tip = tk.Toplevel(self)
                    tip.wm_overrideredirect(True)  # 无边框窗口
                    tip.wm_geometry(f"+{event.x_root+10}+{event.y_root-30}")
                    tip_label = ttk.Label(tip, text=full_name, background="#ffffe0", padding=5)
                    tip_label.pack()
                    event.widget.tip_window = tip
                
                def on_leave(event):
                    if hasattr(event.widget, 'tip_window'):
                        event.widget.tip_window.destroy()
                        del event.widget.tip_window
                
                # 绑定悬停事件
                name_label.bind("<Enter>", on_enter)
                name_label.bind("<Leave>", on_leave)
                
                # 添加点击事件
                item_frame.bind("<Button-1>", lambda e, idx=i: self._select_image(idx))
                img_label.bind("<Button-1>", lambda e, idx=i: self._select_image(idx))
                name_label.bind("<Button-1>", lambda e, idx=i: self._select_image(idx))
                
                # 如果是当前选中的图片，添加高亮效果
                if i == self.current_image_index:
                    item_frame.configure(relief="solid", borderwidth=2)
                
            except Exception as e:
                # 如果加载图片失败，显示错误信息
                error_label = ttk.Label(item_frame, text="无法加载", font=self.default_font)
                error_label.pack(pady=20)
                print(f"加载图片缩略图失败: {str(e)}")
        
        # 更新滚动区域
        self.list_container.update_idletasks()
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        
    def _select_image(self, index):
        """选择指定索引的图片"""
        if 0 <= index < len(self.image_paths):
            self.current_image_index = index
            self._display_image()
            self._update_ui_state()
            self._update_image_list()  # 更新列表以反映选中状态
    
    def _show_import_dialog(self):
        """显示导入图片对话框"""
        print("开始显示导入图片对话框")
        # 定义回调函数，用于处理导入的文件
        def handle_imported_files(file_paths):
            print(f"收到文件路径: {file_paths}")
            # 使用discover_inputs函数来处理文件路径
            import_result = discover_inputs(file_paths)
            print(f"discover_inputs返回结果: {import_result}")
            print(f"发现的文件数量: {len(import_result.files)}")
            
            # 将发现的图片添加到图片列表
            new_images = []
            for file_path in import_result.files:
                # 检查文件是否为支持的图片格式
                ext = os.path.splitext(file_path)[1].lower()
                print(f"检查文件: {file_path}, 扩展名: {ext}, 是否支持: {ext in self.supported_formats}")
                if ext in self.supported_formats:
                    new_images.append(str(file_path))
                    
            # 添加新图片到列表
            print(f"支持的图片数量: {len(new_images)}")
            print(f"当前支持的格式: {self.supported_formats}")
            if new_images:
                self.image_paths.extend(new_images)
                print(f"添加后图片总数: {len(self.image_paths)}")
                
                # 如果这是第一次添加图片，选中第一张
                if self.current_image_index == -1:
                    self.current_image_index = 0
                    print(f"设置当前图片索引: {self.current_image_index}")
                    self._display_image()
                
                # 更新UI
                self._update_ui_state()
                
                # 显示成功消息
                messagebox.showinfo("导入成功", f"成功导入 {len(new_images)} 张图片")
            else:
                print("没有找到支持的图片格式")
                messagebox.showwarning("导入失败", "没有找到支持的图片格式")
        
        # 创建并显示导入对话框
        dialog = ImportDialog(self.root, handle_imported_files)
        
    def _apply_watermark(self):
        """应用水印到当前图片"""
        if self.current_image and self.current_image_index >= 0:
            try:
                # 获取水印参数
                watermark_text = self.watermark_entry.get()
                
                # 创建水印选项
                watermark_options = TextWatermarkOptions(
                    text=watermark_text,
                    font=self.watermark_font,
                    color=self.watermark_color,
                    opacity=self.watermark_opacity,
                    position=GridPosition[self.watermark_position.upper().replace('-', '_')],
                    margin=self.watermark_margin
                )
                
                # 应用水印
                self.current_image = apply_text_watermark(self.current_image, watermark_options)
                
                # 更新预览
                self._display_image()
                
                # 显示成功消息
                messagebox.showinfo("成功", "水印已成功应用")
            except Exception as e:
                messagebox.showerror("错误", f"应用水印时出错: {str(e)}")
        
    def _save_image(self):
        """保存当前处理过的图片"""
        if self.current_image and self.current_image_index >= 0:
            try:
                # 获取原始文件路径和名称
                original_path = self.image_paths[self.current_image_index]
                original_name = os.path.basename(original_path)
                name_without_ext, ext = os.path.splitext(original_name)
                
                # 默认保存路径
                default_dir = os.path.dirname(original_path)
                default_filename = f"{name_without_ext}_watermark{ext}"
                
                # 打开文件保存对话框
                file_path = filedialog.asksaveasfilename(
                    title="保存图片",
                    defaultextension=ext,
                    filetypes=[
                        ("JPEG图片", "*.jpg *.jpeg"),
                        ("PNG图片", "*.png"),
                        ("BMP图片", "*.bmp"),
                        ("所有文件", "*.*")
                    ],
                    initialdir=default_dir,
                    initialfile=default_filename
                )
                
                if file_path:
                    # 保存图片
                    self.current_image.save(file_path)
                    messagebox.showinfo("成功", f"图片已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存图片时出错: {str(e)}")
        
    def _save_all_images(self):
        """保存所有处理过的图片"""
        if not self.image_paths:
            messagebox.showinfo("提示", "没有图片可保存")
            return
        
        try:
            # 选择保存目录
            save_dir = filedialog.askdirectory(title="选择保存目录")
            
            if save_dir:
                # 准备导出选项
                export_options = ExportOptions(
                    naming_mode=NamingMode.APPEND_SUFFIX,
                    suffix="_watermark",
                    resize_mode=ResizeMode.NO_RESIZE,
                    output_dir=Path(save_dir)
                )
                
                # 显示进度消息
                messagebox.showinfo("开始保存", f"开始保存 {len(self.image_paths)} 张图片...")
                
                # 保存所有图片（注意：这里简化了实现，实际应该使用export_images函数）
                saved_count = 0
                for i, img_path in enumerate(self.image_paths):
                    try:
                        # 打开原始图片
                        img = Image.open(img_path)
                        
                        # 获取水印参数
                        watermark_text = self.watermark_entry.get()
                        
                        # 创建水印选项
                        watermark_options = TextWatermarkOptions(
                            text=watermark_text,
                            font=self.watermark_font,
                            color=self.watermark_color,
                            opacity=self.watermark_opacity,
                            position=GridPosition[self.watermark_position.upper().replace('-', '_')],
                            margin=self.watermark_margin
                        )
                        
                        # 应用水印
                        watermarked_img = apply_text_watermark(img, watermark_options)
                        
                        # 构造保存路径
                        original_name = os.path.basename(img_path)
                        name_without_ext, ext = os.path.splitext(original_name)
                        save_path = os.path.join(save_dir, f"{name_without_ext}_watermark{ext}")
                        
                        # 保存图片
                        watermarked_img.save(save_path)
                        saved_count += 1
                    except Exception as e:
                        print(f"保存图片 {img_path} 时出错: {str(e)}")
                
                # 显示完成消息
                messagebox.showinfo("完成", f"成功保存 {saved_count} 张图片到: {save_dir}")
        except Exception as e:
            messagebox.showerror("错误", f"保存图片时出错: {str(e)}")
    
    def _next_image(self):
        """显示下一张图片"""
        if self.image_paths and self.current_image_index < len(self.image_paths) - 1:
            self.current_image_index += 1
            self._display_image()
            self._update_ui_state()
    
    def _prev_image(self):
        """显示上一张图片"""
        if self.image_paths and self.current_image_index > 0:
            self.current_image_index -= 1
            self._display_image()
            self._update_ui_state()
    
    def _display_image(self):
        """在画布上显示当前图片"""
        if self.current_image_index >= 0 and self.current_image_index < len(self.image_paths):
            try:
                # 打开图片
                image_path = self.image_paths[self.current_image_index]
                self.current_image = Image.open(image_path)
                
                # 获取画布尺寸
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                # 如果画布尺寸太小，使用默认尺寸
                if canvas_width < 100 or canvas_height < 100:
                    canvas_width = 600
                    canvas_height = 400
                
                # 计算图片缩放比例
                img_width, img_height = self.current_image.size
                scale = min(canvas_width / img_width, canvas_height / img_height)
                
                # 缩放图片
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                resized_img = self.current_image.resize((new_width, new_height), Image.LANCZOS)
                
                # 转换为Tkinter可用的格式
                self.tk_image = ImageTk.PhotoImage(resized_img)
                
                # 清除画布并显示图片
                self.canvas.delete("all")
                self.canvas.create_image(
                    canvas_width // 2, 
                    canvas_height // 2, 
                    image=self.tk_image,
                    anchor=tk.CENTER
                )
            except Exception as e:
                print(f"显示图片时出错: {str(e)}")
                messagebox.showerror("错误", f"显示图片时出错: {str(e)}")
    
    def _on_watermark_change(self, event=None):
        """水印文本改变时的处理函数"""
        self.watermark_text = self.watermark_entry.get()
        
    def _choose_color(self):
        """选择水印颜色"""
        color = colorchooser.askcolor(initialcolor=self.watermark_color)
        if color[1]:  # color[1]是十六进制颜色代码
            self.watermark_color = color[1]
            self.color_label.config(text=color[1])
    
    def _on_margin_change(self, value):
        """水印边距改变时的处理函数"""
        self.watermark_margin = int(float(value))
        self.margin_label.config(text=f"{self.watermark_margin}px")
    
    def _on_canvas_resize(self, event):
        """画布大小改变时的处理函数"""
        if self.current_image:
            self._display_image()
            
    def _on_opacity_change(self, value):
        """水印透明度改变时的处理函数"""
        self.watermark_opacity = float(value)
        self.opacity_label.config(text=f"{int(self.watermark_opacity * 100)}%")
        
    def _on_fontsize_change(self, event=None):
        """水印字体大小改变时的处理函数"""
        try:
            font_size = int(self.fontsize_entry.get())
            # 确保字体大小在合理范围内
            if 10 <= font_size <= 500:
                self.watermark_font = (self.watermark_font[0], font_size)
        except ValueError:
            # 如果输入不是整数，不做处理
            pass
            
    def _on_font_change(self, event=None):
        """水印字体改变时的处理函数"""
        font_name = self.font_combobox.get()
        self.watermark_font = (font_name, self.watermark_font[1])
    
    def _update_ui_state(self):
        """更新UI状态，根据当前是否有图片选择来启用/禁用按钮"""
        # 更新图片计数器
        total = len(self.image_paths)
        current = self.current_image_index + 1 if self.current_image_index >= 0 else 0
        self.image_counter.config(text=f"{current}/{total}")
        
        # 根据是否有图片来启用/禁用按钮
        has_images = total > 0
        has_current_image = self.current_image_index >= 0
        
        # 启用/禁用导航按钮
        self.btn_prev.config(state=tk.NORMAL if has_images and self.current_image_index > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if has_images and self.current_image_index < total - 1 else tk.DISABLED)
        
        # 启用/禁用应用水印按钮
        self.btn_apply_watermark.config(state=tk.NORMAL if has_current_image else tk.DISABLED)
        
        # 启用/禁用保存按钮
        self.btn_save_image.config(state=tk.NORMAL if has_current_image else tk.DISABLED)
        self.btn_save_all.config(state=tk.NORMAL if has_images else tk.DISABLED)
        
        # 更新图片列表显示
        self._update_image_list()


def main():
    """主函数"""
    # 创建根窗口
    if tkinterdnd2_available:
        # 使用tkinterdnd2的Tk类以支持拖拽
        root = tkinterdnd.Tk()
    else:
        # 使用标准Tk类
        root = tk.Tk()
    
    app = WatermarkGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()