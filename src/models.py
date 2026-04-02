from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

ALLOWED_ACTIONS = {"read", "archive", "flag", "respond", "delegate", "skip"}


class Observation(BaseModel):
    email_id: str
    sender: str
    subject: str
    body: str
    urgency: float = Field(ge=0.0, le=1.0)
    category: str
    inbox_size: int = Field(ge=0)
    time_budget_remaining: int
    step: int = Field(ge=0)


class Action(BaseModel):
    action_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: Optional[str] = None

    def is_valid_action(self) -> bool:
        return self.action_type in ALLOWED_ACTIONS


class Reward(BaseModel):
    value: float
    breakdown: Dict[str, Any]
