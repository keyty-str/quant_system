"""
JWT Token 认证模块
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from loguru import logger
from src.utils.config import get_settings

# 获取配置
settings = get_settings()

# JWT配置
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        编码后的JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    
    logger.debug(f"创建访问令牌: {data.get('sub', 'unknown')}")
    
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    解码JWT Token
    
    Args:
        token: JWT token字符串
        
    Returns:
        解码后的数据，如果无效则返回None
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"Token解码失败: {e}")
        return None


def verify_token(token: str) -> Optional[str]:
    """
    验证Token并返回用户名
    
    Args:
        token: JWT token字符串
        
    Returns:
        用户名，如果无效则返回None
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    username: str = payload.get("sub")
    
    if username is None:
        return None
    
    return username