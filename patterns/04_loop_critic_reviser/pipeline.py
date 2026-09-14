"""Pattern 4: loop with an exit condition (critic/reviser).

Some tasks can't be done well in one shot -- a first draft is rarely the
best draft. This pattern wraps a draft in a loop: a critic agent judges
it, a reviser agent improves it based on the critique, and the loop keeps
going until the critic approves (or a hard iteration cap is hit, so a
stubborn critic and reviser can't loop forever and run up your bill).

Run it:
    PYTHONPATH=. python patterns/04_loop_critic_reviser/pipeline.py
    PYTHONPATH=. python patterns/04_loop_critic_reviser/pipeline.py "your draft text here"
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv  # noqa: E402

from common import llm, tracing  # noqa: E402

load_dotenv()

MAX_ITERATIONS = 3


def _mock_critic(iteration: int):
    def responder(messages, tools, system) -> llm.LLMResponse:
        draft = messages[-1]["content"]
        if "wrench" in draft.lower():
            return llm.LLMResponse(text="APPROVE: concrete, on-brand, and clear.")
        return llm.LLMResponse(
            text=(
                "REVISE: this reads as generic corporate praise. Ground it in one "
                "concrete image from our actual maintenance work (wrenches, toolboxes, turf)."
            )
        )

    return responder


def _mock_reviser(messages, tools, system) -> llm.LLMResponse:
    return llm.LLMResponse(
        text=(
            "Every wrench we hand a trainee keeps a stadium game-ready. Our on-the-job "
            "training turns new hires into the crew that never lets fans down."
        )
    )


def critique(draft: str, iteration: int) -> str:
    tracing.step("critic", f"reviewing draft (iteration {iteration})")
    prompt = (
        "Review this slide body copy against our brand voice (warm, plainspoken, concrete). "
        f"Respond starting with exactly 'APPROVE:' or 'REVISE:'.\n\n{draft}"
    )
    response = llm.chat([{"role": "user", "content": prompt}], mock_fn=_mock_critic(iteration))
    verdict = response.text or ""
    tracing.tool_result("critic", "verdict", verdict)
    return verdict


def revise(draft: str, feedback: str) -> str:
    tracing.step("reviser", "revising draft based on feedback")
    prompt = f"Original draft:\n{draft}\n\nFeedback:\n{feedback}\n\nRewrite the draft to address the feedback."
    response = llm.chat([{"role": "user", "content": prompt}], mock_fn=_mock_reviser)
    return response.text or ""


def run(initial_draft: str) -> tuple[str, int]:
    """The loop: critique, and if not approved, revise and try again. Two
    ways out: the critic approves, or we hit MAX_ITERATIONS -- never an
    unbounded loop."""
    draft = initial_draft
    tracing.system(f"loop start, max_iterations={MAX_ITERATIONS}")

    for iteration in range(1, MAX_ITERATIONS + 1):
        verdict = critique(draft, iteration)
        if verdict.upper().startswith("APPROVE"):
            tracing.system(f"exit condition met on iteration {iteration}: approved")
            return draft, iteration
        feedback = verdict.split(":", 1)[-1].strip()
        draft = revise(draft, feedback)

    tracing.system(f"hit MAX_ITERATIONS={MAX_ITERATIONS} without approval -- returning best effort")
    return draft, MAX_ITERATIONS


if __name__ == "__main__":
    initial = " ".join(sys.argv[1:]) or "Our team does a really great job with employee training and development."
    final_draft, iterations_used = run(initial)
    print(f"\n=== FINAL DRAFT (after {iterations_used} iteration(s)) ===")
    print(final_draft)
