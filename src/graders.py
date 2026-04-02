from __future__ import annotations

from typing import Dict, List


def _safe_div(n: float, d: float) -> float:
    return n / d if d else 0.0


def grade_task_easy(trajectory: List[Dict]) -> float:
    predicted_positive = 0
    true_positive = 0
    actual_positive = 0
    for row in trajectory:
        urgent = row["email"]["urgency"] > 0.7
        flagged = row["action"] == "flag"
        predicted_positive += int(flagged)
        actual_positive += int(urgent)
        true_positive += int(urgent and flagged)
    precision = _safe_div(true_positive, predicted_positive)
    recall = _safe_div(true_positive, actual_positive)
    return max(0.0, min(1.0, precision * recall))


def grade_task_medium(trajectory: List[Dict]) -> float:
    if not trajectory:
        return 0.0
    correctly_handled = 0
    spam_total = 0
    spam_mis = 0
    for row in trajectory:
        email = row["email"]
        action = row["action"]
        if email["category"] == "spam":
            spam_total += 1
            if action != "archive":
                spam_mis += 1
        if email["urgency"] > 0.7 and action in {"flag", "respond", "delegate"}:
            correctly_handled += 1
        elif email["category"] == "spam" and action == "archive":
            correctly_handled += 1
        elif email["category"] not in {"spam"} and action in {"read", "respond", "delegate", "flag"}:
            correctly_handled += 1
    correct_rate = _safe_div(correctly_handled, len(trajectory))
    spam_leak = _safe_div(spam_mis, spam_total)
    return max(0.0, min(1.0, correct_rate * (1 - spam_leak)))


def grade_task_hard(trajectory: List[Dict]) -> float:
    if not trajectory:
        return 0.0

    tp = fp = fn = 0
    important_total = 0
    important_handled = 0
    over_budget_steps = 0

    for row in trajectory:
        email = row["email"]
        action = row["action"]
        step = row["step"]
        time_budget = row["time_budget"]
        urgent = email["urgency"] > 0.7
        important = email["category"] in {"support", "billing", "urgent_alert"}

        predicted_urgent_action = action in {"flag", "respond", "delegate"}
        if urgent and predicted_urgent_action:
            tp += 1
        elif not urgent and predicted_urgent_action:
            fp += 1
        elif urgent and not predicted_urgent_action:
            fn += 1

        important_total += int(important)
        if important and action in {"respond", "delegate", "flag", "read"}:
            important_handled += 1

        if step > time_budget:
            over_budget_steps += 1

    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    urgency_f1 = _safe_div(2 * precision * recall, precision + recall)
    importance_recall = _safe_div(important_handled, important_total)
    time_penalty = min(1.0, over_budget_steps / max(1, len(trajectory)))

    score = urgency_f1 * importance_recall * (1 - time_penalty)
    return max(0.0, min(1.0, score))
