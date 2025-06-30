import unittest
from unittest.mock import patch, MagicMock
import os
import json

# Ensure src is in path for direct script execution
import sys
if os.path.join(os.getcwd(), 'src') not in sys.path and os.path.join(os.getcwd(), '..', 'src') not in sys.path :
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock token_manager before importing destiny_api_client
mock_token_manager = MagicMock()
sys.modules['src.auth.token_manager'] = mock_token_manager

from src.api import destiny_api_client

# Set dummy API key for testing
os.environ["BUNGIE_API_KEY"] = "test_api_key_for_client"
destiny_api_client.API_KEY = "test_api_key_for_client" # Ensure module uses it


class TestDestinyApiClient(unittest.TestCase):

    def setUp(self):
        self.mock_token_manager = mock_token_manager
        self.mock_token_manager.get_access_token.return_value = "fake_access_token"
        
        # Reset API_KEY in the module in case a test modifies it via os.environ
        destiny_api_client.API_KEY = "test_api_key_for_client"


    @patch('requests.get')
    def test_get_linked_profiles_success(self, mock_get):
        """Test successful GetLinkedProfiles call."""
        expected_response_data = {"profiles": [{"membershipId": "123", "membershipType": 1}]}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Response": expected_response_data, "ErrorCode": 1, "ErrorStatus": "Success"}
        mock_get.return_value = mock_response

        membership_id = "999"
        response = destiny_api_client.get_linked_profiles(membership_id, membership_type=254)

        mock_get.assert_called_once_with(
            f"{destiny_api_client.BASE_URL}/Destiny2/254/Profile/{membership_id}/LinkedProfiles/",
            headers={"X-API-Key": "test_api_key_for_client", "Authorization": "Bearer fake_access_token"},
            params=None
        )
        self.assertEqual(response, expected_response_data)
        mock_response.raise_for_status.assert_called_once()

    @patch('requests.get')
    def test_get_profile_success(self, mock_get):
        """Test successful GetProfile call."""
        expected_response_data = {"characterIds": ["char1", "char2"]}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Response": expected_response_data, "ErrorCode": 1}
        mock_get.return_value = mock_response

        membership_type = 1
        destiny_membership_id = "123"
        components = [100, 200] # Profiles, Characters
        
        response = destiny_api_client.get_profile(membership_type, destiny_membership_id, components)

        mock_get.assert_called_once_with(
            f"{destiny_api_client.BASE_URL}/Destiny2/{membership_type}/Profile/{destiny_membership_id}/",
            headers={"X-API-Key": "test_api_key_for_client", "Authorization": "Bearer fake_access_token"},
            params={"components": "100,200"}
        )
        self.assertEqual(response, expected_response_data)

    @patch('requests.get')
    def test_get_character_inventory_success(self, mock_get):
        """Test successful GetCharacter (for inventory) call."""
        expected_response_data = {"inventory": {"data": {"items": []}}}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Response": expected_response_data, "ErrorCode": 1}
        mock_get.return_value = mock_response

        membership_type = 1
        destiny_membership_id = "123"
        character_id = "char1"
        components = [201, 205] # CharacterInventories, CharacterEquipment
        
        response = destiny_api_client.get_character_inventory(membership_type, destiny_membership_id, character_id, components)

        mock_get.assert_called_once_with(
            f"{destiny_api_client.BASE_URL}/Destiny2/{membership_type}/Profile/{destiny_membership_id}/Character/{character_id}/",
            headers={"X-API-Key": "test_api_key_for_client", "Authorization": "Bearer fake_access_token"},
            params={"components": "201,205"}
        )
        self.assertEqual(response, expected_response_data)

    @patch('requests.post')
    def test_transfer_item_success(self, mock_post):
        """Test successful TransferItem call."""
        # TransferItem's "Response" is just the ErrorCode integer
        expected_api_error_code = 1 # PlatformErrorCodes.Success
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Response": expected_api_error_code, "ErrorCode": 1}
        mock_post.return_value = mock_response

        payload = {
            "itemReferenceHash": 12345, "stackSize": 1, "transferToVault": True,
            "itemId": "item_instance_1", "characterId": "char1", "membershipType": 1
        }
        response_code = destiny_api_client.transfer_item(**payload)

        mock_post.assert_called_once_with(
            f"{destiny_api_client.BASE_URL}/Destiny2/Actions/Items/TransferItem/",
            headers={"X-API-Key": "test_api_key_for_client", "Authorization": "Bearer fake_access_token", "Content-Type": "application/json"},
            params=None,
            json=payload
        )
        self.assertEqual(response_code, expected_api_error_code)

    @patch('requests.post')
    def test_equip_item_success(self, mock_post):
        """Test successful EquipItem call."""
        expected_api_error_code = 1 # PlatformErrorCodes.Success
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Response": expected_api_error_code, "ErrorCode": 1}
        mock_post.return_value = mock_response

        payload = {"itemId": "item_instance_1", "characterId": "char1", "membershipType": 1}
        response_code = destiny_api_client.equip_item(**payload)
        
        mock_post.assert_called_once_with(
            f"{destiny_api_client.BASE_URL}/Destiny2/Actions/Items/EquipItem/",
            headers={"X-API-Key": "test_api_key_for_client", "Authorization": "Bearer fake_access_token", "Content-Type": "application/json"},
            params=None,
            json=payload
        )
        self.assertEqual(response_code, expected_api_error_code)

    @patch('requests.post')
    def test_equip_items_success(self, mock_post):
        """Test successful EquipItems call."""
        expected_response_data = {"equipResults": [{"itemInstanceId": "item1", "equipStatus": 1}]}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Response": expected_response_data, "ErrorCode": 1}
        mock_post.return_value = mock_response

        payload = {"itemIds": ["item1", "item2"], "characterId": "char1", "membershipType": 1}
        response_data = destiny_api_client.equip_items(**payload)
        
        mock_post.assert_called_once_with(
            f"{destiny_api_client.BASE_URL}/Destiny2/Actions/Items/EquipItems/",
            headers={"X-API-Key": "test_api_key_for_client", "Authorization": "Bearer fake_access_token", "Content-Type": "application/json"},
            params=None,
            json=payload
        )
        self.assertEqual(response_data, expected_response_data)

    @patch('requests.get')
    def test_api_request_http_error_handling(self, mock_get):
        """Test that _make_api_request handles HTTP errors correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 401 # Unauthorized
        mock_response.text = '{"ErrorCode": 5, "ErrorStatus": "AuthenticationError", "Message": "Bad token"}'
        mock_response.json.return_value = json.loads(mock_response.text)
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        with self.assertRaisesRegex(Exception, "Bungie API HTTP Error: AuthenticationError \(Code: 5\) - Bad token \(HTTP Status: 401\)"):
            destiny_api_client._make_api_request("/some_endpoint")
            
    @patch('requests.get')
    def test_api_request_bungie_api_error_handling(self, mock_get):
        """Test that _make_api_request handles Bungie API errors (ErrorCode != 1)."""
        mock_response = MagicMock()
        mock_response.status_code = 200 # HTTP OK
        # Bungie API error (e.g., invalid parameter)
        mock_response.json.return_value = {"Response": {}, "ErrorCode": 7, "ErrorStatus": "ParameterParseFailure", "Message": "Invalid component"}
        mock_get.return_value = mock_response

        with self.assertRaisesRegex(Exception, "Bungie API Error: ParameterParseFailure \(Code: 7\) - Invalid component"):
            destiny_api_client._make_api_request("/some_endpoint_with_bad_param")

    def test_api_request_no_token(self):
        """Test API request when no access token is available."""
        self.mock_token_manager.get_access_token.return_value = None
        with self.assertRaisesRegex(Exception, "Authentication required, but no access token found."):
            destiny_api_client._make_api_request("/some_auth_endpoint", requires_auth=True)

if __name__ == '__main__':
    if os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) not in sys.path:
         sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if grandparent_dir not in sys.path:
        sys.path.insert(0, grandparent_dir)
    unittest.main()
