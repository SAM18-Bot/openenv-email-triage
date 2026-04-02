from __future__ import annotations

import json
import os
from typing import Dict

from openai import OpenAI

from src.environment import EmailTriageOpenEnv
from src.graders import grade_task_easy, grade_task_hard, grade_task_medium
from src.models import Action

SYSTEM_PROMPT = (
    "You are managing an email inbox. Given the current email, choose the best action. "
    "Reply with JSON: {\"action_type\":\"...\",\"confidence\":0.0}."
)

GEMINI_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def choose_action(client: OpenAI, model_name: str, observation: Dict) -> Action:
    user_prompt = json.dumps(observation)
    try:
        response = client.chat.completions.create(
            model=model_name,
            temperature=0.0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        action = Action(**parsed)
        if not action.is_valid_action():
            raise ValueError("invalid action")
        return action
    except Exception:
        urgency = float(observation.get("urgency", 0.0))
        category = observation.get("category", "internal")
        if urgency > 0.7:
            return Action(action_type="flag", confidence=0.75, reason="heuristic urgent")
        if category == "spam":
            return Action(action_type="archive", confidence=0.7, reason="heuristic spam")
        return Action(action_type="read", confidence=0.6, reason="heuristic default")


def run_task(task_name: str, grader_fn, client: OpenAI, model_name: str, api_base_url: str) -> float:
    env = EmailTriageOpenEnv(max_steps=50)
    obs = env.reset(seed=42)
    done = False

    print(
        f"[START] task_id={task_name} model={model_name} base_url={api_base_url} "
        f"max_steps={env.max_steps} seed=42"
    )

    while not done:
        action = choose_action(client, model_name, obs.model_dump())
        obs, reward, done, _ = env.step(action)
        print(
            f"[STEP] task_id={task_name} step={obs.step} action_type={action.action_type} "
            f"confidence={action.confidence:.3f} reward={reward.value:.3f} done={str(done).lower()}"
        )

    score = grader_fn(env.trajectory)
    print(f"[END] task_id={task_name} steps={env.step_count} score={score:.4f}")
    return score


def _resolve_client_config() -> tuple[str, str, str]:
    hf_token = os.environ.get("HF_TOKEN", "")
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

    api_key = hf_token or openai_api_key or gemini_api_key

    explicit_base_url = os.environ.get("API_BASE_URL", "").strip()
    if explicit_base_url:
        api_base_url = explicit_base_url
    elif gemini_api_key and not (hf_token or openai_api_key):
        api_base_url = GEMINI_OPENAI_BASE_URL
    else:
        api_base_url = "https://api.openai.com/v1"

    explicit_model = os.environ.get("MODEL_NAME", "").strip()
    if explicit_model:
        model_name = explicit_model
    elif api_base_url.rstrip("/") == GEMINI_OPENAI_BASE_URL.rstrip("/"):
        model_name = "gemini-2.0-flash"
    else:
        model_name = "gpt-4o-mini"

    return api_base_url, model_name, api_key


def main() -> None:
    api_base_url, model_name, api_key = _resolve_client_config()
    client = OpenAI(base_url=api_base_url, api_key=api_key)

    tasks = [
        ("task_urgent_detection", grade_task_easy),
        ("task_efficient_processing", grade_task_medium),
        ("task_holistic_management", grade_task_hard),
    ]

    for task_id, grader in tasks:
        score = run_task(task_id, grader, client, model_name, api_base_url)
        print(f"{task_id}: {score:.4f}")


if __name__ == "__main__":
    main()
