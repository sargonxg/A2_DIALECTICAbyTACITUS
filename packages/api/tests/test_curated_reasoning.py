"""Tests for Prompt 2 curated reasoning API contracts."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_curated_library_lists_all_questions(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    response = await client.get(
        "/v1/workspaces/demo-syria/reason/library",
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["workspace_id"] == "demo-syria"
    assert len(body["questions"]) == 23
    assert {question["id"] for question in body["questions"]} >= {"R-1", "W-1", "S-1"}


async def test_curated_library_filters_by_scenario(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    response = await client.get(
        "/v1/workspaces/demo-syria/reason/library?scenario_id=syria",
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    questions = response.json()["questions"]
    assert len(questions) == 8
    assert all(question["scenario_id"] == "syria" for question in questions)


async def test_similarity_rejects_unsupported_question(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/v1/workspaces/demo-syria/reason/similarity",
        json={"question_id": "S-1", "k": 3},
        headers=admin_headers,
    )

    assert response.status_code == 422


async def test_similarity_returns_supported_neighbours(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/v1/workspaces/demo-syria/reason/similarity",
        json={"question_id": "S-7", "k": 2},
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["question_id"] == "S-7"
    assert len(body["neighbours"]) == 2
    assert body["neighbours"][0]["workspace_id"].startswith("corpus-successor-")
