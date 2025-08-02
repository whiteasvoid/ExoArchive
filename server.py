import http.server
import socketserver
import os
import json
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
import requests
from http.cookies import SimpleCookie
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
BUNGIE_API_KEY = os.getenv("BUNGIE_API_KEY")
BUNGIE_CLIENT_ID = os.getenv("BUNGIE_CLIENT_ID")
BUNGIE_CLIENT_SECRET = os.getenv("BUNGIE_CLIENT_SECRET")

PORT = 8000
# Define the web directory relative to the script file
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web')

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom request handler to serve static files and handle API requests.
    """
    def __init__(self, *args, **kwargs):
        # Initialize the handler to serve files from the WEB_DIR directory
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        """
        Handle GET requests.
        - If the path is /login, serve the login.html file.
        - If the path is /api/oauth-client-id, return the client ID.
        - If the path starts with /callback, handle the OAuth callback.
        - If the path starts with /api/proxy, forward the request to the Bungie API.
        - Otherwise, serve static files.
        """
        parsed_path = urlparse(self.path).path

        if parsed_path == '/login':
            self.path = '/login.html'
            super().do_GET()
        elif parsed_path == '/profile':
            self.path = '/profile.html'
            super().do_GET()
        elif parsed_path == '/api/oauth-client-id':
            self._handle_oauth_client_id_request()
        elif parsed_path == '/callback':
            self._handle_callback_request()
        elif parsed_path == '/api/user':
            self._handle_user_api_request()
        elif parsed_path == '/api/logout':
            self._handle_logout_request()
        elif parsed_path.startswith('/api/proxy'):
            self._handle_proxy_request()
        else:
            super().do_GET()

    def _handle_user_api_request(self):
        """Handles requests to the /api/user endpoint."""

        # Check if the user is authenticated by looking for an access token in cookies
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            if 'access_token' in cookie:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'authenticated': True}).encode('utf-8'))
                return

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'authenticated': False}).encode('utf-8'))

    def _handle_logout_request(self):
        """Handles the /api/logout endpoint."""

        # Clear the access token by setting an empty cookie with an expired date
        cookie = SimpleCookie()
        cookie['access_token'] = ''
        cookie['access_token']['expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        cookie['access_token']['path'] = '/'
        
        # Send a response indicating the user has been logged out
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Set-Cookie', cookie['access_token'].OutputString())
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'logged_out'}).encode('utf-8'))

    def _handle_oauth_client_id_request(self):
        """Sends the Bungie client ID as JSON."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'clientId': BUNGIE_CLIENT_ID}).encode('utf-8'))

    def _handle_callback_request(self):
        """Handles the OAuth callback from Bungie."""
        query_components = parse_qs(urlparse(self.path).query)
        code = query_components.get('code', [None])[0]

        if not code:
            self._redirect_to_callback_page(status='error', error='No authorization code received.')
            return

        try:
            # Exchange the authorization code for an access token
            token_url = 'https://www.bungie.net/platform/app/oauth/token/'
            payload = {
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': BUNGIE_CLIENT_ID,
                'client_secret': BUNGIE_CLIENT_SECRET,
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            
            response = requests.post(token_url, data=payload, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data.get('access_token')
            
            # Set the access token in a HttpOnly cookie
            cookie = SimpleCookie()
            cookie['access_token'] = access_token
            cookie['access_token']['expires'] = (datetime.utcnow() + timedelta(hours=1)).strftime("%a, %d %b %Y %H:%M:%S GMT")
            cookie['access_token']['path'] = '/'
            cookie['access_token']['httponly'] = True
            cookie['access_token']['secure'] = True

            self._redirect_to_callback_page(status='success', extra_headers=[('Set-Cookie', cookie['access_token'].OutputString())])

        except requests.exceptions.RequestException as e:
            error_message = f"Token exchange failed: {e}"
            if e.response:
                error_message += f" - {e.response.text}"
            print(error_message)
            self._redirect_to_callback_page(status='error', error=str(e))

    def _redirect_to_callback_page(self, status, error=None, extra_headers=None):
        """Redirects the user to the callback.html page with status parameters."""
        redirect_url = f'/callback.html?status={status}'
        if error:
            from urllib.parse import quote
            redirect_url += f'&error={quote(error)}'
        
        self.send_response(302)
        self.send_header('Location', redirect_url)
        if extra_headers:
            for key, value in extra_headers:
                self.send_header(key, value)
        self.end_headers()

    def _handle_proxy_request(self):
        """Handles proxying requests to the Bungie API."""
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
            
            # Add the user's access token to the request if it exists in the cookies
            cookie_header = self.headers.get('Cookie')
            if cookie_header:
                cookie = SimpleCookie()
                cookie.load(cookie_header)
                if 'access_token' in cookie:
                    access_token = cookie['access_token'].value
                    headers['Authorization'] = f'Bearer {access_token}'

            response = requests.get(bungie_url, headers=headers)
            
            # If the token is invalid or expired, Bungie returns a 401
            if response.status_code == 401:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode('utf-8'))
                return

            response.raise_for_status()

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
    import ssl

    # Use a TCP server to handle requests
    httpd = socketserver.TCPServer(("", PORT), CustomHandler)

    # --- SSL/HTTPS Setup ---
    # README.md contains instructions on how to generate the required key.pem and cert.pem files.
    key_path = os.path.join("certs", "key.pem")
    cert_path = os.path.join("certs", "cert.pem")

    if os.path.exists(key_path) and os.path.exists(cert_path):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        print(f"Serving at https://localhost:{PORT}")
    else:
        print("---")
        print("WARNING: Could not find key.pem and cert.pem.")
        print("The server will run on HTTP, but Bungie authentication requires HTTPS.")
        print("Generate a self-signed certificate to enable HTTPS.")
        print("---")
        print(f"Serving at http://localhost:{PORT}")

    # Start the server and keep it running until interrupted
    httpd.serve_forever()
