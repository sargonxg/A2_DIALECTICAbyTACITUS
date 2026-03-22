"""
Waitlist Router — Email capture for early access.
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["waitlist"])

# In-memory store (migrate to DB later)
_waitlist: dict[str, dict] = {}

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class WaitlistRequest(BaseModel):
    email: str
    source: str = "demo"


class WaitlistResponse(BaseModel):
    id: str
    message: str


@router.post("/waitlist", response_model=WaitlistResponse)
async def join_waitlist(req: WaitlistRequest) -> WaitlistResponse:
    """Join the DIALECTICA early access waitlist."""
    email = req.email.strip().lower()

    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=422, detail="Invalid email address.")

    # Check for duplicate
    for entry in _waitlist.values():
        if entry["email"] == email:
            return WaitlistResponse(id=entry["id"], message="You're already on the list!")

    entry_id = str(uuid.uuid4())[:8]
    _waitlist[entry_id] = {
        "id": entry_id,
        "email": email,
        "source": req.source,
        "created_at": datetime.now(UTC).isoformat(),
    }

    logger.info("waitlist_signup email=%s source=%s id=%s", email, req.source, entry_id)

    return WaitlistResponse(id=entry_id, message="Welcome to DIALECTICA! We'll be in touch.")


def get_waitlist_count() -> int:
    return len(_waitlist)
