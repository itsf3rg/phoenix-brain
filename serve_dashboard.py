import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "dashboard"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    # Allow CORS so the dashboard can talk to the Uvicorn Brain on port 8000
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving Dashboard UI at http://localhost:{PORT}")
    httpd.serve_forever()
