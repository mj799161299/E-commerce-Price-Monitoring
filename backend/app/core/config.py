from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "电商价格监控系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://price_monitor:password@localhost:5432/price_monitor"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # AES加密密钥（用于加密API凭证）
    AES_KEY: str = "your-aes-key-32-bytes-long-key!"
    
    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # API限流配置
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
