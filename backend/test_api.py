"""
快速测试脚本 - 验证后端API功能
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000"


async def test_api():
    """测试API功能"""
    async with httpx.AsyncClient() as client:
        print("=" * 50)
        print("开始测试后端API")
        print("=" * 50)
        
        # 1. 测试健康检查
        print("\n1. 测试健康检查...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.json()}")
        except Exception as e:
            print(f"   错误: {e}")
            return
        
        # 2. 测试用户注册
        print("\n2. 测试用户注册...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "123456"
                }
            )
            print(f"   状态码: {response.status_code}")
            if response.status_code == 201:
                print(f"   响应: {response.json()}")
            else:
                print(f"   响应: {response.text}")
        except Exception as e:
            print(f"   错误: {e}")
        
        # 3. 测试用户登录
        print("\n3. 测试用户登录...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "username": "testuser",
                    "password": "123456"
                }
            )
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                print(f"   获取到Token: {token[:50]}...")
                
                # 4. 测试获取用户信息
                print("\n4. 测试获取用户信息...")
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(
                    f"{BASE_URL}/api/auth/me",
                    headers=headers
                )
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.json()}")
                
                # 5. 测试配置API凭证
                print("\n5. 测试配置API凭证...")
                response = await client.post(
                    f"{BASE_URL}/api/config/platforms/taobao",
                    headers=headers,
                    json={
                        "platform": "taobao",
                        "app_key": "test_app_key",
                        "app_secret": "test_app_secret",
                        "pid": "test_pid"
                    }
                )
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.json()}")
                
                # 6. 测试获取监控列表
                print("\n6. 测试获取监控列表...")
                response = await client.get(
                    f"{BASE_URL}/api/monitor/items",
                    headers=headers
                )
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.json()}")
                
            else:
                print(f"   响应: {response.text}")
        except Exception as e:
            print(f"   错误: {e}")
        
        print("\n" + "=" * 50)
        print("测试完成！")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_api())
