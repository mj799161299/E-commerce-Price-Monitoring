from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.models import User, APIConfig
from app.models.schemas import APIConfigCreate, APIConfigResponse
from app.utils.crypto import CryptoUtil
from app.adapters.platform_adapter import TaobaoAdapter, JDAdapter, PDDAdapter

router = APIRouter()


@router.post("/platforms/{platform}", response_model=APIConfigResponse, status_code=status.HTTP_201_CREATED)
async def save_api_config(
    platform: str,
    config_data: APIConfigCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """保存平台API配置"""
    # 验证平台名称
    if platform not in ["taobao", "jd", "pdd"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的平台"
        )
    
    # 检查是否已存在配置
    result = await db.execute(
        select(APIConfig).where(
            APIConfig.user_id == current_user.id,
            APIConfig.platform == platform
        )
    )
    existing_config = result.scalar_one_or_none()
    
    if existing_config:
        # 更新现有配置
        existing_config.app_key = CryptoUtil.encrypt(config_data.app_key)
        existing_config.app_secret = CryptoUtil.encrypt(config_data.app_secret)
        if config_data.pid:
            existing_config.pid = CryptoUtil.encrypt(config_data.pid)
        existing_config.is_valid = False  # 需要重新测试
        api_config = existing_config
    else:
        # 创建新配置
        api_config = APIConfig(
            user_id=current_user.id,
            platform=platform,
            app_key=CryptoUtil.encrypt(config_data.app_key),
            app_secret=CryptoUtil.encrypt(config_data.app_secret),
            pid=CryptoUtil.encrypt(config_data.pid) if config_data.pid else None,
            is_valid=False
        )
        db.add(api_config)
    
    await db.commit()
    await db.refresh(api_config)
    
    # 构造响应（不返回敏感信息）
    response = APIConfigResponse(
        id=api_config.id,
        platform=api_config.platform,
        is_valid=api_config.is_valid,
        update_time=api_config.update_time,
        has_app_key=bool(api_config.app_key),
        has_app_secret=bool(api_config.app_secret),
        has_pid=bool(api_config.pid)
    )
    
    return response


@router.get("/platforms/{platform}", response_model=APIConfigResponse)
async def get_api_config(
    platform: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取平台API配置"""
    result = await db.execute(
        select(APIConfig).where(
            APIConfig.user_id == current_user.id,
            APIConfig.platform == platform
        )
    )
    api_config = result.scalar_one_or_none()
    
    if not api_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到API配置"
        )
    
    # 构造响应（不返回敏感信息）
    response = APIConfigResponse(
        id=api_config.id,
        platform=api_config.platform,
        is_valid=api_config.is_valid,
        update_time=api_config.update_time,
        has_app_key=bool(api_config.app_key),
        has_app_secret=bool(api_config.app_secret),
        has_pid=bool(api_config.pid)
    )
    
    return response


@router.post("/platforms/{platform}/test")
async def test_api_config(
    platform: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """测试平台API连通性"""
    # 获取API配置
    result = await db.execute(
        select(APIConfig).where(
            APIConfig.user_id == current_user.id,
            APIConfig.platform == platform
        )
    )
    api_config = result.scalar_one_or_none()
    
    if not api_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到API配置，请先配置"
        )
    
    # 解密凭证
    try:
        app_key = CryptoUtil.decrypt(api_config.app_key)
        app_secret = CryptoUtil.decrypt(api_config.app_secret)
        pid = CryptoUtil.decrypt(api_config.pid) if api_config.pid else None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"解密凭证失败: {str(e)}"
        )
    
    # 创建适配器并测试连接
    try:
        if platform == "taobao":
            adapter = TaobaoAdapter(app_key, app_secret, pid)
        elif platform == "jd":
            adapter = JDAdapter(app_key, app_secret)
        elif platform == "pdd":
            adapter = PDDAdapter(app_key, app_secret, pid)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的平台"
            )
        
        # 测试连接
        is_valid = await adapter.test_connection()
        
        # 更新配置状态
        api_config.is_valid = is_valid
        await db.commit()
        
        return {
            "success": is_valid,
            "message": "API连接测试成功" if is_valid else "API连接测试失败，请检查凭证"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"测试失败: {str(e)}"
        }


@router.get("/quota")
async def get_api_quota(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取API配额使用情况"""
    # TODO: 实现配额统计逻辑
    # 这里需要记录每次API调用，然后统计今日使用量
    return {
        "taobao": {"used": 0, "limit": 10000},
        "jd": {"used": 0, "limit": 20000},
        "pdd": {"used": 0, "limit": 10000}
    }
