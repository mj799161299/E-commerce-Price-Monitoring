from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# 用户相关模型
class UserRegister(BaseModel):
    """用户注册"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    is_active: bool
    create_time: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """令牌数据"""
    user_id: Optional[int] = None


# API配置相关模型
class APIConfigCreate(BaseModel):
    """创建API配置"""
    platform: str = Field(..., pattern="^(taobao|jd|pdd)$")
    app_key: str
    app_secret: str
    pid: Optional[str] = None


class APIConfigUpdate(BaseModel):
    """更新API配置"""
    app_key: Optional[str] = None
    app_secret: Optional[str] = None
    pid: Optional[str] = None


class APIConfigResponse(BaseModel):
    """API配置响应（不返回敏感信息）"""
    id: int
    platform: str
    is_valid: bool
    update_time: datetime
    has_app_key: bool = True
    has_app_secret: bool = True
    has_pid: bool = False
    
    class Config:
        from_attributes = True


# 监控商品相关模型
class MonitorItemCreate(BaseModel):
    """创建监控商品"""
    goods_url: str
    threshold_price: float = Field(..., gt=0)
    threshold_type: str = Field(..., pattern="^(price|coupon_price|discount)$")
    monitor_interval: int = Field(default=60, ge=10, le=1440)  # 10分钟到24小时


class MonitorItemUpdate(BaseModel):
    """更新监控商品"""
    threshold_price: Optional[float] = Field(None, gt=0)
    threshold_type: Optional[str] = Field(None, pattern="^(price|coupon_price|discount)$")
    monitor_interval: Optional[int] = Field(None, ge=10, le=1440)
    is_active: Optional[bool] = None


class MonitorItemResponse(BaseModel):
    """监控商品响应"""
    id: int
    goods_id: str
    platform: str
    goods_title: str
    goods_url: str
    goods_image: Optional[str]
    current_price: Optional[float]
    threshold_price: float
    threshold_type: str
    monitor_interval: int
    is_active: bool
    is_valid: bool
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True


# 价格历史相关模型
class PriceHistoryResponse(BaseModel):
    """价格历史响应"""
    id: int
    price: float
    coupon_price: Optional[float]
    fetch_time: datetime
    
    class Config:
        from_attributes = True
