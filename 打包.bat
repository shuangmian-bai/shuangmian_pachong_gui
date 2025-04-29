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

REM 设置版本名称
if %IS_RELEASE%==1 (
    set MULTI_EXE_NAME=%RELEASE_NAME%
    set SINGLE_EXE_NAME=%RELEASE_NAME%_单文件版本
    set CONSOLE_FLAG=
) else (
    set MULTI_EXE_NAME=%DEBUG_NAME%
    set SINGLE_EXE_NAME=%DEBUG_NAME%_单文件版本
    set CONSOLE_FLAG=--console
)

REM 定义统一的清理函数
:cleanup
if exist "build" (
    echo 正在清理 build 文件夹...
    rmdir /s /q build
)
if exist "*.spec" (
    echo 正在清理 spec 文件...
    del /q *.spec
)
goto :eof

REM 统一处理多文件和单文件版本
for %%M in ("多文件", "单文件") do (
    if "%%M"=="多文件" (
        set CURRENT_NAME=%MULTI_EXE_NAME%
        set ONEFILE_FLAG=
        set DISTPATH_FLAG=--distpath %OUTPUT_DIR%
    ) else (
        set CURRENT_NAME=%SINGLE_EXE_NAME%
        set ONEFILE_FLAG=--onefile
        set DISTPATH_FLAG=--distpath .
    )

    REM 删除旧的可执行文件
    if exist "%CURRENT_NAME%.exe" (
        echo 正在删除旧的 %%M 可执行文件...
        del /q "%CURRENT_NAME%.exe"
    )

    REM 打包版本
    echo 正在打包 %%M 版本...
    %PYINSTALLER_CMD% %ONEFILE_FLAG% %CONSOLE_FLAG% --name=%CURRENT_NAME% %DISTPATH_FLAG%

    REM 清理临时文件
    call :cleanup
)

echo 打包完成！
pause
