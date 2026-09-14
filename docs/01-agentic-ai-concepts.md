# 1. What Is "Agentic AI," Actually?

## From chatbot to agent

A plain LLM call is a function: text in, text out. Nothing changes about
*how* it answers based on what it learns partway through. That's not
agentic -- it's a smart autocomplete.

An **agentic** system adds a loop with consequences:

1. The model can decide to **act** (call a tool, fetch data, call another
   agent), not just talk.
2. The **result of that action feeds back in**, and the model gets to
   decide what to do next based on it.
3. The loop runs until some **goal or exit condition** is reached, not a
   fixed number of steps decided in advance.

That's it. Every pattern in this repo is a different shape of that same
idea -- one agent looping on itself (pattern 1), several agents chained in
a row (pattern 2), several running at once (pattern 3), one agent looping
with another checking its work (pattern 4), one agent picking which of
several others should run (pattern 5), and agents split across separate
processes or organizations entirely (pattern 6).

## The four building blocks

Every agent in this repo (and in virtually every agent framework you'll
encounter -- Google's ADK, LangGraph, CrewAI, OpenAI's Agents SDK, ...) is
made of the same four things:

| Building block | What it is | Where it lives in this repo |
|---|---|---|
| **Model** | The LLM that reasons about what to do next | `common/llm.py` |
| **Tools** | Functions the model can ask to have run | `common/cymbal_tools.py`, `common/svg_poster.py` |
| **State / memory** | What the agent remembers across steps | the `messages` list each pattern builds up |
| **Orchestration** | The code deciding when to call the model, run a tool, hand off to another agent, or stop | the `run()` / `_run_async_impl`-style function in each pattern |

Frameworks mostly differ in how much of the third and fourth columns they
write for you. This repo writes them by hand every time, on purpose --
once you've built the loop yourself, a framework's version stops looking
like magic.

## Two axes worth teaching explicitly

**Deterministic vs. dynamic control flow.** Patterns 2 and 3 (sequential,
parallel) have a control flow *you* wrote and that never changes between
runs. Patterns 1, 4, and 5 have control flow the *model* decides, at
least partly, at runtime. Neither is "more agentic" than the other --
production systems mix both, using dynamic control flow only where the
judgment call genuinely can't be hard-coded (see the capstone).

**In-process vs. cross-process (or cross-organization).** Patterns 1
through 5 all run inside one Python process. Pattern 6 crosses a network
boundary. This distinction matters enormously in practice: it's the
difference between "a function call I can put a breakpoint on" and "a
service another team owns, that can be slow, down, or wrong in ways you
don't control." Most real "multi-agent" systems in industry are really
about that second category -- getting agents built by different teams (or
different companies) to interoperate.

## Where A2A (and MCP) fit

Two open protocols show up constantly in this space, and it's worth being
precise about what each one is *for*:

- **MCP (Model Context Protocol)** standardizes how a model/agent
  discovers and calls **tools and data sources** -- "here's a menu of
  functions and resources you can use," typically local or same-team.
  Think of it as the protocol for the "tools" building block above.
- **A2A (Agent2Agent Protocol)** standardizes how **one agent talks to
  another independent agent**, potentially owned by a different team or
  company -- discovery via an **agent card**, then invoking a **task**.
  Think of it as the protocol for making the "orchestration" building
  block work *across* a network boundary, between peers rather than
  between an agent and its own tools.

Pattern 6 in this repo implements a deliberately simplified version of the
A2A idea (agent card + task endpoint) using plain FastAPI, so you can see
every byte on the wire without an SDK in the way. See
`patterns/06_agent_to_agent_http/README.md` for exactly what's simplified
and where to find the real spec and official SDK.

## "Plain Python, no framework" -- why, and what you lose

This repo intentionally skips agent frameworks so every mechanism is
visible: the tool-calling loop, the message history, the exit conditions,
the concurrency, the network boundary. That's a deliberate trade-off:

- **What you gain:** nothing is hidden. Every pattern is 60-150 lines you
  can read start to finish. Vendor differences (see
  `common/llm.py`'s OpenAI vs. Anthropic branches) are visible instead of
  abstracted away.
- **What a real framework buys you** that this repo doesn't reimplement:
  automatic retries and backoff, streaming responses, built-in tracing/
  observability, session persistence across restarts, structured
  multi-agent transfer protocols, and a much larger tool/connector
  ecosystem. Once these patterns feel obvious, look at Google's
  [Agent Development Kit](https://google.github.io/adk-docs/) (which has
  `SequentialAgent` / `ParallelAgent` / `LoopAgent` / `RemoteA2aAgent`
  primitives mapping almost 1:1 onto patterns 2, 3, 4, and 6 here),
  [LangGraph](https://langchain-ai.github.io/langgraph/), or
  [CrewAI](https://www.crewai.com/) to see the same ideas with the
  plumbing done for you.

Next: [02-pattern-catalog.md](02-pattern-catalog.md) for a side-by-side
comparison of every pattern, or jump straight to
[04-setup-and-running.md](04-setup-and-running.md) to start running code.
