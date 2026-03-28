# openenv-email-triage

OpenEnv hackathon submission: a realistic reinforcement-learning environment for email inbox triage.

## Overview
- Simulates stochastic email arrivals via Poisson process.
- Supports three tasks (easy/medium/hard) with deterministic graders in [0, 1].
- Exposes FastAPI endpoints:
  - `POST /reset`
  - `POST /step`
  - `GET /state`

## Action Space
`read`, `archive`, `flag`, `respond`, `delegate`, `skip`

## Observation Keys
`email_id`, `sender`, `subject`, `body`, `urgency`, `category`, `inbox_size`, `time_budget_remaining`, `step`

## Run locally
```bash
pip install -r requirements.txt
uvicorn src.api:app --host 0.0.0.0 --port 7860
```

## Run baseline
```bash
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o-mini
export HF_TOKEN=$OPENAI_API_KEY
python inference.py
```

## Docker
```bash
docker build -t openenv-email-triage .
docker run -p 7860:7860 openenv-email-triage
```
