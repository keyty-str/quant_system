"""
Redis缓存模块
用于实时数据分发和临时存储
"""

import json
import asyncio
from typing import Any, Optional, List, Dict
from datetime import timedelta
from loguru import logger
from redis.asyncio import Redis, ConnectionPool
from src.utils.config import get_settings


class RedisCache:
    """Redis缓存连接管理"""
    
    pool: ConnectionPool = None
    client: Redis = None
    
    @classmethod
    async def connect(cls):
        """连接Redis缓存"""
        settings = get_settings()
        
        try:
            cls.pool = ConnectionPool.from_url(
                settings.redis_url,
                max_connections=20,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            cls.client = Redis(connection_pool=cls.pool)
            
            # 测试连接
            await cls.client.ping()
            logger.info(f"Redis连接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise
    
    @classmethod
    async def close(cls):
        """关闭Redis连接"""
        if cls.client:
            await cls.client.aclose()
            if cls.pool:
                await cls.pool.disconnect()
            logger.info("Redis连接已关闭")
    
    @classmethod
    async def check_connection(cls) -> bool:
        """检查Redis连接状态"""
        try:
            if cls.client:
                await cls.client.ping()
                return True
            return False
        except Exception:
            return False
    
    # ========== 基础缓存操作 ==========
    
    @classmethod
    async def set(
        cls, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值（自动JSON序列化）
            expire: 过期时间（秒）
            
        Returns:
            bool: 设置是否成功
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            result = await cls.client.set(key, value, ex=expire)
            return result
        except Exception as e:
            logger.error(f"Redis SET失败 {key}: {e}")
            return False
    
    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在返回None
        """
        try:
            value = await cls.client.get(key)
            if value is None:
                return None
            
            # 尝试JSON反序列化
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis GET失败 {key}: {e}")
            return None
    
    @classmethod
    async def delete(cls, *keys: str) -> int:
        """删除缓存
        
        Args:
            keys: 要删除的键列表
            
        Returns:
            删除的键数量
        """
        try:
            return await cls.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE失败: {e}")
            return 0
    
    @classmethod
    async def exists(cls, key: str) -> bool:
        """检查键是否存在"""
        try:
            return await cls.client.exists(key) == 1
        except Exception:
            return False
    
    @classmethod
    async def expire(cls, key: str, seconds: int) -> bool:
        """设置键的过期时间"""
        try:
            return await cls.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE失败 {key}: {e}")
            return False
    
    @classmethod
    async def ttl(cls, key: str) -> int:
        """获取键的剩余过期时间"""
        try:
            return await cls.client.ttl(key)
        except Exception:
            return -1
    
    # ========== Hash操作 ==========
    
    @classmethod
    async def hset(
        cls, 
        name: str, 
        key: Optional[str] = None, 
        value: Any = None,
        mapping: Optional[Dict] = None
    ) -> int:
        """设置Hash字段
        
        Args:
            name: Hash名称
            key: 字段名
            value: 字段值
            mapping: 字段字典（与key/value互斥）
            
        Returns:
            设置的字段数量
        """
        try:
            if mapping:
                # 序列化字典值
                serialized = {}
                for k, v in mapping.items():
                    if isinstance(v, (dict, list)):
                        serialized[k] = json.dumps(v, ensure_ascii=False)
                    else:
                        serialized[k] = v
                return await cls.client.hset(name, mapping=serialized)
            else:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                return await cls.client.hset(name, key, value)
        except Exception as e:
            logger.error(f"Redis HSET失败 {name}: {e}")
            return 0
    
    @classmethod
    async def hget(cls, name: str, key: str) -> Optional[Any]:
        """获取Hash字段"""
        try:
            value = await cls.client.hget(name, key)
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis HGET失败 {name}.{key}: {e}")
            return None
    
    @classmethod
    async def hgetall(cls, name: str) -> Dict[str, Any]:
        """获取Hash所有字段"""
        try:
            data = await cls.client.hgetall(name)
            result = {}
            for k, v in data.items():
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    result[k] = v
            return result
        except Exception as e:
            logger.error(f"Redis HGETALL失败 {name}: {e}")
            return {}
    
    @classmethod
    async def hdel(cls, name: str, *keys: str) -> int:
        """删除Hash字段"""
        try:
            return await cls.client.hdel(name, *keys)
        except Exception as e:
            logger.error(f"Redis HDEL失败 {name}: {e}")
            return 0
    
    # ========== List操作 ==========
    
    @classmethod
    async def lpush(cls, name: str, *values: Any) -> int:
        """从左侧推入列表"""
        try:
            serialized = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized.append(json.dumps(v, ensure_ascii=False))
                else:
                    serialized.append(v)
            return await cls.client.lpush(name, *serialized)
        except Exception as e:
            logger.error(f"Redis LPUSH失败 {name}: {e}")
            return 0
    
    @classmethod
    async def rpush(cls, name: str, *values: Any) -> int:
        """从右侧推入列表"""
        try:
            serialized = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized.append(json.dumps(v, ensure_ascii=False))
                else:
                    serialized.append(v)
            return await cls.client.rpush(name, *serialized)
        except Exception as e:
            logger.error(f"Redis RPUSH失败 {name}: {e}")
            return 0
    
    @classmethod
    async def lrange(cls, name: str, start: int, end: int) -> List[Any]:
        """获取列表范围"""
        try:
            values = await cls.client.lrange(name, start, end)
            result = []
            for v in values:
                try:
                    result.append(json.loads(v))
                except (json.JSONDecodeError, TypeError):
                    result.append(v)
            return result
        except Exception as e:
            logger.error(f"Redis LRANGE失败 {name}: {e}")
            return []
    
    @classmethod
    async def ltrim(cls, name: str, start: int, end: int) -> bool:
        """修剪列表"""
        try:
            await cls.client.ltrim(name, start, end)
            return True
        except Exception as e:
            logger.error(f"Redis LTRIM失败 {name}: {e}")
            return False
    
    # ========== Set操作 ==========
    
    @classmethod
    async def sadd(cls, name: str, *values: Any) -> int:
        """添加集合成员"""
        try:
            serialized = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized.append(json.dumps(v, ensure_ascii=False))
                else:
                    serialized.append(v)
            return await cls.client.sadd(name, *serialized)
        except Exception as e:
            logger.error(f"Redis SADD失败 {name}: {e}")
            return 0
    
    @classmethod
    async def smembers(cls, name: str) -> List[Any]:
        """获取集合所有成员"""
        try:
            members = await cls.client.smembers(name)
            result = []
            for m in members:
                try:
                    result.append(json.loads(m))
                except (json.JSONDecodeError, TypeError):
                    result.append(m)
            return result
        except Exception as e:
            logger.error(f"Redis SMEMBERS失败 {name}: {e}")
            return []
    
    @classmethod
    async def sismember(cls, name: str, value: Any) -> bool:
        """检查成员是否在集合中"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            return await cls.client.sismember(name, value)
        except Exception as e:
            logger.error(f"Redis SISMEMBER失败 {name}: {e}")
            return False
    
    @classmethod
    async def srem(cls, name: str, *values: Any) -> int:
        """删除集合成员"""
        try:
            serialized = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized.append(json.dumps(v, ensure_ascii=False))
                else:
                    serialized.append(v)
            return await cls.client.srem(name, *serialized)
        except Exception as e:
            logger.error(f"Redis SREM失败 {name}: {e}")
            return 0
    
    # ========== Sorted Set操作 ==========
    
    @classmethod
    async def zadd(
        cls, 
        name: str, 
        mapping: Dict[str, float]
    ) -> int:
        """添加有序集合成员"""
        try:
            return await cls.client.zadd(name, mapping)
        except Exception as e:
            logger.error(f"Redis ZADD失败 {name}: {e}")
            return 0
    
    @classmethod
    async def zrange(
        cls, 
        name: str, 
        start: int, 
        end: int, 
        withscores: bool = False
    ) -> List[Any]:
        """获取有序集合范围"""
        try:
            return await cls.client.zrange(name, start, end, withscores=withscores)
        except Exception as e:
            logger.error(f"Redis ZRANGE失败 {name}: {e}")
            return []
    
    @classmethod
    async def zrem(cls, name: str, *values: str) -> int:
        """删除有序集合成员"""
        try:
            return await cls.client.zrem(name, *values)
        except Exception as e:
            logger.error(f"Redis ZREM失败 {name}: {e}")
            return 0
    
    # ========== 发布/订阅 ==========
    
    @classmethod
    async def publish(cls, channel: str, message: Any) -> int:
        """发布消息
        
        Args:
            channel: 频道名称
            message: 消息内容（自动JSON序列化）
            
        Returns:
            订阅该频道的客户端数量
        """
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message, ensure_ascii=False)
            return await cls.client.publish(channel, message)
        except Exception as e:
            logger.error(f"Redis PUBLISH失败 {channel}: {e}")
            return 0
    
    @classmethod
    async def subscribe(cls, *channels: str):
        """订阅频道（返回订阅对象）"""
        try:
            pubsub = cls.client.pubsub()
            await pubsub.subscribe(*channels)
            return pubsub
        except Exception as e:
            logger.error(f"Redis SUBSCRIBE失败: {e}")
            raise
    
    # ========== 股票数据专用缓存方法 ==========
    
    @classmethod
    async def cache_stock_data(
        cls, 
        code: str, 
        data: Dict, 
        expire: int = 300
    ) -> bool:
        """缓存股票数据
        
        Args:
            code: 股票代码
            data: 股票数据
            expire: 过期时间（秒），默认5分钟
        """
        key = f"stock:data:{code}"
        return await cls.set(key, data, expire)
    
    @classmethod
    async def get_stock_data(cls, code: str) -> Optional[Dict]:
        """获取缓存的股票数据"""
        key = f"stock:data:{code}"
        return await cls.get(key)
    
    @classmethod
    async def cache_sector_data(
        cls, 
        sector: str, 
        data: Dict, 
        expire: int = 300
    ) -> bool:
        """缓存板块数据"""
        key = f"sector:data:{sector}"
        return await cls.set(key, data, expire)
    
    @classmethod
    async def get_sector_data(cls, sector: str) -> Optional[Dict]:
        """获取缓存的板块数据"""
        key = f"sector:data:{sector}"
        return await cls.get(key)
    
    @classmethod
    async def cache_stock_list(cls, stock_list: List[str], expire: int = 3600) -> bool:
        """缓存股票列表"""
        key = "stock:list:all"
        return await cls.set(key, stock_list, expire)
    
    @classmethod
    async def get_stock_list(cls) -> Optional[List[str]]:
        """获取缓存的股票列表"""
        key = "stock:list:all"
        return await cls.get(key)
    
    @classmethod
    async def cache_indicator(
        cls, 
        code: str, 
        indicator: str, 
        data: Dict, 
        expire: int = 600
    ) -> bool:
        """缓存技术指标"""
        key = f"indicator:{indicator}:{code}"
        return await cls.set(key, data, expire)
    
    @classmethod
    async def get_indicator(cls, code: str, indicator: str) -> Optional[Dict]:
        """获取缓存的技术指标"""
        key = f"indicator:{indicator}:{code}"
        return await cls.get(key)
    
    @classmethod
    async def add_stock_to_watchlist(cls, user_id: str, code: str) -> bool:
        """添加股票到自选列表"""
        key = f"user:watchlist:{user_id}"
        return await cls.sadd(key, code) == 1
    
    @classmethod
    async def get_watchlist(cls, user_id: str) -> List[str]:
        """获取用户自选列表"""
        key = f"user:watchlist:{user_id}"
        return await cls.smembers(key)
    
    @classmethod
    async def remove_stock_from_watchlist(cls, user_id: str, code: str) -> bool:
        """从自选列表移除股票"""
        key = f"user:watchlist:{user_id}"
        return await cls.srem(key, code) == 1
    
    # ========== 实时行情推送 ==========
    
    @classmethod
    async def publish_realtime_quote(cls, code: str, quote: Dict) -> int:
        """发布实时行情"""
        channel = f"quote:realtime:{code}"
        return await cls.publish(channel, quote)
    
    @classmethod
    async def subscribe_realtime_quote(cls, code: str):
        """订阅实时行情"""
        channel = f"quote:realtime:{code}"
        return await cls.subscribe(channel)
    
    # ========== 信号推送 ==========
    
    @classmethod
    async def publish_signal(cls, signal: Dict) -> int:
        """发布交易信号"""
        channel = "signal:trade"
        return await cls.publish(channel, signal)
    
    @classmethod
    async def subscribe_signal(cls):
        """订阅交易信号"""
        channel = "signal:trade"
        return await cls.subscribe(channel)
    
    # ========== 批量操作 ==========
    
    @classmethod
    async def pipeline(cls):
        """获取Pipeline对象"""
        return cls.client.pipeline(transaction=True)
    
    @classmethod
    async def scan_keys(cls, pattern: str, count: int = 100) -> List[str]:
        """扫描匹配模式的键
        
        Args:
            pattern: 匹配模式，如 "stock:*"
            count: 每次扫描的数量
            
        Returns:
            匹配的键列表
        """
        try:
            keys = []
            cursor = 0
            while True:
                cursor, batch = await cls.client.scan(cursor, match=pattern, count=count)
                keys.extend(batch)
                if cursor == 0:
                    break
            return keys
        except Exception as e:
            logger.error(f"Redis SCAN失败 {pattern}: {e}")
            return []
    
    @classmethod
    async def clear_pattern(cls, pattern: str) -> int:
        """清除匹配模式的键
        
        Args:
            pattern: 匹配模式
            
        Returns:
            删除的键数量
        """
        keys = await cls.scan_keys(pattern)
        if keys:
            return await cls.delete(*keys)
        return 0