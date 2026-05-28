# 部署指南

## 环境要求

| 组件 | 最低版本 | 用途 |
|------|----------|------|
| Python | 3.10+ | 后端运行环境 |
| Redis | 6.0+ | 缓存服务（可选） |
| Git | 2.0+ | 代码管理 |
| Node.js | 16.0+ | Serverless Devs 工具链 |
| npm | 8.0+ | 安装 Serverless Devs |

## 本地部署

### 1. 克隆仓库

```bash
git clone https://github.com/crs2006220-gif/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件并填入配置：

```env
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
API_PREFIX=/api/v1
```

| 变量 | 说明 | 必填 |
|------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 是 |
| `DEEPSEEK_BASE_URL` | API 服务地址 | 是 |
| `DEEPSEEK_MODEL` | 模型名称 | 是 |
| `REDIS_HOST` | Redis 地址 | 否（无 Redis 自动降级） |
| `REDIS_PORT` | Redis 端口 | 否 |
| `API_PREFIX` | API 路由前缀 | 否 |

### 5. 启动 Redis（可选）

**Windows (WSL2)**：
```bash
wsl redis-server
```

Windows 端自动通过 `localhost:6379` 转发到 WSL2。

**Linux / macOS**：
```bash
redis-server
```

### 6. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：
- 前端页面：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 阿里云 FC 3.0 部署

### 1. 安装 Serverless Devs

```bash
npm install -g @serverless-devs/s
```

### 2. 配置阿里云凭证

```bash
s config add
```

按提示输入：
- AccountID：阿里云账号 ID
- AccessKeyID：RAM 用户的 AccessKey
- AccessKeySecret：对应的 Secret

### 3. 配置文件

项目根目录的 `s.yaml` 已包含完整部署配置：

```yaml
edition: 3.0.0
name: ai-resume-analysis
resources:
  ai-resume-fc:
    component: fc3
    props:
      region: cn-hangzhou
      functionName: ai-resume-analyzer
      runtime: python3.10
      handler: server.app
      code: ./code
      memorySize: 1024
      timeout: 60
```

### 4. 执行部署

```bash
s deploy --assume-yes
```

部署完成后会输出函数 URL：
```
url:
  system_url: https://ai-resuanalyzer-xxxxx.cn-hangzhou.fcapp.run
```

### 5. 更新环境变量

在阿里云 FC 控制台 → 函数详情 → 环境变量中配置 DEEPSEEK_API_KEY，或直接在 `s.yaml` 中修改后重新部署。

## GitHub Pages 部署

### 1. 推送前端文件

确保仓库根目录有 `index.html` 文件（已配置好指向 FC 后端的 API 地址）。

```bash
git add index.html
git commit -m "Add frontend for GitHub Pages"
git push origin master
```

### 2. 启用 GitHub Pages

1. 打开仓库 Settings → Pages
2. Source 选择 `Deploy from a branch`
3. Branch 选择 `master`，目录选择 `/ (root)`
4. 点击 Save

### 3. 验证

等待几秒后，访问：`https://<username>.github.io/ai-resume-analyzer/`

## 前端 API 地址配置

如果后端 URL 发生变化，需修改 `index.html` 中的 API 地址：

```javascript
// 查找这行并修改
const res = await fetch('https://ai-resuanalyzer-xxxxx.cn-hangzhou.fcapp.run/api/v1/resume/upload', ...)
```

## 常见问题

### Q: 部署后访问 FC URL 出现文件下载而非网页？

FC 3.0 默认域名会强制添加 `Content-Disposition: attachment` 头。解决方案：
1. **推荐**：使用 GitHub Pages 托管前端（本项目已配置）
2. **替代**：在 FC 控制台绑定自定义域名

### Q: Redis 连接失败是否影响使用？

不影响。系统设计为 Redis 不可用时自动跳过缓存，所有功能正常运行，只是重复上传不会命中缓存。

### Q: PDF 解析结果为空？

可能原因：
- PDF 为扫描版（图片），不含可提取文本
- PDF 文件损坏或加密
- 文件过大（建议 < 10MB）

### Q: 部署时报错 "Runtime change not supported"？

同一函数不能切换运行时类型（如 `python3.10` ↔ `custom`）。需先 `s remove --assume-yes` 删除后重新部署。

### Q: 冷启动时间长？

FC 3.0 首次请求会有 3-5s 冷启动延迟。可通过配置 `instanceConcurrency` 和预留实例优化。
