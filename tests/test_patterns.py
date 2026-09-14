"""Smoke tests for each pattern, run fully offline via LLM_PROVIDER=mock.

These test the *plumbing* (the loop terminates, concurrency returns every
result, the loop's exit condition actually fires) -- not model quality,
since there's no real model in the loop here.

Pattern folders are numbered for teaching order (01_..., 02_..., ...),
which means they aren't legal Python package names (identifiers can't
start with a digit) -- so each module is loaded directly from its file
path with importlib instead of a normal `import` statement. See
docs/04-setup-and-running.md for why the folders are numbered anyway.
"""

import importlib.util
import os
import sys
from pathlib import Path

os.environ.setdefault("LLM_PROVIDER", "mock")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def _load(alias: str, relative_path: str):
    path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pattern_1_agent_loop_produces_final_answer():
    agent = _load("pattern1_agent", "patterns/01_agent_loop_with_tools/agent.py")
    answer = agent.run("What imagery and colors should I use for a poster?")
    assert isinstance(answer, str) and len(answer) > 0


def test_pattern_2_sequential_pipeline_produces_headline_and_body():
    pipeline = _load("pattern2_pipeline", "patterns/02_sequential_pipeline/pipeline.py")
    draft = pipeline.run("our excellent on-the-job training")
    assert "HEADLINE" in draft and "BODY" in draft


def test_pattern_3_parallel_fanout_returns_every_language():
    pipeline = _load("pattern3_pipeline", "patterns/03_parallel_fanout/pipeline.py")
    results = pipeline.run("hello team")
    assert set(results.keys()) == set(pipeline.LANGUAGES.keys())
    assert all(results.values())


def test_pattern_4_loop_converges_within_the_iteration_cap():
    pipeline = _load("pattern4_pipeline", "patterns/04_loop_critic_reviser/pipeline.py")
    draft, iterations_used = pipeline.run("Our team does a really great job.")
    assert 1 <= iterations_used <= pipeline.MAX_ITERATIONS
    assert "wrench" in draft.lower()


def test_pattern_5_routes_press_release_requests_correctly():
    orchestrator = _load("pattern5_orchestrator", "patterns/05_dynamic_multi_agent_routing/orchestrator.py")
    output = orchestrator.run("we need a press release about the training program")
    assert "CYMBAL STADIUMS" in output


def test_pattern_5_routes_memo_requests_correctly():
    orchestrator = _load("pattern5_orchestrator_memo", "patterns/05_dynamic_multi_agent_routing/orchestrator.py")
    output = orchestrator.run("send the team an internal memo about the new schedule")
    assert "team" in output.lower()


def test_pattern_6_agent_card_and_task_endpoint():
    fastapi_testclient = importlib.import_module("fastapi.testclient")
    service = _load("pattern6_service", "patterns/06_agent_to_agent_http/illustration_agent_service.py")
    client = fastapi_testclient.TestClient(service.app)

    card = client.get("/.well-known/agent.json").json()
    assert card["task_endpoint"] == "/tasks/illustrate"

    response = client.post("/tasks/illustrate", json={"headline": "Test Headline", "keywords": ["training"]})
    assert response.status_code == 200
    assert response.json()["svg"].startswith("<svg")
