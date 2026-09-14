"""Pattern 6 (server side): agent-to-agent communication over HTTP.

Every other pattern in this repo runs agents *in the same Python process*.
Real organizations don't work that way: one team owns the illustration
agent, deploys it, and improves it on its own schedule, while other teams
just need to *use* it. That requires a network boundary -- the caller and
the callee can be written in different languages, deployed independently,
and owned by different teams, as long as they agree on a wire protocol.

This service exposes two things over HTTP:

    1. GET  /.well-known/agent.json   -- an "agent card": machine-readable
       metadata describing what this agent can do and how to call it, so a
       caller can *discover* its capabilities instead of both teams
       hand-coordinating an interface up front.
    2. POST /tasks/illustrate         -- the actual work: hand it a
       headline + keywords, get back an on-brand SVG poster.

This is a simplified, from-scratch re-implementation of the core idea
behind Google's Agent2Agent (A2A) protocol (agent cards + task
invocation), built with nothing but FastAPI so every byte on the wire is
visible. It is NOT the official A2A SDK -- see
docs/01-agentic-ai-concepts.md for how this maps onto the real spec, and
when you'd reach for the real thing instead.

Run it (from the repo root, in its own terminal):
    PYTHONPATH=. uvicorn illustration_agent_service:app \\
        --app-dir patterns/06_agent_to_agent_http --port 8001
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from common import tracing  # noqa: E402
from common.svg_poster import generate_poster_svg  # noqa: E402

AGENT_NAME = "illustration_agent"

AGENT_CARD = {
    "name": AGENT_NAME,
    "description": "Generates an on-brand poster illustration for a piece of Cymbal Stadiums content.",
    "version": "1.0.0",
    "skills": [
        {
            "id": "illustrate",
            "name": "Illustrate content",
            "description": "Given a headline and a few keywords, returns an on-brand SVG poster.",
        }
    ],
    "task_endpoint": "/tasks/illustrate",
}

app = FastAPI(title=AGENT_NAME)


class IllustrateRequest(BaseModel):
    headline: str
    keywords: list[str] = []


class IllustrateResponse(BaseModel):
    agent: str = AGENT_NAME
    svg: str


@app.get("/.well-known/agent.json")
def agent_card() -> dict:
    """Discovery endpoint. A caller fetches this *before* knowing anything
    else about this agent, to learn what it can do and where to send work."""
    tracing.tool_result(AGENT_NAME, "agent_card", "served")
    return AGENT_CARD


@app.post("/tasks/illustrate", response_model=IllustrateResponse)
def illustrate(request: IllustrateRequest) -> IllustrateResponse:
    tracing.step(AGENT_NAME, f"illustrate task received: headline={request.headline!r}")
    svg = generate_poster_svg(request.headline, request.keywords)
    tracing.step(AGENT_NAME, "illustrate task complete")
    return IllustrateResponse(svg=svg)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
