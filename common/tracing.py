"""A dependency-free console tracer shared by every pattern.

The point of this repo is to make agent control flow visible. Every
pattern calls into this module (instead of scattering ``print`` calls)
so a classroom demo prints a consistent, readable trace of who did what:
which agent is acting, which tool it called and with what arguments, and
what came back.
"""

from __future__ import annotations

import datetime
import json
import os
from typing import Any

_COLORS = {
    "agent": "\033[36m",  # cyan
    "tool": "\033[33m",  # yellow
    "result": "\033[32m",  # green
    "system": "\033[90m",  # gray
    "reset": "\033[0m",
}

# Disable ANSI colors when NO_COLOR is set or output isn't a real terminal.
_USE_COLOR = os.getenv("NO_COLOR") is None


def _emit(kind: str, actor: str, message: str) -> None:
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {actor:<28} {message}"
    if _USE_COLOR:
        color = _COLORS.get(kind, "")
        print(f"{color}{line}{_COLORS['reset']}")
    else:
        print(line)


def step(actor: str, message: str) -> None:
    """A generic reasoning/decision step for an agent."""
    _emit("agent", actor, message)


def tool_call(actor: str, tool_name: str, arguments: dict[str, Any]) -> None:
    _emit("tool", actor, f"-> calling tool '{tool_name}'({_fmt(arguments)})")


def tool_result(actor: str, tool_name: str, result: Any) -> None:
    _emit("result", actor, f"<- '{tool_name}' returned {_fmt(result)}")


def system(message: str) -> None:
    _emit("system", "system", message)


def _fmt(value: Any, limit: int = 220) -> str:
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    return text if len(text) <= limit else text[: limit - 3] + "..."
