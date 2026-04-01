# 股票量化交易系统 - A股热门板块预测

基于趋势跟随策略的股票量化系统，通过AkShare和Tushare的历史行情数据进行量化分析，预测未来一月的热门板块。

## 系统特性

- **数据源**：AkShare + Tushare 双数据源
- **策略类型**：趋势跟随策略
- **预测目标**：A股未来一月热门板块
- **存储方案**：MongoDB（长期存储）+ Redis（实时缓存）
- **部署方式**：Docker容器化部署
- **可视化**：React + Ant Design + ECharts 多端可视化界面

## 架构概览

```
┌─────────────────────────────────────────┐
│          协调调度层（借鉴三审流程）       │
│   中书(规划) → 门下(审查) → 尚书(执行)    │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│          可视化UI层（React前端）          │
│   Web端 + 移动端 + 数据大屏               │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│          应用服务层（FastAPI）            │
│   API网关 + 任务调度 + 回测引擎           │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│          策略计算层                       │
│   趋势策略 + 板块分析 + 信号生成         │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│          数据处理层                       │
│   数据清洗 + 特征工程 + 指标计算         │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│          数据接入层                       │
│   AkShare + Tushare + 实时行情          │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│          存储层                          │
│   MongoDB（历史数据）+ Redis（实时数据） │
└─────────────────────────────────────────┘
```

## 技术栈

### 后端

- Python 3.9+
- FastAPI (Web框架)
- MongoDB 6.0 (数据库)
- Redis 7.0 (缓存和消息队列)
- AkShare, Tushare (数据源)
- pandas, numpy, talib (数据处理)

### 前端

- React 18 + TypeScript
- Ant Design 5.x (UI组件库)
- ECharts 5.x (图表库)
- Redux Toolkit (状态管理)
- Vite (构建工具)

### 部署

- Docker + Docker Compose
- Nginx (反向代理和静态文件服务)

## 快速开始

### 1. 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.9+ (用于本地开发)
- Node.js 16+ (用于前端开发)

### 2. 使用Docker部署（推荐）

#### 2.1 克隆项目

```bash
cd quant_system
```

#### 2.2 配置环境变量

复制并修改配置文件：

```bash
cp configs/env.example configs/.env
```

编辑 `configs/.env` 文件，配置以下参数：

```env
# MongoDB配置
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DB=quant_system
MONGO_USER=admin
MONGO_PASS=your_password

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASS=your_password

# 数据源配置
AKSHARE_ENABLED=true
TUSHARE_TOKEN=your_tushare_token

# API配置
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your_secret_key
```

#### 2.3 启动服务

```bash
docker-compose up -d
```

这将启动以下服务：

- MongoDB数据库 (端口27017)
- Redis缓存 (端口6379)
- 后端API服务 (端口8000)
- 前端Web界面 (端口3000)
- Nginx反向代理 (端口80)

#### 2.4 访问系统

- Web界面: http://localhost
- API文档: http://localhost/api/docs
- 监控面板: http://localhost:3000 (如果需要)

### 3. 本地开发部署

#### 3.1 后端开发环境

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp ../configs/env.example ../configs/.env
# 编辑.env文件

# 启动后端服务
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3.2 前端开发环境

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端开发服务器默认运行在 http://localhost:5173

#### 3.3 数据库服务

使用Docker启动数据库服务：

```bash
# 启动MongoDB和Redis
docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=your_password mongo:6.0
docker run -d --name redis -p 6379:6379 redis:7.0-alpine
```

## 项目结构

```
quant_system/
├── backend/                 # 后端Python代码
│   ├── src/                # 源代码
│   │   ├── data/          # 数据采集和处理
│   │   ├── strategies/    # 策略实现
│   │   ├── backtest/      # 回测引擎
│   │   ├── prediction/    # 预测模块
│   │   ├── coordination/  # 协调调度
│   │   ├── api/           # API接口
│   │   └── utils/         # 工具函数
│   ├── tests/             # 测试代码
│   └── requirements.txt   # Python依赖
├── frontend/               # 前端React代码
│   ├── src/               # 源代码
│   │   ├── components/    # 通用组件
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API服务
│   │   ├── store/         # Redux状态
│   │   └── utils/         # 工具函数
│   ├── public/            # 静态资源
│   └── package.json       # 前端依赖
├── docker/                 # Docker配置
│   ├── nginx/             # Nginx配置
│   ├── mongodb/           # MongoDB初始化脚本
│   └── redis/             # Redis配置
├── configs/                # 配置文件
│   ├── env.example        # 环境变量示例
│   └── settings.py        # 应用配置
├── scripts/                # 脚本工具
├── docker-compose.yml      # Docker编排文件
└── README.md              # 项目文档
```

