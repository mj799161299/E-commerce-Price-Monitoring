from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from app.core.config import settings
import base64


class CryptoUtil:
    """数据加密工具类"""
    
    @staticmethod
    def encrypt(data: str) -> str:
        """AES加密"""
        if not data:
            return ""
        
        try:
            # 确保密钥长度为32字节
            key = settings.AES_KEY.encode('utf-8')[:32].ljust(32, b'\0')
            
            # 创建AES加密器
            cipher = AES.new(key, AES.MODE_CBC)
            
            # 加密数据
            encrypted_data = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
            
            # 返回base64编码的IV+密文
            result = base64.b64encode(cipher.iv + encrypted_data).decode('utf-8')
            return result
        except Exception as e:
            raise ValueError(f"加密失败: {str(e)}")
    
    @staticmethod
    def decrypt(encrypted_data: str) -> str:
        """AES解密"""
        if not encrypted_data:
            return ""
        
        try:
            # 确保密钥长度为32字节
            key = settings.AES_KEY.encode('utf-8')[:32].ljust(32, b'\0')
            
            # 解码base64
            raw = base64.b64decode(encrypted_data)
            
            # 提取IV和密文
            iv = raw[:16]
            encrypted = raw[16:]
            
            # 创建AES解密器
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # 解密并去除填充
            decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")
