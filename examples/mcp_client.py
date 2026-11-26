import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient

# 加载 .env（DASHSCOPE_API_KEY）
load_dotenv(Path(__file__).with_name(".env"))
load_dotenv(Path(__file__).resolve().parents[1] / "agentflow" / "backend" / ".env")

PYTHON = r"E:\Users\86150\anaconda3\envs\fastapi_env02\python.exe"
SERVER_DIR = r"e:/Ollama/project/mcp"

# 1. 用你的 MCP 配置创建客户端
#    注意：sse 和 streamable_http 都占用 8000 端口，不能同时启用，二选一即可
client = MultiServerMCPClient(
    {
        "date-tool-stdio": {
            "transport": "stdio",
            "command": PYTHON,
            "args": [f"{SERVER_DIR}/mcp_server_stdio.py"],
        },
        # "date-tool-sse": {"transport": "sse", "url": "http://127.0.0.1:8001/sse"},
        "date-tool-streamable": {"transport": "streamable_http", "url": "http://127.0.0.1:8001/mcp"},
    }
)

async def main():
    # 2. 从 MCP 服务拉取工具，自动转成 LangChain Tool
    tools = await client.get_tools()

    # 3. 把工具交给 agent，用自然语言触发 MCP 调用
    import os
    model = init_chat_model(
        "qwen-plus",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_provider="openai",
    )
    agent = create_agent(model, tools)
    result = await agent.ainvoke({"messages": [("user", "今天几号?")]})

    # 4. 验证是否真的调用了 MCP 工具
    for index, message in enumerate(result["messages"]):
        print(f"\n--- [{index}] {type(message).__name__} ---")
        if getattr(message, "tool_calls", None):
            for call in message.tool_calls:
                print("工具调用:", call["name"], call["args"], "id:", call["id"])
        if message.type == "tool":
            print("工具返回:", message.name, message.tool_call_id, "->", message.content)

    print("\n最终回答:", result["messages"][-1].content)

asyncio.run(main())
