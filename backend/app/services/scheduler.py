"""
定时任务服务
负责管理所有商品的价格监控任务
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import MonitorItem, PriceHistory, APIConfig, User
from app.adapters.platform_adapter import TaobaoAdapter, JDAdapter, PDDAdapter
from app.utils.crypto import CryptoUtil
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务调度服务"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.running_jobs = {}  # 存储运行中的任务 {monitor_id: job}
    
    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("定时任务调度器已启动")
    
    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("定时任务调度器已关闭")
    
    async def add_monitor_job(self, monitor_item: MonitorItem, db: AsyncSession):
        """添加监控任务"""
        job_id = f"monitor_{monitor_item.id}"
        
        # 如果任务已存在，先移除
        if job_id in self.running_jobs:
            self.remove_monitor_job(monitor_item.id)
        
        # 添加新任务
        job = self.scheduler.add_job(
            self._check_price,
            trigger=IntervalTrigger(minutes=monitor_item.monitor_interval),
            args=[monitor_item.id],
            id=job_id,
            name=f"监控商品: {monitor_item.goods_title}",
            replace_existing=True
        )
        
        self.running_jobs[monitor_item.id] = job
        logger.info(f"已添加监控任务: {monitor_item.goods_title} (间隔: {monitor_item.monitor_interval}分钟)")
    
    def remove_monitor_job(self, monitor_id: int):
        """移除监控任务"""
        job_id = f"monitor_{monitor_id}"
        
        if job_id in self.running_jobs:
            self.scheduler.remove_job(job_id)
            del self.running_jobs[monitor_id]
            logger.info(f"已移除监控任务: {monitor_id}")
    
    async def _check_price(self, monitor_id: int):
        """检查商品价格（任务执行函数）"""
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            try:
                # 获取监控项
                result = await db.execute(
                    select(MonitorItem).where(MonitorItem.id == monitor_id)
                )
                monitor_item = result.scalar_one_or_none()
                
                if not monitor_item:
                    logger.warning(f"监控项不存在: {monitor_id}")
                    self.remove_monitor_job(monitor_id)
                    return
                
                # 检查是否启用
                if not monitor_item.is_active:
                    logger.info(f"监控项已暂停: {monitor_item.goods_title}")
                    return
                
                # 获取用户的API配置
                result = await db.execute(
                    select(APIConfig).where(
                        APIConfig.user_id == monitor_item.user_id,
                        APIConfig.platform == monitor_item.platform
                    )
                )
                api_config = result.scalar_one_or_none()
                
                if not api_config or not api_config.is_valid:
                    logger.warning(f"API配置无效: {monitor_item.platform}")
                    return
                
                # 解密API凭证
                app_key = CryptoUtil.decrypt(api_config.app_key)
                app_secret = CryptoUtil.decrypt(api_config.app_secret)
                pid = CryptoUtil.decrypt(api_config.pid) if api_config.pid else None
                
                # 创建适配器
                if monitor_item.platform == "taobao":
                    adapter = TaobaoAdapter(app_key, app_secret, pid)
                elif monitor_item.platform == "jd":
                    adapter = JDAdapter(app_key, app_secret)
                elif monitor_item.platform == "pdd":
                    adapter = PDDAdapter(app_key, app_secret, pid)
                else:
                    logger.error(f"不支持的平台: {monitor_item.platform}")
                    return
                
                # 获取商品信息
                goods_info = await adapter.get_goods_info(monitor_item.goods_id)
                
                if not goods_info or not goods_info.get("price"):
                    logger.warning(f"获取商品信息失败: {monitor_item.goods_title}")
                    return
                
                current_price = goods_info.get("price")
                coupon_price = goods_info.get("coupon_price")
                
                # 更新当前价格
                monitor_item.current_price = current_price
                
                # 记录价格历史
                price_history = PriceHistory(
                    monitor_id=monitor_item.id,
                    price=current_price,
                    coupon_price=coupon_price,
                    fetch_time=datetime.now()
                )
                db.add(price_history)
                
                # 检查阈值
                should_alert = await self._check_threshold(
                    monitor_item, current_price, coupon_price, db
                )
                
                if should_alert:
                    # 触发推送
                    await self._send_alert(monitor_item, current_price, coupon_price, db)
                
                await db.commit()
                logger.info(f"价格检查完成: {monitor_item.goods_title} - ¥{current_price}")
                
            except Exception as e:
                logger.error(f"价格检查失败: {monitor_id}, 错误: {str(e)}")
                await db.rollback()
    
    async def _check_threshold(
        self, 
        monitor_item: MonitorItem, 
        current_price: float, 
        coupon_price: float,
        db: AsyncSession
    ) -> bool:
        """检查是否触发阈值"""
        threshold_price = monitor_item.threshold_price
        threshold_type = monitor_item.threshold_type
        
        # 基础阈值：商品实时售价低于X元
        if threshold_type == "price":
            if current_price <= threshold_price:
                logger.info(f"触发价格阈值: {monitor_item.goods_title} - ¥{current_price} <= ¥{threshold_price}")
                return True
        
        # 券后价低于X元
        elif threshold_type == "coupon_price":
            if coupon_price and coupon_price <= threshold_price:
                logger.info(f"触发券后价阈值: {monitor_item.goods_title} - ¥{coupon_price} <= ¥{threshold_price}")
                return True
        
        # 降幅阈值（需要历史价格对比）
        elif threshold_type == "discount":
            # 获取最近的历史价格
            result = await db.execute(
                select(PriceHistory)
                .where(PriceHistory.monitor_id == monitor_item.id)
                .order_by(PriceHistory.fetch_time.desc())
                .limit(2)
            )
            history = result.scalars().all()
            
            if len(history) >= 2:
                last_price = history[1].price
                if last_price > 0:
                    discount_rate = ((last_price - current_price) / last_price) * 100
                    if discount_rate >= threshold_price:
                        logger.info(f"触发降幅阈值: {monitor_item.goods_title} - 降幅{discount_rate:.2f}% >= {threshold_price}%")
                        return True
        
        return False
    
    async def _send_alert(
        self, 
        monitor_item: MonitorItem, 
        current_price: float, 
        coupon_price: float,
        db: AsyncSession
    ):
        """发送降价提醒"""
        from app.models.models import PushChannel
        from app.services.push import push_manager
        import json
        
        logger.info(f"触发降价提醒: {monitor_item.goods_title} - ¥{current_price}")
        
        # 获取用户的推送渠道配置
        result = await db.execute(
            select(PushChannel).where(
                PushChannel.user_id == monitor_item.user_id,
                PushChannel.is_active == True
            )
        )
        push_channels = result.scalars().all()
        
        if not push_channels:
            logger.info(f"用户未配置推送渠道: {monitor_item.user_id}")
            return
        
        # 遍历所有启用的推送渠道
        for channel in push_channels:
            try:
                # 解密推送配置
                channel_config_str = CryptoUtil.decrypt(channel.channel_config)
                channel_config = json.loads(channel_config_str)
                
                # 发送推送
                success = await push_manager.send_alert(
                    channel_type=channel.channel_type,
                    channel_config=channel_config,
                    goods_title=monitor_item.goods_title,
                    goods_url=monitor_item.goods_url,
                    current_price=current_price,
                    threshold_price=monitor_item.threshold_price,
                    coupon_price=coupon_price
                )
                
                if success:
                    logger.info(f"推送成功: {channel.channel_type} - {monitor_item.goods_title}")
                else:
                    logger.warning(f"推送失败: {channel.channel_type} - {monitor_item.goods_title}")
                    
            except Exception as e:
                logger.error(f"推送异常: {channel.channel_type} - {str(e)}")


# 全局调度器实例
scheduler_service = SchedulerService()
