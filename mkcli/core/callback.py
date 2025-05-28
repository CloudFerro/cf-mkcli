import requests
import threading
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass
from typing import Optional, Self

# NOTE(EA): this code comes from https://gitlab.cloudferro.com/jtompolski/CFCliV4


@dataclass
class CallbackState:
    code: Optional[str] = None


class HandleOpenIDCallback(BaseHTTPRequestHandler):
    state: CallbackState = CallbackState()

    def _send_response(self, status_code: int, message: str = ""):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        if message:
            self.wfile.write(message.encode())

    def _handle_favicon(self) -> None:
        """Handle favicon.ico requests"""
        # Send a minimal 1x1 transparent ICO file
        favicon = bytes.fromhex("00000100010001000000000000000000")
        self._send_response(200, favicon, "image/x-icon")

    def do_GET(self):
        if self.path == "/ready":
            self._send_response(200, "ready")
            return
        if not self.path.startswith("/callback"):
            self._send_response(400, "Not found")
            return

        try:
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            code = qs.get("code", [None])[0]

            if code:
                self.state.code = code
                self._send_response(200, "Authentication code received")
            else:
                self._send_response(400, "Missing auth code")
                self.send_response(400)
        except Exception as e:
            self.send_response(500, f"Internal server error: {str(e)}")

    def log_message(self, format, *args):
        """Supress logging of requests to the console"""
        pass


class CallbackServer:
    def __init__(self, host: str = "localhost", port: int = 3333):
        self.host = host
        self.port = port
        self.handler = HandleOpenIDCallback
        self.httpd = HTTPServer((self.host, self.port), self.handler)
        self.t = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def start(self) -> None:
        self.t.start()

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def ready(self) -> bool:
        try:
            res = requests.get(f"{self.base_url}/ready")
            return res.status_code == 200
        except requests.RequestException:
            return False

    @property
    def access_code(self) -> Optional[str]:
        return self.handler.state.code

    def called(self) -> bool:
        return self.access_code is not None
