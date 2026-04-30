from abc import ABC, abstractmethod
from typing import Dict, Optional
import re
import httpx


class PlatformAdapter(ABC):
    """平台API适配器基类"""
    
    @abstractmethod
    async def get_goods_info(self, goods_id: str) -> Dict:
        """获取商品信息"""
        pass
    
    @abstractmethod
    async def parse_goods_id(self, url_or_code: str) -> str:
        """解析商品ID"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """测试API连通性"""
        pass


class TaobaoAdapter(PlatformAdapter):
    """淘宝/天猫API适配器"""
    
    def __init__(self, app_key: str, app_secret: str, pid: Optional[str] = None):
        self.app_key = app_key
        self.app_secret = app_secret
        self.pid = pid
    
    async def get_goods_info(self, goods_id: str) -> Dict:
        """获取商品信息"""
        # TODO: 调用淘宝联盟API获取商品信息
        # 这里返回模拟数据，实际需要调用 taobao.tbk.item.info.get 接口
        
        import hashlib
        
        # 使用商品ID生成哈希值，使不同商品显示不同的数据
        hash_val = int(hashlib.md5(goods_id.encode()).hexdigest()[:8], 16)
        
        # 价格范围：20-3000元
        base_price = 20 + (hash_val % 2980)
        price = round(base_price / 1.0, 2)
        
        # 券后价：比原价低5-25%
        discount_percent = 5 + (hash_val % 21)  # 5-25%
        coupon_price = round(price * (100 - discount_percent) / 100, 2)
        
        # 图片颜色基于哈希值
        colors = ['FF6B6B', 'FFA07A', 'FFB347', 'FF69B4', 'FF1493', 'DC143C', 'FF4500']
        color_index = hash_val % len(colors)
        color = colors[color_index]
        
        # 商品标题
        categories = ['女装', '男装', '手机', '数码', '家电', '美妆', '食品', '家居', '童装', '运动']
        category = categories[hash_val % len(categories)]
        
        title = f"淘宝{category}-{goods_id}"
        
        # 图片URL
        image = f"https://via.placeholder.com/300/{color}/FFFFFF?text=TB+{goods_id[:6]}"
        
        return {
            "title": title,
            "price": price,
            "coupon_price": coupon_price,
            "image": image
        }
    
    async def parse_goods_id(self, url_or_code: str) -> str:
        """解析商品ID"""
        # 支持多种淘宝/天猫链接格式

        # 如果是淘口令，需要先解析淘口令获取真实链接
        if "￥" in url_or_code or "￥" in url_or_code or "¥" in url_or_code:
            # TODO: 调用淘宝API解析淘口令
            raise ValueError("暂不支持淘口令解析，请使用商品链接")

        # PC端格式
        patterns = [
            # 标准淘宝链接: https://item.taobao.com/item.htm?id=123456
            r'item\.taobao\.com/item\.htm\?[^\?]*id=(\d+)',
            r'item\.taobao\.com/item\.htm\?id=(\d+)',
            # 天猫链接: https://detail.tmall.com/item.htm?id=123456
            r'detail\.tmall\.com/item\.htm\?[^\?]*id=(\d+)',
            r'detail\.tmall\.com/item\.htm\?id=(\d+)',
            # 天猫国际: https://detail.tmall.hk/item.htm?id=123456
            r'detail\.tmall\.hk/item\.htm\?[^\?]*id=(\d+)',
            r'detail\.tmall\.hk/item\.htm\?id=(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url_or_code)
            if match:
                return match.group(1)

        # 移动端格式
        mobile_patterns = [
            # 淘宝H5: https://h5.m.taobao.com/awp/core/detail.htm?id=123456
            r'h5\.m\.taobao\.com/awp/core/detail\.htm\?[^\?]*id=(\d+)',
            r'h5\.m\.taobao\.com/awp/core/detail\.htm\?id=(\d+)',
            # 淘宝H5其他格式: https://h5.m.taobao.com/awp/core/detail.htm?detailItemId=123456
            r'h5\.m\.taobao\.com/awp/core/detail\.htm\?[^\?]*detailItemId=(\d+)',
            # 淘宝客户端: taobao://item.taobao.com/item.htm?id=123456
            r'taobao://item\.taobao\.com/item\.htm\?[^\?]*id=(\d+)',
            # 天猫H5: https://h5.m.tmall.com/awp/core/detail.htm?id=123456
            r'h5\.m\.tmall\.com/awp/core/detail\.htm\?[^\?]*id=(\d+)',
            r'h5\.m\.tmall\.com/awp/core/detail\.htm\?id=(\d+)',
            # 天猫客户端: tmall://tmallclient/item_detail.htm?id=123456
            r'tmall://[^\?]*\?id=(\d+)',
            # 移动端简化格式
            r'm\.taobao\.com/[^\?]*\?id=(\d+)',
            r'm\.tmall\.com/[^\?]*\?id=(\d+)',
        ]

        for pattern in mobile_patterns:
            match = re.search(pattern, url_or_code)
            if match:
                return match.group(1)

        # 通用ID提取（作为后备方案）
        match = re.search(r'[?&]id=(\d+)', url_or_code)
        if match:
            return match.group(1)

        raise ValueError("无法从链接中解析商品ID，请提供标准淘宝/天猫商品链接")
    
    async def test_connection(self) -> bool:
        """测试API连通性"""
        # TODO: 调用淘宝API测试连接
        # 这里简单返回True，实际需要调用API验证凭证
        return True


class JDAdapter(PlatformAdapter):
    """京东API适配器"""
    
    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret = app_secret
    
    async def get_goods_info(self, goods_id: str) -> Dict:
        """获取商品信息"""
        # TODO: 调用京东联盟API获取商品信息
        # 这里返回模拟数据，实际需要调用 jd.union.open.goods.promotiongoodsinfo.query 接口
        
        # 基于商品ID生成伪随机数据，使不同商品显示不同的价格和图片
        import hashlib
        
        # 使用商品ID生成哈希值
        hash_val = int(hashlib.md5(goods_id.encode()).hexdigest()[:8], 16)
        
        # 价格范围：50-5000元
        base_price = 50 + (hash_val % 4950)
        price = base_price / 1.0
        
        # 券后价：比原价低5-20%
        discount_percent = 5 + (hash_val % 16)  # 5-20%
        coupon_price = round(price * (100 - discount_percent) / 100, 2)
        
        # 图片颜色基于哈希值
        colors = ['FF6B6B', '4ECDC4', '45B7D1', '96CEB4', 'FFEAA7', 'DDA0DD', '98D8C8']
        color_index = hash_val % len(colors)
        color = colors[color_index]
        
        # 商品标题
        categories = ['手机', '笔记本电脑', '平板电脑', '家电', '服饰', '食品', '美妆', '家居']
        category = categories[hash_val % len(categories)]
        
        title = f"京东{category}-{goods_id}"
        
        # 图片URL（使用占位图，但不同商品显示不同颜色）
        image = f"https://via.placeholder.com/300/{color}/FFFFFF?text=JD+{goods_id[:6]}"
        
        return {
            "title": title,
            "price": price,
            "coupon_price": coupon_price,
            "image": image
        }
    
    async def parse_goods_id(self, url_or_code: str) -> str:
        """解析商品ID"""
        # 支持多种京东链接格式（包括PC端和移动端）

        # 检测并处理短链接 (3.cn, u.jd.com等)
        if re.search(r'(?:3\.cn|u\.jd\.com|k\.pl|jd\.cn)/', url_or_code):
            try:
                goods_id = await self._resolve_short_url(url_or_code)
                if goods_id:
                    return goods_id
            except Exception as e:
                raise ValueError(f"解析短链接失败: {str(e)}")

        patterns = [
            # PC端标准格式: https://item.jd.com/123456.html
            r'item\.jd\.com/(\d+)\.html',
            # PC端带查询参数: https://item.jd.com/123456.html?query=1
            r'item\.jd\.com/(\d+)',
            # 移动端商品页: https://item.m.jd.com/product/123456.html
            r'item\.m\.jd\.com/product/(\d+)\.html',
            # 移动端ware格式: https://item.m.jd.com/ware/123456.html
            r'item\.m\.jd\.com/ware/(\d+)\.html',
            # 全球购PC端: https://item.jd.hk/123456.html
            r'item\.jd\.hk/(\d+)\.html',
            # 移动端简化格式: https://m.jd.com/product/123456.html
            r'm\.jd\.com/product/(\d+)\.html',
            # 移动端product格式: https://product.m.jd.com/product/123456.html
            r'product\.m\.jd\.com/product/(\d+)\.html',
            # 京东APP深度链接: openjd://jd.com/product/123456
            r'openjd://[^\?]*product/(\d+)',
            r'openapp\.jdmobile://[^\?]*(\d{8,})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url_or_code)
            if match:
                return match.group(1)

        # 尝试从URL路径中提取纯数字ID（最后一段数字）
        # 例如：https://item.jd.com/123456?xxx 或 /123456
        match = re.search(r'/(\d{8,})(?:\?|#|\.html|$)', url_or_code)
        if match:
            return match.group(1)

        raise ValueError("无法从链接中解析商品ID，请提供标准京东商品链接")

    async def _resolve_short_url(self, short_url: str) -> str:
        """解析京东短链接，获取真实商品ID"""
        # 提取URL（支持从文案中提取）
        url_match = re.search(r'(https?://[^\s「」【】]+)', short_url)
        if url_match:
            short_url = url_match.group(1)
        
        # 清理URL中的特殊字符
        short_url = short_url.split('?')[0] if '?' in short_url else short_url
        
        try:
            # 使用httpx跟踪重定向
            async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
                response = await client.get(short_url)
                final_url = str(response.url)
                
                # 从最终URL中提取商品ID
                patterns = [
                    r'item\.jd\.com/(\d+)',
                    r'product/(\d+)',
                    r'/(\d{8,})\.html',
                    r'/(\d{8,})(?:\?|#|$)',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, final_url)
                    if match:
                        return match.group(1)
                
                raise ValueError("无法从重定向后的链接中提取商品ID")
        except httpx.TimeoutException:
            raise ValueError("解析短链接超时，请稍后重试")
        except Exception as e:
            raise ValueError(f"解析短链接失败: {str(e)}")
    
    async def test_connection(self) -> bool:
        """测试API连通性"""
        # TODO: 调用京东API测试连接
        return True


class PDDAdapter(PlatformAdapter):
    """拼多多API适配器"""
    
    def __init__(self, client_id: str, client_secret: str, pid: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.pid = pid
    
    async def get_goods_info(self, goods_id: str) -> Dict:
        """获取商品信息"""
        # TODO: 调用多多进宝API获取商品信息
        # 这里返回模拟数据，实际需要调用 pdd.ddk.goods.detail 接口
        
        import hashlib
        
        # 使用商品ID生成哈希值，使不同商品显示不同的数据
        hash_val = int(hashlib.md5(goods_id.encode()).hexdigest()[:8], 16)
        
        # 价格范围：10-500元（拼多多价格相对较低）
        base_price = 10 + (hash_val % 490)
        price = round(base_price / 1.0, 2)
        
        # 券后价：比原价低10-40%（拼多多优惠力度大）
        discount_percent = 10 + (hash_val % 31)  # 10-40%
        coupon_price = round(price * (100 - discount_percent) / 100, 2)
        
        # 图片颜色基于哈希值
        colors = ['FF4757', 'FF6348', 'FF7F50', 'FFA502', 'FFD700', '2ED573', '1E90FF']
        color_index = hash_val % len(colors)
        color = colors[color_index]
        
        # 商品标题
        categories = ['水果', '百货', '服饰', '食品', '美妆', '家居', '数码', '家电', '母婴', '运动']
        category = categories[hash_val % len(categories)]
        
        title = f"拼多多{category}-{goods_id}"
        
        # 图片URL
        image = f"https://via.placeholder.com/300/{color}/FFFFFF?text=PDD+{goods_id[:6]}"
        
        return {
            "title": title,
            "price": price,
            "coupon_price": coupon_price,
            "image": image
        }
    
    async def parse_goods_id(self, url_or_code: str) -> str:
        """解析商品ID"""
        # 支持多种拼多多链接格式（包括PC端和移动端）

        # PC端和移动端通用格式（goods_id参数）
        patterns = [
            # 移动端标准格式: https://mobile.yangkeduo.com/goods.html?goods_id=123456
            r'mobile\.yangkeduo\.com/goods\.html\?[^\?]*goods_id=(\d+)',
            r'mobile\.yangkeduo\.com/goods\.html\?goods_id=(\d+)',
            # 移动端简化格式: https://m.pinduoduo.com/goods.html?goods_id=123456
            r'm\.pinduoduo\.com/goods\.html\?[^\?]*goods_id=(\d+)',
            r'm\.pinduoduo\.com/goods\.html\?goods_id=(\d+)',
            # PC端格式: https://pinduoduo.com/goods.html?goods_id=123456
            r'pinduoduo\.com/[^\?]*\?goods_id=(\d+)',
            # 拼多多APP深度链接: pinduoduo://com.xunmeng.pinduoduo/goods.html?goods_id=123456
            r'pinduoduo://[^\?]*goods_id=(\d+)',
            # 商品详情页: https://mobile.yangkeduo.com/goods2.html?goods_id=123456
            r'mobile\.yangkeduo\.com/goods2\.html\?[^\?]*goods_id=(\d+)',
            r'mobile\.yangkeduo\.com/goods2\.html\?goods_id=(\d+)',
            # 拼多多小程序格式
            r'yangkeduo\.com/goods\.html\?goods_id=(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url_or_code)
            if match:
                return match.group(1)

        # 通用goods_id提取（作为后备方案）
        match = re.search(r'goods_id=(\d+)', url_or_code)
        if match:
            return match.group(1)

        # 检测短链接
        if "pinduoduo.com" in url_or_code or "yangkeduo.com" in url_or_code:
            # TODO: 处理短链接重定向
            raise ValueError("暂不支持短链接，请使用完整商品链接（需包含goods_id参数）")

        raise ValueError("无法从链接中解析商品ID，请提供标准拼多多商品链接（需包含goods_id参数）")
    
    async def test_connection(self) -> bool:
        """测试API连通性"""
        # TODO: 调用拼多多API测试连接
        return True
