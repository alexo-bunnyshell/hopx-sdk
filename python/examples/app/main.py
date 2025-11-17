#!/usr/bin/env python3
"""
Simple web app for template building example
"""
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.environ.get("PORT", 8000))

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hello from Hopx template!")

    def log_message(self, format, *args):
        pass  # Suppress logs

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), SimpleHandler)
    print(f"Server running on port {PORT}")
    server.serve_forever()
