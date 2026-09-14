# 4. Setup and Running

## Requirements

- Python 3.10+ (uses `list[str]`-style generics and `match`-free modern
  syntax throughout; 3.10 or newer is safest)
- No API key required to start -- see "Mock mode" below

## Install

```bash
git clone <this-repo-url>
cd agentic-ai-patterns
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Mock mode -- run everything with zero API keys

Every pattern defaults to `LLM_PROVIDER=mock` (set in `.env.example`),
which uses small, scripted-but-realistic stand-ins for the model instead
of a real API call. This is intentional and important for a classroom:

- Nobody needs an API key on day one.
- Every run is deterministic -- great for a live demo, and for students
  comparing notes ("did you get the same output as me?").
- You can read each pattern's `_mock_*` function to see exactly what a
  real model call is standing in for.

Run any pattern directly from the repo root:

```bash
PYTHONPATH=. python patterns/01_agent_loop_with_tools/agent.py
PYTHONPATH=. python patterns/02_sequential_pipeline/pipeline.py
PYTHONPATH=. python patterns/03_parallel_fanout/pipeline.py
PYTHONPATH=. python patterns/04_loop_critic_reviser/pipeline.py
PYTHONPATH=. python patterns/05_dynamic_multi_agent_routing/orchestrator.py
```

Pattern 6 and the capstone involve a second process (the illustration
agent) and need `--app-dir` instead of a dotted module path, because its
folder name (`06_agent_to_agent_http`) starts with a digit and isn't a
legal Python package name on its own -- a deliberate trade-off so folders
stay numbered in teaching order. Two terminals:

```bash
# terminal 1
PYTHONPATH=. uvicorn illustration_agent_service:app --app-dir patterns/06_agent_to_agent_http --port 8001

# terminal 2
PYTHONPATH=. python patterns/06_agent_to_agent_http/client.py
PYTHONPATH=. python capstone/marketing_content_studio/studio.py
```

> Every entry-point script inserts the repo root onto `sys.path` itself
> (see the `sys.path.insert(...)` line near the top of each file), so
> `PYTHONPATH=.` is technically redundant for those -- but it's included
> in every command here as a habit that also makes `uvicorn --app-dir`
> and any future scripts work without surprises. If you forget it and see
> `ModuleNotFoundError: No module named 'common'`, that's the fix.

## Using a real model

Set `LLM_PROVIDER` in `.env` to `openai` or `anthropic` and add the
matching API key. Nothing else changes -- the same `run()` functions, the
same trace output shape, just real model reasoning instead of the
scripted mock.

```bash
# .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

or

```bash
# .env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-5
```

A good in-class moment: run the same pattern in mock mode, then in real
mode, side by side, and compare. Ask "where did the real model's decision
differ from our scripted guess, and why?"

## Running the test suite

Every pattern has an offline smoke test (mock mode, no API key) in
`tests/`, checking that the plumbing works: loops terminate, parallel
fan-out returns every result, the critic/reviser loop actually converges,
routing picks the right specialist, and the HTTP agent's endpoints
respond correctly.

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Handy for verifying your own changes/exercises didn't break anything
structural, and for instructors to confirm a fresh clone still works
before a session.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'common'` | Ran a script from inside its own folder, or skipped `PYTHONPATH=.` | Run commands from the repo root as shown above |
| `httpx.ConnectError` from pattern 6's client or the capstone | Illustration agent isn't running | Start it first (see the two-terminal command above) |
| `openai.AuthenticationError` / `anthropic.AuthenticationError` | `LLM_PROVIDER` set to a real provider but the API key is missing/wrong | Check `.env`, or switch back to `LLM_PROVIDER=mock` |
| Colors look wrong in your terminal or CI logs | ANSI color codes | Set `NO_COLOR=1` to get plain text output |
| `uvicorn: command not found` | `fastapi`/`uvicorn` not installed | `pip install -r requirements.txt` (they're in there) |

Next: read [05-teaching-guide.md](05-teaching-guide.md) if you're
preparing to run this as a workshop.
