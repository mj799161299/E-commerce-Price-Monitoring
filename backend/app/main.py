from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, monitor, api_config, push
from contextlib import asynccontextmanager

# 导入调度器
from app.services.scheduler import scheduler_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    scheduler_service.start()
    print("定时任务调度器已启动")
    
    yield
    
    # 关闭时执行
    scheduler_service.shutdown()
    print("定时任务调度器已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(monitor.router, prefix="/api/monitor", tags=["商品监控"])
app.include_router(api_config.router, prefix="/api/config", tags=["API配置"])
app.include_router(push.router, prefix="/api/push", tags=["消息推送"])


@app.get("/")
async def root():
    return {
        "message": "电商价格监控系统API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}
