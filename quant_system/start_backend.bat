@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   股票量化系统 - 后端启动脚本
echo ========================================
echo.

REM 设置颜色
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "RESET=%ESC%[0m"

echo %BLUE%[信息]%RESET% 启动后端服务...
echo.

REM 切换到后端目录
cd backend

REM 检查虚拟环境
if not exist "venv" (
    echo %YELLOW%[警告]%RESET% 虚拟环境不存在，正在创建...
    python -m venv venv
    if errorlevel 1 (
        echo %RED%[错误]%RESET% 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo %GREEN%[成功]%RESET% 虚拟环境创建成功
)

REM 激活虚拟环境
echo %BLUE%[信息]%RESET% 激活虚拟环境...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo %RED%[错误]%RESET% 激活虚拟环境失败
    pause
    exit /b 1
)
echo %GREEN%[成功]%RESET% 虚拟环境已激活

REM 检查依赖
echo %BLUE%[信息]%RESET% 检查依赖包...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[警告]%RESET% 依赖包未安装，正在安装...
    echo %BLUE%[信息]%RESET% 这可能需要几分钟时间，请耐心等待...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    if errorlevel 1 (
        echo %RED%[错误]%RESET% 安装依赖失败
        pause
        exit /b 1
    )
    echo %GREEN%[成功]%RESET% 依赖包安装完成
) else (
    echo %GREEN%[成功]%RESET% 依赖包已安装
)

REM 检查配置文件
if not exist "..\configs\.env" (
    echo %YELLOW%[警告]%RESET% 配置文件不存在，使用默认配置
    echo %YELLOW%[提示]%RESET% 请创建configs/.env文件配置数据库连接等信息
)

REM 创建日志目录
if not exist "logs" mkdir logs

echo.
echo %BLUE%[信息]%RESET% 启动FastAPI服务...
echo %BLUE%[信息]%RESET% 服务地址: http://localhost:8000
echo %BLUE%[信息]%RESET% API文档: http://localhost:8000/docs
echo %BLUE%[信息]%RESET% 按 Ctrl+C 停止服务
echo.

REM 启动服务
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo %BLUE%[信息]%RESET% 后端服务已停止
pause