"""
健康检查路由
"""

from fastapi import APIRouter
from datetime import datetime
from loguru import logger

router = APIRouter()


@router.get("/")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "股票量化交易系统",
        "version": "1.0.0"
    }


@router.get("/ping")
async def ping():
    """简单ping测试"""
    return {"message": "pong"}


@router.get("/ready")
async def readiness_check():
    """就绪检查"""
    # 这里可以检查数据库连接等
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/live")
async def liveness_check():
    """存活检查"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }