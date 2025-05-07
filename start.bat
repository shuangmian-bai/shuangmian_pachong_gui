@echo off
REM 进入当前目录
cd /d %~dp0%

REM 激活虚拟环境（Windows）
call venv\Scripts\activate

REM 运行主程序
python main.py

REM 按任意键关闭窗口（方便查看错误信息）
pause
