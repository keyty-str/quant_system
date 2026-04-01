@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   股票量化系统 - 前端启动脚本
echo ========================================
echo.

REM 设置颜色
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "RESET=%ESC%[0m"

echo %BLUE%[信息]%RESET% 启动前端服务...
echo.

REM 切换到前端目录
cd frontend

REM 检查package.json
if not exist "package.json" (
    echo %RED%[错误]%RESET% package.json文件不存在
    pause
    exit /b 1
)

REM 检查node_modules
if not exist "node_modules" (
    echo %YELLOW%[警告]%RESET% 依赖包未安装，正在安装...
    echo %BLUE%[信息]%RESET% 这可能需要几分钟时间，请耐心等待...
    npm install --registry=https://registry.npmmirror.com
    if errorlevel 1 (
        echo %RED%[错误]%RESET% 安装依赖失败
        pause
        exit /b 1
    )
    echo %GREEN%[成功]%RESET% 依赖包安装完成
) else (
    echo %GREEN%[成功]%RESET% 依赖包已安装
)

REM 检查环境配置
if not exist ".env" (
    echo %BLUE%[信息]%RESET% 创建前端环境配置...
    (
        echo # 前端环境配置
        echo VITE_API_BASE_URL=http://localhost:8000
        echo VITE_WS_URL=ws://localhost:8000
    ) > .env
    echo %GREEN%[成功]%RESET% 环境配置创建完成
)

echo.
echo %BLUE%[信息]%RESET% 启动React开发服务器...
echo %BLUE%[信息]%RESET% 服务地址: http://localhost:5173
echo %BLUE%[信息]%RESET% 按 Ctrl+C 停止服务
echo.

REM 启动开发服务器
npm run dev

echo.
echo %BLUE%[信息]%RESET% 前端服务已停止
pause