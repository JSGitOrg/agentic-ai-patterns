"""Pattern 1: the agent loop with tools (a.k.a. "ReAct" loop).

This is the foundational agentic pattern. Every other pattern in this repo
is built by composing more of these loops together -- in sequence, in
parallel, in a cycle, or across a network. One agent, one goal, and a
`while` loop that lets the *model* decide if and when to call a tool,
instead of a fixed call graph you wrote in advance.

Run it:
    PYTHONPATH=. python patterns/01_agent_loop_with_tools/agent.py
    PYTHONPATH=. python patterns/01_agent_loop_with_tools/agent.py "your own question"

See patterns/01_agent_loop_with_tools/README.md for the walkthrough.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv  # noqa: E402

from common import llm, tracing  # noqa: E402
from common.cymbal_tools import (  # noqa: E402
    TOOL_SCHEMAS,
    lookup_audience_persona,
    lookup_brand_guidelines,
)

load_dotenv()

AGENT_NAME = "brand_assistant"
MAX_TURNS = 5

SYSTEM_PROMPT = """You are the Cymbal Stadiums brand assistant. Employees ask you how
to apply the brand to a specific piece of content. Use your tools to look
up the real brand guidelines and the target audience's persona before you
answer -- never invent brand colors or voice from scratch. Keep your final
answer to one short, actionable paragraph."""

TOOLS = [TOOL_SCHEMAS["lookup_brand_guidelines"], TOOL_SCHEMAS["lookup_audience_persona"]]

TOOL_IMPLS = {
    "lookup_brand_guidelines": lambda args: lookup_brand_guidelines(**args),
    "lookup_audience_persona": lambda args: lookup_audience_persona(**args),
}


def _mock_responder(messages: list[llm.Message], tools, system) -> llm.LLMResponse:
    """Stands in for the model when LLM_PROVIDER=mock. Real models would
    decide dynamically which tools to call and how to phrase the answer --
    this hard-codes one plausible path so the *loop mechanics* are visible
    without needing an API key.
    """
    already_called_tools = any(m.get("role") == "tool" for m in messages)
    if not already_called_tools:
        return llm.LLMResponse(
            text=None,
            tool_calls=[
                llm.ToolCall(id="call_1", name="lookup_brand_guidelines", arguments={"topic": "poster"}),
                llm.ToolCall(id="call_2", name="lookup_audience_persona", arguments={"audience": "external"}),
            ],
        )
    return llm.LLMResponse(
        text=(
            "For an external-facing poster: lead with Cymbal Purple (#5B2A86) and "
            "Turf Green (#DAF7A6), keep the tone warm and plainspoken -- like a proud "
            "groundskeeper, not a corporate deck -- and lean on stadium/maintenance "
            "imagery (lights, yard markers, wrenches), since facility managers "
            "evaluating our program respond to authenticity over polish."
        )
    )


def run(question: str) -> str:
    """The agent loop: ask the model, run any tools it asks for, repeat
    until it answers in plain text (or we hit MAX_TURNS as a safety valve
    against a model that never stops calling tools).
    """
    tracing.system(f"user -> {AGENT_NAME}: {question}")
    messages: list[llm.Message] = [{"role": "user", "content": question}]

    for turn in range(1, MAX_TURNS + 1):
        response = llm.chat(messages, system=SYSTEM_PROMPT, tools=TOOLS, mock_fn=_mock_responder)
        messages.append(llm.assistant_message_from_response(response))

        if not response.has_tool_calls:
            tracing.step(AGENT_NAME, f"final answer on turn {turn}")
            return response.text or ""

        for call in response.tool_calls:
            tracing.tool_call(AGENT_NAME, call.name, call.arguments)
            result = TOOL_IMPLS[call.name](call.arguments)
            tracing.tool_result(AGENT_NAME, call.name, result)
            messages.append(llm.tool_result_message(call, result))

    raise RuntimeError(f"{AGENT_NAME} did not produce a final answer within {MAX_TURNS} turns")


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or (
        "What imagery and colors should I use for a poster aimed at external partners?"
    )
    answer = run(question)
    print("\n=== FINAL ANSWER ===")
    print(answer)
