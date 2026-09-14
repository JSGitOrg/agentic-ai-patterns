"""A deterministic, offline stand-in for an image-generation tool.

A real illustration agent would call an image model (Imagen, DALL-E,
Gemini image, ...), which costs money and needs its own API key. To keep
this training runnable for an entire classroom at zero image-gen cost,
the illustration agent (pattern 06 / capstone) instead renders a simple
on-brand SVG poster from a headline and a few keywords.

The *pattern* being taught here -- a specialist agent that runs as its
own process and is discoverable and callable over the network -- is
identical either way. Swapping this function for a real image-generation
API call is a one-function change; see patterns/06_agent_to_agent_http/README.md.
"""

from __future__ import annotations

import hashlib

PALETTE = ["#5B2A86", "#DAF7A6", "#FF7E5F", "#2E2E38"]

_SHAPES = {
    "team": "<circle cx='0' cy='0' r='26' />",
    "training": "<rect x='-28' y='-18' width='56' height='36' rx='6' />",
    "stadium": "<polygon points='-30,20 0,-24 30,20' />",
    "maintenance": "<rect x='-6' y='-30' width='12' height='60' rx='4' transform='rotate(35)' />",
}
_DEFAULT_SHAPE = "<rect x='-24' y='-24' width='48' height='48' rx='10' />"


def _pick_shape(keywords: list[str]) -> str:
    joined = " ".join(keywords).lower()
    for key, shape in _SHAPES.items():
        if key in joined:
            return shape
    return _DEFAULT_SHAPE


def generate_poster_svg(headline: str, keywords: list[str]) -> str:
    """Render a small on-brand SVG poster. Deterministic: same headline
    always produces the same layout, so the pattern is easy to demo and
    to test without an LLM in the loop.
    """
    seed = int(hashlib.sha256(headline.encode("utf-8")).hexdigest(), 16)
    background = PALETTE[seed % 2]
    foreground = PALETTE[2 + (seed % 2)]
    shape = _pick_shape(keywords)
    safe_headline = (headline[:42] + "...") if len(headline) > 45 else headline

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
  <rect width="400" height="300" fill="{background}" />
  <g transform="translate(200,120)" fill="{foreground}">{shape}</g>
  <text x="200" y="250" text-anchor="middle" font-family="sans-serif" font-size="18" fill="#ffffff">{safe_headline}</text>
</svg>"""
