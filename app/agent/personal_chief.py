from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.sqlite import SqliteStore
from pathlib import Path
import sqlite3
import os

#加载环境变量
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DB_path=Path(__file__).resolve().parents[2]/"personal_chief.db"
store_conn = sqlite3.connect(DB_path, check_same_thread=False)
store = SqliteStore(store_conn)
store.setup()

#初始化checkpointer
#连接sqlite
connection=sqlite3.connect(DB_path,check_same_thread=False) # (check_same_thread=False)  sqlite 默认：同一个数据库连接对象，只能在创建它的那个线程里使用
#初始化checkpointer
checkpointer=SqliteSaver(connection)
#自动建表
checkpointer.setup()

#多模态大模型
model=init_chat_model(
    model="deepseek-flash",
    model_provider="openai",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

#web搜索工具，以tavily作为web搜索工具
web_search=TavilySearch(
    max_results=5,
    topic="general"
)

#Agent系统提示词
system_prompt="""
你是一名私人厨师。收到用户提供的食材照片或清单后,请按以下流程操作:

1. 识别和评估食材:若用户提供照片,首先辨识所有可见食材。基于食材的外观状态,评估其新鲜度与可用量,整理出一份“当前可用 食材清单”。

2. 智能食谱检索:优先调用 web_search 工具,以“可用食材清单”为核心关键词,查找可行菜谱。

3. 多维度评估与排序:从营养价值和制作难度两个维度对检索到的候选食谱进行量化打分,并根据得分排序,制作简单且营养丰富的排 名靠前。

4.结构化方案输出:把排序后的食谱整理为一份结构清晰的建议报告,要包含食谱信息、得分、推荐理由、食谱的参考图片,帮助用户 快速做出决策。

请严格按照流程,优先调用 web_search 工具搜索食谱,搜索不到的情况下才能自己发挥。
"""
agent=create_agent(
    model=model,
    tools=[web_search],
    checkpointer=checkpointer,
    store=store,
    system_prompt=system_prompt
)
