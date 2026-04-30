# API 测试指南

## 前置准备

1. 确保 Docker 容器正在运行：
```bash
docker-compose ps
```

2. 初始化数据库（首次运行）：
```bash
docker exec -it price_monitor_backend python init_db.py
```

3. 访问 API 文档：http://localhost:8000/docs

## 测试流程

### 1. 用户注册

**接口**: POST /api/auth/register

**请求体**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "123456"
}
```

**预期响应**: 201 Created
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true,
  "create_time": "2024-01-01T00:00:00"
}
```

### 2. 用户登录

**接口**: POST /api/auth/login

**请求体**:
```json
{
  "username": "testuser",
  "password": "123456"
}
```

**预期响应**: 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**重要**: 保存 access_token，后续请求需要在 Header 中携带：
```
Authorization: Bearer <access_token>
```

### 3. 获取当前用户信息

**接口**: GET /api/auth/me

**Headers**:
```
Authorization: Bearer <access_token>
```

**预期响应**: 200 OK
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "is_active": true,
  "create_time": "2024-01-01T00:00:00"
}
```

### 4. 配置平台API凭证

**接口**: POST /api/config/platforms/taobao

**Headers**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "platform": "taobao",
  "app_key": "your_app_key",
  "app_secret": "your_app_secret",
  "pid": "your_pid"
}
```

**预期响应**: 201 Created
```json
{
  "id": 1,
  "platform": "taobao",
  "is_valid": false,
  "update_time": "2024-01-01T00:00:00",
  "has_app_key": true,
  "has_app_secret": true,
  "has_pid": true
}
```

### 5. 测试API连通性

**接口**: POST /api/config/platforms/taobao/test

**Headers**:
```
Authorization: Bearer <access_token>
```

**预期响应**: 200 OK
```json
{
  "success": true,
  "message": "API连接测试成功"
}
```

### 6. 添加监控商品

**接口**: POST /api/monitor/items

**Headers**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "goods_url": "https://item.taobao.com/item.htm?id=123456789",
  "threshold_price": 99.99,
  "threshold_type": "price",
  "monitor_interval": 60
}
```

**预期响应**: 201 Created
```json
{
  "id": 1,
  "goods_id": "123456789",
  "platform": "taobao",
  "goods_title": "淘宝商品-123456789",
  "goods_url": "https://item.taobao.com/item.htm?id=123456789",
  "goods_image": "https://via.placeholder.com/300",
  "current_price": 99.99,
  "threshold_price": 99.99,
  "threshold_type": "price",
  "monitor_interval": 60,
  "is_active": true,
  "is_valid": true,
  "create_time": "2024-01-01T00:00:00",
  "update_time": "2024-01-01T00:00:00"
}
```

### 7. 获取监控商品列表

**接口**: GET /api/monitor/items

**Headers**:
```
Authorization: Bearer <access_token>
```

**预期响应**: 200 OK
```json
[
  {
    "id": 1,
    "goods_id": "123456789",
    "platform": "taobao",
    "goods_title": "淘宝商品-123456789",
    ...
  }
]
```

### 8. 更新监控商品

**接口**: PUT /api/monitor/items/1

**Headers**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "threshold_price": 89.99,
  "is_active": true
}
```

### 9. 获取价格历史

**接口**: GET /api/monitor/items/1/history

**Headers**:
```
Authorization: Bearer <access_token>
```

**预期响应**: 200 OK
```json
[
  {
    "id": 1,
    "price": 99.99,
    "coupon_price": 89.99,
    "fetch_time": "2024-01-01T00:00:00"
  }
]
```

### 10. 删除监控商品

**接口**: DELETE /api/monitor/items/1

**Headers**:
```
Authorization: Bearer <access_token>
```

**预期响应**: 200 OK
```json
{
  "message": "删除成功"
}
```

## 使用 Swagger UI 测试

1. 访问 http://localhost:8000/docs
2. 点击右上角的 "Authorize" 按钮
3. 输入格式：`Bearer <access_token>`
4. 点击 "Authorize" 确认
5. 现在可以直接在页面上测试所有需要认证的接口

## 常见错误

### 401 Unauthorized
- 检查是否携带了正确的 Authorization Header
- 检查 token 是否过期（默认7天）

### 400 Bad Request
- 检查请求体格式是否正确
- 检查必填字段是否都已提供

### 404 Not Found
- 检查资源ID是否存在
- 检查资源是否属于当前用户

### 500 Internal Server Error
- 查看后端日志：`docker-compose logs backend`
- 检查数据库连接是否正常
