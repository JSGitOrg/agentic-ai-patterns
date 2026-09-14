"""Pattern 6 (client side): call the remote illustration agent.

Discover its agent card first, then call the task endpoint the card
points to. This is exactly how you'd call any other microservice, except
the *shape* of what you're calling (its skills, description, and where to
send a request) is discoverable at runtime rather than something both
teams had to agree on and hard-code in advance.

Run the server first, in its own terminal:
    PYTHONPATH=. uvicorn illustration_agent_service:app \\
        --app-dir patterns/06_agent_to_agent_http --port 8001

Then, in a second terminal, from the repo root:
    PYTHONPATH=. python patterns/06_agent_to_agent_http/client.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import httpx  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

from common import tracing  # noqa: E402

load_dotenv()

DEFAULT_URL = os.getenv("ILLUSTRATION_AGENT_URL", "http://localhost:8001")


def discover(base_url: str = DEFAULT_URL) -> dict:
    tracing.step("client", f"discovering agent card at {base_url}/.well-known/agent.json")
    response = httpx.get(f"{base_url}/.well-known/agent.json", timeout=10.0)
    response.raise_for_status()
    card = response.json()
    tracing.tool_result("client", "agent_card", card["description"])
    return card


def illustrate(headline: str, keywords: list[str], base_url: str = DEFAULT_URL) -> str:
    card = discover(base_url)
    endpoint = base_url + card["task_endpoint"]
    tracing.tool_call("client", f"POST {endpoint}", {"headline": headline, "keywords": keywords})
    response = httpx.post(endpoint, json={"headline": headline, "keywords": keywords}, timeout=30.0)
    response.raise_for_status()
    svg = response.json()["svg"]
    tracing.tool_result("client", "illustrate", f"{len(svg)} bytes of SVG")
    return svg


if __name__ == "__main__":
    headline = " ".join(sys.argv[1:]) or "Every Wrench Turned Is a Game Saved"

    try:
        svg = illustrate(headline, ["training", "maintenance"])
    except httpx.ConnectError:
        print(
            "\nCould not reach the illustration agent. Start it first, in another "
            "terminal, from the repo root:\n"
            "  PYTHONPATH=. uvicorn illustration_agent_service:app "
            "--app-dir patterns/06_agent_to_agent_http --port 8001\n"
        )
        raise

    out_path = Path(__file__).resolve().parent / "poster.svg"
    out_path.write_text(svg)
    print(f"Saved poster to {out_path}")
