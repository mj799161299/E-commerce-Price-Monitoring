# 电商价格监控系统

基于 Vue 3 + FastAPI + PostgreSQL 的全合规电商价格监控 Web 应用。

## 项目简介

本项目是一款基于前后端分离架构、完全依托电商平台官方开放 API、全合规的 Web 端价格监控应用。支持淘宝/天猫、京东、拼多多三大平台，实现商品一键添加、多维度价格阈值设置、定时合规查询、多渠道实时降价提醒。

## 技术栈

### 前端
- Vue 3 + TypeScript
- Element Plus (UI组件库)
- Pinia (状态管理)
- Vue Router (路由管理)
- Axios (HTTP客户端)
- ECharts (数据可视化)
- Vite (构建工具)

### 后端
- FastAPI (Web框架)
- PostgreSQL (数据库)
- SQLAlchemy 2.0 (ORM)
- APScheduler (定时任务)
- JWT (用户认证)
- PyCryptodome (数据加密)

### 部署
- Docker + Docker Compose
- Nginx (前端服务器)
- Gunicorn + Uvicorn (后端服务器)

## 项目结构

```
.
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据库模型
│   │   ├── services/       # 业务逻辑
│   │   ├── adapters/       # 平台API适配器
│   │   ├── utils/          # 工具函数
│   │   ├── core/           # 核心配置
│   │   └── main.py         # 应用入口
│   ├── requirements.txt    # Python依赖
│   ├── Dockerfile          # Docker配置
│   └── .env.example        # 环境变量示例
│
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── api/           # API接口
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 公共组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   ├── utils/         # 工具函数
│   │   ├── App.vue        # 根组件
│   │   └── main.ts        # 应用入口
│   ├── package.json       # Node依赖
│   ├── vite.config.ts     # Vite配置
│   ├── Dockerfile         # Docker配置
│   └── nginx.conf         # Nginx配置
│
├── docker-compose.yml     # Docker Compose配置
└── README.md              # 项目文档

```

## 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+

### 使用 Docker Compose 部署（推荐）

1. 克隆项目
```bash
git clone <repository-url>
cd 多电商价格监控工具
```

2. 配置环境变量
```bash
# 复制后端环境变量示例文件
cp backend/.env.example backend/.env

# 编辑 backend/.env 和 docker-compose.yml，修改以下配置：
# - 数据库密码
# - JWT密钥
# - AES加密密钥
```

3. 启动所有服务
```bash
docker-compose up -d
```

4. 访问应用
- 前端：http://localhost
- 后端API文档：http://localhost:8000/docs

### 本地开发

#### 后端开发

1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件
```

3. 启动开发服务器
```bash
uvicorn app.main:app --reload
```

#### 前端开发

1. 安装依赖
```bash
cd frontend
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

3. 访问 http://localhost:3000

## 核心功能

### 已实现（骨架）
- ✅ 项目基础架构
- ✅ 前后端分离架构
- ✅ Docker容器化部署
- ✅ 数据库模型设计
- ✅ API路由骨架
- ✅ 用户认证框架
- ✅ 前端路由配置
- ✅ 状态管理配置

### 待实现
- ⏳ 用户注册/登录功能
- ⏳ API凭证管理
- ⏳ 商品监控管理
- ⏳ 价格阈值设置
- ⏳ 定时任务调度
- ⏳ 消息推送功能
- ⏳ 历史价格可视化
- ⏳ 三大平台API对接

## 数据库设计

项目包含6个核心数据表：

1. **users** - 用户表
2. **api_config** - API凭证配置表
3. **monitor_items** - 监控商品表
4. **price_history** - 历史价格表
5. **operation_logs** - 操作日志表
6. **push_channels** - 推送渠道配置表

详细设计请参考产品规划文档。

## API文档

启动后端服务后，访问以下地址查看自动生成的API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发计划

详细的开发计划和功能规划请参考 `多电商价格监控工具.md` 文档。

## 注意事项

1. **安全配置**：生产环境务必修改默认密码和密钥
2. **API申请**：需要自行申请淘宝联盟、京东联盟、多多进宝的API凭证
3. **合规使用**：仅使用官方开放API，严禁爬虫行为
4. **数据备份**：定期备份PostgreSQL数据库

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