## 核心功能

### 1. 数据采集

- AkShare数据源：A股历史行情、板块数据
- Tushare数据源：补充数据、财务数据
- 实时行情：WebSocket实时推送

### 2. 策略引擎

- 趋势跟随策略：移动平均、MACD、布林带
- 板块热度分析：成交量、涨幅、资金流向
- 信号生成：买卖信号、板块推荐
- 风险控制：止损、仓位管理

### 3. 回测系统

- 历史回测：多股票、多时间段
- 性能评估：夏普比率、最大回撤、年化收益率
- 可视化报告：图表和统计报告

### 4. 预测模块

- 板块预测：基于趋势分析预测热门板块
- 置信度评估：为预测提供置信度评分
- 结果解释：提供预测依据和逻辑

### 5. 可视化界面

- 实时监控仪表板
- 策略分析界面
- 预测结果展示
- 数据管理模块

## 使用指南

### 1. 首次使用

1. 启动系统后，访问 http://localhost
2. 使用默认管理员账户登录（admin/admin123）
3. 配置数据源参数（Tushare Token等）
4. 初始化数据库和缓存

### 2. 数据采集

1. 进入"数据管理"页面
2. 点击"开始数据采集"
3. 选择数据源（AkShare/Tushare）
4. 设置采集参数（股票池、时间范围）
5. 等待采集完成

### 3. 策略配置

1. 进入"策略分析"页面
2. 创建新策略或选择现有策略
3. 配置策略参数（技术指标、阈值）
4. 保存策略配置

### 4. 回测分析

1. 进入"回测系统"页面
2. 选择策略和股票池
3. 设置回测时间范围
4. 启动回测
5. 查看回测结果和性能指标

### 5. 预测分析

1. 进入"预测结果"页面
2. 查看当前热门板块预测
3. 分析预测置信度
4. 查看历史预测准确度

## 监控和维护

### 1. 系统监控

- 访问 http://localhost/api/health 查看系统健康状态
- 查看日志文件：`logs/`目录
- 监控资源使用情况

### 2. 数据备份

```bash
# 备份MongoDB数据
docker exec mongodb mongodump --out /backup/$(date +%Y%m%d)

# 备份Redis数据
docker exec redis redis-cli BGSAVE
```

### 3. 系统更新

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d
```

## 故障排除

### 1. 数据库连接失败

- 检查MongoDB服务状态：`docker ps | grep mongodb`
- 检查连接配置：`configs/.env`
- 查看日志：`docker logs mongodb`

### 2. Redis连接失败

- 检查Redis服务状态：`docker ps | grep redis`
- 检查连接配置：`configs/.env`
- 查看日志：`docker logs redis`

### 3. API服务无法访问

- 检查后端服务状态：`docker ps | grep backend`
- 查看后端日志：`docker logs quant_system-backend-1`
- 检查端口占用：`netstat -tulpn | grep 8000`

### 4. 前端页面无法加载

- 检查前端服务状态：`docker ps | grep frontend`
- 查看前端日志：`docker logs quant_system-frontend-1`
- 检查Nginx配置：`docker exec nginx nginx -t`

## 开发指南

### 1. 代码规范

- Python代码遵循PEP8规范
- TypeScript代码使用ESLint和Prettier
- 提交前运行测试：`pytest` 和 `npm test`

### 2. 添加新策略

1. 在 `backend/src/strategies/` 创建新策略文件
2. 继承基类策略并实现必要方法
3. 在策略配置中注册新策略
4. 编写单元测试

### 3. 添加新数据源

1. 在 `backend/src/data/collectors/` 创建新适配器
2. 实现数据采集接口
3. 添加数据验证和清洗逻辑
4. 更新数据源配置

### 4. 添加新可视化组件

1. 在 `frontend/src/components/` 创建新组件
2. 使用Ant Design组件库
3. 集成ECharts图表
4. 添加响应式设计

## 许可证

本项目仅供学习和研究使用，不构成任何投资建议。使用本系统进行实盘交易的风险由用户自行承担。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交Issue到项目仓库
- 发送邮件到项目维护者

## 更新日志

### v1.0.0 (2026-04-01)

- 初始版本发布
- 实现基础数据采集功能
- 实现趋势跟随策略
- 实现回测系统
- 实现可视化界面
- 支持Docker部署
