"""
配置管理模块
"""

import os
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""
    
    # API配置
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # CORS配置
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://frontend:3000",
            "http://nginx:80"
        ],
        env="CORS_ORIGINS"
    )
    
    # MongoDB配置
    MONGO_HOST: str = Field(default="mongodb", env="MONGO_HOST")
    MONGO_PORT: int = Field(default=27017, env="MONGO_PORT")
    MONGO_DB: str = Field(default="quant_system", env="MONGO_DB")
    MONGO_USER: str = Field(default="admin", env="MONGO_USER")
    MONGO_PASS: str = Field(default="password123", env="MONGO_PASS")
    
    # Redis配置
    REDIS_HOST: str = Field(default="redis", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_PASS: str = Field(default="password123", env="REDIS_PASS")
    
    # 数据源配置
    AKSHARE_ENABLED: bool = Field(default=True, env="AKSHARE_ENABLED")
    TUSHARE_TOKEN: str = Field(default="", env="TUSHARE_TOKEN")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/quant_system.log", env="LOG_FILE")
    
    # 策略配置
    DEFAULT_STRATEGY: str = Field(default="trend_following", env="DEFAULT_STRATEGY")
    BACKTEST_DAYS: int = Field(default=365, env="BACKTEST_DAYS")
    
    # 数据配置
    DATA_UPDATE_INTERVAL: int = Field(default=300, env="DATA_UPDATE_INTERVAL")  # 秒
    
    @property
    def mongodb_url(self) -> str:
        """生成MongoDB连接URL"""
        return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASS}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}?authSource=admin"
    
    @property
    def redis_url(self) -> str:
        """生成Redis连接URL"""
        return f"redis://:{self.REDIS_PASS}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    class Config:
        env_file = "../configs/.env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()