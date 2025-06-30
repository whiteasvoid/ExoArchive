import unittest
from unittest.mock import patch, MagicMock
import os

# Ensure src is in path for direct script execution
import sys
if os.path.join(os.getcwd(), 'src') not in sys.path and os.path.join(os.getcwd(), '..', 'src') not in sys.path :
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock token_manager and destiny_api_client before importing item_actions
mock_token_manager = MagicMock()
mock_destiny_api_client = MagicMock()
mock_player_information = MagicMock() # For get_current_user_primary_destiny_membership

sys.modules['src.auth.token_manager'] = mock_token_manager
sys.modules['src.api.destiny_api_client'] = mock_destiny_api_client
sys.modules['src.api.player_information'] = mock_player_information # Mock this too

from src.api import item_actions # Now import item_actions

class TestItemActions(unittest.TestCase):

    def setUp(self):
        self.mock_token_manager = mock_token_manager
        self.mock_destiny_api_client = mock_destiny_api_client
        self.mock_player_information = mock_player_information
        
        # Reset mocks before each test
        self.mock_token_manager.reset_mock()
        self.mock_destiny_api_client.reset_mock()
        self.mock_player_information.reset_mock()

        # Default successful auth and membership lookup
        self.mock_token_manager.get_access_token.return_value = "fake_access_token"
        self.mock_player_information.get_current_user_primary_destiny_membership.return_value = ("destiny_mem_id", 1)


    def test_move_item_to_vault_success(self):
        self.mock_destiny_api_client.transfer_item.return_value = 1 # Success code
        
        success, message = item_actions.move_item_to_vault(123, "item_instance_1", 1, "char1")
        
        self.assertTrue(success)
        self.assertEqual(message, "Item moved to vault successfully.")
        self.mock_destiny_api_client.transfer_item.assert_called_once_with(
            item_reference_hash=123,
            stack_size=1,
            transfer_to_vault=True,
            item_id="item_instance_1",
            character_id="char1",
            membership_type=1 
        )

    def test_move_item_to_vault_api_failure(self):
        self.mock_destiny_api_client.transfer_item.return_value = 1623 # Example error code (DestinyItemNotFound)
        
        success, message = item_actions.move_item_to_vault(123, "item_instance_1", 1, "char1")
        
        self.assertFalse(success)
        self.assertIn("Bungie API Error Code: 1623", message)

    def test_move_item_to_vault_no_auth(self):
        self.mock_token_manager.get_access_token.return_value = None
        success, message = item_actions.move_item_to_vault(123, "item_instance_1", 1, "char1")
        self.assertFalse(success)
        self.assertEqual(message, "User not authenticated.")
        self.mock_destiny_api_client.transfer_item.assert_not_called()

    def test_move_item_to_vault_no_membership(self):
        self.mock_player_information.get_current_user_primary_destiny_membership.return_value = (None, None)
        success, message = item_actions.move_item_to_vault(123, "item_instance_1", 1, "char1")
        self.assertFalse(success)
        self.assertEqual(message, "Could not determine primary Destiny membership.")
        self.mock_destiny_api_client.transfer_item.assert_not_called()


    def test_move_item_to_character_success(self):
        self.mock_destiny_api_client.transfer_item.return_value = 1 # Success code
        
        success, message = item_actions.move_item_to_character(456, "item_instance_2", 1, "char2")
        
        self.assertTrue(success)
        self.assertEqual(message, "Item moved to character successfully.")
        self.mock_destiny_api_client.transfer_item.assert_called_once_with(
            item_reference_hash=456,
            stack_size=1,
            transfer_to_vault=False,
            item_id="item_instance_2",
            character_id="char2",
            membership_type=1
        )

    def test_equip_item_on_character_success(self):
        self.mock_destiny_api_client.equip_item.return_value = 1 # Success code
        
        success, message = item_actions.equip_item_on_character("item_instance_3", "char1")
        
        self.assertTrue(success)
        self.assertEqual(message, "Item equipped successfully.")
        self.mock_destiny_api_client.equip_item.assert_called_once_with(
            item_id="item_instance_3",
            character_id="char1",
            membership_type=1
        )

    def test_equip_multiple_items_success(self):
        # Mock the return value for equip_items
        self.mock_destiny_api_client.equip_items.return_value = {
            "equipResults": [
                {"itemInstanceId": "item1", "equipStatus": 1},
                {"itemInstanceId": "item2", "equipStatus": 1}
            ]
        }
        
        success, message = item_actions.equip_multiple_items_on_character(["item1", "item2"], "char1")
        
        self.assertTrue(success)
        self.assertEqual(message, "All items equipped successfully.")
        self.mock_destiny_api_client.equip_items.assert_called_once_with(
            item_ids=["item1", "item2"],
            character_id="char1",
            membership_type=1
        )

    def test_equip_multiple_items_partial_failure(self):
        self.mock_destiny_api_client.equip_items.return_value = {
            "equipResults": [
                {"itemInstanceId": "item1", "equipStatus": 1},
                {"itemInstanceId": "item2", "equipStatus": 1641} # DestinyItemUniqueEquipRestricted
            ]
        }
        
        success, message = item_actions.equip_multiple_items_on_character(["item1", "item2"], "char1")
        
        self.assertFalse(success)
        self.assertIn("One or more items failed to equip", message)
        self.assertIn("Item item2: Failed (Code 1641)", message)

    def test_equip_item_api_exception(self):
        self.mock_destiny_api_client.equip_item.side_effect = Exception("Network Error")
        
        success, message = item_actions.equip_item_on_character("item_instance_3", "char1")
        
        self.assertFalse(success)
        self.assertEqual(message, "Network Error")


if __name__ == '__main__':
    if os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) not in sys.path:
         sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if grandparent_dir not in sys.path:
        sys.path.insert(0, grandparent_dir)
    unittest.main()
