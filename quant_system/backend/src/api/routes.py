"""
API路由模块
"""

from fastapi import APIRouter
from src.api.routes import health, data, strategy, backtest, prediction, sector

# 创建API路由器
api_router = APIRouter()

# 注册路由
api_router.include_router(health.router, prefix="/health", tags=["健康检查"])
api_router.include_router(data.router, prefix="/data", tags=["数据管理"])
api_router.include_router(strategy.router, prefix="/strategy", tags=["策略管理"])
api_router.include_router(backtest.router, prefix="/backtest", tags=["回测系统"])
api_router.include_router(prediction.router, prefix="/prediction", tags=["预测系统"])
api_router.include_router(sector.router, prefix="/sector", tags=["板块分析"])