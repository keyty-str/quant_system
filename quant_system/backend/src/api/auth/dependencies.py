"""
认证依赖项
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from loguru import logger

from src.api.auth.jwt import decode_token, verify_token
from src.data.storage.mongodb import MongoDB
from src.models.user import User, TokenData
from src.utils.config import get_settings

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

settings = get_settings()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[User]:
    """
    获取当前登录用户
    
    Args:
        token: JWT token
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: 如果token无效或用户不存在
    """
    if token is None:
        return None
    
    # 验证token
    username = verify_token(token)
    
    if username is None:
        logger.warning("Token验证失败")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证失败，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库获取用户
    try:
        user_data = await MongoDB.find_one("users", {"username": username})
        
        if user_data is None:
            logger.warning(f"用户不存在: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户是否激活
        if not user_data.get("is_active", True):
            logger.warning(f"用户已禁用: {username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用",
            )
        
        # 转换为User对象
        user = User(
            _id=str(user_data["_id"]),
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data.get("full_name"),
            role=user_data.get("role", "user"),
            is_active=user_data.get("is_active", True),
            created_at=user_data["created_at"],
            last_login=user_data.get("last_login")
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误",
        )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        当前活跃用户
        
    Raises:
        HTTPException: 如果用户未激活
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前管理员用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        当前管理员用户
        
    Raises:
        HTTPException: 如果用户不是管理员
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
        )
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    
    return current_user