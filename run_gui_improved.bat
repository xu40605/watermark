@echo off
REM 改进版水印GUI应用程序启动脚本
REM 这个版本解决了双击运行时的路径问题和错误处理

REM 切换到批处理文件所在目录
cd /d %~dp0

REM 打印当前目录，便于调试
echo 当前工作目录: %cd%

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境。请先安装Python并确保添加到系统PATH。
    pause
    exit /b 1
)

REM 打印Python版本信息
python --version

REM 检查是否安装了必要的依赖
python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未找到Pillow库，正在尝试安装...
    pip install pillow
    if %errorlevel% neq 0 (
        echo 错误: 安装Pillow库失败。请手动运行 'pip install pillow'
        pause
        exit /b 1
    )
)

REM 运行水印GUI应用程序
echo 正在启动水印GUI应用程序...
python watermark_gui.py

REM 如果程序意外退出，显示详细错误信息
if %errorlevel% neq 0 (
    echo 错误: 程序执行出错，退出代码: %errorlevel%
    echo 请尝试在命令提示符中运行以下命令查看详细错误:
    echo cd /d %cd%
    echo python watermark_gui.py
    pause
)