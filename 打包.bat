@echo off
REM 设置当前工作目录为脚本所在目录
cd /d "%~dp0"

REM 检查 PyInstaller 是否已安装
python -m pip install --upgrade pyinstaller

REM 打包 Main.py 为多文件可执行文件，并包含静态资源
pyinstaller ^
    --add-data "static/icon/shuangmian.ico;static/icon" ^
    --add-data "Settings.ini;." ^
    Main.py

REM 清理临时文件（可选）
rmdir /s /q build
del /q *.spec

REM 提示用户打包完成
echo.
echo 打包完成！可执行文件位于 dist 目录中。
pause
