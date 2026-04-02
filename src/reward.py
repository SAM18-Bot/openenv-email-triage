from __future__ import annotations

from typing import Dict


def compute_step_reward(
    urgency: float,
    category: str,
    action_type: str,
    step: int,
    time_budget: int,
) -> Dict[str, float]:
    score = 0.0
    breakdown = {
        "urgent_correct": 0.0,
        "normal_correct": 0.0,
        "urgent_missed": 0.0,
        "time_penalty": 0.0,
    }

    urgent = urgency > 0.7
    if urgent and action_type in {"flag", "respond", "delegate"}:
        breakdown["urgent_correct"] = 0.5
    elif urgent and action_type in {"skip", "archive"}:
        breakdown["urgent_missed"] = -0.8
    elif not urgent:
        if category == "spam" and action_type == "archive":
            breakdown["normal_correct"] = 0.2
        elif category != "spam" and action_type in {"read", "respond", "delegate", "flag"}:
            breakdown["normal_correct"] = 0.2

    if step > time_budget:
        breakdown["time_penalty"] = -0.1

    score = sum(breakdown.values())
    breakdown["total"] = score
    return breakdown


def compute_terminal_bonus(throughput: float, satisfaction: float) -> Dict[str, float]:
    result = {"throughput_bonus": 0.0, "satisfaction_penalty": 0.0}
    if throughput > 0.7:
        result["throughput_bonus"] = 2.0
    if satisfaction < 0.5:
        result["satisfaction_penalty"] = -1.5
    result["total"] = result["throughput_bonus"] + result["satisfaction_penalty"]
    return result
