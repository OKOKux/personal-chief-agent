import time
from langchain_core.messages import HumanMessage
from fastapi import APIRouter, HTTPException

from app.common.logger import log
from app.common.message_utils import _extract
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter()

try:
    from app.agent.personal_chief import agent  # 从personal_chief.py文件加载agent
    AGENT_ERROR: str | None = None
    log.info("chef agent loaded")
except Exception as exc:
    agent = None
    AGENT_ERROR = f"{type(exc).__name__}: {exc}"
    log.error("chef agent failed to load: %s", AGENT_ERROR)

#@router.post() 注册接口，response_model 保证返回格式
@router.post("/chat", response_model=ChatResponse, summary="和厨师 Agent 对话")#装饰器 让 FastAPI 找到这个函数
def chat(req: ChatRequest) -> ChatResponse:
    if agent is None:
        raise HTTPException(
            status_code=503,
            detail=f"Agent 未就绪，先检查 .env 里的 DEEPSEEK_API_KEY / DEEPSEEK_BASE_URL / TAVILY_API_KEY：{AGENT_ERROR}",
        )

    started = time.perf_counter()
    log.info("chat request: %s", req.message[:80])

    if req.image:
        #如果有图片则将图片和文字分开
        content=[
            {"type":"text","text":req.message},#文字块
            {"type":"image_url","image_url":{"url":req.image}},#图片块
        ]
    #没有则只保存文字
    else:
        content=req.message

    try:
        result = agent.invoke({"messages": [HumanMessage(content=content)]},
        config={"configurable":{"thread_id":req.thread_id}})#传递消息给模型
    except Exception as exc:
        log.exception("agent invoke failed")
        raise HTTPException(
            status_code=500,
            detail=f"Agent 调用失败：{type(exc).__name__}: {exc}",
        ) from exc

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    reply, tools = _extract(result)

    if not reply:
        log.error("empty reply, raw result keys: %s", list(result.keys()))
        raise HTTPException(
            status_code=502,
            detail="Agent 没有返回文本内容，详细输出见服务端日志",
        )

    log.info("chat done in %d ms, tools=%s", elapsed_ms, tools)
    return ChatResponse(reply=reply, tools_used=tools, elapsed_ms=elapsed_ms)