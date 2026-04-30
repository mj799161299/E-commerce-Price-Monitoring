"""
消息推送服务
支持多种推送渠道：Server酱、企业微信、钉钉、飞书、邮件
"""
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PushService:
    """推送服务基类"""
    
    async def send(self, title: str, content: str, config: Dict) -> bool:
        """发送推送"""
        raise NotImplementedError


class ServerChanPush(PushService):
    """Server酱推送"""
    
    async def send(self, title: str, content: str, config: Dict) -> bool:
        """
        发送Server酱推送
        config: {"sendkey": "your_sendkey"}
        """
        sendkey = config.get("sendkey")
        if not sendkey:
            logger.error("Server酱推送失败: sendkey未配置")
            return False
        
        url = f"https://sctapi.ftqq.com/{sendkey}.send"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    data={
                        "title": title,
                        "desp": content
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == 0:
                        logger.info(f"Server酱推送成功: {title}")
                        return True
                    else:
                        logger.error(f"Server酱推送失败: {result.get('message')}")
                        return False
                else:
                    logger.error(f"Server酱推送失败: HTTP {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Server酱推送异常: {str(e)}")
            return False


class WeComPush(PushService):
    """企业微信机器人推送"""
    
    async def send(self, title: str, content: str, config: Dict) -> bool:
        """
        发送企业微信推送
        config: {"webhook": "your_webhook_url"}
        """
        webhook = config.get("webhook")
        if not webhook:
            logger.error("企业微信推送失败: webhook未配置")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook,
                    json={
                        "msgtype": "markdown",
                        "markdown": {
                            "content": f"## {title}\n\n{content}"
                        }
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("errcode") == 0:
                        logger.info(f"企业微信推送成功: {title}")
                        return True
                    else:
                        logger.error(f"企业微信推送失败: {result.get('errmsg')}")
                        return False
                else:
                    logger.error(f"企业微信推送失败: HTTP {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"企业微信推送异常: {str(e)}")
            return False


class DingTalkPush(PushService):
    """钉钉机器人推送"""
    
    async def send(self, title: str, content: str, config: Dict) -> bool:
        """
        发送钉钉推送
        config: {"webhook": "your_webhook_url", "secret": "optional_secret"}
        """
        webhook = config.get("webhook")
        if not webhook:
            logger.error("钉钉推送失败: webhook未配置")
            return False
        
        # TODO: 如果配置了secret，需要计算签名
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook,
                    json={
                        "msgtype": "markdown",
                        "markdown": {
                            "title": title,
                            "text": f"## {title}\n\n{content}"
                        }
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("errcode") == 0:
                        logger.info(f"钉钉推送成功: {title}")
                        return True
                    else:
                        logger.error(f"钉钉推送失败: {result.get('errmsg')}")
                        return False
                else:
                    logger.error(f"钉钉推送失败: HTTP {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"钉钉推送异常: {str(e)}")
            return False


class FeishuPush(PushService):
    """飞书机器人推送"""
    
    async def send(self, title: str, content: str, config: Dict) -> bool:
        """
        发送飞书推送
        config: {"webhook": "your_webhook_url"}
        """
        webhook = config.get("webhook")
        if not webhook:
            logger.error("飞书推送失败: webhook未配置")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook,
                    json={
                        "msg_type": "text",
                        "content": {
                            "text": f"{title}\n\n{content}"
                        }
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == 0:
                        logger.info(f"飞书推送成功: {title}")
                        return True
                    else:
                        logger.error(f"飞书推送失败: {result.get('msg')}")
                        return False
                else:
                    logger.error(f"飞书推送失败: HTTP {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"飞书推送异常: {str(e)}")
            return False


class EmailPush(PushService):
    """邮件推送"""
    
    async def send(self, title: str, content: str, config: Dict) -> bool:
        """
        发送邮件推送
        config: {
            "smtp_host": "smtp.example.com",
            "smtp_port": 465,
            "smtp_user": "user@example.com",
            "smtp_password": "password",
            "to_email": "recipient@example.com"
        }
        """
        smtp_host = config.get("smtp_host")
        smtp_port = config.get("smtp_port", 465)
        smtp_user = config.get("smtp_user")
        smtp_password = config.get("smtp_password")
        to_email = config.get("to_email")
        
        if not all([smtp_host, smtp_user, smtp_password, to_email]):
            logger.error("邮件推送失败: 配置不完整")
            return False
        
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = title
            
            # 添加邮件正文
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 发送邮件
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            logger.info(f"邮件推送成功: {title}")
            return True
        except Exception as e:
            logger.error(f"邮件推送异常: {str(e)}")
            return False


class PushManager:
    """推送管理器"""
    
    def __init__(self):
        self.push_services = {
            "serverchan": ServerChanPush(),
            "wecom": WeComPush(),
            "dingtalk": DingTalkPush(),
            "feishu": FeishuPush(),
            "email": EmailPush()
        }
    
    async def send_alert(
        self, 
        channel_type: str, 
        channel_config: Dict,
        goods_title: str,
        goods_url: str,
        current_price: float,
        threshold_price: float,
        coupon_price: Optional[float] = None
    ) -> bool:
        """发送降价提醒"""
        service = self.push_services.get(channel_type)
        if not service:
            logger.error(f"不支持的推送渠道: {channel_type}")
            return False
        
        # 构造推送内容
        title = f"【降价提醒】{goods_title}"
        
        content = f"""
商品名称: {goods_title}

当前价格: ¥{current_price}
设置阈值: ¥{threshold_price}
"""
        
        if coupon_price:
            content += f"券后价格: ¥{coupon_price}\n"
        
        content += f"\n商品链接: {goods_url}"
        
        # 发送推送
        return await service.send(title, content, channel_config)


# 全局推送管理器实例
push_manager = PushManager()
