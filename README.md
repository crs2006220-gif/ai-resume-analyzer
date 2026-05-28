# AI Resume Analysis System

基于 FastAPI + DeepSeek 的智能简历分析系统，支持 PDF 简历解析、AI 信息提取、岗位匹配度评分与改进建议。

## 功能特性

- PDF 简历解析与结构化提取（姓名、联系方式、教育/工作经历、技能）
- DeepSeek V4 Pro 驱动的简历内容深度分析
- 岗位匹配度四维评分（综合/岗位匹配/结构/内容）
- 优劣势识别与个性化改进建议
- Redis 缓存机制，重复上传秒级响应
- SSE 流式进度推送，实时展示处理阶段

## 技术栈

### 后端

| 分类 | 技术 | 用途 |
|---|---|---|
| Web 框架 | FastAPI 0.115 | 高性能异步 API 服务 |
| ASGI 服务器 | Uvicorn 0.34 | 支持热重载的开发服务器 |
| AI / LLM | DeepSeek API (OpenAI 兼容) | 简历信息提取 & 匹配度评分 |
| PDF 解析 | PyMuPDF 1.25 | PDF 文本提取 |
| 缓存 | Redis 5.2 + redis-py (异步) | 简历分析结果缓存，TTL 1h |
| 配置管理 | Pydantic Settings 2.8 | .env 环境变量自动加载 |
| 数据校验 | Pydantic 2.10 | 请求/响应 Schema 校验 |
| 跨域 | CORSMiddleware | 前后端分离跨域支持 |
| 文件处理 | python-multipart | multipart/form-data 文件上传 |
| HTTP 客户端 | httpx 0.28 | 异步 HTTP 请求（预留给外部 API 调用） |

### 前端

| 分类 | 技术 | 用途 |
|---|---|---|
| 框架 | Vue 3 (CDN) | 响应式 UI |
| 组件库 | Element Plus (CDN) | 上传、评分、标签等 UI 组件 |
| 进度交互 | fetch + 模拟进度算法 | 三阶段平滑进度条（15% → 90% → 100%） |
| 样式 | 原生 CSS | 轻量级自定义样式 |

### 部署环境

| 组件 | 要求 | 说明 |
|---|---|---|
| Python | 3.11+ | 后端运行环境 |
| Redis | 6.0+ | 缓存服务（WSL2 或原生安装） |
| 操作系统 | Windows / Linux / macOS | 跨平台兼容 |
| 端口 | 8000 | FastAPI 默认端口 |
| WSL2（可选） | Windows 用户运行 Redis 推荐方案 | localhost 自动转发 |

## 项目结构

```
Demo/
├── .env                      # 环境变量（不提交 Git）
├── .env.example              # 环境变量模板
├── requirements.txt          # Python 依赖
├── README.md
├── static/
│   └── index.html            # Vue3 + Element Plus 前端页面
└── app/
    ├── __init__.py
    ├── config.py             # Pydantic Settings 配置管理
    ├── main.py               # FastAPI 入口，路由挂载，静态文件
    ├── models/
    │   └── resume.py         # Pydantic 数据模型
    ├── routers/
    │   ├── __init__.py
    │   ├── resume.py         # 简历上传/解析/流式分析接口
    │   └── matching.py       # 匹配度评分接口
    ├── services/
    │   ├── __init__.py
    │   ├── pdf_parser.py     # PyMuPDF PDF 文本提取
    │   ├── ai_extractor.py   # DeepSeek API 简历信息提取
    │   └── matcher.py        # DeepSeek API 匹配度计算
    └── utils/
        ├── cache.py          # Redis 缓存工具
        └── redis_client.py   # Redis 异步连接管理
```

## 环境变量

| 变量 | 必填 | 默认值 | 说明 |
|---|---|---|---|
| `DEEPSEEK_API_KEY` | 是 | - | DeepSeek API 密钥 |
| `DEEPSEEK_BASE_URL` | 否 | `https://api.deepseek.com` | API 基础地址 |
| `DEEPSEEK_MODEL` | 否 | `deepseek-v4-pro` | 模型名称 |
| `REDIS_HOST` | 否 | `localhost` | Redis 地址 |
| `REDIS_PORT` | 否 | `6379` | Redis 端口 |
| `REDIS_DB` | 否 | `0` | Redis 数据库编号 |
| `API_PREFIX` | 否 | `/api/v1` | API 路由前缀 |

## API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/` | 前端页面 |
| `GET` | `/health` | 健康检查 |
| `GET` | `/docs` | Swagger UI 文档 |
| `GET` | `/redoc` | ReDoc 文档 |
| `GET` | `/openapi.json` | OpenAPI Schema |
| `POST` | `/api/v1/resume/upload` | 上传 PDF + 岗位，返回完整分析结果（含缓存） |
| `POST` | `/api/v1/resume/upload/stream` | SSE 流式上传分析，实时进度推送 |
| `POST` | `/api/v1/resume/parse` | 仅解析 PDF，返回结构化简历信息 |
| `POST` | `/api/v1/matching/score` | 传入简历 JSON + 岗位，返回匹配度评分 |

## 快速开始

```bash
# 1. 克隆项目
git clone <repo-url> && cd Demo

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY

# 4. 启动 Redis（WSL2 / Linux）
redis-server

# 5. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000` 使用前端页面，`http://localhost:8000/docs` 查看 API 文档。

## 架构演进与未来规划 (Architecture Roadmap)

### 1. 引入向量数据库 (Vector Database) 实现语义检索

- **当前痛点**：现有的关键词匹配（Keyword Matching）无法识别同义词（如 "Java" 与 "J2EE"）或深层语义关联。
- **解决方案**：引入 **Milvus** 或 **PgVector** 等向量数据库。在简历入库和岗位创建时，利用 Embedding 模型将文本转化为高维向量存储。
- **预期效果**：实现基于语义的相似度搜索（Semantic Search）。例如，当 HR 搜索「高并发经验」时，系统能自动召回简历中包含「线程池调优」、「QPS 优化」等描述的候选人，大幅提升召回率。

### 2. 引入异步任务队列 (Async Task Queue)

- **当前痛点**：目前的简历解析和 AI 评分是同步阻塞的。当 PDF 文件较大或 LLM 响应较慢时，HTTP 请求容易超时，且无法处理高并发上传。
- **解决方案**：引入 **Celery + Redis / RabbitMQ** 构建异步任务队列。用户点击「分析」后，后端立即返回 `Task ID`，前端通过轮询或 WebSocket 获取处理进度（如：PDF 解析中...、AI 评分中...）。
- **预期效果**：实现系统的**最终一致性**，解耦文件上传与 AI 推理过程，显著提升系统的吞吐量（Throughput）和抗并发能力。

### 3. RAG (检索增强生成) 架构优化

- **当前痛点**：直接将整份简历和岗位描述拼接进 Prompt，容易超出 LLM 的 Context Window 限制，且 AI 评分缺乏企业标准的参考依据，容易产生幻觉。
- **解决方案**：构建 **RAG（Retrieval-Augmented Generation）** 系统。将企业的「岗位胜任力模型」和「优秀简历范例」作为知识库。在评分前，先检索与当前岗位最相关的 Few-Shot 示例注入 Prompt。
- **预期效果**：大幅降低 AI 幻觉，提高评分的准确性、一致性和可解释性，使 AI 评分更贴合企业实际用人标准。
