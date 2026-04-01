# 股票量化系统 - 环境检测报告和运行指南

## 📊 当前系统环境检测结果

### ✅ 已检测的环境组件

| 组件               | 版本     | 状态        | 要求                |
| ------------------ | -------- | ----------- | ------------------- |
| **Python**         | 3.11.9   | ✅ 满足要求 | Python 3.9+         |
| **pip**            | 26.0.1   | ✅ 可用     | 最新版本            |
| **Node.js**        | v22.17.0 | ✅ 满足要求 | Node.js 16+         |
| **npm**            | 10.9.2   | ✅ 可用     | 最新版本            |
| **Docker**         | 28.3.3   | ✅ 可用     | Docker 20+          |
| **Docker Compose** | v2.39.2  | ✅ 可用     | Docker Compose 2.0+ |

### 🎯 环境评估结果

**总体评估：✅ 环境配置完美，所有组件均满足要求**

您的系统环境已经完全准备好运行股票量化系统，无需额外安装任何软件。

---

## 🚀 快速启动指南

### 方式一：使用自动化脚本（强烈推荐）

#### 1. 首次环境配置

```bash
# 运行环境配置脚本
setup_windows.bat
```

此脚本将自动：

- 检测系统环境
- 创建Python虚拟环境
- 安装所有Python依赖
- 安装所有Node.js依赖
- 创建配置文件

#### 2. 启动系统

**启动后端服务：**

```bash
start_backend.bat
```

**启动前端服务：**

```bash
start_frontend.bat
```

### 方式二：使用Docker Compose（推荐）

```bash
# 一键启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式三：手动启动

#### 后端启动

```bash
cd quant_system/backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 前端启动

```bash
cd quant_system/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 🌐 服务访问地址

### 使用Docker Compose部署

| 服务         | 地址                       | 说明        |
| ------------ | -------------------------- | ----------- |
| **前端界面** | http://localhost:3000      | React应用   |
| **后端API**  | http://localhost:8000      | FastAPI服务 |
| **API文档**  | http://localhost:8000/docs | Swagger UI  |

### 手动启动

| 服务         | 地址                       | 说明           |
| ------------ | -------------------------- | -------------- |
| **前端界面** | http://localhost:5173      | Vite开发服务器 |
| **后端API**  | http://localhost:8000      | FastAPI服务    |
| **API文档**  | http://localhost:8000/docs | Swagger UI     |

---

## ⚙️ 环境配置说明

### 1. 数据库配置

系统需要以下数据库服务：

#### MongoDB

- **默认地址**：`mongodb://localhost:27017/quant_system`
- **用途**：存储股票数据、回测结果、用户配置
- **安装**：Docker已包含，或单独安装MongoDB 6.0+

#### Redis

- **默认地址**：`redis://localhost:6379/0`
- **用途**：缓存实时数据、消息队列
- **安装**：Docker已包含，或单独安装Redis 7.0+

### 2. 数据源配置

#### Tushare Token（必需）

