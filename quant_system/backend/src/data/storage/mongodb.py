"""
MongoDB数据库连接模块
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from loguru import logger
from src.utils.config import get_settings


class MongoDB:
    """MongoDB数据库连接管理"""
    
    client: AsyncIOMotorClient = None
    db = None
    
    @classmethod
    async def connect(cls):
        """连接MongoDB数据库"""
        settings = get_settings()
        
        try:
            cls.client = AsyncIOMotorClient(
                settings.mongodb_url,
                maxPoolSize=10,
                minPoolSize=1,
                maxIdleTimeMS=30000,
                connectTimeoutMS=5000,
                serverSelectionTimeoutMS=5000
            )
            
            # 测试连接
            await cls.client.admin.command('ping')
            
            cls.db = cls.client[settings.MONGO_DB]
            logger.info(f"MongoDB连接成功: {settings.MONGO_HOST}:{settings.MONGO_PORT}")
            
            # 创建索引
            await cls._create_indexes()
            
        except Exception as e:
            logger.error(f"MongoDB连接失败: {e}")
            raise
    
    @classmethod
    async def close(cls):
        """关闭MongoDB连接"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB连接已关闭")
    
    @classmethod
    async def check_connection(cls) -> bool:
        """检查MongoDB连接状态"""
        try:
            if cls.client:
                await cls.client.admin.command('ping')
                return True
            return False
        except Exception:
            return False
    
    @classmethod
    async def _create_indexes(cls):
        """创建数据库索引"""
        try:
            # 股票数据索引
            await cls.db.stock_data.create_index([("code", 1), ("date", -1)])
            await cls.db.stock_data.create_index([("date", -1)])
            
            # 板块数据索引
            await cls.db.sector_data.create_index([("name", 1), ("date", -1)])
            await cls.db.sector_data.create_index([("date", -1)])
            
            # 回测结果索引
            await cls.db.backtest_results.create_index([("strategy", 1), ("created_at", -1)])
            
            # 用户索引
            await cls.db.users.create_index([("username", 1)], unique=True)
            await cls.db.users.create_index([("email", 1)], unique=True)
            
            logger.info("数据库索引创建完成")
            
        except Exception as e:
            logger.warning(f"创建索引时出错: {e}")
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """获取集合"""
        if cls.db is None:
            raise Exception("数据库未连接")
        return cls.db[collection_name]
    
    @classmethod
    async def insert_one(cls, collection_name: str, document: dict):
        """插入单个文档"""
        collection = cls.get_collection(collection_name)
        result = await collection.insert_one(document)
        return result.inserted_id
    
    @classmethod
    async def insert_many(cls, collection_name: str, documents: list):
        """插入多个文档"""
        collection = cls.get_collection(collection_name)
        result = await collection.insert_many(documents)
        return result.inserted_ids
    
    @classmethod
    async def find_one(cls, collection_name: str, filter_dict: dict):
        """查询单个文档"""
        collection = cls.get_collection(collection_name)
        return await collection.find_one(filter_dict)
    
    @classmethod
    async def find_many(cls, collection_name: str, filter_dict: dict, limit: int = 0, sort: list = None):
        """查询多个文档"""
        collection = cls.get_collection(collection_name)
        cursor = collection.find(filter_dict)
        
        if sort:
            cursor = cursor.sort(sort)
        if limit > 0:
            cursor = cursor.limit(limit)
        
        return await cursor.to_list(length=limit)
    
    @classmethod
    async def update_one(cls, collection_name: str, filter_dict: dict, update_dict: dict):
        """更新单个文档"""
        collection = cls.get_collection(collection_name)
        result = await collection.update_one(filter_dict, {"$set": update_dict})
        return result.modified_count
    
    @classmethod
    async def update_many(cls, collection_name: str, filter_dict: dict, update_dict: dict):
        """更新多个文档"""
        collection = cls.get_collection(collection_name)
        result = await collection.update_many(filter_dict, {"$set": update_dict})
        return result.modified_count
    
    @classmethod
    async def delete_one(cls, collection_name: str, filter_dict: dict):
        """删除单个文档"""
        collection = cls.get_collection(collection_name)
        result = await collection.delete_one(filter_dict)
        return result.deleted_count
    
    @classmethod
    async def delete_many(cls, collection_name: str, filter_dict: dict):
        """删除多个文档"""
        collection = cls.get_collection(collection_name)
        result = await collection.delete_many(filter_dict)
        return result.deleted_count
    
    @classmethod
    async def count_documents(cls, collection_name: str, filter_dict: dict = None):
        """统计文档数量"""
        collection = cls.get_collection(collection_name)
        if filter_dict is None:
            filter_dict = {}
        return await collection.count_documents(filter_dict)