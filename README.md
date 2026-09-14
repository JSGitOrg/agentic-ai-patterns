# Agentic AI Patterns -- A Hands-On Training

A training repo for teaching agentic AI concepts through one real,
cohesive use case: **the Cymbal Stadiums Marketing Content Studio** -- a
multi-agent system that turns a raw idea into approved, on-brand,
multi-language slide content with a matching illustration.

Everything is built **from scratch in plain Python** -- no agent
framework. The point is to make the mechanics of "agentic AI" visible:
what a tool-calling loop actually does, what "multi-agent" actually means
at the code level, and what it takes for two agents to talk to each other
over a network. Once these are second nature, picking up a framework
(Google's ADK, LangGraph, CrewAI, ...) is mostly learning new names for
ideas you already understand.

**No API key needed to get started.** Every pattern runs fully offline
with `LLM_PROVIDER=mock` (the default) -- realistic, scripted model
replies so you can study the *control flow* before spending any API
credits. Flip one environment variable to run the same code against a
real model (OpenAI or Anthropic).

## Start here

| If you want to... | Go to |
|---|---|
| Understand the concepts first | [`docs/01-agentic-ai-concepts.md`](docs/01-agentic-ai-concepts.md) |
| See all 6 patterns compared side by side | [`docs/02-pattern-catalog.md`](docs/02-pattern-catalog.md) |
| Read the full use case this repo builds toward | [`docs/03-use-case-marketing-studio.md`](docs/03-use-case-marketing-studio.md) |
| Just install and run something | [`docs/04-setup-and-running.md`](docs/04-setup-and-running.md) |
| Run this as a workshop/course module | [`docs/05-teaching-guide.md`](docs/05-teaching-guide.md) |

## Quickstart

```bash
git clone <this-repo-url>
cd agentic-ai-patterns
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

PYTHONPATH=. python patterns/01_agent_loop_with_tools/agent.py
```

## The six patterns

Each has its own runnable code and a README explaining the idea, when to
use it, and what to point out in class.

1. **[Agent loop with tools](patterns/01_agent_loop_with_tools/)** -- the
   foundational ReAct loop: model decides, turn by turn, whether to call a
   tool or answer.
2. **[Sequential pipeline](patterns/02_sequential_pipeline/)** -- a fixed
   chain of steps where each depends on the last.
3. **[Parallel fan-out / fan-in](patterns/03_parallel_fanout/)** --
   independent sub-tasks run concurrently, then merge.
4. **[Loop with an exit condition](patterns/04_loop_critic_reviser/)** --
   a critic/reviser cycle that repeats until approved, capped so it can't
   run forever.
5. **[Dynamic multi-agent routing](patterns/05_dynamic_multi_agent_routing/)**
   -- an orchestrator that decides, per request, which specialist should
   handle it.
6. **[Agent-to-agent over HTTP](patterns/06_agent_to_agent_http/)** -- two
   independent processes: one agent discovers another's capabilities via
   an "agent card," then calls it as a remote task. A simplified,
   from-scratch teaching version of the idea behind Google's A2A protocol.

## The capstone

**[`capstone/marketing_content_studio/`](capstone/marketing_content_studio/)**
combines patterns 2, 3, 4, and 6 into the real pipeline: sequential
research + draft -> loop until on-brand -> parallel localization into 3
languages + a remote agent-to-agent call for the illustration -> a
finished, saved content package.

```bash
# terminal 1
PYTHONPATH=. uvicorn illustration_agent_service:app --app-dir patterns/06_agent_to_agent_http --port 8001

# terminal 2
PYTHONPATH=. python capstone/marketing_content_studio/studio.py
```

## Repo layout

```
common/            Shared, vendor-agnostic building blocks
  llm.py             chat()+tool-calling wrapper (mock / OpenAI / Anthropic)
  tracing.py         console tracer used by every pattern
  cymbal_tools.py     shared "brand guidelines" / "audience persona" tools
  svg_poster.py       offline, deterministic illustration tool

patterns/          One self-contained pattern per numbered folder
capstone/          The full use case, composing several patterns
docs/              Concepts, pattern catalog, use case, setup, teaching guide
```

## Why plain Python instead of a framework?

Because the fastest way to actually understand what "agentic AI" means is
to write the loop yourself once. See the last section of
[`docs/01-agentic-ai-concepts.md`](docs/01-agentic-ai-concepts.md) for the
full trade-off, and a pointer to where each pattern's built-in equivalent
lives in Google's Agent Development Kit, LangGraph, and CrewAI.
