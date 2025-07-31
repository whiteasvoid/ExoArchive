import http.server
import socketserver
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
BUNGIE_API_KEY = os.getenv("BUNGIE_API_KEY")

PORT = 8000
# Define the web directory relative to the script file
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web')

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom request handler to serve static files and the API key.
    """
    def __init__(self, *args, **kwargs):
        # Initialize the handler to serve files from the WEB_DIR directory
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        """
        Handle GET requests.
        - If the path is /api/config, return the API key.
        - If the path starts with /api/proxy, forward the request to the Bungie API.
        - Otherwise, serve static files.
        """
        if self.path == '/api/config':
            self._handle_api_config()
        elif self.path.startswith('/api/proxy'):
            self._handle_proxy_request()
        else:
            super().do_GET()

    def _handle_api_config(self):
        """Handles serving the API key."""
        if not BUNGIE_API_KEY:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'API key not configured.'}).encode('utf-8'))
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'apiKey': BUNGIE_API_KEY}).encode('utf-8'))

    def _handle_proxy_request(self):
        """Handles proxying requests to the Bungie API."""
        from urllib.parse import urlparse, parse_qs
        import requests

        query_components = parse_qs(urlparse(self.path).query)
        bungie_url = query_components.get('url', [None])[0]

        if not bungie_url:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Missing "url" query parameter.'}).encode('utf-8'))
            return

        if not BUNGIE_API_KEY:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'API key not configured on the server.'}).encode('utf-8'))
            return

        try:
            headers = {'X-API-Key': BUNGIE_API_KEY}
            response = requests.get(bungie_url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes

            self.send_response(response.status_code)
            self.send_header('Content-type', response.headers['Content-Type'])
            self.end_headers()
            self.wfile.write(response.content)

        except requests.exceptions.RequestException as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

# --- Main execution ---
if __name__ == "__main__":
    # Use a TCP server to handle requests
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        # Start the server and keep it running until interrupted
        httpd.serve_forever()
