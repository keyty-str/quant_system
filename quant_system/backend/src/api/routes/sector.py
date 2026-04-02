"""
板块分析路由
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/sectors")
async def get_sectors():
    """获取板块列表"""
    return {
        "status": "success",
        "data": {
            "sectors": []
        }
    }