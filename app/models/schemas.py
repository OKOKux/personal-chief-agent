from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="用户说的话，比如「我有鸡蛋和西红柿，能做什么菜」",
    )
    image: str | None = Field(
        default=None,
        description="图片的 data URL",
    )
    thread_id:str= Field(
        default="default",
        min_length=1,
        max_length=64,
    )

class ChatResponse(BaseModel):
    reply: str = Field(..., description="Agent 的最终回答")
    tools_used: list[str] = Field(default_factory=list, description="本次调用过的工具名")
    elapsed_ms: int = Field(..., description="服务端耗时（毫秒）")
