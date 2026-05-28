# 项目总结文档

## 项目背景与目标

AI Resume Analysis System 是一个面向招聘场景的智能简历分析平台。传统简历筛选依赖 HR 人工阅读，效率低且标准不统一。本项目通过 **DeepSeek V4 Pro 大模型** 实现简历自动解析、结构化提取和岗位匹配度评分，帮助面试官快速了解候选人概况，提升招聘效率。

**目标用户**：技术面试官、HR、猎头顾问

## 核心功能

### 1. PDF 简历解析

基于 PyMuPDF 提取 PDF 中的文本内容，支持：
- 中英文混排简历
- 多页 PDF 文档
- 复杂排版自适应

### 2. AI 信息提取

通过 DeepSeek V4 Pro 将非结构化简历文本转换为结构化数据：
- **基本信息**：姓名、邮箱、电话、所在地
- **教育背景**：学校、学历、专业、时间
- **工作经历**：公司、职位、时间、职责描述
- **技能标签**：编程语言、框架、工具、软技能

### 3. 四维匹配度评分

| 维度 | 权重 | 说明 |
|------|------|------|
| 综合能力 | 40% | 技术栈、项目经验、教育背景 |
| 岗位匹配度 | 30% | 与目标岗位 JD 的相关性 |
| 简历结构 | 15% | 排版清晰度、信息完整性 |
| 内容质量 | 15% | 描述具体性、量化成果 |

### 4. 优劣势分析与建议

- 自动识别候选人核心竞争力
- 标注简历薄弱环节
- 生成可操作的改进建议清单

## 技术亮点

### 为什么选择 DeepSeek V4 Pro

- **性价比**：API 定价仅为 GPT-4 的 1/10，适合高频调用场景
- **中文能力**：在中文简历理解、岗位匹配等任务上表现优异
- **OpenAI 兼容**：可直接使用 `openai` SDK，零迁移成本

### 为什么选择 FastAPI

- 原生异步支持，PDF 解析 + AI 调用全程非阻塞
- 自动生成 OpenAPI / Swagger 文档，便于前后端协作
- Pydantic 集成提供请求/响应自动校验

### 为什么选择阿里云 FC 3.0

- Serverless 按需付费，无流量时零成本
- Python 3.10 原生支持，部署简单
- 自动弹性伸缩，轻松应对并发高峰

## 挑战与解决方案

### 挑战 1：大模型 JSON 输出不稳定

DeepSeek API 在结构化提取时偶尔返回格式错误的 JSON。

**解决**：在 Prompt 中严格限定输出 JSON Schema，并在解析时使用 `json.loads()` 包裹 try-except，失败后重试一次。

### 挑战 2：阿里云 FC 3.0 部署兼容性

FC 3.0 Python 3.10 运行时使用事件处理模型，不会自动识别 FastAPI ASGI 应用。依赖项需打包为 Linux `manylinux2014` 兼容格式。默认域名强制添加 `Content-Disposition: attachment` 导致浏览器下载而非渲染 HTML。

**解决**：
- 编写 ASGI 适配器 (`server.py`)，将 FC 事件格式转换为 ASGI 标准接口
- 通过 `pip download --platform manylinux2014_x86_64` 下载 Linux 兼容依赖
- 前端改用 GitHub Pages 托管，通过绝对 URL 调用后端 API

### 挑战 3：Windows-WSL2 跨环境 Redis 通信

Redis 运行在 WSL2 中，Windows 宿主机的 Python 服务需跨网络访问。

**解决**：利用 WSL2 的 `localhost` 自动转发机制，Windows 端直接使用 `localhost:6379` 即可连接 WSL2 中的 Redis 实例。

### 挑战 4：UploadFile 生命周期管理

FastAPI 的 `UploadFile` 在 `StreamingResponse` 上下文外会被自动关闭，导致 SSE 流式响应中无法读取文件内容。

**解决**：在进入 async generator 前将文件内容读入 `bytes` 变量，通过闭包传递，避免依赖 UploadFile 实例。

## 性能优化

### Redis 缓存策略

```
上传 PDF → SHA256 哈希 → 查询 Redis 缓存
    ↓ 命中                          ↓ 未命中
直接返回 ←←←←←←←   AI 分析 → 写入缓存 → 返回结果
```

- 缓存 Key：`resume:{sha256_file_hash}:{position_hash}`
- TTL：3600 秒（1 小时）
- 优雅降级：Redis 不可用时自动跳过，不影响核心流程

### 异步全链路

```
HTTP 请求 → FastAPI 异步路由 → asyncio 并发
    ├── PDF 解析（CPU 密集，同步执行）
    ├── AI 提取（IO 密集，异步 HTTP 调用）
    └── 匹配评分（IO 密集，异步 HTTP 调用）
```

### SSE 流式进度

前端通过 EventSource / fetch ReadableStream 接收实时进度推送，避免长时间等待无反馈。

## 未来规划

- [ ] **向量检索**：将简历信息 Embedding 化，支持语义相似度搜索
- [ ] **RAG 架构**：结合岗位知识库，提供更精准的匹配建议
- [ ] **批量分析**：支持多份简历批量上传与横向对比
- [ ] **简历优化建议**：针对简历薄弱项给出具体修改方案
- [ ] **多格式支持**：扩展支持 DOCX、Markdown 格式简历
- [ ] **自定义评分维度**：允许面试官自定义评分权重
