@echo off
echo Installing watermark tool dependencies...
pip install -r requirements.txt
echo.
echo Installation complete!
echo.
echo Usage examples:
echo   python watermark_tool.py C:\path\to\images
echo   python watermark_tool.py C:\path\to\images --font-size 30 --color red --position center
echo.
pause
