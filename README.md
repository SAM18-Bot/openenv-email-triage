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

## API keys and environment variables
You need two tokens depending on how you run:

1. `HF_TOKEN`
   - Create/get this from your Hugging Face account settings (Access Tokens).
   - Used for Hugging Face Space/private resource access in deployments.
2. `OPENAI_API_KEY` (or set same value in `HF_TOKEN` if you route OpenAI through that variable)
   - Create/get this from your OpenAI account API keys page.
   - Used by `inference.py` through the OpenAI Python client.

`inference.py` reads:
- `API_BASE_URL` (default: `https://api.openai.com/v1`)
- `MODEL_NAME` (default: `gpt-4o-mini`)
- `HF_TOKEN` (primary api key value in this baseline)

### Example env setup
```bash
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4o-mini
export OPENAI_API_KEY=sk-...
export HF_TOKEN=$OPENAI_API_KEY
```

## Install and run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.api:app --host 0.0.0.0 --port 7860
```

## Run baseline
```bash
python inference.py
```

## Run tests
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Notes:
- `pytest.ini` sets `pythonpath = .`, so imports like `from src...` resolve without manually exporting `PYTHONPATH`.
- If you are behind a proxy/firewall, package install may fail until proxy settings are configured.

## Docker
```bash
docker build -t openenv-email-triage .
docker run -p 7860:7860 openenv-email-triage
```
