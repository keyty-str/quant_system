"""
健康检查路由
"""

from fastapi import APIRouter
from datetime import datetime
from loguru import logger

router = APIRouter()


@router.get("/")
async def health_check():
    """健康检查接口 - 包含所有服务状态"""
    from src.data.storage.mongodb import MongoDB
    from src.data.storage.redis_cache import RedisCache
    
    # 检查 MongoDB 连接状态
    mongodb_connected = False
    try:
        mongodb_connected = await MongoDB.check_connection()
    except Exception as e:
        logger.error(f"MongoDB健康检查失败: {e}")
    
    # 检查 Redis 连接状态
    redis_connected = False
    try:
        redis_connected = await RedisCache.check_connection()
    except Exception as e:
        logger.error(f"Redis健康检查失败: {e}")
    
    # 总体状态
    all_healthy = mongodb_connected and redis_connected
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.now().isoformat(),
        "service": "股票量化交易系统",
        "version": "1.0.0",
        "services": {
            "mongodb": mongodb_connected,
            "redis": redis_connected
        }
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