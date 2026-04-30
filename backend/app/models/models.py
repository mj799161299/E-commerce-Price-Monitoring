from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Numeric, Text, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    create_time = Column(TIMESTAMP, server_default=func.now())
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class APIConfig(Base):
    """API凭证配置表"""
    __tablename__ = "api_config"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    platform = Column(String(20), nullable=False)  # taobao/jd/pdd
    app_key = Column(Text, nullable=False)  # 加密存储
    app_secret = Column(Text, nullable=False)  # 加密存储
    pid = Column(Text)  # 推广位ID，加密存储
    is_valid = Column(Boolean, default=False)
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class MonitorItem(Base):
    """监控商品表"""
    __tablename__ = "monitor_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    goods_id = Column(String(50), nullable=False, index=True)
    platform = Column(String(20), nullable=False)
    goods_title = Column(Text, nullable=False)
    goods_url = Column(Text, nullable=False)
    goods_image = Column(Text)
    current_price = Column(Numeric(10, 2))
    threshold_price = Column(Numeric(10, 2), nullable=False)
    threshold_type = Column(String(20), nullable=False)  # price/coupon_price/discount
    monitor_interval = Column(Integer, nullable=False)  # 分钟
    is_active = Column(Boolean, default=True)
    is_valid = Column(Boolean, default=True)
    create_time = Column(TIMESTAMP, server_default=func.now())
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class PriceHistory(Base):
    """历史价格表"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    monitor_id = Column(Integer, ForeignKey("monitor_items.id"), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    coupon_price = Column(Numeric(10, 2))
    fetch_time = Column(TIMESTAMP, nullable=False, server_default=func.now())


class OperationLog(Base):
    """操作日志表"""
    __tablename__ = "operation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    log_type = Column(String(20), nullable=False)  # api_call/price_update/alert/error
    content = Column(Text, nullable=False)
    monitor_id = Column(Integer, ForeignKey("monitor_items.id"))
    create_time = Column(TIMESTAMP, server_default=func.now())


class PushChannel(Base):
    """推送渠道配置表"""
    __tablename__ = "push_channels"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    channel_type = Column(String(20), nullable=False)  # serverchan/wecom/dingtalk/feishu/email
    channel_config = Column(Text, nullable=False)  # 加密存储
    is_active = Column(Boolean, default=True)
    create_time = Column(TIMESTAMP, server_default=func.now())
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
