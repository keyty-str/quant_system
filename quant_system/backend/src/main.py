"""
股票量化交易系统 - 后端主入口
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from loguru import logger

from src.api.routes import api_router
from src.data.storage.mongodb import MongoDB
from src.data.storage.redis_cache import RedisCache
from src.utils.config import get_settings
from src.utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    setup_logging()
    logger.info("股票量化系统启动中...")
    
    # 初始化数据库连接
    try:
        await MongoDB.connect()
        await RedisCache.connect()
        logger.info("数据库连接成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise
    
    yield
    
    # 关闭时执行
    await MongoDB.close()
    await RedisCache.close()
    logger.info("股票量化系统已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    
    app = FastAPI(
        title="股票量化交易系统API",
        description="基于趋势跟随策略的A股量化系统，支持板块预测和回测分析",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加路由
    app.include_router(api_router, prefix="/api")
    
    # 全局异常处理
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"全局异常: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误"}
        )
    
    # 健康检查
    @app.get("/health")
    async def health_check():
        """健康检查接口"""
        try:
            # 检查数据库连接
            mongo_status = await MongoDB.check_connection()
            redis_status = await RedisCache.check_connection()
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "services": {
                    "mongodb": mongo_status,
                    "redis": redis_status
                }
            }
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            raise HTTPException(status_code=503, detail="服务不可用")
    
    # 根路径
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "message": "欢迎使用股票量化交易系统API",
            "docs": "/api/docs",
            "health": "/health"
        }
    
    return app


# 创建应用实例
app = create_app()

# 导入datetime用于健康检查
from datetime import datetime


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )