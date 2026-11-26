import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient

# 加载 .env：优先脚本同目录，其次项目根目录
load_dotenv(Path(__file__).with_name(".env"))
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# 1. 用你的 MCP 配置创建客户端
client = MultiServerMCPClient(
    {
        "time": {
            "transport": "stdio",
            "command": "E:\\Users\\86150\\anaconda3\\envs\\fastapi_env02\\Scripts\\mcp-server-time.exe",
            "args": ["--local-timezone=America/New_York"],
        },
        "bing-cn-mcp-server": {
            "transport": "streamable_http",
            "url": "https://mcp.api-inference.modelscope.net/97a40769577e46/mcp",
        },
    }
)

async def main():
    # 2. 从 MCP 服务拉取工具，自动转成 LangChain Tool
    print("[1/4] 正在拉取 MCP 工具（time + bing）...")
    tools = await client.get_tools()
    print(f"[1/4] 工具已就绪: {[t.name for t in tools]}")

    # 3. 把工具交给 agent，用自然语言触发 MCP 调用
    print("[2/4] 正在初始化模型 qwen-plus ...")
    model = init_chat_model(
        "qwen-plus",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_provider="openai",
    )
    agent = create_agent(model, tools)

    print("[3/4] 正在调用 Agent（模型推理 + 联网搜索可能需要几十秒）...")
    try:
        result = await asyncio.wait_for(
            agent.ainvoke({"messages": [("user", "用必应搜索查一下今天的人工智能新闻")]}),
            timeout=300,
        )
    except asyncio.TimeoutError:
        print("Agent 调用超过 300 秒已中断，可能是模型或远程搜索响应过慢。")
        return
    print("[4/4] Agent 执行完成，正在输出结果...")

    # 4. 验证是否真的调用了 MCP 工具
    # for index, message in enumerate(result["messages"]):
    #     print(f"\n--- [{index}] {type(message).__name__} ---")
    #     if getattr(message, "tool_calls", None):
    #         for call in message.tool_calls:
    #             print("工具调用:", call["name"], call["args"], "id:", call["id"])
    #     if message.type == "tool":
    #         print("工具返回:", message.name, message.tool_call_id, "->", message.content)

    print("\n最终回答:", result["messages"][-1].content)

asyncio.run(main())
