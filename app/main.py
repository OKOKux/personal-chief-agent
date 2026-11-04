"""
启动：uvicorn app.main:app --reload --port 8000
"""
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1]/".env")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import chat
from app.api.v1.chat import AGENT_ERROR, agent

app = FastAPI(
    title="私人厨师 Agent API",
    description="给私人厨师 Agent 套的一层 HTTP 接口：传一句话，拿回一份菜谱建议。",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)

@app.get("/", summary="服务信息")
def root() -> dict:
    return {
        "name": "私人厨师 Agent API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health",
            "docs": "GET /docs",
        },
    }


@app.get("/health", summary="健康检查")
def health() -> dict:
    ready = agent is not None
    return {
        "status": "ok" if ready else "degraded",
        "agent_ready": ready,
        "error": AGENT_ERROR,
    }


