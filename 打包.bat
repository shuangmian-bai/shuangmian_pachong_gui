@echo off
REM 设置变量是否为发布版本（1 为发布版本，0 为测试版本）
set IS_RELEASE=1

REM 检查 PyInstaller 是否已安装
python -m pip install --upgrade pyinstaller

REM 删除 dist 文件夹（如果存在）
if exist "dist" (
    rmdir /s /q dist
)

REM 根据 IS_RELEASE 变量设置 pyinstaller 命令
if %IS_RELEASE%==1 (
    REM 打包 Main.py 为多文件可执行文件，并设置图标，且不显示控制台窗口
    pyinstaller --noconsole --icon=./static/icon/shuangmian.ico --name=shuangmian_pachong_gui Main.py
) else (
    REM 打包 Main.py 为多文件可执行文件，并设置图标，显示控制台窗口
    pyinstaller --icon=./static/icon/shuangmian.ico --name=shuangmian_pachong_gui Main.py
)

REM 复制 static 文件夹到 dist 目录
xcopy /s /e /i "static" "dist\shuangmian_pachong_gui\static"

REM 清理临时文件（可选）
rmdir /s /q build
del /q *.spec
