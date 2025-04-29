@echo off
chcp 65001 >nul

REM 设置变量是否为发布版本（1 为发布版本，0 为测试版本）
set IS_RELEASE=1

REM 设置输出文件夹和文件名变量
set OUTPUT_DIR=dist
set RELEASE_NAME=pachong_gui
set DEBUG_NAME=shuangmian_debug

REM 检查 PyInstaller 是否已安装
pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
   echo PyInstaller 未安装，请先安装 PyInstaller。
   echo 安装命令：pip install pyinstaller
   echo.
   echo 按下任意键后退出...
   pause >nul
   exit /b 1
)
echo PyInstaller 已安装。

REM 删除输出文件夹（如果存在）
if exist "%OUTPUT_DIR%" (
    echo 正在删除旧的输出文件夹...
    rmdir /s /q "%OUTPUT_DIR%"
)

REM 设置 pyinstaller 命令的通用部分
set PYINSTALLER_CMD=pyinstaller --icon=./static/icon/shuangmian.ico --add-data "static;static" --hidden-import=importlib_resources.trees Main.py

REM 根据发布版本设置文件名
if %IS_RELEASE%==1 (
    set MULTI_EXE_NAME=%RELEASE_NAME%
    set SINGLE_EXE_NAME=%RELEASE_NAME%_单文件版本
) else (
    set MULTI_EXE_NAME=%DEBUG_NAME%
    set SINGLE_EXE_NAME=%DEBUG_NAME%_单文件版本
)

REM 删除旧的单文件可执行文件
if exist "%SINGLE_EXE_NAME%.exe" (
    echo 正在删除旧的单文件可执行文件...
    del /q "%SINGLE_EXE_NAME%.exe"
)

REM 打包多文件版本
echo 正在打包多文件版本...
%PYINSTALLER_CMD% --noconsole --name=%MULTI_EXE_NAME%
if %errorlevel% neq 0 (
    echo 打包多文件版本失败。
    pause
    exit /b 1
)

REM 打包单文件版本
echo 正在打包单文件版本...
%PYINSTALLER_CMD% --onefile --noconsole --name=%SINGLE_EXE_NAME% --distpath .
if %errorlevel% neq 0 (
    echo 打包单文件版本失败。
    pause
    exit /b 1
)

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
