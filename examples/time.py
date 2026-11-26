import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# 加载 backend/.env 里的 DASHSCOPE_API_KEY
load_dotenv(Path(__file__).resolve().parents[1] / "agentflow" / "backend" / ".env")

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient

# 直接用当前解释器启动 mcp-server-time，避免 uvx 联网拉包超时
client = MultiServerMCPClient(
    {
        "time": {
            "transport": "stdio",
            "command": sys.executable,
            "args": ["-m", "mcp_server_time", "--local-timezone=America/New_York"],
        }
    }
)


async def main():
    tools = await client.get_tools()

    model = init_chat_model(
        "qwen-plus",
        api_key=os.environ["DASHSCOPE_API_KEY"],
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_provider="openai",
    )
    agent = create_agent(model, tools)
    result = await agent.ainvoke({"messages": [("user", "现在纽约时间几点？")]})
    print("\n最终回答:", result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
