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
        If the path is /api/config, return the API key.
        Otherwise, serve static files as usual.
        """
        if self.path == '/api/config':
            if not BUNGIE_API_KEY:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {'error': 'API key not configured on the server.'}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # Create a dictionary to hold the API key
            config = {'apiKey': BUNGIE_API_KEY}
            # Write the JSON response
            self.wfile.write(json.dumps(config).encode('utf-8'))
        else:
            # For any other path, fall back to the default behavior
            # which serves files from the directory specified in the constructor.
            super().do_GET()

# --- Main execution ---
if __name__ == "__main__":
    # Use a TCP server to handle requests
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        # Start the server and keep it running until interrupted
        httpd.serve_forever()
