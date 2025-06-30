import unittest
from unittest.mock import patch, MagicMock
import os

# Ensure src is in path for direct script execution
import sys
if os.path.join(os.getcwd(), 'src') not in sys.path and os.path.join(os.getcwd(), '..', 'src') not in sys.path :
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.auth import bungie_auth

# Set dummy environment variables for testing
# In a real test setup, you might use a .env.test file or mock os.getenv
os.environ["BUNGIE_CLIENT_ID"] = "test_client_id"
os.environ["BUNGIE_API_KEY"] = "test_api_key"
# CLIENT_SECRET is only checked in refresh_access_token, which we can test separately or mock its absence
# os.environ["BUNGIE_CLIENT_SECRET"] = "test_client_secret" 

class TestBungieAuth(unittest.TestCase):

    def setUp(self):
        # Reload bungie_auth to pick up mocked env vars if tests modify them
        # For this simple case, setting them once globally might be fine.
        self.CLIENT_ID = "test_client_id"
        self.REDIRECT_URI = "http://localhost:8000/callback"
        bungie_auth.CLIENT_ID = self.CLIENT_ID # Ensure module uses our test ID
        bungie_auth.REDIRECT_URI = self.REDIRECT_URI

    def test_get_authorization_url(self):
        """Test generation of the authorization URL."""
        expected_url_part = f"{bungie_auth.AUTH_URL}?client_id={self.CLIENT_ID}&response_type=code&redirect_uri={self.REDIRECT_URI}"
        # Note: The order of query parameters might vary, so checking parts or parsing is safer
        generated_url = bungie_auth.get_authorization_url()
        self.assertIn(f"client_id={self.CLIENT_ID}", generated_url)
        self.assertIn("response_type=code", generated_url)
        self.assertIn(f"redirect_uri={self.REDIRECT_URI}", generated_url)
        self.assertTrue(generated_url.startswith(bungie_auth.AUTH_URL))

    @patch('requests.post')
    def test_request_token_success(self, mock_post):
        """Test successfully exchanging an authorization code for a token."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        expected_token_info = {"access_token": "new_access_token", "expires_in": 3600, "membership_id": "123"}
        mock_response.json.return_value = expected_token_info 
        mock_post.return_value = mock_response

        auth_code = "sample_auth_code"
        token_info = bungie_auth.request_token(auth_code)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], bungie_auth.TOKEN_URL)
        self.assertEqual(kwargs['data']['grant_type'], "authorization_code")
        self.assertEqual(kwargs['data']['code'], auth_code)
        self.assertEqual(kwargs['data']['client_id'], self.CLIENT_ID)
        self.assertEqual(kwargs['data']['redirect_uri'], self.REDIRECT_URI)
        self.assertEqual(kwargs['headers']['Content-Type'], "application/x-www-form-urlencoded")
        
        self.assertEqual(token_info, expected_token_info)
        mock_response.raise_for_status.assert_called_once()

    @patch('requests.post')
    def test_request_token_http_error(self, mock_post):
        """Test token request failure due to HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "invalid_grant", "error_description": "Bad code"}
        mock_response.text = '{"error": "invalid_grant", "error_description": "Bad code"}'
        # Configure raise_for_status to actually raise an error
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_post.return_value = mock_response

        with self.assertRaisesRegex(Exception, "Bungie API HTTP Error: invalid_grant \(Code: N/A\) - Bad code \(HTTP Status: 400\)"):
            bungie_auth.request_token("invalid_auth_code")

    @patch('requests.post')
    def test_refresh_access_token_success_confidential(self, mock_post):
        """Test successfully refreshing an access token for a confidential client."""
        # Temporarily set CLIENT_SECRET for this test
        original_secret = bungie_auth.CLIENT_SECRET
        bungie_auth.CLIENT_SECRET = "test_client_secret_for_refresh"
        os.environ["BUNGIE_CLIENT_SECRET"] = "test_client_secret_for_refresh" # ensure module sees it if it re-evaluates getenv

        mock_response = MagicMock()
        mock_response.status_code = 200
        expected_refreshed_info = {"access_token": "refreshed_token", "expires_in": 3600}
        mock_response.json.return_value = expected_refreshed_info
        mock_post.return_value = mock_response

        refresh_token_value = "sample_refresh_token"
        refreshed_info = bungie_auth.refresh_access_token(refresh_token_value)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], bungie_auth.TOKEN_URL)
        self.assertEqual(kwargs['data']['grant_type'], "refresh_token")
        self.assertEqual(kwargs['data']['refresh_token'], refresh_token_value)
        self.assertEqual(kwargs['data']['client_id'], self.CLIENT_ID)
        self.assertEqual(kwargs['data']['client_secret'], "test_client_secret_for_refresh")
        
        self.assertEqual(refreshed_info, expected_refreshed_info)
        mock_response.raise_for_status.assert_called_once()

        # Restore original CLIENT_SECRET state
        bungie_auth.CLIENT_SECRET = original_secret
        if original_secret is None: # if it was originally None, unset env var
             if "BUNGIE_CLIENT_SECRET" in os.environ: del os.environ["BUNGIE_CLIENT_SECRET"]
        else:
            os.environ["BUNGIE_CLIENT_SECRET"] = original_secret


    def test_refresh_access_token_no_secret_public(self):
        """Test refresh token attempt when CLIENT_SECRET is not configured (e.g., public client)."""
        original_secret = bungie_auth.CLIENT_SECRET
        bungie_auth.CLIENT_SECRET = None # Simulate no client secret
        if "BUNGIE_CLIENT_SECRET" in os.environ:
            del os.environ["BUNGIE_CLIENT_SECRET"]


        with patch('builtins.print') as mock_print: # To capture the print output
            result = bungie_auth.refresh_access_token("any_refresh_token")
            self.assertIsNone(result)
            mock_print.assert_any_call("CLIENT_SECRET not configured. Cannot refresh token for public clients.")
        
        # Restore
        bungie_auth.CLIENT_SECRET = original_secret
        if original_secret:
            os.environ["BUNGIE_CLIENT_SECRET"] = original_secret


if __name__ == '__main__':
    # If running directly, need to adjust sys.path for imports from src
    if os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) not in sys.path:
         sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if grandparent_dir not in sys.path:
        sys.path.insert(0, grandparent_dir)
    unittest.main()
