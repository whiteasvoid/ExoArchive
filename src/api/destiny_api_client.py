import requests
import os
from src.auth import token_manager # Use the token_manager to get the access token

API_KEY = os.getenv("BUNGIE_API_KEY")
if not API_KEY:
    # This should ideally be handled more gracefully, perhaps at app startup.
    print("Warning: BUNGIE_API_KEY not found. API calls will likely fail.")

BASE_URL = "https://www.bungie.net/Platform"

def _make_api_request(endpoint, method="GET", params=None, data=None, requires_auth=True):
    """Helper function to make requests to the Bungie API."""
    access_token = None
    if requires_auth:
        access_token = token_manager.get_access_token()
        if not access_token:
            # In a real app, this might trigger a re-authentication flow
            # or return a more specific error/status to the caller.
            raise Exception("Authentication required, but no access token found.")

    headers = {
        "X-API-Key": API_KEY
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            headers["Content-Type"] = "application/json" # Common for POST
            response = requests.post(url, headers=headers, params=params, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()  # Raises an exception for HTTP errors (4xx or 5xx)
        
        # Check if the response is JSON and has the expected Bungie API structure
        if "Response" not in response.json():
            # This could indicate an API error that didn't result in an HTTP error status
            # e.g. ErrorCode != 1 but HTTP 200
            error_status = response.json().get("ErrorStatus", "Unknown API Error")
            error_code = response.json().get("ErrorCode", "N/A")
            message = response.json().get("Message", "")
            raise Exception(f"Bungie API Error: {error_status} (Code: {error_code}) - {message}")
            
        return response.json()["Response"]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {response.status_code} - {response.text}")
        # Attempt to parse Bungie's error message if available
        try:
            bungie_error = response.json()
            error_status = bungie_error.get("ErrorStatus", "Unknown API Error")
            error_code = bungie_error.get("ErrorCode", "N/A")
            message = bungie_error.get("Message", "")
            raise Exception(f"Bungie API HTTP Error: {error_status} (Code: {error_code}) - {message} (HTTP Status: {response.status_code})")
        except json.JSONDecodeError: # If response is not JSON
            raise Exception(f"Bungie API HTTP Error: {response.status_code} - {response.text}") from http_err
    except requests.exceptions.RequestException as req_err:
        print(f"Request exception occurred: {req_err}")
        raise Exception(f"Request failed: {req_err}")
    except Exception as e:
        print(f"An unexpected error occurred in _make_api_request: {e}")
        raise # Re-raise the exception to be handled by the caller


def get_linked_profiles(membership_id, membership_type="All"):
    """
    Returns a summary information about all profiles linked to the
    requesting membership type/membership ID that have valid Destiny information.
    https://bungie-net.github.io/#Destiny2.GetLinkedProfiles
    """
    # This endpoint typically does not require OAuth for the user if fetching public info
    # or if the membershipId and membershipType are for the authenticated user.
    # However, the API key is always required.
    # If fetching for the *current authenticated user*, no specific OAuth scope seems mandatory by docs,
    # but using the token if available is good practice.
    
    # Re-evaluating: The documentation for GetLinkedProfiles doesn't list specific OAuth scopes as *required*.
    # It says "it will only return linked accounts whose linkages you are allowed to view."
    # This implies if you are authenticated, you might see more.
    # For a DIM clone, we usually operate on behalf of an authenticated user.
    
    endpoint = f"/Destiny2/{membership_type}/Profile/{membership_id}/LinkedProfiles/"
    # Let's assume this might need auth if we want to ensure we see all viewable profiles for the user
    return _make_api_request(endpoint, requires_auth=True) 


def get_profile(membership_type, destiny_membership_id, components):
    """
    Returns Destiny Profile information for the supplied membership.
    https://bungie-net.github.io/#Destiny2.GetProfile
    Components is a list of numeric DestinyComponentType values.
    Example: [100, 200] for Profiles and Characters.
    """
    components_str = ",".join(map(str, components))
    endpoint = f"/Destiny2/{membership_type}/Profile/{destiny_membership_id}/"
    params = {"components": components_str}
    return _make_api_request(endpoint, params=params)

def get_character_inventory(membership_type, destiny_membership_id, character_id, components):
    """
    Returns character information for the supplied character, focusing on inventory.
    https://bungie-net.github.io/#Destiny2.GetCharacter
    Components is a list of numeric DestinyComponentType values.
    Example: [201, 205] for CharacterInventories and CharacterEquipment.
    """
    components_str = ",".join(map(str, components))
    endpoint = f"/Destiny2/{membership_type}/Profile/{destiny_membership_id}/Character/{character_id}/"
    params = {"components": components_str}
    return _make_api_request(endpoint, params=params)

# --- DestinyComponentType Enum (subset for inventory/profile) ---
# For reference, from https://bungie-net.github.io/#/components/schemas/Destiny.DestinyComponentType
class DestinyComponentType:
    PROFILES = 100
    PROFILE_INVENTORIES = 102 # Vault, etc.
    PROFILE_CURRENCIES = 103
    CHARACTERS = 200
    CHARACTER_INVENTORIES = 201 # Character's unequipped items
    CHARACTER_EQUIPMENT = 205   # Character's equipped items
    ITEM_INSTANCES = 300        # Basic instance data (damage type, primary stat)
    ITEM_OBJECTIVES = 301
    ITEM_PERKS = 302
    ITEM_RENDER_DATA = 303
    ITEM_STATS = 304
    ITEM_SOCKETS = 305
    ITEM_REUSABLE_PLUGS = 310

# --- Item Action Endpoints ---

def transfer_item(item_reference_hash, stack_size, transfer_to_vault, item_id, character_id, membership_type):
    """
    Transfer an item to/from your vault.
    https://bungie-net.github.io/#Destiny2.TransferItem
    Requires OAuth scope: MoveEquipDestinyItems
    """
    endpoint = "/Destiny2/Actions/Items/TransferItem/"
    payload = {
        "itemReferenceHash": item_reference_hash,
        "stackSize": stack_size,
        "transferToVault": transfer_to_vault,
        "itemId": item_id,
        "characterId": character_id,
        "membershipType": membership_type
    }
    # This endpoint returns an InventoryChangedResponse ( Bungie Platform Error Code + sequence number)
    # The actual response data under "Response" is just an integer (error code).
    # We might want to return the full JSON to get ErrorCode, Message etc. for better error handling.
    # For now, _make_api_request will raise an exception if ErrorCode is not 1.
    response_json = _make_api_request(endpoint, method="POST", data=payload, requires_auth=True)
    return response_json # This will be the Bungie API's ErrorCode (e.g., 1 for Success)

def equip_item(item_id, character_id, membership_type):
    """
    Equip an item. You must have a valid Destiny Account, and either be in a social space, in orbit, or offline.
    https://bungie-net.github.io/#Destiny2.EquipItem
    Requires OAuth scope: MoveEquipDestinyItems
    """
    endpoint = "/Destiny2/Actions/Items/EquipItem/"
    payload = {
        "itemId": item_id,
        "characterId": character_id,
        "membershipType": membership_type
    }
    response_json = _make_api_request(endpoint, method="POST", data=payload, requires_auth=True)
    return response_json # This will be the Bungie API's ErrorCode

def equip_items(item_ids, character_id, membership_type):
    """
    Equip a list of items. All items must be from the same character.
    https://bungie-net.github.io/#Destiny2.EquipItems
    Requires OAuth scope: MoveEquipDestinyItems
    """
    endpoint = "/Destiny2/Actions/Items/EquipItems/"
    payload = {
        "itemIds": item_ids, # This should be a list of itemInstanceIds
        "characterId": character_id,
        "membershipType": membership_type
    }
    # This endpoint returns a DestinyEquipItemResults object within the "Response"
    response_data = _make_api_request(endpoint, method="POST", data=payload, requires_auth=True)
    return response_data # This contains equipResults list


if __name__ == "__main__":
    # This is for example usage and basic testing.
    # Requires a valid, non-expired access token to be stored by token_manager.py
    # and BUNGIE_API_KEY to be set in environment or .env
    
    print("Attempting to use the Destiny API Client...")
    
    # First, ensure we are "logged in" (i.e., tokens are stored)
    if not token_manager.get_access_token():
        print("No access token found. Please run the auth_ui.py example to authenticate first.")
    else:
        print(f"Using Access Token: {token_manager.get_access_token()[:20]}...")
        current_bnet_membership_id = token_manager.get_membership_id()
        if not current_bnet_membership_id:
            print("Could not retrieve Bungie.net membership ID from stored tokens.")
        else:
            print(f"Current Bungie.net Membership ID: {current_bnet_membership_id}")
            
            # Variables for testing item actions (these would come from your app's state)
            # Replace with actual values from your inventory after fetching it.
            example_item_instance_id = None # e.g., "6917529033722175964" 
            example_item_reference_hash = None # e.g., 3159615086 (Gjallarhorn)
            example_character_id = None # e.g., "2305843009470314193"
            example_destiny_membership_id = None
            example_membership_type = None

            try:
                # 1. Get Linked Profiles to find a Destiny account
                print("\nFetching linked profiles to get Destiny account info...")
                linked_profiles = get_linked_profiles(current_bnet_membership_id, membership_type=254) # 254 for BungieNext
                
                if linked_profiles and linked_profiles.get("profiles"):
                    # Prioritize primary cross-save or first available
                    profile_to_use = next((p for p in linked_profiles["profiles"] if p.get("isCrossSavePrimary")), linked_profiles["profiles"][0])
                    example_destiny_membership_id = profile_to_use.get("membershipId")
                    example_membership_type = profile_to_use.get("membershipType")
                    print(f"Using Destiny Profile: ID {example_destiny_membership_id}, Type {example_membership_type}")

                    # 2. Get Character IDs from that profile
                    if example_destiny_membership_id and example_membership_type is not None:
                        print("\nFetching profile for character list...")
                        profile_data = get_profile(example_membership_type, example_destiny_membership_id, [DestinyComponentType.CHARACTERS])
                        characters_data = profile_data.get("characters", {}).get("data", {})
                        if characters_data:
                            example_character_id = list(characters_data.keys())[0] # Use the first character
                            print(f"Using Character ID: {example_character_id}")
                        else:
                            print("No characters found for the Destiny profile.")
                else:
                    print("No Destiny profiles found for this Bungie.net account.")

                # --- Example Item Action (Commented out by default to prevent accidental actions) ---
                # Ensure you have valid item_instance_id, item_reference_hash, character_id, membership_id, and membership_type
                # from your fetched inventory before uncommenting and running these.
                
                # --- Test Transfer (Example: move an item from inventory to vault) ---
                # if example_item_instance_id and example_item_reference_hash and example_character_id and example_destiny_membership_id and example_membership_type is not None:
                #     print(f"\nAttempting to transfer item {example_item_instance_id} to vault...")
                #     try:
                #         transfer_result = transfer_item(
                #             item_reference_hash=example_item_reference_hash, # Hash of the item definition
                #             stack_size=1, # Assuming it's an instanced item
                #             transfer_to_vault=True,
                #             item_id=example_item_instance_id, # Instance ID of the item
                #             character_id=example_character_id,
                #             membership_type=example_membership_type
                #         )
                #         print(f"Transfer API call completed. Bungie API ErrorCode: {transfer_result}")
                #         if transfer_result == 1: # PlatformErrorCodes.Success
                #             print("Item transfer successful (simulated).")
                #         else:
                #             print("Item transfer might have failed or had issues. Check ErrorCode.")
                #     except Exception as e:
                #         print(f"Error during item transfer: {e}")
                # else:
                #     print("\nSkipping item transfer test: Not all example IDs are set.")

                # --- Test Equip Item (Example: equip an item) ---
                # if example_item_instance_id and example_character_id and example_destiny_membership_id and example_membership_type is not None:
                #     print(f"\nAttempting to equip item {example_item_instance_id} on character {example_character_id}...")
                #     try:
                #         equip_result = equip_item(
                #             item_id=example_item_instance_id,
                #             character_id=example_character_id,
                #             membership_type=example_membership_type
                #         )
                #         print(f"Equip API call completed. Bungie API ErrorCode: {equip_result}")
                #         if equip_result == 1: # PlatformErrorCodes.Success
                #             print("Item equip successful (simulated).")
                #         else:
                #             print("Item equip might have failed. Check ErrorCode.")
                #     except Exception as e:
                #         print(f"Error during item equip: {e}")
                # else:
                #      print("\nSkipping item equip test: Not all example IDs are set.")

            except Exception as e:
                print(f"An API call or setup failed: {e}")
    
    print("\nDestiny API Client example finished.")
