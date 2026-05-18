#!/usr/bin/env python3
"""Cloudflare bypass proxy for hanime-server using cloudscraper (no browser needed)."""

import os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import cloudscraper

LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "7789"))
PROXY_URL = os.environ.get("PROXY_URL", "")

_scraper = None


def get_scraper():
    global _scraper
    if _scraper is None:
        s = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "desktop": True, "mobile": False},
            interpreter="js2py",
        )
        if PROXY_URL:
            s.proxies.update({"http": PROXY_URL, "https": PROXY_URL})
        _scraper = s
    return _scraper


class Handler(BaseHTTPRequestHandler):
    def _target_url(self):
        host = self.headers.get("x-hostname", "")
        return None if not host else f"https://{host}{self.path or '/'}"

    def _request(self, method):
        url = self._target_url()
        if not url:
            return self.send_error(400, "Missing x-hostname header")
        try:
            scraper = get_scraper()
            force = self.headers.get("x-bypass-cache", "") == "true"
            if force:
                scraper.cookies.clear()

            body = None
            if method == "POST":
                clen = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(clen) if clen else None

            resp = getattr(scraper, method.lower())(url, data=body, timeout=120, allow_redirects=True)

            self.send_response(resp.status_code)
            for h in ["content-type", "content-length", "cache-control"]:
                if h in resp.headers:
                    self.send_header(h, resp.headers[h])
            self.end_headers()
            self.wfile.write(resp.content)
        except Exception as e:
            self.send_error(502, f"cloudscraper error: {e}")

    def do_GET(self):
        self._request("GET")

    def do_POST(self):
        self._request("POST")

    def log_message(self, fmt, *args):
        sys.stderr.write("[flare-adapter] " + fmt % args + "
")


def main():
    get_scraper()
    srv = HTTPServer(("0.0.0.0", LISTEN_PORT), Handler)
    print(f"[flare-adapter] Listening on 0.0.0.0:{LISTEN_PORT}  proxy={PROXY_URL or 'none'}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
