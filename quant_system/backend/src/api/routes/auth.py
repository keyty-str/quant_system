"""
认证API路由
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from passlib.context import CryptContext

from src.api.auth.dependencies import get_current_active_user
from src.api.auth.jwt import create_access_token
from src.data.storage.mongodb import MongoDB
from src.models.user import User, UserCreate, Token

router = APIRouter(prefix="/auth", tags=["认证管理"])

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


@router.post("/register", response_model=User, summary="用户注册")
async def register(user_data: UserCreate):
    """
    用户注册接口
    
    Args:
        user_data: 用户注册信息
        
    Returns:
        创建的用户信息
    """
    try:
        # 检查用户名是否已存在
        existing_user = await MongoDB.find_one("users", {"username": user_data.username})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        existing_email = await MongoDB.find_one("users", {"email": user_data.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 创建用户
        user_dict = {
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": get_password_hash(user_data.password),
            "full_name": user_data.full_name,
            "role": "user",  # 默认普通用户
            "is_active": True,
            "created_at": datetime.now(),
            "last_login": None
        }
        
        # 插入数据库
        user_id = await MongoDB.insert_one("users", user_dict)
        
        logger.info(f"用户注册成功: {user_data.username}")
        
        # 返回用户信息（不包含密码）
        return User(
            _id=str(user_id),
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            role="user",
            is_active=True,
            created_at=user_dict["created_at"],
            last_login=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


@router.post("/login", response_model=Token, summary="用户登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录接口
    
    Args:
        form_data: 登录表单数据（username, password）
        
    Returns:
        访问令牌和用户信息
    """
    try:
        # 查找用户
        user_data = await MongoDB.find_one("users", {"username": form_data.username})
        
        if not user_data:
            logger.warning(f"用户不存在: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 验证密码
        if not verify_password(form_data.password, user_data["hashed_password"]):
            logger.warning(f"密码错误: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户是否激活
        if not user_data.get("is_active", True):
            logger.warning(f"用户已禁用: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用",
            )
        
        # 更新最后登录时间
        await MongoDB.update_one("users", {"_id": user_data["_id"]}, {"last_login": datetime.now()})
        
        # 创建访问令牌
        access_token = create_access_token(data={"sub": user_data["username"]})
        
        logger.info(f"用户登录成功: {form_data.username}")
        
        # 返回token和用户信息
        user = User(
            _id=str(user_data["_id"]),
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data.get("full_name"),
            role=user_data.get("role", "user"),
            is_active=user_data.get("is_active", True),
            created_at=user_data["created_at"],
            last_login=datetime.now()
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )


@router.get("/me", response_model=User, summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    获取当前登录用户信息
    
    Args:
        current_user: 当前用户（通过依赖注入获取）
        
    Returns:
        当前用户信息
    """
    return current_user


@router.post("/logout", summary="用户登出")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    用户登出接口
    
    注意：由于JWT是无状态的，登出主要是客户端清除token。
    如果需要服务端维护黑名单，可以结合Redis实现。
    """
    logger.info(f"用户登出: {current_user.username}")
    return {"message": "登出成功"}