# Auto-generated hardware hook (no network calls). 2025-08-17T03:39:27Z
import os
from typing import Optional, Dict


def load_token(env_var: str) -> Optional[str]:
    tok = os.environ.get(env_var, "").strip()
    return tok or None


def client_info(name: str, env_var: str) -> Dict[str, str]:
    return {
        "backend": name,
        "token_present": "yes" if load_token(env_var) else "no",
        "env_var": env_var,
        "activation": "disabled",  # DO NOT ACTIVATE
    }


# IONQ_API_TOKEN
