"""Shared domain 'tools' for the Cymbal Stadiums scenario used across this
repo. In a real system these would call a CMS, a design-system API, a
translation vendor, etc. Here they are plain deterministic Python
functions, so every pattern runs with zero external dependencies besides
(optionally) an LLM.
"""

from __future__ import annotations

BRAND_GUIDELINES = {
    "colors": {
        "primary": "#5B2A86 (Cymbal Purple)",
        "secondary": "#DAF7A6 (Turf Green)",
        "accent": "sunset orange-to-pink gradient",
    },
    "voice": "warm, plainspoken, a little proud -- like a groundskeeper who loves the stadium",
    "imagery": ["stadium lights", "yard-line markers", "wrenches & toolboxes", "turf & popcorn"],
    "avoid": ["stock corporate jargon", "baking text into illustrations"],
}

AUDIENCE_PERSONAS = {
    "internal": "Stadium ops & maintenance staff across 40 venues; skims content on a shared phone between shifts.",
    "external": "Facility managers at partner venues evaluating Cymbal's maintenance program.",
    "leadership": "Regional directors who forward this content to their own teams; wants the headline to carry the whole point.",
}


def lookup_brand_guidelines(topic: str = "") -> dict:
    """Tool: return Cymbal Stadiums' brand voice and visual guidelines."""
    return {"topic": topic or "general", **BRAND_GUIDELINES}


def lookup_audience_persona(audience: str) -> dict:
    """Tool: return a short persona description for a named audience."""
    key = audience.lower().strip()
    return {
        "audience": audience,
        "persona": AUDIENCE_PERSONAS.get(key, AUDIENCE_PERSONAS["internal"]),
    }


TOOL_SCHEMAS = {
    "lookup_brand_guidelines": {
        "name": "lookup_brand_guidelines",
        "description": "Look up Cymbal Stadiums' brand voice and visual guidelines.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Optional topic to focus the lookup on."}
            },
        },
    },
    "lookup_audience_persona": {
        "name": "lookup_audience_persona",
        "description": (
            "Look up a short persona description for a named audience. "
            "Valid audiences: internal, external, leadership."
        ),
        "parameters": {
            "type": "object",
            "properties": {"audience": {"type": "string"}},
            "required": ["audience"],
        },
    },
}
