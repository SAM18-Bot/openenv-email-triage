from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List, Optional, Tuple

from src.email_generator import EmailGenerator
from src.models import Action, Observation, Reward
from src.reward import compute_step_reward, compute_terminal_bonus


class EmailTriageOpenEnv:
    def __init__(self, max_steps: int = 50, queue_limit: int = 100, time_budget: int = 35) -> None:
        self.max_steps = max_steps
        self.queue_limit = queue_limit
        self.time_budget = time_budget
        self.generator = EmailGenerator()
        self.reset()

    def _to_observation(self, email: Dict) -> Observation:
        return Observation(
            email_id=email["email_id"],
            sender=email["sender"],
            subject=email["subject"],
            body=email["body"],
            urgency=float(email["urgency"]),
            category=email["category"],
            inbox_size=len(self.queue),
            time_budget_remaining=max(self.time_budget - self.step_count, 0),
            step=self.step_count,
        )

    def _current_email(self) -> Dict:
        if not self.queue:
            self.queue.extend(self.generator.poisson_new_emails(lam=2.0, cap=3) or [self.generator.sample_email()])
        return self.queue[0]

    def reset(self, seed: Optional[int] = None) -> Observation:
        self.generator = EmailGenerator(seed=seed)
        self.queue: Deque[Dict] = deque()
        self.step_count = 0
        self.done = False
        self.handled_count = 0
        self.trajectory: List[Dict] = []
        self.total_reward = 0.0

        initial_count = 5 if seed is None else 5 + (seed % 6)
        for _ in range(initial_count):
            self.queue.append(self.generator.sample_email())

        return self._to_observation(self._current_email())

    def step(self, action: Action | Dict) -> Tuple[Observation, Reward, bool, Dict]:
        if self.done:
            obs = self._to_observation(self._current_email())
            return obs, Reward(value=0.0, breakdown={"message": "episode_done"}), True, self.state()

        parsed_action = action if isinstance(action, Action) else Action(**action)
        if not parsed_action.is_valid_action():
            parsed_action = Action(action_type="read", confidence=0.0, reason="invalid action fallback")

        current = self._current_email()
        self.step_count += 1
        self.handled_count += 1

        step_breakdown = compute_step_reward(
            urgency=current["urgency"],
            category=current["category"],
            action_type=parsed_action.action_type,
            step=self.step_count,
            time_budget=self.time_budget,
        )

        self.trajectory.append(
            {
                "email": current,
                "action": parsed_action.action_type,
                "step": self.step_count,
                "time_budget": self.time_budget,
                "confidence": parsed_action.confidence,
            }
        )

        self.queue.popleft()
        self.queue.extend(self.generator.poisson_new_emails(lam=1.3, cap=3))

        self.done = self.step_count >= self.max_steps or len(self.queue) > self.queue_limit
        terminal_breakdown = {"total": 0.0}
        if self.done:
            throughput = self.handled_count / self.max_steps
            satisfaction = self._satisfaction_proxy()
            terminal_breakdown = compute_terminal_bonus(throughput=throughput, satisfaction=satisfaction)

        total = step_breakdown["total"] + terminal_breakdown["total"]
        self.total_reward += total

        obs = self._to_observation(self._current_email())
        reward = Reward(value=total, breakdown={"step": step_breakdown, "terminal": terminal_breakdown})
        return obs, reward, self.done, self.state()

    def _satisfaction_proxy(self) -> float:
        if not self.trajectory:
            return 0.0
        positive = 0
        for row in self.trajectory:
            urgency = row["email"]["urgency"]
            action = row["action"]
            if urgency > 0.7 and action in {"flag", "respond", "delegate"}:
                positive += 1
            elif urgency <= 0.7 and action != "skip":
                positive += 1
        return positive / len(self.trajectory)

    def state(self) -> Dict:
        high = sum(1 for x in self.queue if x["urgency"] > 0.7)
        medium = sum(1 for x in self.queue if 0.3 < x["urgency"] <= 0.7)
        low = sum(1 for x in self.queue if x["urgency"] <= 0.3)
        return {
            "step": self.step_count,
            "done": self.done,
            "queue_size": len(self.queue),
            "queue_tiers": {"high": high, "medium": medium, "low": low},
            "time_budget": self.time_budget,
            "time_budget_remaining": max(self.time_budget - self.step_count, 0),
            "handled_count": self.handled_count,
            "total_reward": self.total_reward,
            "trajectory": self.trajectory,
        }
