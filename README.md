# datetime-toolkit MCP Server

一个**纯本地、零配置、无需任何 API Key** 的日期时间 MCP 工具集。所有计算基于 Python 标准库 `zoneinfo`，不读取本地文件、不访问网络，因此可以安全地提交到 MCP 目录并被托管平台审核通过。

## 提供的工具（8 个）

| 工具 | 说明 |
|------|------|
| `get_current_time(tz?)` | 获取指定时区的当前时间 |
| `convert_time(time_text, from_tz?, to_tz?)` | 时区转换，如北京时间转纽约时间 |
| `timestamp_to_datetime(timestamp, tz?)` | Unix 时间戳转可读时间 |
| `datetime_to_timestamp(time_text, tz?)` | 时间字符串转 Unix 时间戳 |
| `add_to_date(date_text, days?, hours?, minutes?, tz?)` | 日期加减 |
| `days_between(start_date, end_date, tz?)` | 计算两个日期相差天数 |
| `weekday_of(date_text, tz?)` | 查询某天是星期几 |
| `list_timezones(query?)` | 按关键字搜索 IANA 时区名 |

`tz` 参数留空时默认 `Asia/Shanghai`，可通过环境变量 `DATETIME_TOOLKIT_TZ` 修改。

## 本地安装与运行

```bash
pip install -r requirements.txt

# stdio 模式（供 Claude Desktop / Cursor / Trae 等本地客户端使用）
python server.py

# streamable-http 模式（供远程访问 / 托管平台使用）
set MCP_TRANSPORT=streamable-http   # Windows
# export MCP_TRANSPORT=streamable-http  # macOS/Linux
python server.py
# 服务地址：http://127.0.0.1:8000/mcp
```

## 服务配置（Server config）

### stdio（本地客户端，推荐）

复制到 `claude_desktop_config.json` / `.cursor/mcp.json` / Trae 的 MCP 配置中。
`args[0]` 请替换为本仓库 `server.py` 的**绝对路径**：

```json
{
  "mcpServers": {
    "datetime-toolkit": {
      "command": "python",
      "args": ["/absolute/path/to/datetime-mcp-server/server.py"]
    }
  }
}
```

### streamable-http（远程/托管）

先按上文启动 HTTP 模式，再连接：

```json
{
  "mcpServers": {
    "datetime-toolkit": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

> 环境变量（可选）：`DATETIME_TOOLKIT_TZ` 默认时区、`MCP_TRANSPORT` 传输方式、`MCP_HOST` / `MCP_PORT` HTTP 监听地址。本服务无需任何 API Key。

## Docker

```bash
docker build -t datetime-toolkit-mcp .
docker run -i --rm -p 8000:8000 datetime-toolkit-mcp
```

## 发布到 MCP 目录

本项目已包含提交所需的全部文件：

- `server.py` — 服务入口
- `requirements.txt` — 依赖声明
- `README.md` — 本说明
- `chatmcp.yaml` — 托管配置（MCP.so / ChatMCP）
- `Dockerfile` — 容器化部署
- `LICENSE` — MIT 许可证（商业友好，符合托管要求）

### 提交到 mcp.so

1. 把本目录推送到你的 GitHub 仓库（`https://github.com/xiaohuo12/datetime-toolkit-mcp`）
2. 打开 <https://mcp.so/submit>
3. 填入仓库 URL，平台会自动抓取名称、描述、工具和配置
4. 核对信息后提交，等待审核（审核周期可能较长）
5. 审核通过后，你的服务会出现在 MCP Playground 中

### 审核慢的替代平台

MCP.so 审核较慢时，同一套仓库可以直接提交到这些目录/市场，流程类似：

- **Glama MCP**：<https://glama.ai/mcp/servers> — 支持 GitHub 仓库直接导入，审核较快
- **Smithery**：<https://smithery.ai/> — 面向 Claude/Cursor，支持 stdio 与远程部署
- **PulseMCP**：<https://www.pulsemcp.com/servers> — 社区目录，提交入口在站内
- **MCP 广场（魔搭 ModelScope）**：<https://www.modelscope.cn/mcp> — 国内平台，支持托管
- **官方 MCP Registry**：<https://registry.modelcontextprotocol.io/> — 官方注册表，可同时提交

> 提示：这些平台大多读取同一份 `README.md` 和仓库元数据，因此把 README 写清楚能显著提高收录通过率。

## 许可证

MIT — 见 [LICENSE](LICENSE)。