1. 访问 [Tushare官网](https://tushare.pro/)
2. 注册账号并获取Token
3. 在 `configs/.env` 文件中配置：
   ```
   TUSHARE_TOKEN=your_token_here
   ```

#### AkShare（可选）

- 已默认启用，无需额外配置
- 用于获取A股历史行情数据

### 3. 环境变量配置

编辑 `configs/.env` 文件：

```env
# 数据库配置
MONGODB_URL=mongodb://localhost:27017/quant_system
REDIS_URL=redis://localhost:6379/0

# API配置
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here

# 数据源配置
TUSHARE_TOKEN=your-tushare-token-here
AKSHARE_ENABLED=true

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/quant_system.log

# 前端配置
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🔧 系统功能模块

### 已实现的核心功能

#### 1. 数据采集模块

- ✅ AkShare数据源接入
- ✅ Tushare数据源接入
- ✅ 实时行情数据采集
- ✅ 历史数据存储

#### 2. 策略引擎

- ✅ 趋势跟随策略
- ✅ 均值回归策略
- ✅ 动量策略
- ✅ 技术指标计算

#### 3. 回测系统

- ✅ 历史回测引擎
- ✅ 性能评估指标
- ✅ 可视化报告
- ✅ 交易记录分析

#### 4. 预测系统

- ✅ 板块热度分析
- ✅ 趋势预测
- ✅ 置信度评估
- ✅ 预测准确度统计

#### 5. 协调调度系统

- ✅ 任务调度器
- ✅ 资源分配器
- ✅ 工作流管理
- ✅ 状态监控

#### 6. 可视化界面

- ✅ 仪表板（实时数据展示）
- ✅ 数据管理界面
- ✅ 策略管理界面
- ✅ 回测分析界面
- ✅ 预测结果界面
- ✅ 板块分析界面
- ✅ 系统设置界面

---

## 📋 使用流程

### 1. 首次使用

1. 运行 `setup_windows.bat` 配置环境
2. 编辑 `configs/.env` 配置Tushare Token
3. 启动数据库服务（MongoDB和Redis）
4. 启动后端和前端服务

### 2. 日常使用

1. 启动数据库服务
2. 运行 `start_backend.bat`
3. 运行 `start_frontend.bat`
4. 访问 http://localhost:5173

### 3. 数据采集

1. 在"数据管理"页面配置数据源
2. 设置股票池和时间范围
3. 启动数据采集任务
4. 监控采集进度

### 4. 策略开发

1. 在"策略管理"页面创建新策略
2. 配置策略参数和指标
3. 保存并激活策略
4. 查看策略信号

### 5. 回测分析

1. 在"回测系统"页面选择策略
2. 设置回测参数（时间、资金、股票池）
3. 运行回测任务
4. 分析回测结果和性能指标

### 6. 预测分析

1. 在"预测系统"页面生成预测
2. 选择预测周期（1周/1月/3月）
3. 查看热门板块排名
4. 分析预测置信度和理由

---

## 🛠️ 故障排除

### 常见问题及解决方案

#### 1. Python虚拟环境问题

**问题**：无法创建或激活虚拟环境
**解决**：

```bash
# 使用系统Python创建虚拟环境
python -m venv venv

# 如果失败，尝试使用完整路径
C:\Python311\python.exe -m venv venv
```

#### 2. 依赖安装失败

**问题**：pip安装依赖失败
**解决**：

```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 或者升级pip后重试
python -m pip install --upgrade pip
```

#### 3. Node.js依赖问题

**问题**：npm install失败
**解决**：

```bash
# 使用国内镜像源
npm install --registry=https://registry.npmmirror.com

# 或者清除缓存后重试
npm cache clean --force
npm install
```

#### 4. 数据库连接问题

**问题**：无法连接MongoDB或Redis
**解决**：

1. 确保数据库服务已启动
2. 检查连接地址和端口
3. 验证防火墙设置
4. 检查数据库认证信息

#### 5. 端口占用问题

**问题**：端口被占用
**解决**：

```bash
# 查看端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# 结束占用端口的进程
taskkill /PID <进程ID> /F
```

#### 6. 权限问题

**问题**：文件权限不足
**解决**：

1. 以管理员身份运行命令行
2. 检查文件夹权限
3. 修改文件夹权限设置

---

## 📞 技术支持

### 获取帮助

1. 查看README.md文档
2. 检查日志文件：`logs/quant_system.log`
3. 查看Docker日志：`docker-compose logs`
4. 访问API文档：http://localhost:8000/docs

### 系统监控

- **健康检查**：http://localhost:8000/health
- **系统状态**：http://localhost:8000/status
- **API文档**：http://localhost:8000/docs

---

## 🎯 下一步计划

系统已基本完成，后续可以扩展：

1. **更多数据源**：接入更多金融数据API
2. **机器学习策略**：集成ML算法进行预测
3. **实盘交易**：对接券商API实现自动化交易
4. **移动端应用**：开发iOS/Android应用
5. **云部署**：支持AWS、阿里云等云平台部署

---

## 📄 许可证

本项目仅供学习和研究使用，不构成任何投资建议。使用本系统进行实盘交易的风险由用户自行承担。

**祝您使用愉快！** 🎉
