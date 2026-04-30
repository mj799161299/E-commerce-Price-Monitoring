from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.models import User, PushChannel
from app.utils.crypto import CryptoUtil
from app.services.push import push_manager
from pydantic import BaseModel
import json

router = APIRouter()


class PushChannelCreate(BaseModel):
    """创建推送渠道"""
    channel_type: str  # serverchan/wecom/dingtalk/feishu/email
    channel_config: dict  # 渠道配置（JSON）


class PushChannelResponse(BaseModel):
    """推送渠道响应"""
    id: int
    channel_type: str
    is_active: bool
    
    class Config:
        from_attributes = True


@router.post("/channels", response_model=PushChannelResponse, status_code=status.HTTP_201_CREATED)
async def add_push_channel(
    channel_data: PushChannelCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """添加推送渠道"""
    # 验证渠道类型
    valid_types = ["serverchan", "wecom", "dingtalk", "feishu", "email"]
    if channel_data.channel_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的推送渠道类型，支持: {', '.join(valid_types)}"
        )
    
    # 检查是否已存在相同类型的渠道
    result = await db.execute(
        select(PushChannel).where(
            PushChannel.user_id == current_user.id,
            PushChannel.channel_type == channel_data.channel_type
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该推送渠道已存在，请使用更新接口"
        )
    
    # 加密配置
    config_str = json.dumps(channel_data.channel_config)
    encrypted_config = CryptoUtil.encrypt(config_str)
    
    # 创建推送渠道
    push_channel = PushChannel(
        user_id=current_user.id,
        channel_type=channel_data.channel_type,
        channel_config=encrypted_config,
        is_active=True
    )
    
    db.add(push_channel)
    await db.commit()
    await db.refresh(push_channel)
    
    return push_channel


@router.get("/channels", response_model=List[PushChannelResponse])
async def get_push_channels(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取推送渠道列表"""
    result = await db.execute(
        select(PushChannel).where(PushChannel.user_id == current_user.id)
    )
    channels = result.scalars().all()
    return channels


@router.put("/channels/{channel_id}", response_model=PushChannelResponse)
async def update_push_channel(
    channel_id: int,
    channel_data: PushChannelCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新推送渠道"""
    result = await db.execute(
        select(PushChannel).where(
            PushChannel.id == channel_id,
            PushChannel.user_id == current_user.id
        )
    )
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="推送渠道不存在"
        )
    
    # 更新配置
    config_str = json.dumps(channel_data.channel_config)
    encrypted_config = CryptoUtil.encrypt(config_str)
    
    channel.channel_type = channel_data.channel_type
    channel.channel_config = encrypted_config
    
    await db.commit()
    await db.refresh(channel)
    
    return channel


@router.delete("/channels/{channel_id}")
async def delete_push_channel(
    channel_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除推送渠道"""
    result = await db.execute(
        select(PushChannel).where(
            PushChannel.id == channel_id,
            PushChannel.user_id == current_user.id
        )
    )
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="推送渠道不存在"
        )
    
    await db.delete(channel)
    await db.commit()
    
    return {"message": "删除成功"}


@router.post("/channels/{channel_id}/test")
async def test_push_channel(
    channel_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """测试推送渠道"""
    result = await db.execute(
        select(PushChannel).where(
            PushChannel.id == channel_id,
            PushChannel.user_id == current_user.id
        )
    )
    channel = result.scalar_one_or_none()
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="推送渠道不存在"
        )
    
    # 解密配置
    try:
        config_str = CryptoUtil.decrypt(channel.channel_config)
        channel_config = json.loads(config_str)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解密配置失败: {str(e)}"
        )
    
    # 发送测试消息
    success = await push_manager.send_alert(
        channel_type=channel.channel_type,
        channel_config=channel_config,
        goods_title="测试商品",
        goods_url="https://example.com",
        current_price=99.99,
        threshold_price=100.00,
        coupon_price=89.99
    )
    
    return {
        "success": success,
        "message": "测试推送发送成功" if success else "测试推送发送失败"
    }
