import unittest
from unittest.mock import patch, MagicMock
import os

import sys
if os.path.join(os.getcwd(), 'src') not in sys.path and os.path.join(os.getcwd(), '..', 'src') not in sys.path :
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before importing player_information
mock_token_manager = MagicMock()
mock_destiny_api_client = MagicMock()

# This is tricky because player_information imports from .destiny_api_client (relative)
# and also from src.auth. We need to ensure these are correctly mocked *before*
# player_information is imported.
sys.modules['src.auth.token_manager'] = mock_token_manager
sys.modules['src.api.destiny_api_client'] = mock_destiny_api_client 

# Now import the module to be tested
from src.api import player_information
from src.api.destiny_api_client import DestinyComponentType # Actual enum

class TestPlayerInformation(unittest.TestCase):

    def setUp(self):
        self.mock_token_manager = mock_token_manager
        self.mock_destiny_api_client = mock_destiny_api_client
        
        # Reset mocks for each test
        self.mock_token_manager.reset_mock()
        self.mock_destiny_api_client.reset_mock()

        # Default setup for successful calls
        self.mock_token_manager.get_membership_id.return_value = "bungie_net_user_123"


    def test_get_current_user_primary_destiny_membership_success(self):
        # Mock get_linked_profiles from destiny_api_client
        self.mock_destiny_api_client.get_linked_profiles.return_value = {
            "profiles": [
                {"membershipId": "destiny_id_1", "membershipType": 1, "isCrossSavePrimary": False, "dateLastPlayed": "2023-01-01T00:00:00Z"},
                {"membershipId": "destiny_id_primary", "membershipType": 2, "isCrossSavePrimary": True, "dateLastPlayed": "2023-01-02T00:00:00Z"}
            ]
        }
        
        mem_id, mem_type = player_information.get_current_user_primary_destiny_membership()
        
        self.assertEqual(mem_id, "destiny_id_primary")
        self.assertEqual(mem_type, 2)
        self.mock_destiny_api_client.get_linked_profiles.assert_called_once_with("bungie_net_user_123", membership_type=254)

    def test_get_current_user_primary_destiny_membership_no_primary_fallback_to_recent(self):
        self.mock_destiny_api_client.get_linked_profiles.return_value = {
            "profiles": [
                {"membershipId": "destiny_id_older", "membershipType": 1, "isCrossSavePrimary": False, "dateLastPlayed": "2023-01-01T00:00:00Z"},
                {"membershipId": "destiny_id_recent", "membershipType": 3, "isCrossSavePrimary": False, "dateLastPlayed": "2023-01-03T00:00:00Z"}
            ]
        }
        mem_id, mem_type = player_information.get_current_user_primary_destiny_membership()
        self.assertEqual(mem_id, "destiny_id_recent")
        self.assertEqual(mem_type, 3)

    def test_get_current_user_primary_destiny_membership_no_token(self):
        self.mock_token_manager.get_membership_id.return_value = None
        mem_id, mem_type = player_information.get_current_user_primary_destiny_membership()
        self.assertIsNone(mem_id)
        self.assertIsNone(mem_type)
        self.mock_destiny_api_client.get_linked_profiles.assert_not_called()

    def test_get_current_user_primary_destiny_membership_api_fails(self):
        self.mock_destiny_api_client.get_linked_profiles.side_effect = Exception("API Call Failed")
        mem_id, mem_type = player_information.get_current_user_primary_destiny_membership()
        self.assertIsNone(mem_id)
        self.assertIsNone(mem_type)
        
    def test_get_current_user_primary_destiny_membership_no_profiles_returned(self):
        self.mock_destiny_api_client.get_linked_profiles.return_value = {"profiles": []}
        mem_id, mem_type = player_information.get_current_user_primary_destiny_membership()
        self.assertIsNone(mem_id)
        self.assertIsNone(mem_type)

    @patch.object(player_information, 'get_current_user_primary_destiny_membership')
    def test_get_character_inventories_success(self, mock_get_primary_member):
        mock_get_primary_member.return_value = ("destiny_mem_id", 1)
        
        # Mock get_profile from destiny_api_client
        self.mock_destiny_api_client.get_profile.return_value = {
            "characters": {
                "data": {
                    "char_id_1": {"classHash": 111, "raceHash": 222, "light": 1800},
                    "char_id_2": {"classHash": 333, "raceHash": 444, "light": 1810}
                }
            }
        }
        
        # Mock get_character_inventory from destiny_api_client
        # This will be called for each character
        self.mock_destiny_api_client.get_character_inventory.side_effect = [
            { # Data for char_id_1
                "equipment": {"data": {"items": [{"itemHash": 10, "itemInstanceId": "inst1"}]}},
                "inventory": {"data": {"items": [{"itemHash": 20, "itemInstanceId": "inst2"}]}},
                "itemComponents": {
                    "instances": {"data": {"inst1": {"primaryStat": {"value": 100}}}},
                    "sockets": {"data": {}}, "stats": {"data": {}}, "perks": {"data": {}},
                    "reusablePlugs": {"data": {}}, "objectives": {"data": {}}
                }
            },
            { # Data for char_id_2
                "equipment": {"data": {"items": [{"itemHash": 30, "itemInstanceId": "inst3"}]}},
                "inventory": {"data": {"items": []}},
                 "itemComponents": {
                    "instances": {"data": {"inst3": {"primaryStat": {"value": 200}}}},
                    "sockets": {"data": {}}, "stats": {"data": {}}, "perks": {"data": {}},
                    "reusablePlugs": {"data": {}}, "objectives": {"data": {}}
                }
            }
        ]

        inventories = player_information.get_character_inventories_for_current_user()

        self.assertIsNotNone(inventories)
        self.assertIn("char_id_1", inventories)
        self.assertIn("char_id_2", inventories)
        self.assertEqual(len(inventories["char_id_1"]["equipment"]), 1)
        self.assertEqual(inventories["char_id_1"]["equipment"][0]["itemInstanceId"], "inst1")
        self.assertIn("inst1", inventories["char_id_1"]["item_instances"])
        
        self.mock_destiny_api_client.get_profile.assert_called_once_with(
            1, "destiny_mem_id", [DestinyComponentType.CHARACTERS]
        )
        self.assertEqual(self.mock_destiny_api_client.get_character_inventory.call_count, 2)


    @patch.object(player_information, 'get_current_user_primary_destiny_membership')
    def test_get_profile_inventory_success(self, mock_get_primary_member):
        mock_get_primary_member.return_value = ("destiny_mem_id", 1)

        self.mock_destiny_api_client.get_profile.return_value = {
            "profileInventory": {"data": {"items": [{"itemHash": 789, "itemInstanceId": "vault_inst1"}]}},
            "itemComponents": {
                 "instances": {"data": {"vault_inst1": {"primaryStat": {"value": 300}}}},
                 "sockets": {"data": {}}, "stats": {"data": {}}, "perks": {"data": {}},
                 "reusablePlugs": {"data": {}}, "objectives": {"data": {}}
            }
        }
        
        profile_inv = player_information.get_profile_inventory_for_current_user()
        
        self.assertIsNotNone(profile_inv)
        self.assertEqual(len(profile_inv["items"]), 1)
        self.assertEqual(profile_inv["items"][0]["itemInstanceId"], "vault_inst1")
        self.assertIn("vault_inst1", profile_inv["item_instances"])
        
        self.mock_destiny_api_client.get_profile.assert_called_once()
        # Check that correct components were requested for profile inventory
        args, kwargs = self.mock_destiny_api_client.get_profile.call_args
        requested_components = kwargs['components']
        self.assertIn(DestinyComponentType.PROFILE_INVENTORIES, requested_components)
        self.assertIn(DestinyComponentType.ITEM_INSTANCES, requested_components)


if __name__ == '__main__':
    if os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) not in sys.path:
         sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if grandparent_dir not in sys.path:
        sys.path.insert(0, grandparent_dir)
    unittest.main()
