import os
import urllib.parse
from typing import Dict

from dotenv import load_dotenv

LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
OPENID_SCOPES = "openid profile email"
LEGACY_SCOPE_ALIASES = {"r_liteprofile", "r_emailaddress", "w_member_social"}


def load_environment() -> None:
    load_dotenv(override=False)


def get_env_variable(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def normalize_scopes(scopes: str) -> str:
    requested = {
        item.strip().lower() for item in (scopes or "").split() if item.strip()
    }
    if not requested:
        return OPENID_SCOPES

    requested -= LEGACY_SCOPE_ALIASES
    requested.update({"openid", "profile", "email"})

    normalized = [
        scope for scope in ("openid", "profile", "email") if scope in requested
    ]
    return " ".join(normalized) if normalized else OPENID_SCOPES


def build_authorization_url(state: str, scopes: str) -> str:
    params = {
        "response_type": "code",
        "client_id": get_env_variable("LINKEDIN_CLIENT_ID"),
        "redirect_uri": get_env_variable("LINKEDIN_REDIRECT_URI"),
        "scope": normalize_scopes(scopes),
        "state": state,
    }
    return f"{LINKEDIN_AUTH_URL}?{urllib.parse.urlencode(params)}"


def get_userinfo(access_token: str) -> Dict[str, object]:
    import requests

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        "https://api.linkedin.com/v2/userinfo", headers=headers, timeout=20
    )
    response.raise_for_status()
    return response.json()


def token_request_payload(code: str) -> Dict[str, str]:
    return {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": get_env_variable("LINKEDIN_REDIRECT_URI"),
        "client_id": get_env_variable("LINKEDIN_CLIENT_ID"),
        "client_secret": get_env_variable("LINKEDIN_CLIENT_SECRET"),
    }


def get_access_token_response(code: str) -> Dict[str, object]:
    import requests

    payload = token_request_payload(code)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(
        LINKEDIN_TOKEN_URL, data=payload, headers=headers, timeout=20
    )
    response.raise_for_status()
    return response.json()
