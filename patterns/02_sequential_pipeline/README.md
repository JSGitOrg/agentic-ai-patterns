# Pattern 2 -- Sequential Pipeline

## The idea

```mermaid
flowchart LR
    A[research_stage] --> B[writer_stage] --> C[Draft]
```

A fixed chain of steps, each one depending on the output of the one
before it. No model gets to decide the order -- *you* already know
research has to happen before writing, so you hard-code that instead of
paying an LLM call to "decide" something that never varies.

This is the same idea as a Unix pipe (`fetch | parse | render`) or a CI
pipeline (`build -> test -> deploy`), just with an LLM call as one or more
of the stages.

## When to reach for this vs. Pattern 1

| | Pattern 1 (agent loop) | Pattern 2 (sequential) |
|---|---|---|
| Who decides what happens next? | The model | You, in code |
| Order can vary per request? | Yes | No |
| Easiest to unit test? | Harder (nondeterministic branching) | Easy (fixed steps) |
| Good for | Open-ended Q&A, research | Known, repeatable workflows |

A lot of real "agentic" systems are actually mostly Pattern 2 with a
Pattern 1 loop embedded in one or two of the stages -- see the capstone.

## Run it

```bash
PYTHONPATH=. python patterns/02_sequential_pipeline/pipeline.py
```

## Things to point out in class

- `writer_stage` cannot run before `research_stage` finishes -- there's a
  genuine data dependency (it needs `research["guidelines"]`). That
  dependency is the *definition* of "sequential" here; if the stages were
  independent, you'd want Pattern 3 instead.
- Stage 1 doesn't call an LLM at all. Not every pipeline stage needs to be
  "an agent" -- plain deterministic code is often the right stage.
- This whole file has no branching and no loop. That's a feature: it's the
  cheapest, most predictable, most testable pattern in this repo. Reach
  for Patterns 1/4/5 only when you actually need the flexibility they add.
