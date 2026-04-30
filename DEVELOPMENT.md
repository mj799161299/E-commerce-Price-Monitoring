# 开发指南

## 后端开发

### 添加新的API路由

1. 在 `backend/app/api/` 目录下创建新的路由文件
2. 定义路由和处理函数
3. 在 `backend/app/main.py` 中注册路由

示例：
```python
# backend/app/api/example.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
async def example():
    return {"message": "示例"}
```

### 添加数据库模型

1. 在 `backend/app/models/models.py` 中定义新模型
2. 使用 Alembic 生成迁移文件
3. 执行迁移

```bash
# 生成迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

### 添加平台适配器

1. 在 `backend/app/adapters/` 目录下创建新的适配器
2. 继承 `PlatformAdapter` 基类
3. 实现必需的方法

## 前端开发

### 添加新页面

1. 在 `frontend/src/views/` 创建新的 Vue 组件
2. 在 `frontend/src/router/index.ts` 中添加路由配置

### 添加API接口

1. 在 `frontend/src/api/` 目录下创建或编辑接口文件
2. 使用 `request` 工具发起请求

示例：
```typescript
// frontend/src/api/example.ts
import request from '@/utils/request'

export const getExample = () => {
  return request.get('/example')
}
```

### 状态管理

使用 Pinia 管理全局状态：

```typescript
// frontend/src/stores/example.ts
import { defineStore } from 'pinia'

export const useExampleStore = defineStore('example', () => {
  const data = ref(null)
  
  const fetchData = async () => {
    // 获取数据
  }
  
  return { data, fetchData }
})
```

## 调试技巧

### 后端调试

1. 查看日志：`docker-compose logs -f backend`
2. 进入容器：`docker exec -it price_monitor_backend bash`
3. 使用 FastAPI 自动文档测试接口：http://localhost:8000/docs

### 前端调试

1. 使用浏览器开发者工具
2. 查看 Vue DevTools
3. 检查网络请求

## 常见问题

### 数据库连接失败

检查 `docker-compose.yml` 和 `.env` 中的数据库配置是否一致。

### 前端无法访问后端API

检查 CORS 配置和 Nginx 代理配置。

### Docker 构建失败

清理 Docker 缓存：
```bash
docker-compose down
docker system prune -a
docker-compose up --build
```

## 代码规范

### Python

- 遵循 PEP 8 规范
- 使用类型注解
- 编写文档字符串

### TypeScript

- 使用 ESLint 检查代码
- 遵循 Vue 3 组合式 API 风格
- 使用 TypeScript 类型系统

## 测试

### 后端测试

```bash
cd backend
pytest
```

### 前端测试

```bash
cd frontend
npm run test
```

## 部署

### 生产环境部署

1. 修改所有默认密码和密钥
2. 设置 `DEBUG=False`
3. 配置 HTTPS
4. 设置防火墙规则
5. 配置数据库备份

### 性能优化

1. 启用 Nginx gzip 压缩
2. 配置 CDN
3. 优化数据库查询
4. 使用 Redis 缓存
