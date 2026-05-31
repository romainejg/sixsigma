"""Application configuration and environment helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DATABASE_PATH = BASE_DIR / "data" / "app.db"


def get_api_key() -> Optional[str]:
    """Return API key from environment first, then Streamlit secrets."""
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key

    try:
        import streamlit as st

        secret_key = st.secrets.get("OPENAI_API_KEY")
        if secret_key:
            return str(secret_key)
    except Exception:
        return None

    return None


def get_mock_mode() -> bool:
    """Enable mock mode when API key is missing or explicitly requested."""
    explicit = os.getenv("MOCK_MODE", "").strip().lower()
    if explicit in {"1", "true", "yes", "on"}:
        return True
    if explicit in {"0", "false", "no", "off"}:
        return False
    return get_api_key() is None


MOCK_MODE = get_mock_mode()
