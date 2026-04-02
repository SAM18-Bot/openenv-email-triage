from __future__ import annotations

import os

import uvicorn

from src.api import app


def main() -> None:
    """Run the API server for local and multi-mode deployments."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run("server.app:app", host=host, port=port)
