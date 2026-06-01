import os

import pytest
import requests
from dotenv import load_dotenv

from myfeedmemory.auth import linkedinoauth

load_dotenv(override=False)


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(f"Skip LinkedIn integration test because {name} is not set")
    return value


def test_linkedin_authorization_endpoint_reachable():
    _require_env("LINKEDIN_CLIENT_ID")
    _require_env("LINKEDIN_REDIRECT_URI")

    scopes = os.getenv("LINKEDIN_SCOPES", "openid profile email")
    state = os.getenv("LINKEDIN_TEST_STATE", "pytest-state")

    url = linkedinoauth.build_authorization_url(state=state, scopes=scopes)
    response = requests.get(url, allow_redirects=False, timeout=30)

    assert response.status_code in {200, 302, 303, 307}

    body = response.text.lower()
    assert "invalid_scope_error" not in body
    assert "redirect_uri" not in body or "mismatch" not in body
    assert "the requested permission scope is not valid" not in body


def test_linkedin_token_exchange_manual():
    _require_env("LINKEDIN_CLIENT_ID")
    _require_env("LINKEDIN_CLIENT_SECRET")
    _require_env("LINKEDIN_REDIRECT_URI")

    auth_code = os.getenv("LINKEDIN_AUTH_CODE")
    if not auth_code:
        pytest.skip("Skip manual token exchange because LINKEDIN_AUTH_CODE is not set")

    token_resp = linkedinoauth.get_access_token_response(auth_code)
    assert "access_token" in token_resp
    assert int(token_resp.get("expires_in", 0)) > 0
