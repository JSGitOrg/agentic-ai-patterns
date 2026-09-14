"""Pattern 2: sequential pipeline (a.k.a. deterministic workflow).

Unlike pattern 1 (where the *model* decides what happens next), here
*you* decide the order: research always runs before writing. This is the
right pattern whenever step B genuinely needs step A's output and the
order never changes -- it's simpler, cheaper, and easier to test than
letting a model improvise the control flow every time.

Run it:
    PYTHONPATH=. python patterns/02_sequential_pipeline/pipeline.py
    PYTHONPATH=. python patterns/02_sequential_pipeline/pipeline.py "your topic here"
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv  # noqa: E402

from common import llm, tracing  # noqa: E402
from common.cymbal_tools import lookup_audience_persona, lookup_brand_guidelines  # noqa: E402

load_dotenv()


def research_stage(topic: str, audience: str) -> dict:
    """Stage 1: gather facts. A pipeline stage doesn't have to call an LLM
    at all -- deterministic tool calls are a perfectly good stage."""
    tracing.step("research_stage", f"gathering brand + persona facts for audience={audience!r}")
    guidelines = lookup_brand_guidelines(topic)
    persona = lookup_audience_persona(audience)
    return {"topic": topic, "guidelines": guidelines, "persona": persona}


def _mock_writer(messages, tools, system) -> llm.LLMResponse:
    return llm.LLMResponse(
        text=(
            "HEADLINE: Every Wrench Turned Is a Game Saved\n"
            "BODY: Our on-the-job training program puts real tools in new hands fast, so "
            "every stadium stays game-ready -- taught by the crews who already keep it that way."
        )
    )


def writer_stage(topic: str, research: dict) -> str:
    """Stage 2: turn the researched facts into slide copy. This stage
    cannot start until stage 1 has finished -- that dependency is exactly
    what makes the pipeline sequential rather than parallel (pattern 3)."""
    tracing.step("writer_stage", "drafting headline + body from research")
    prompt = (
        f"Topic: {topic}\n"
        f"Brand guidelines: {research['guidelines']}\n"
        f"Audience persona: {research['persona']['persona']}\n\n"
        "Write a slide headline (<=8 words) and a 1-2 sentence body that follows "
        "the brand voice above and speaks to this audience.\n"
        "Respond exactly as:\nHEADLINE: ...\nBODY: ..."
    )
    response = llm.chat([{"role": "user", "content": prompt}], mock_fn=_mock_writer)
    return response.text or ""


def run(topic: str, audience: str = "internal") -> str:
    tracing.system(f"sequential pipeline start: topic={topic!r} audience={audience!r}")
    research = research_stage(topic, audience)
    draft = writer_stage(topic, research)
    tracing.system("sequential pipeline done")
    return draft


if __name__ == "__main__":
    topic = " ".join(sys.argv[1:]) or "our excellent on-the-job training"
    print("\n=== DRAFT ===")
    print(run(topic))
