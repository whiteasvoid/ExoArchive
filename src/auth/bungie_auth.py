import webbrowser
import requests
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("BUNGIE_CLIENT_ID")
CLIENT_SECRET = os.getenv("BUNGIE_CLIENT_SECRET") # Required for confidential clients to refresh tokens
API_KEY = os.getenv("BUNGIE_API_KEY")

# Ensure these are set in your .env file or environment variables
if not CLIENT_ID or not API_KEY:
    raise ValueError("BUNGIE_CLIENT_ID and BUNGIE_API_KEY must be set in .env or environment variables")

AUTH_URL = "https://www.bungie.net/en/oauth/authorize"
TOKEN_URL = "https://www.bungie.net/platform/app/oauth/token/"
# This should be a URL that your application controls and can handle the redirect
REDIRECT_URI = "https://localhost:8000/callback" # Example, replace with your actual redirect URI

def get_authorization_url():
    """Generates the authorization URL for the user to navigate to."""
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        # "state": "YOUR_CSRF_TOKEN" # Optional: Add CSRF protection
    }
    # According to Bungie docs, scope should not be included in the auth request,
    # it's defined in the application portal.
    # However, if specific scopes are needed beyond the default, this is where they'd be added.
    # params["scope"] = "ReadDestinyInventoryAndVault MoveEquipDestinyItems"

    # Construct URL with query parameters
    auth_request = requests.Request('GET', AUTH_URL, params=params).prepare()
    return auth_request.url

def request_token(authorization_code):
    """Exchanges an authorization code for an access token."""
    payload = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": CLIENT_ID,
        # For public clients, client_secret is not sent.
        # For confidential clients, it's required for token refresh but might be optional here
        # depending on client type registration with Bungie.
        # "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-API-Key": API_KEY  # Added X-API-Key header
    }
    # If it's a confidential client and client_secret is to be sent in headers (Basic Auth)
    # import base64
    # auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    # headers["Authorization"] = f"Basic {auth_header}"
    # And remove client_id and client_secret from payload if using Basic Auth

    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    response.raise_for_status()  # Raises an exception for HTTP errors
    return response.json()

def refresh_access_token(refresh_token_value):
    """Refreshes an access token using a refresh token.
    This is primarily for confidential clients. Public clients typically don't get refresh tokens.
    """
    if not CLIENT_SECRET:
        print("CLIENT_SECRET not configured. Cannot refresh token for public clients.")
        return None

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token_value,
        "client_id": CLIENT_ID, # Optional if using Basic Auth
        "client_secret": CLIENT_SECRET # Optional if using Basic Auth
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-API-Key": API_KEY  # Added X-API-Key header
    }
    # Example for confidential client using Basic Auth for client credentials
    # import base64
    # auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    # headers["Authorization"] = f"Basic {auth_header}"
    # And remove client_id and client_secret from payload if using Basic Auth

    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    # Example usage (conceptual - would be part of a larger application flow)

    # 1. Get authorization URL and direct user
    auth_url_to_visit = get_authorization_url()
    print(f"Please visit this URL to authorize: {auth_url_to_visit}")
    # In a real app, you'd open this URL in a browser or use a web view.
    # webbrowser.open(auth_url_to_visit)

    # 2. After user authorizes, they are redirected to REDIRECT_URI with a 'code'
    # This part would be handled by a web server listening at REDIRECT_URI
    # For this example, let's assume we got the code manually:
    # auth_code_from_redirect = input("Enter the authorization code from the redirect URL: ")

    # if auth_code_from_redirect:
    #     try:
    #         token_info = request_token(auth_code_from_redirect)
    #         print("\nToken Info:")
    #         print(token_info)

    #         access_token = token_info.get("access_token")
    #         refresh_token = token_info.get("refresh_token") # May not be present for public clients
    #         expires_in = token_info.get("expires_in")
    #         membership_id = token_info.get("membership_id")

    #         print(f"\nAccess Token: {access_token}")
    #         print(f"Membership ID: {membership_id}")

    #         # 3. (For confidential clients) Refresh token if needed
    #         if refresh_token and CLIENT_SECRET:
    #             # This is usually done when the access_token is about to expire or has expired
    #             # For demonstration, let's try to refresh it immediately (not typical)
    #             # time.sleep(1) # Give it a second
    #             print("\nAttempting to refresh token (for confidential clients)...")
    #             try:
    #                 refreshed_token_info = refresh_access_token(refresh_token)
    #                 if refreshed_token_info:
    #                     print("Refreshed Token Info:")
    #                     print(refreshed_token_info)
    #                     # Update your stored tokens
    #             except requests.HTTPError as e:
    #                 print(f"Error refreshing token: {e.response.status_code} - {e.response.text}")

    #     except requests.HTTPError as e:
    #         print(f"Error requesting token: {e.response.status_code} - {e.response.text}")
    #     except Exception as e:
    #         print(f"An unexpected error occurred: {e}")
    pass # Placeholder for actual UI/server logic in a real application
