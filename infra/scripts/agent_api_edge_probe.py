#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding


PROBE_LOG_PATH = Path("/tmp/agent-api-probe.log")
REVOKED_FINGERPRINT = os.environ["REVOKED_FINGERPRINT_SHA256"]


class AgentApiProbeHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def do_GET(self) -> None:  # noqa: N802
        self._respond()

    def do_POST(self) -> None:  # noqa: N802
        self._respond()

    def do_PUT(self) -> None:  # noqa: N802
        self._respond()

    def do_DELETE(self) -> None:  # noqa: N802
        self._respond()

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        return

    def _respond(self) -> None:
        escaped_certificate = self.headers.get("X-Agent-Client-Certificate", "")
        status = 204 if not escaped_certificate else 400
        fingerprint = "missing"
        if escaped_certificate:
            try:
                certificate = x509.load_pem_x509_certificate(unquote(escaped_certificate).encode())
                fingerprint = hashlib.sha256(certificate.public_bytes(Encoding.DER)).hexdigest()
                status = 401 if fingerprint == REVOKED_FINGERPRINT else 200
            except ValueError:
                fingerprint = "invalid"

        with PROBE_LOG_PATH.open("a", encoding="utf-8") as probe_log:
            probe_log.write(f"{self.command} {self.path} {fingerprint} {status}\n")
        body = b"" if status == 204 else json.dumps({"status": status}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    PROBE_LOG_PATH.unlink(missing_ok=True)
    with ThreadingHTTPServer(("0.0.0.0", 8080), AgentApiProbeHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
