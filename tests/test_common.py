"""Smoke tests for the shared, framework-free building blocks in common/."""

import os
import sys
from pathlib import Path

os.environ.setdefault("LLM_PROVIDER", "mock")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.cymbal_tools import lookup_audience_persona, lookup_brand_guidelines  # noqa: E402
from common.svg_poster import generate_poster_svg  # noqa: E402


def test_generate_poster_svg_is_deterministic():
    first = generate_poster_svg("Test Headline", ["training"])
    second = generate_poster_svg("Test Headline", ["training"])
    assert first == second
    assert first.startswith("<svg")


def test_generate_poster_svg_varies_with_headline():
    a = generate_poster_svg("Headline A", [])
    b = generate_poster_svg("A Totally Different Headline B", [])
    assert a != b


def test_lookup_brand_guidelines_has_colors():
    guidelines = lookup_brand_guidelines("poster")
    assert "colors" in guidelines
    assert "primary" in guidelines["colors"]


def test_lookup_audience_persona_known_audience():
    persona = lookup_audience_persona("external")
    assert "facility managers" in persona["persona"].lower()


def test_lookup_audience_persona_falls_back_for_unknown_audience():
    persona = lookup_audience_persona("some-made-up-audience")
    assert "persona" in persona and persona["persona"]
