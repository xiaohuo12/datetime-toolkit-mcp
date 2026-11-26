from datetime import datetime

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("date-tool-stdio")

@mcp.tool()
def get_today() -> str:
    """返回当前的年月日，格式 YYYY-MM-DD。"""
    return datetime.now().strftime("%Y-%m-%d")

if __name__ == "__main__":
    mcp.run()
