"""datetime-toolkit: 纯本地的日期时间 MCP 工具集。

特点：
- 不读取任何本地文件、不需要 API Key，全部基于标准库 zoneinfo 计算
- 默认 stdio 传输；设置 MCP_TRANSPORT=streamable-http 可切换为远程托管模式
- 工具描述来自 docstring，会被 AI 客户端直接读取用于判断何时调用
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

from mcp.server.fastmcp import FastMCP

DEFAULT_TZ = os.getenv("DATETIME_TOOLKIT_TZ", "Asia/Shanghai")
DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
DATE_FMT = "%Y-%m-%d"
_INPUT_FORMATS = (
    DATETIME_FMT,
    DATE_FMT,
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M",
)

mcp = FastMCP(
    "datetime-toolkit",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8000")),
)


def _zone(tz: str = "") -> ZoneInfo:
    """根据时区名返回 ZoneInfo，留空则用默认时区。"""
    name = (tz or DEFAULT_TZ).strip()
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(f"未知时区 {name!r}，可用 list_timezones 查询") from exc


def _parse(text: str, tz: ZoneInfo) -> datetime:
    """把常见时间字符串解析成带时区的 datetime。"""
    value = text.strip()
    for fmt in _INPUT_FORMATS:
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=tz)
        except ValueError:
            continue
    raise ValueError(
        f"无法解析时间 {text!r}，支持 YYYY-MM-DD HH:MM:SS / YYYY-MM-DD / ISO 格式"
    )


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


@mcp.tool()
def get_current_time(tz: str = "") -> str:
    """获取指定时区的当前时间。

    Args:
        tz: IANA 时区名，如 Asia/Shanghai、America/New_York、UTC。留空使用服务默认时区。
    """
    zone = _zone(tz)
    now = datetime.now(zone)
    return f"{now.strftime(DATETIME_FMT)} {zone.key} (UTC{now.strftime('%z')})"


@mcp.tool()
def convert_time(time_text: str, from_tz: str = "", to_tz: str = "UTC") -> str:
    """把一个时间从源时区转换到目标时区。

    Args:
        time_text: 时间字符串，如 2026-11-26 09:30:00
        from_tz: 源时区，留空表示服务默认时区
        to_tz: 目标时区，默认 UTC
    """
    source = _zone(from_tz)
    target = _zone(to_tz)
    converted = _parse(time_text, source).astimezone(target)
    return _iso(converted)


@mcp.tool()
def timestamp_to_datetime(timestamp: float, tz: str = "") -> str:
    """Unix 时间戳（秒）转为指定时区的可读时间。

    Args:
        timestamp: Unix 时间戳，单位为秒，如 1764101400
        tz: 目标时区，留空使用服务默认时区
    """
    zone = _zone(tz)
    return _iso(datetime.fromtimestamp(timestamp, zone))


@mcp.tool()
def datetime_to_timestamp(time_text: str, tz: str = "") -> int:
    """时间字符串转为 Unix 时间戳（秒）。

    Args:
        time_text: 时间字符串，如 2026-11-26 09:30:00
        tz: 该时间所属时区，留空使用服务默认时区
    """
    zone = _zone(tz)
    return int(_parse(time_text, zone).timestamp())


@mcp.tool()
def add_to_date(
    date_text: str,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    tz: str = "",
) -> str:
    """在给定时间上加减天数/小时/分钟，返回计算结果。

    Args:
        date_text: 起始时间字符串
        days: 增加的天数，负数表示减少
        hours: 增加的小时数，负数表示减少
        minutes: 增加的分钟数，负数表示减少
        tz: 时区，留空使用服务默认时区
    """
    zone = _zone(tz)
    result = _parse(date_text, zone) + timedelta(
        days=days, hours=hours, minutes=minutes
    )
    return _iso(result)


@mcp.tool()
def days_between(start_date: str, end_date: str, tz: str = "") -> int:
    """计算两个日期相差的天数（结束日期减开始日期）。

    Args:
        start_date: 开始日期，如 2026-01-01
        end_date: 结束日期，如 2026-11-26
        tz: 时区，留空使用服务默认时区
    """
    zone = _zone(tz)
    start = _parse(start_date, zone).date()
    end = _parse(end_date, zone).date()
    return (end - start).days


@mcp.tool()
def weekday_of(date_text: str, tz: str = "") -> str:
    """查询某一天是星期几。

    Args:
        date_text: 日期字符串，如 2026-11-26
        tz: 时区，留空使用服务默认时区
    """
    zone = _zone(tz)
    weekday = _parse(date_text, zone).date().weekday()
    names = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")
    return names[weekday]


@mcp.tool()
def list_timezones(query: str = "") -> list[str]:
    """按关键字搜索 IANA 时区名，最多返回 50 条，便于填写 tz 参数。

    Args:
        query: 关键字，如 Shanghai、America、UTC；留空返回前 50 个时区
    """
    names = sorted(available_timezones())
    if not query:
        return names[:50]
    keyword = query.lower()
    return [name for name in names if keyword in name.lower()][:50]


def main() -> None:
    """根据 MCP_TRANSPORT 选择传输方式。"""
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
    mcp.run(transport="streamable-http" if transport in ("streamable-http", "http") else "stdio")


if __name__ == "__main__":
    main()
