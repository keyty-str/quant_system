"""
初始化root用户脚本
"""
import asyncio
from datetime import datetime
from passlib.context import CryptContext
from src.data.storage.mongodb import MongoDB
from src.utils.config import get_settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 配置
ROOT_USERNAME = "root"
ROOT_PASSWORD = "test123"
ROOT_EMAIL = "admin@quantsystem.com"


async def init_root_user():
    """初始化root用户"""
    settings = get_settings()
    
    try:
        # 连接数据库
        await MongoDB.connect()
        print("数据库连接成功")
        
        # 检查root用户是否已存在
        existing_user = await MongoDB.find_one("users", {"username": ROOT_USERNAME})
        
        if existing_user:
            print(f"Root用户已存在: {ROOT_USERNAME}")
            return
        
        # 创建root用户
        user_dict = {
            "username": ROOT_USERNAME,
            "email": ROOT_EMAIL,
            "hashed_password": pwd_context.hash(ROOT_PASSWORD),
            "full_name": "系统管理员",
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now(),
            "last_login": None
        }
        
        # 插入数据库
        user_id = await MongoDB.insert_one("users", user_dict)
        
        print(f"Root用户创建成功!")
        print(f"用户名: {ROOT_USERNAME}")
        print(f"密码: {ROOT_PASSWORD}")
        print(f"角色: admin")
        print(f"用户ID: {user_id}")
        
    except Exception as e:
        print(f"初始化root用户失败: {e}")
    
    # 注意：不在这里关闭数据库连接，因为该函数可能被main.py调用
    # 连接的生命周期由主应用管理


if __name__ == "__main__":
    print("开始初始化root用户...")
    asyncio.run(init_root_user())