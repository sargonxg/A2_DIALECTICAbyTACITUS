"""
Templates Router — Domain-specific workspace configuration templates.
"""

from __future__ import annotations

import os
from typing import Any

import yaml
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/v1/templates", tags=["templates"])

TEMPLATES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "..", "data", "templates"
)


class TemplateInfo(BaseModel):
    id: str
    name: str
    description: str
    tier: str
    domain: str


class TemplateDetail(TemplateInfo):
    symbolic_rules: dict[str, Any] = {}
    extraction: dict[str, Any] = {}
    analysis: dict[str, Any] = {}
    actor_types: list[str] = []


def _load_templates() -> dict[str, dict]:
    """Load all YAML templates from data/templates/."""
    templates: dict[str, dict] = {}
    templates_dir = TEMPLATES_DIR

    # Also check relative to CWD
    if not os.path.isdir(templates_dir):
        templates_dir = os.path.join(os.getcwd(), "data", "templates")

    if not os.path.isdir(templates_dir):
        return templates

    for fname in os.listdir(templates_dir):
        if fname.endswith((".yaml", ".yml")):
            fpath = os.path.join(templates_dir, fname)
            with open(fpath) as f:
                data = yaml.safe_load(f)
                if data and "id" in data:
                    templates[data["id"]] = data

    return templates


@router.get("", response_model=list[TemplateInfo])
async def list_templates() -> list[TemplateInfo]:
    """List available workspace templates."""
    templates = _load_templates()
    return [
        TemplateInfo(
            id=t["id"],
            name=t.get("name", t["id"]),
            description=t.get("description", ""),
            tier=t.get("tier", "essential"),
            domain=t.get("domain", "general"),
        )
        for t in templates.values()
    ]


@router.get("/{template_id}", response_model=TemplateDetail)
async def get_template(template_id: str) -> TemplateDetail:
    """Get full template configuration."""
    templates = _load_templates()
    t = templates.get(template_id)
    if not t:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

    return TemplateDetail(
        id=t["id"],
        name=t.get("name", t["id"]),
        description=t.get("description", ""),
        tier=t.get("tier", "essential"),
        domain=t.get("domain", "general"),
        symbolic_rules=t.get("symbolic_rules", {}),
        extraction=t.get("extraction", {}),
        analysis=t.get("analysis", {}),
        actor_types=t.get("actor_types", []),
    )
