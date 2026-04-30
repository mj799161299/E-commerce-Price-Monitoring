from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.models import User, MonitorItem, PriceHistory, APIConfig, OperationLog
from app.models.schemas import MonitorItemCreate, MonitorItemUpdate, MonitorItemResponse, PriceHistoryResponse
from app.utils.crypto import CryptoUtil
from app.adapters.platform_adapter import TaobaoAdapter, JDAdapter, PDDAdapter
import re

router = APIRouter()


def detect_platform(url: str) -> str:
    """检测商品URL所属平台"""
    url_lower = url.lower()
    
    # 淘宝/天猫链接
    if any(domain in url_lower for domain in ['taobao.com', 'tmall.com', 'tmall.hk']):
        return "taobao"
    
    # 京东链接（包括短链接域名）
    if any(domain in url_lower for domain in ['jd.com', 'jd.hk', 'jd.cn', '3.cn', 'u.jd.com', 'k.pl']):
        return "jd"
    
    # 拼多多链接
    if any(domain in url_lower for domain in ['pinduoduo.com', 'yangkeduo.com']):
        return "pdd"
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="不支持的商品链接，仅支持淘宝/天猫、京东、拼多多"
    )


async def get_platform_adapter(platform: str, user_id: int, db: AsyncSession):
    """获取平台适配器"""
    # 获取用户的API配置
    result = await db.execute(
        select(APIConfig).where(
            APIConfig.user_id == user_id,
            APIConfig.platform == platform
        )
    )
    api_config = result.scalar_one_or_none()
    
    if not api_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"请先配置{platform}平台的API凭证"
        )
    
    if not api_config.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{platform}平台的API凭证未通过验证，请重新配置"
        )
    
    # 解密凭证
    try:
        app_key = CryptoUtil.decrypt(api_config.app_key)
        app_secret = CryptoUtil.decrypt(api_config.app_secret)
        pid = CryptoUtil.decrypt(api_config.pid) if api_config.pid else None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解密API凭证失败: {str(e)}"
        )
    
    # 创建适配器
    if platform == "taobao":
        return TaobaoAdapter(app_key, app_secret, pid)
    elif platform == "jd":
        return JDAdapter(app_key, app_secret)
    elif platform == "pdd":
        return PDDAdapter(app_key, app_secret, pid)


@router.post("/items", response_model=MonitorItemResponse, status_code=status.HTTP_201_CREATED)
async def add_monitor_item(
    item_data: MonitorItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """添加监控商品"""
    # 检测平台
    platform = detect_platform(item_data.goods_url)
    
    # 获取平台适配器
    adapter = await get_platform_adapter(platform, current_user.id, db)
    
    # 解析商品ID
    try:
        goods_id = await adapter.parse_goods_id(item_data.goods_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"解析商品ID失败: {str(e)}"
        )
    
    # 检查是否已添加
    result = await db.execute(
        select(MonitorItem).where(
            MonitorItem.user_id == current_user.id,
            MonitorItem.goods_id == goods_id,
            MonitorItem.platform == platform
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该商品已在监控列表中"
        )
    
    # 获取商品信息
    try:
        goods_info = await adapter.get_goods_info(goods_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"获取商品信息失败: {str(e)}"
        )
    
    # 创建监控项
    monitor_item = MonitorItem(
        user_id=current_user.id,
        goods_id=goods_id,
        platform=platform,
        goods_title=goods_info.get("title", "未知商品"),
        goods_url=item_data.goods_url,
        goods_image=goods_info.get("image"),
        current_price=goods_info.get("price"),
        threshold_price=item_data.threshold_price,
        threshold_type=item_data.threshold_type,
        monitor_interval=item_data.monitor_interval,
        is_active=True,
        is_valid=True
    )
    
    db.add(monitor_item)
    await db.commit()
    await db.refresh(monitor_item)
    
    # 记录初始价格
    if goods_info.get("price"):
        price_history = PriceHistory(
            monitor_id=monitor_item.id,
            price=goods_info.get("price"),
            coupon_price=goods_info.get("coupon_price")
        )
        db.add(price_history)
        await db.commit()
    
    # 添加定时任务
    from app.services.scheduler import scheduler_service
    await scheduler_service.add_monitor_job(monitor_item, db)
    
    return monitor_item


@router.get("/items", response_model=List[MonitorItemResponse])
async def get_monitor_items(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取监控商品列表"""
    result = await db.execute(
        select(MonitorItem).where(MonitorItem.user_id == current_user.id)
        .order_by(MonitorItem.create_time.desc())
    )
    items = result.scalars().all()
    return items


@router.get("/items/{item_id}", response_model=MonitorItemResponse)
async def get_monitor_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取单个监控商品详情"""
    result = await db.execute(
        select(MonitorItem).where(
            MonitorItem.id == item_id,
            MonitorItem.user_id == current_user.id
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="监控商品不存在"
        )
    
    return item


@router.put("/items/{item_id}", response_model=MonitorItemResponse)
async def update_monitor_item(
    item_id: int,
    item_data: MonitorItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新监控商品"""
    result = await db.execute(
        select(MonitorItem).where(
            MonitorItem.id == item_id,
            MonitorItem.user_id == current_user.id
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="监控商品不存在"
        )
    
    # 记录是否需要更新定时任务
    need_update_job = False
    
    # 更新字段
    if item_data.threshold_price is not None:
        item.threshold_price = item_data.threshold_price
    if item_data.threshold_type is not None:
        item.threshold_type = item_data.threshold_type
    if item_data.monitor_interval is not None:
        item.monitor_interval = item_data.monitor_interval
        need_update_job = True
    if item_data.is_active is not None:
        item.is_active = item_data.is_active
        need_update_job = True
    
    await db.commit()
    await db.refresh(item)
    
    # 更新定时任务
    if need_update_job:
        from app.services.scheduler import scheduler_service
        if item.is_active:
            await scheduler_service.add_monitor_job(item, db)
        else:
            scheduler_service.remove_monitor_job(item.id)
    
    return item


@router.delete("/items/{item_id}")
async def delete_monitor_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除监控商品"""
    result = await db.execute(
        select(MonitorItem).where(
            MonitorItem.id == item_id,
            MonitorItem.user_id == current_user.id
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="监控商品不存在"
        )
    
    # 移除定时任务
    from app.services.scheduler import scheduler_service
    scheduler_service.remove_monitor_job(item.id)
    
    # 先删除关联的价格历史记录
    price_result = await db.execute(
        select(PriceHistory).where(PriceHistory.monitor_id == item_id)
    )
    price_records = price_result.scalars().all()
    for record in price_records:
        await db.delete(record)
    
    # 删除关联的操作日志
    log_result = await db.execute(
        select(OperationLog).where(OperationLog.monitor_id == item_id)
    )
    log_records = log_result.scalars().all()
    for record in log_records:
        await db.delete(record)
    
    await db.delete(item)
    await db.commit()
    
    return {"message": "删除成功"}


@router.get("/items/{item_id}/history", response_model=List[PriceHistoryResponse])
async def get_price_history(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取商品历史价格"""
    # 验证商品归属
    result = await db.execute(
        select(MonitorItem).where(
            MonitorItem.id == item_id,
            MonitorItem.user_id == current_user.id
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="监控商品不存在"
        )
    
    # 获取价格历史
    result = await db.execute(
        select(PriceHistory).where(PriceHistory.monitor_id == item_id)
        .order_by(PriceHistory.fetch_time.desc())
        .limit(100)  # 最多返回100条记录
    )
    history = result.scalars().all()
    
    return history
