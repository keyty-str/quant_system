@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   股票量化系统 - 环境配置和启动脚本
echo ========================================
echo.

REM 设置颜色
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "YELLOW=%ESC%[33m"
set "BLUE=%ESC%[34m"
set "RESET=%ESC%[0m"

echo %BLUE%[信息]%RESET% 开始检测系统环境...
echo.

REM 检测Python
echo %BLUE%[检测]%RESET% Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[错误]%RESET% Python未安装或不在PATH中
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo %GREEN%[成功]%RESET% Python版本: !PYTHON_VERSION!
)

REM 检测pip
echo %BLUE%[检测]%RESET% pip环境...
pip --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[错误]%RESET% pip未安装
    pause
    exit /b 1
) else (
    echo %GREEN%[成功]%RESET% pip已安装
)

REM 检测Node.js
echo %BLUE%[检测]%RESET% Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[错误]%RESET% Node.js未安装或不在PATH中
    pause
    exit /b 1
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo %GREEN%[成功]%RESET% Node.js版本: !NODE_VERSION!
)

REM 检测npm
echo %BLUE%[检测]%RESET% npm环境...
npm --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[错误]%RESET% npm未安装
    pause
    exit /b 1
) else (
    for /f "tokens=1" %%i in ('npm --version 2^>^&1') do set NPM_VERSION=%%i
    echo %GREEN%[成功]%RESET% npm版本: !NPM_VERSION!
)

REM 检测Docker
echo %BLUE%[检测]%RESET% Docker环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[警告]%RESET% Docker未安装或不在PATH中
    echo %YELLOW%[提示]%RESET% 您可以选择手动安装依赖或使用Docker部署
) else (
    echo %GREEN%[成功]%RESET% Docker已安装
)

echo.
echo %BLUE%[信息]%RESET% 开始配置项目环境...
echo.

REM 配置后端环境
echo %BLUE%[配置]%RESET% 后端Python环境...
cd backend

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo %BLUE%[信息]%RESET% 创建Python虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo %RED%[错误]%RESET% 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo %GREEN%[成功]%RESET% 虚拟环境创建成功
) else (
    echo %GREEN%[信息]%RESET% 虚拟环境已存在
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

REM 升级pip
echo %BLUE%[信息]%RESET% 升级pip...
python -m pip install --upgrade pip >nul 2>&1

REM 安装Python依赖
echo %BLUE%[信息]%RESET% 安装Python依赖包...
echo %BLUE%[信息]%RESET% 这可能需要几分钟时间，请耐心等待...
pip install -r requirements.txt
if errorlevel 1 (
    echo %RED%[错误]%RESET% 安装Python依赖失败
    echo %YELLOW%[提示]%RESET% 尝试使用国内镜像源...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    if errorlevel 1 (
        echo %RED%[错误]%RESET% 安装依赖失败，请检查网络连接
        pause
        exit /b 1
    )
)
echo %GREEN%[成功]%RESET% Python依赖安装完成

cd ..

REM 配置前端环境
echo %BLUE%[配置]%RESET% 前端Node.js环境...
cd frontend

REM 检查package.json
if not exist "package.json" (
    echo %RED%[错误]%RESET% package.json文件不存在
    pause
    exit /b 1
)

REM 安装Node.js依赖
echo %BLUE%[信息]%RESET% 安装Node.js依赖包...
echo %BLUE%[信息]%RESET% 这可能需要几分钟时间，请耐心等待...
npm install
if errorlevel 1 (
    echo %RED%[错误]%RESET% 安装Node.js依赖失败
    echo %YELLOW%[提示]%RESET% 尝试使用国内镜像源...
    npm install --registry=https://registry.npmmirror.com
    if errorlevel 1 (
        echo %RED%[错误]%RESET% 安装依赖失败，请检查网络连接
        pause
        exit /b 1
    )
)
echo %GREEN%[成功]%RESET% Node.js依赖安装完成

cd ..

REM 创建环境配置文件
echo %BLUE%[配置]%RESET% 创建环境配置文件...
cd configs

if not exist ".env" (
    echo %BLUE%[信息]%RESET% 创建.env配置文件...
    (
        echo # 股票量化系统配置文件
        echo # 数据库配置
        echo MONGODB_URL=mongodb://localhost:27017/quant_system
        echo REDIS_URL=redis://localhost:6379/0
        echo.
        echo # API配置
        echo API_HOST=0.0.0.0
        echo API_PORT=8000
        echo SECRET_KEY=your-secret-key-here
        echo.
        echo # 数据源配置
        echo TUSHARE_TOKEN=your-tushare-token-here
        echo AKSHARE_ENABLED=true
        echo.
        echo # 日志配置
        echo LOG_LEVEL=INFO
        echo LOG_FILE=logs/quant_system.log
        echo.
        echo # 前端配置
        echo VITE_API_BASE_URL=http://localhost:8000
    ) > .env
    echo %GREEN%[成功]%RESET% 配置文件创建完成
    echo %YELLOW%[提示]%RESET% 请编辑configs/.env文件配置您的Tushare Token
) else (
    echo %GREEN%[信息]%RESET% 配置文件已存在
)

cd ..

echo.
echo %GREEN%[完成]%RESET% 环境配置完成！
echo.
echo ========================================
echo   启动方式说明
echo ========================================
echo.
echo %BLUE%方式1: 使用Docker Compose（推荐）%RESET%
echo   命令: docker-compose up -d
echo   访问: http://localhost:3000
echo.
echo %BLUE%方式2: 手动启动%RESET%
echo   后端: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn src.main:app --reload
echo   前端: cd frontend ^&^& npm run dev
echo   访问: http://localhost:5173
echo.
echo %BLUE%方式3: 使用启动脚本%RESET%
echo   后端: start_backend.bat
echo   前端: start_frontend.bat
echo.
echo ========================================
echo   重要提示
echo ========================================
echo.
echo %YELLOW%1.%RESET% 请确保MongoDB和Redis服务已启动
echo %YELLOW%2.%RESET% 请配置configs/.env中的Tushare Token
echo %YELLOW%3.%RESET% 首次运行需要初始化数据库
echo %YELLOW%4.%RESET% 详细文档请查看README.md
echo.
echo %GREEN%祝您使用愉快！%RESET%
echo.

pause