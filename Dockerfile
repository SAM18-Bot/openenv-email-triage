FROM python:3.11-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS runtime
COPY . .
EXPOSE 7860
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "7860"]
