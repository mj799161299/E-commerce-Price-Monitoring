# 🔧 前端问题修复说明

## 问题描述

1. **登录后一直重定向到登录页** - 已修复
2. **注册提示"请求失败"** - 已修复

## 问题原因

### 1. 登录问题
- 后端返回 `access_token`
- 前端期望 `token`
- 导致token保存失败，获取用户信息时401

### 2. 注册问题  
- FastAPI返回错误信息字段是 `detail`
- 前端只处理了 `message`
- 导致422错误显示不正确

## 已修复文件

1. `frontend/src/stores/user.ts` - 修复token字段名
2. `frontend/src/utils/request.ts` - 修复错误处理逻辑

## 应用修复的方法

### 方法1：重新构建前端（推荐但较慢）

```powershell
# 停止前端容器
docker-compose stop frontend

# 重新构建并启动
docker-compose up -d --build frontend

# 等待构建完成（可能需要几分钟）
```

### 方法2：本地开发模式（快速测试）

```powershell
# 进入前端目录
cd frontend

# 安装依赖（首次需要）
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:3000
```

### 方法3：手动复制文件到容器（临时方案）

```powershell
# 复制修改后的文件到容器
docker cp frontend/src/stores/user.ts price_monitor_frontend:/usr/share/nginx/html/assets/
docker cp frontend/src/utils/request.ts price_monitor_frontend:/usr/share/nginx/html/assets/

# 注意：这个方法不推荐，因为文件已经被打包了
```

## 验证修复

### 测试登录

1. 访问 http://localhost
2. 使用测试账号登录：
   - 用户名: `newuser`
   - 密码: `123456`
3. 应该能成功进入仪表盘

### 测试注册

1. 点击"立即注册"
2. 填写信息：
   - 用户名: `testuser2`
   - 邮箱: `test2@example.com`
   - 密码: `123456`
3. 应该能成功注册并跳转到登录页

## 临时解决方案（无需重新构建）

如果不想重新构建，可以直接使用后端API测试：

### 使用Swagger UI

1. 访问 http://localhost:8000/docs
2. 测试注册接口 `/api/auth/register`
3. 测试登录接口 `/api/auth/login`
4. 复制返回的 `access_token`
5. 点击右上角 "Authorize"
6. 输入 `Bearer <access_token>`
7. 测试其他接口

### 使用Postman或curl

```bash
# 注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user1@example.com","password":"123456"}'

# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"123456"}'

# 获取用户信息
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## 后续建议

1. **开发环境使用本地开发服务器** - `npm run dev` 可以热更新
2. **生产环境才使用Docker构建** - 避免频繁重新构建
3. **配置开发环境代理** - vite.config.ts已配置代理到后端

## 开发模式启动步骤

```powershell
# 终端1：后端（使用Docker）
docker-compose up -d backend db

# 终端2：前端（本地开发）
cd frontend
npm install  # 首次需要
npm run dev

# 访问 http://localhost:3000
```

这样修改前端代码可以立即看到效果，无需重新构建Docker镜像。

## 已知可用账号

- 用户名: `testuser`, 密码: `123456`
- 用户名: `newuser`, 密码: `123456`

## 注意事项

- 前端Docker容器使用的是构建后的静态文件
- 修改源代码后需要重新构建才能生效
- 开发时建议使用本地开发服务器（npm run dev）
- 生产部署时才使用Docker构建
