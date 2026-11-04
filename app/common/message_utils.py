from langchain_core.messages import AIMessage

def _content_to_text(content) -> str:
    """AIMessage.content 可能是 str，也可能是多模态的 list，统一转成字符串。"""
    #是字符串直接返回
    if isinstance(content, str):
        return content
    #是列表就遍历，字符串直接拼，字典且 type=="text" 就取 text
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):#字符串
                parts.append(item)

            elif isinstance(item, dict):#字典
                if item.get("type") == "text":
                    parts.append(item.get("text", ""))

        return "".join(parts)

    return str(content) if content else ""


def _extract(result: dict) -> tuple[str, list[str]]:
    """从 agent.invoke 的返回值里取出「最终回答」和「用过的工具」。"""
    messages = result.get("messages", []) or []

    reply = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            text = _content_to_text(msg.content).strip()#找第一条有文字内容的 AIMessage
            if text:
                reply = text
                break

    tools: list[str] = []
    for msg in messages:
        for call in getattr(msg, "tool_calls", None) or []:
            name = call.get("name") if isinstance(call, dict) else getattr(call, "name", None)
            if name:
                tools.append(name)
    return reply, tools