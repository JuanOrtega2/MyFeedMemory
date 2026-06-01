import argparse
import json
import os
import socketserver
import threading
import urllib.parse
import http.server
from typing import Tuple

from dotenv import load_dotenv

from myfeedmemory.auth import linkedinoauth

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
DEFAULT_SCOPES = "openid profile email"


def ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def save_tokens(tokens: dict) -> None:
    ensure_data_dir()
    path = os.path.join(DATA_DIR, "linkedin_tokens.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2)


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        params = urllib.parse.parse_qs(parsed.query)
        error = params.get("error", [None])[0]
        error_description = params.get("error_description", [None])[0]
        code = params.get("code", [None])[0]

        if error:
            self.send_plain_text(400, f"OAuth error: {error}: {error_description}")
            self.server.auth_error = f"{error}: {error_description}"
            self.server.shutdown()
            return

        if not code:
            self.send_plain_text(400, "Missing authorization code in callback.")
            self.server.auth_error = "Missing authorization code in callback."
            self.server.shutdown()
            return

        state = params.get("state", [None])[0]
        if self.server.auth_state and state != self.server.auth_state:
            self.send_plain_text(400, "State mismatch in callback.")
            self.server.auth_error = "State mismatch in callback."
            self.server.shutdown()
            return

        try:
            token_resp = linkedinoauth.get_access_token_response(code)
            access_token = token_resp.get("access_token")
            userinfo = linkedinoauth.get_userinfo(access_token) if access_token else {}
            save_tokens({**token_resp, "userinfo": userinfo})
            self.send_plain_text(200, "Authentication succeeded. Tokens saved.")
            self.server.auth_result = {"tokens": token_resp, "userinfo": userinfo}
        except Exception as exc:
            self.send_plain_text(500, f"Token exchange failed: {exc}")
            self.server.auth_error = str(exc)
        finally:
            self.server.shutdown()

    def send_plain_text(self, status: int, message: str) -> None:
        payload = message.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def run_local_server(
    port: int, state: str
) -> Tuple[threading.Thread, socketserver.TCPServer]:
    handler = CallbackHandler
    httpd = ReusableTCPServer(("localhost", port), handler)
    httpd.auth_state = state
    httpd.auth_result = None
    httpd.auth_error = None
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return thread, httpd


def main(print_only: bool = False, port: int = 8000, scopes: str = DEFAULT_SCOPES):
    load_dotenv(override=False)
    try:
        linkedinoauth.get_env_variable("LINKEDIN_CLIENT_ID")
        linkedinoauth.get_env_variable("LINKEDIN_CLIENT_SECRET")
        linkedinoauth.get_env_variable("LINKEDIN_REDIRECT_URI")
    except RuntimeError as e:
        print("Missing LinkedIn environment configuration:", e)
        print(
            "Set LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, and LINKEDIN_REDIRECT_URI."
        )
        return

    normalized_scopes = linkedinoauth.normalize_scopes(scopes)
    state = os.urandom(16).hex()
    auth_url = linkedinoauth.build_authorization_url(
        state=state, scopes=normalized_scopes
    )

    print("Open this URL in a browser to authorize:")
    print(auth_url)

    if not print_only:
        try:
            import webbrowser

            webbrowser.open(auth_url)
        except Exception:
            pass

    thread, httpd = run_local_server(port, state)
    print(f"Waiting for callback on http://localhost:{port}/callback")

    try:
        thread.join()
    except KeyboardInterrupt:
        httpd.shutdown()
        print("Server stopped by user.")
        return

    if httpd.auth_error:
        print("Authentication failed:", httpd.auth_error)
    else:
        print("Authentication succeeded.")
        tokens = httpd.auth_result["tokens"] if httpd.auth_result else {}
        if tokens:
            print("Access token saved. Expires in:", tokens.get("expires_in"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print the authorization URL and do not open the browser",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Local callback server port"
    )
    parser.add_argument(
        "--scopes", type=str, default=DEFAULT_SCOPES, help="Space-separated scopes"
    )
    args = parser.parse_args()
    main(print_only=args.print_only, port=args.port, scopes=args.scopes)
