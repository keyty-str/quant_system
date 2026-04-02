"""
用户模型定义
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(BaseModel):
    """用户创建模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)


class UserUpdate(BaseModel):
    """用户更新模型"""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class UserInDB(UserBase):
    """数据库用户模型"""
    id: str = Field(alias="_id")
    hashed_password: str
    role: str = Field(default="user")  # admin, user
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

    class Config:
        populate_by_name = True


class User(UserBase):
    """用户响应模型"""
    id: str = Field(alias="_id")
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        populate_by_name = True


class Token(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str
    user: User


class TokenData(BaseModel):
    """Token数据模型"""
    username: Optional[str] = None