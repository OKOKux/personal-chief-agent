# 私人厨师 Agent

丢给它一张食材照片或者一句话，它联网搜菜谱、按营养和难度打分排序，返回一份带参考图的做法建议。

## 功能

- 文字 + 图片输入（拍照识别食材）
- 多轮对话，每个会话独立记忆（SQLite 存储，关掉浏览器也不丢）
- 联网搜索真实菜谱（Tavily），搜不到才自己发挥
- 前端单页，聊天记录存在浏览器 localStorage

## 快速开始

需要 Python 3.13+ 和 [uv](https://docs.astral.sh/uv/)。

```bash
# 1. 装依赖
uv sync

# 2. 配环境变量
#    复制 .env.example 成 .env，把 key 填进去
```

`.env` 里需要的变量：

| 变量 | 说明 |
| --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek 开放平台申请的 API key |
| `DEEPSEEK_BASE_URL` | 默认 `https://api.deepseek.com` |
| `TAVILY_API_KEY` | Tavily 搜索 key，去 tavily.com 免费注册 |

```bash
# 3. 起后端
uv run uvicorn app.main:app --reload --port 8000
```

然后用浏览器打开 `web/chief.html`。

- 接口文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/health

## 接口

### `POST /chat`

```json
{
  "message": "我有鸡蛋和西红柿",
  "image": null,
  "thread_id": "abc123"
}
```

`message` 必填；`image` 可传 `data:image/jpeg;base64,...` 或 http(s) 图片地址；`thread_id` 决定会话隔离，不传就用默认值。

返回：

```json
{
  "reply": "根据你现有的食材……",
  "tools_used": ["tavily_search"],
  "elapsed_ms": 12400
}
```

## 项目结构

```
app/
  main.py                 FastAPI 入口：CORS、路由挂载、/ 和 /health
  api/v1/chat.py          POST /chat，组装多模态消息、调 agent、抽结果
  models/schemas.py       ChatRequest / ChatResponse 数据模型
  common/logger.py        日志
  common/message_utils.py 从 agent 返回结果里抽文本和工具名
  agent/personal_chief.py Agent 本体：模型 + Tavily + SQLite 记忆
web/
  chief.html              前端单页
  marked.min.js           markdown 渲染（v15.0.12）
learn/                    学习用的 notebook
langgraph.json            LangGraph CLI 配置
```

## 开发笔记

- 数据库 `personal_chief.db` 是 LangGraph 的会话存档，不进 git，删了只是丢历史对话。
- 前端改了 `.html` 直接刷新页面；后端 `--reload` 会自动重载。
- `pyproject.toml` 里 `notebook`、`langgraph-cli` 在 dev 组，只装运行时可以 `uv sync --no-dev`。