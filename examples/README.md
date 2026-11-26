# Examples

本目录是学习/调试用的 MCP 客户端与服务端示例脚本，**不是本仓库主服务**（主服务见上一级的 `server.py`）。

## 文件说明

| 文件 | 作用 |
|------|------|
| `mcp_server_stdio.py` | 最简单的 FastMCP 服务端，stdio 传输，只提供 `get_today` |
| `mcp_server_sse.py` | SSE 传输版本 |
| `mcp_server_streamable.py` | streamable-http 传输版本 |
| `mcp_client.py` | 用 `langchain_mcp_adapters` 连接上面服务的客户端 |
| `biyin.py` | 连接远程必应搜索 MCP + qwen-plus 模型的示例 |
| `time.py` | 用当前解释器启动 `mcp-server-time` 的示例 |

## 运行前必读

1. **路径需要修改**：脚本里的 Python 解释器和项目路径写死为本机环境（`E:\Users\86150\anaconda3\...`），在你自己机器上运行时请改成对应路径。
2. **密钥配置**：`biyin.py` / `time.py` 依赖大模型 API Key。复制同目录的 `.env.example` 为 `.env` 并填入你自己的密钥；`.env` 已被 `.gitignore` 忽略，不会被提交。
3. **端口冲突**：`mcp_server_sse.py` 与 `mcp_server_streamable.py` 都监听 8001 端口，不要同时启动。

这些示例仅用于学习 MCP 的三种传输方式和客户端接入，生产使用请参考仓库根目录的 `datetime-toolkit` 服务。
