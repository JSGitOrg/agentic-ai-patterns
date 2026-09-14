"""Pattern 5: dynamic multi-agent routing (orchestrator / handoff).

An orchestrator agent looks at an incoming request and decides, at
runtime, which specialist agent should handle it -- by calling one of
several "handoff" tools. Unlike Pattern 2 (sequential), the path through
the system is not fixed in code; unlike Pattern 1, the "tools" being
called are entire other agents, not simple data lookups.

Run it:
    PYTHONPATH=. python patterns/05_dynamic_multi_agent_routing/orchestrator.py
    PYTHONPATH=. python patterns/05_dynamic_multi_agent_routing/orchestrator.py "we need a press release about the training program"
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv  # noqa: E402

from common import llm, tracing  # noqa: E402

load_dotenv()

ORCHESTRATOR_SYSTEM = """You triage incoming content requests for the Cymbal Stadiums
communications team. For every request, call exactly one of your handoff
tools to route it to the specialist who should write it. Do not write the
content yourself -- only decide who should."""

HANDOFF_TOOLS = [
    {
        "name": "handoff_to_social_media_writer",
        "description": "Route a request for a short, punchy social media post.",
        "parameters": {"type": "object", "properties": {"request": {"type": "string"}}, "required": ["request"]},
    },
    {
        "name": "handoff_to_press_release_writer",
        "description": "Route a request for a formal, external-facing press release.",
        "parameters": {"type": "object", "properties": {"request": {"type": "string"}}, "required": ["request"]},
    },
    {
        "name": "handoff_to_internal_memo_writer",
        "description": "Route a request for an internal-only memo or announcement.",
        "parameters": {"type": "object", "properties": {"request": {"type": "string"}}, "required": ["request"]},
    },
]


def social_media_writer(request: str) -> str:
    tracing.step("social_media_writer", "writing post")

    def mock(messages, tools, system) -> llm.LLMResponse:
        return llm.LLMResponse(
            text="Every wrench turned, every game saved. Our crews keep 40 stadiums "
            "game-day ready. #CymbalStadiums"
        )

    prompt = f"Write a punchy, <=280 character social post about: {request}"
    return llm.chat([{"role": "user", "content": prompt}], mock_fn=mock).text or ""


def press_release_writer(request: str) -> str:
    tracing.step("press_release_writer", "writing release")

    def mock(messages, tools, system) -> llm.LLMResponse:
        return llm.LLMResponse(
            text=(
                "CYMBAL STADIUMS EXPANDS ON-THE-JOB TRAINING PROGRAM -- Cymbal Stadiums "
                "today announced the expansion of its hands-on maintenance training "
                "program, pairing new hires with veteran crews across its 40-venue network."
            )
        )

    prompt = f"Write a short, formal press-release paragraph about: {request}"
    return llm.chat([{"role": "user", "content": prompt}], mock_fn=mock).text or ""


def internal_memo_writer(request: str) -> str:
    tracing.step("internal_memo_writer", "writing memo")

    def mock(messages, tools, system) -> llm.LLMResponse:
        return llm.LLMResponse(
            text=(
                "Team -- starting next month, every new hire will shadow a senior crew "
                "member for their first two weeks on the job. Reach out to your regional "
                "lead with questions."
            )
        )

    prompt = f"Write a short internal memo about: {request}"
    return llm.chat([{"role": "user", "content": prompt}], mock_fn=mock).text or ""


SPECIALISTS = {
    "handoff_to_social_media_writer": social_media_writer,
    "handoff_to_press_release_writer": press_release_writer,
    "handoff_to_internal_memo_writer": internal_memo_writer,
}


def _mock_orchestrator(messages, tools, system) -> llm.LLMResponse:
    """Stands in for the model's routing decision. A real model reads the
    request's intent; this heuristic keys off a couple of obvious words so
    the routing logic is visible without an API key."""
    request_text = messages[-1]["content"].lower()
    if "press release" in request_text or "external" in request_text or "announce" in request_text:
        tool_name = "handoff_to_press_release_writer"
    elif "memo" in request_text or "internal" in request_text:
        tool_name = "handoff_to_internal_memo_writer"
    else:
        tool_name = "handoff_to_social_media_writer"

    return llm.LLMResponse(
        text=None,
        tool_calls=[llm.ToolCall(id="route_1", name=tool_name, arguments={"request": messages[-1]["content"]})],
    )


def run(request: str) -> str:
    tracing.system(f"orchestrator received: {request!r}")
    response = llm.chat(
        [{"role": "user", "content": request}],
        system=ORCHESTRATOR_SYSTEM,
        tools=HANDOFF_TOOLS,
        mock_fn=_mock_orchestrator,
    )
    if not response.has_tool_calls:
        raise RuntimeError("orchestrator did not route the request to a specialist")

    call = response.tool_calls[0]
    tracing.tool_call("orchestrator", call.name, call.arguments)
    specialist = SPECIALISTS[call.name]
    result = specialist(call.arguments["request"])
    tracing.tool_result("orchestrator", call.name, "handed off")
    return result


if __name__ == "__main__":
    request = " ".join(sys.argv[1:]) or "We need a quick social post celebrating our new training program."
    print("\n=== SPECIALIST OUTPUT ===")
    print(run(request))
