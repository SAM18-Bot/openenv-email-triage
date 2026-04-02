from __future__ import annotations

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from src.environment import EmailTriageOpenEnv
from src.models import Action

app = FastAPI(title="OpenEnv Email Triage")
env = EmailTriageOpenEnv()


class ResetRequest(BaseModel):
    seed: Optional[int] = None


@app.get("/")
def root():
    return {
        "name": "openenv-email-triage",
        "status": "ok",
        "endpoints": ["/reset", "/step", "/state"],
    }


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/reset")
def reset(payload: ResetRequest | None = None):
    seed = payload.seed if payload else None
    obs = env.reset(seed=seed)
    return obs.model_dump()


@app.post("/step")
def step(action: Action):
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info,
    }


@app.get("/state")
def state():
    return env.state()
