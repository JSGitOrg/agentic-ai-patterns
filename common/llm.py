"""A tiny, provider-agnostic chat + tool-calling client.

Why this file exists
---------------------
None of the patterns in this repo use an agent framework. The whole point
of the training is to show *exactly* what an "agent" is doing under the
hood: a loop that sends messages to a model, optionally lets the model ask
to call a tool, runs that tool in plain Python, and feeds the result back
in. This module is the only place that talks to a specific vendor's SDK,
so every pattern's own code stays vendor-neutral and short.

Supported backends (set LLM_PROVIDER in your environment / .env):

    mock        (default) No network call, no API key. Deterministic,
                scripted replies so every pattern runs offline and you can
                watch the *control flow* before spending API credits.
    openai      api.openai.com (or any OpenAI-compatible endpoint).
    anthropic   api.anthropic.com (Claude).

Swapping LLM_PROVIDER is the only change needed to move a pattern from
mock to a real model -- none of the orchestration code in patterns/ or
capstone/ changes. That is the core lesson of this repo: the *pattern*
(sequential, parallel, loop, routing, remote agent) lives in your own
code, not in the model or the SDK.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

Message = dict[str, Any]
ToolSpec = dict[str, Any]


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    text: Optional[str]
    tool_calls: list[ToolCall] = field(default_factory=list)

    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


MockResponder = Callable[[list[Message], list[ToolSpec], Optional[str]], LLMResponse]


def provider() -> str:
    return os.getenv("LLM_PROVIDER", "mock").lower()


def chat(
    messages: list[Message],
    *,
    system: Optional[str] = None,
    tools: Optional[list[ToolSpec]] = None,
    model: Optional[str] = None,
    mock_fn: Optional[MockResponder] = None,
) -> LLMResponse:
    """Send one turn to the configured model and return its reply.

    ``messages`` holds the conversation so far in a simple internal shape:
    ``{"role": "user" | "assistant" | "tool", ...}``. Callers build this
    list themselves (see ``tool_result_message`` /
    ``assistant_message_from_response`` below) -- there is no hidden
    session object, because seeing the history grow is part of the lesson.
    """
    tools = tools or []
    p = provider()

    if p == "mock":
        if mock_fn is not None:
            return mock_fn(messages, tools, system)
        return LLMResponse(text="[mock] no mock_fn supplied for this call")

    if p == "openai":
        return _chat_openai(messages, system, tools, model)

    if p == "anthropic":
        return _chat_anthropic(messages, system, tools, model)

    raise ValueError(f"Unknown LLM_PROVIDER={p!r}. Use 'mock', 'openai', or 'anthropic'.")


def _chat_openai(
    messages: list[Message],
    system: Optional[str],
    tools: list[ToolSpec],
    model: Optional[str],
) -> LLMResponse:
    from openai import OpenAI  # imported lazily: 'mock' mode needs no deps

    client = OpenAI()
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    full_messages: list[Message] = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    kwargs: dict[str, Any] = {"model": model, "messages": full_messages}
    if tools:
        kwargs["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("parameters", {"type": "object", "properties": {}}),
                },
            }
            for t in tools
        ]

    response = client.chat.completions.create(**kwargs)
    choice = response.choices[0].message

    tool_calls = [
        ToolCall(
            id=tc.id,
            name=tc.function.name,
            arguments=json.loads(tc.function.arguments or "{}"),
        )
        for tc in (choice.tool_calls or [])
    ]
    return LLMResponse(text=choice.content, tool_calls=tool_calls)


def _chat_anthropic(
    messages: list[Message],
    system: Optional[str],
    tools: list[ToolSpec],
    model: Optional[str],
) -> LLMResponse:
    import anthropic  # imported lazily: 'mock' mode needs no deps

    client = anthropic.Anthropic()
    model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

    kwargs: dict[str, Any] = {"model": model, "max_tokens": 1024, "messages": messages}
    if system:
        kwargs["system"] = system
    if tools:
        kwargs["tools"] = [
            {
                "name": t["name"],
                "description": t.get("description", ""),
                "input_schema": t.get("parameters", {"type": "object", "properties": {}}),
            }
            for t in tools
        ]

    response = client.messages.create(**kwargs)

    text_parts: list[str] = []
    tool_calls: list[ToolCall] = []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)
        elif block.type == "tool_use":
            tool_calls.append(ToolCall(id=block.id, name=block.name, arguments=block.input))

    return LLMResponse(text="\n".join(text_parts) or None, tool_calls=tool_calls)


def assistant_message_from_response(resp: LLMResponse) -> Message:
    """Turn a model reply into the history entry you append before tool
    results. OpenAI and Anthropic shape this differently -- spelled out
    here instead of hidden, since that seam is worth seeing at least once.
    """
    if provider() == "anthropic":
        content: list[dict[str, Any]] = []
        if resp.text:
            content.append({"type": "text", "text": resp.text})
        for tc in resp.tool_calls:
            content.append({"type": "tool_use", "id": tc.id, "name": tc.name, "input": tc.arguments})
        return {"role": "assistant", "content": content}

    message: Message = {"role": "assistant", "content": resp.text}
    if resp.tool_calls:
        message["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
            }
            for tc in resp.tool_calls
        ]
    return message


def tool_result_message(tool_call: ToolCall, result: Any) -> Message:
    """Build the message that reports a tool's output back to the model."""
    payload = result if isinstance(result, str) else json.dumps(result, default=str)

    if provider() == "anthropic":
        return {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": tool_call.id, "content": payload}
            ],
        }

    return {"role": "tool", "tool_call_id": tool_call.id, "content": payload}
