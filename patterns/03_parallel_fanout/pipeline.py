"""Pattern 3: parallel fan-out / fan-in.

When several sub-tasks are independent of each other (translating the
same text into Spanish, French, and German -- none needs the others'
output) running them one after another just wastes wall-clock time. Fan
them out concurrently, then fan back in once they've all finished.

LLM calls are I/O-bound (you're mostly waiting on a network response), so
a plain `ThreadPoolExecutor` is enough here -- no need for `asyncio` to
get the speedup. (If you're comfortable with async, `asyncio.gather` is
the equivalent tool; threads are used here because more students already
know them.)

Run it:
    PYTHONPATH=. python patterns/03_parallel_fanout/pipeline.py
    PYTHONPATH=. python patterns/03_parallel_fanout/pipeline.py "your text here"
"""

from __future__ import annotations

import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv  # noqa: E402

from common import llm, tracing  # noqa: E402

load_dotenv()

LANGUAGES = {"es": "Spanish", "fr": "French", "de": "German"}

# Real network/model calls take noticeable time. Mock mode simulates that
# with a short sleep so the parallel-vs-sequential timing comparison below
# is actually visible instead of instant.
_SIMULATED_LATENCY_SECONDS = 0.6


def _mock_translator(lang_name: str):
    def responder(messages, tools, system) -> llm.LLMResponse:
        time.sleep(_SIMULATED_LATENCY_SECONDS)
        source_text = messages[-1]["content"]
        return llm.LLMResponse(text=f"[{lang_name}] {source_text}")

    return responder


def translate(text: str, lang_code: str) -> str:
    lang_name = LANGUAGES[lang_code]
    tracing.step(f"translator:{lang_code}", f"translating into {lang_name}")
    prompt = f"Translate the following slide copy into {lang_name}. Keep it concise:\n\n{text}"
    response = llm.chat([{"role": "user", "content": prompt}], mock_fn=_mock_translator(lang_name))
    tracing.step(f"translator:{lang_code}", "done")
    return response.text or ""


def run(text: str) -> dict[str, str]:
    """Fan out one `translate` call per language onto a thread pool, then
    fan back in by collecting every future's result."""
    tracing.system(f"parallel fan-out over {list(LANGUAGES)} for: {text!r}")
    results: dict[str, str] = {}
    started = time.perf_counter()

    with ThreadPoolExecutor(max_workers=len(LANGUAGES)) as pool:
        future_to_code = {pool.submit(translate, text, code): code for code in LANGUAGES}
        for future in as_completed(future_to_code):
            code = future_to_code[future]
            results[code] = future.result()

    elapsed = time.perf_counter() - started
    tracing.system(f"parallel fan-in complete in {elapsed:.2f}s")
    return results


if __name__ == "__main__":
    text = " ".join(sys.argv[1:]) or "By supporting each other, we get big things done!"

    parallel_results = run(text)
    print("\n=== PARALLEL RESULTS ===")
    for code, translation in parallel_results.items():
        print(f"{code}: {translation}")

    sequential_estimate = len(LANGUAGES) * _SIMULATED_LATENCY_SECONDS
    print(f"\n(Running these one at a time would take roughly {sequential_estimate:.1f}s "
          f"instead of ~{_SIMULATED_LATENCY_SECONDS:.1f}s.)")
