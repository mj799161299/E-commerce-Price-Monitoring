"""
数据库初始化脚本
运行此脚本创建所有数据库表
"""
import asyncio
from app.core.database import engine, Base
from app.models.models import User, APIConfig, MonitorItem, PriceHistory, OperationLog, PushChannel


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        # 删除所有表（开发环境使用，生产环境请注释）
        # await conn.run_sync(Base.metadata.drop_all)
        
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
    
    print("数据库表创建成功！")


if __name__ == "__main__":
    asyncio.run(init_db())
