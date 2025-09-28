@echo off
REM 运行水印GUI应用程序

REM 设置Python环境变量（如果需要）
REM set PATH=C:\Python39\Scripts;C:\Python39;%PATH%

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境。请先安装Python。
    pause
    exit /b 1
)

REM 运行水印GUI应用程序
python watermark_gui.py

REM 如果程序意外退出，显示错误信息
if %errorlevel% neq 0 (
    echo 程序执行出错。
    pause
)