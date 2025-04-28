@echo off
chcp 65001 >nul
REM 设置变量是否为发布版本（1 为发布版本，0 为测试版本）
set IS_RELEASE=1

REM 设置输出文件夹和文件名变量
set OUTPUT_DIR=dist
set RELEASE_NAME=pachong_gui
set DEBUG_NAME=shuangmian_debug

REM 检查 PyInstaller 是否已安装
python -m pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    python -m pip install --upgrade pyinstaller
)

REM 删除 dist 文件夹（如果存在）
if exist "%OUTPUT_DIR%" (
    rmdir /s /q "%OUTPUT_DIR%"
)

REM 设置 pyinstaller 命令的通用部分
set PYINSTALLER_CMD=pyinstaller --icon=./static/icon/shuangmian.ico --add-data "static;static" Main.py

REM 根据 IS_RELEASE 变量调整 pyinstaller 命令
if %IS_RELEASE%==1 (
    %PYINSTALLER_CMD% --noconsole --name=%RELEASE_NAME%
) else (
    %PYINSTALLER_CMD% --name=%DEBUG_NAME%
)

REM 清理临时文件（可选）
if exist "build" (
    rmdir /s /q build
)
if exist "*.spec" (
    del /q *.spec
)