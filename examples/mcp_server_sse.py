from datetime import datetime

from mcp.server.fastmcp import FastMCP

# SSE 传输：服务常驻，客户端通过 http://127.0.0.1:8000/sse 连接
mcp = FastMCP("date-tool-sse", host="127.0.0.1", port=8001)

@mcp.tool()
def get_today() -> str:
    """返回当前的年月日，格式 YYYY-MM-DD。"""
    return datetime.now().strftime("%Y-%m-%d")

if __name__ == "__main__":
    mcp.run(transport="sse")
