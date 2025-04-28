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
    echo PyInstaller 未安装，正在安装...
    python -m pip install --upgrade pyinstaller
)

REM 删除输出文件夹（如果存在）
if exist "%OUTPUT_DIR%" (
    echo 正在删除旧的输出文件夹...
    rmdir /s /q "%OUTPUT_DIR%"
)

REM 设置 pyinstaller 命令的通用部分
set PYINSTALLER_CMD=pyinstaller --icon=./static/icon/shuangmian.ico --add-data "static;static" Main.py

REM 打包多文件版本
if %IS_RELEASE%==1 (
    echo 正在打包发布版本（多文件）...
    %PYINSTALLER_CMD% --noconsole --name=%RELEASE_NAME%
) else (
    echo 正在打包调试版本（多文件）...
    %PYINSTALLER_CMD% --name=%DEBUG_NAME%
)

REM 打包单文件版本
set SINGLE_EXE_NAME=%RELEASE_NAME%
if %IS_RELEASE%==0 (
    set SINGLE_EXE_NAME=%DEBUG_NAME%
)
echo 正在打包单文件版本...
%PYINSTALLER_CMD% --onefile --noconsole --name=%SINGLE_EXE_NAME% --distpath .

REM 清理临时文件
echo 正在清理临时文件...
if exist "build" (
    rmdir /s /q build
)
if exist "*.spec" (
    del /q *.spec
)

echo 打包完成！
pause