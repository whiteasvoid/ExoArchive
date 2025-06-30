from .destiny_api_client import transfer_item, equip_item, equip_items
from .player_information import get_current_user_primary_destiny_membership
from src.auth import token_manager # For checking auth status

# This module will provide higher-level functions for item actions,
# abstracting some of the direct parameter passing if needed,
# and ensuring the user is authenticated.

def move_item_to_vault(item_reference_hash, item_instance_id, stack_size, character_id):
    """
    Moves a specified item from a character to the vault.
    """
    if not token_manager.get_access_token():
        print("Error: User not authenticated. Cannot move item.")
        return False, "User not authenticated."

    destiny_membership_id, destiny_membership_type = get_current_user_primary_destiny_membership()
    if not destiny_membership_id or destiny_membership_type is None:
        return False, "Could not determine primary Destiny membership."

    try:
        print(f"Attempting to move item {item_instance_id} (hash: {item_reference_hash}) from char {character_id} to vault.")
        result_code = transfer_item(
            item_reference_hash=item_reference_hash,
            stack_size=stack_size,
            transfer_to_vault=True,
            item_id=item_instance_id,
            character_id=character_id,
            membership_type=destiny_membership_type
        )
        if result_code == 1: # PlatformErrorCodes.Success
            print(f"Successfully moved item {item_instance_id} to vault.")
            return True, "Item moved to vault successfully."
        else:
            # destiny_api_client._make_api_request should raise an exception with Bungie error message
            return False, f"Bungie API Error Code: {result_code} (See logs for more details)"
    except Exception as e:
        print(f"Error moving item {item_instance_id} to vault: {e}")
        return False, str(e)

def move_item_to_character(item_reference_hash, item_instance_id, stack_size, target_character_id):
    """
    Moves a specified item from the vault to a character.
    Note: The source character_id for vault items is often the last character that handled it,
    or a generic one. For simplicity, the API handles "transferToVault=False" by pulling from
    the vault if the item is there and character_id is the target.
    """
    if not token_manager.get_access_token():
        print("Error: User not authenticated. Cannot move item.")
        return False, "User not authenticated."

    destiny_membership_id, destiny_membership_type = get_current_user_primary_destiny_membership()
    if not destiny_membership_id or destiny_membership_type is None:
        return False, "Could not determine primary Destiny membership."

    try:
        print(f"Attempting to move item {item_instance_id} (hash: {item_reference_hash}) from vault to char {target_character_id}.")
        result_code = transfer_item(
            item_reference_hash=item_reference_hash,
            stack_size=stack_size,
            transfer_to_vault=False, # Moving FROM vault TO character
            item_id=item_instance_id,
            character_id=target_character_id, # Target character
            membership_type=destiny_membership_type
        )
        if result_code == 1: # PlatformErrorCodes.Success
            print(f"Successfully moved item {item_instance_id} to character {target_character_id}.")
            return True, "Item moved to character successfully."
        else:
            return False, f"Bungie API Error Code: {result_code} (See logs for more details)"
    except Exception as e:
        print(f"Error moving item {item_instance_id} to character: {e}")
        return False, str(e)

def equip_item_on_character(item_instance_id, character_id):
    """
    Equips a specified item on a character.
    """
    if not token_manager.get_access_token():
        print("Error: User not authenticated. Cannot equip item.")
        return False, "User not authenticated."

    destiny_membership_id, destiny_membership_type = get_current_user_primary_destiny_membership()
    if not destiny_membership_id or destiny_membership_type is None:
        return False, "Could not determine primary Destiny membership."
    
    try:
        print(f"Attempting to equip item {item_instance_id} on character {character_id}.")
        result_code = equip_item(
            item_id=item_instance_id,
            character_id=character_id,
            membership_type=destiny_membership_type
        )
        if result_code == 1: # PlatformErrorCodes.Success
            print(f"Successfully equipped item {item_instance_id} on character {character_id}.")
            return True, "Item equipped successfully."
        else:
            return False, f"Bungie API Error Code: {result_code} (See logs for more details)"
    except Exception as e:
        print(f"Error equipping item {item_instance_id}: {e}")
        return False, str(e)

def equip_multiple_items_on_character(item_instance_ids, character_id):
    """
    Equips multiple items on a character.
    item_instance_ids should be a list of instance IDs.
    """
    if not token_manager.get_access_token():
        print("Error: User not authenticated. Cannot equip items.")
        return False, "User not authenticated."

    destiny_membership_id, destiny_membership_type = get_current_user_primary_destiny_membership()
    if not destiny_membership_id or destiny_membership_type is None:
        return False, "Could not determine primary Destiny membership."

    try:
        print(f"Attempting to equip items {item_instance_ids} on character {character_id}.")
        # The response from equip_items is a DestinyEquipItemResults object
        equip_results_response = equip_items(
            item_ids=item_instance_ids,
            character_id=character_id,
            membership_type=destiny_membership_type
        )
        
        # equipResults is a list of DestinyEquipItemResult
        equip_results = equip_results_response.get("equipResults", [])
        
        all_successful = True
        error_messages = []
        for result in equip_results:
            item_id = result.get("itemInstanceId")
            status_code = result.get("equipStatus")
            if status_code != 1: # Not PlatformErrorCodes.Success
                all_successful = False
                error_messages.append(f"Item {item_id}: Failed (Code {status_code})")
                print(f"Failed to equip item {item_id}. Error Code: {status_code}")
            else:
                print(f"Successfully equipped item {item_id}.")
        
        if all_successful:
            return True, "All items equipped successfully."
        else:
            return False, "One or more items failed to equip: " + "; ".join(error_messages)
            
    except Exception as e:
        print(f"Error equipping multiple items: {e}")
        return False, str(e)


if __name__ == '__main__':
    # Example Usage (requires tokens to be stored and API key to be set)
    # This is conceptual and requires actual item/character IDs.
    if not token_manager.get_access_token():
        print("Please authenticate first using the auth_ui.py example.")
    else:
        print("Authenticated. Ready for item action tests (ensure you have valid IDs).")
        
        # --- !!! DANGER ZONE: These actions modify your Destiny account state. !!! ---
        # --- !!! Use with extreme caution and valid (preferably test) item IDs. !!! ---

        # Replace with actual data from your account after fetching inventory
        TEST_CHARACTER_ID = "YOUR_CHARACTER_ID_HERE" # e.g. from get_character_inventories_for_current_user()
        
        # Example: Moving an item (replace with a real item's IDs from your inventory)
        # You would get these from the inventory fetching functions
        TEST_ITEM_INSTANCE_ID_TO_VAULT = "ITEM_INSTANCE_ID_FROM_CHARACTER_INV" 
        TEST_ITEM_HASH_TO_VAULT = 0 # ITEM_DEFINITION_HASH_OF_ABOVE_ITEM
        
        # if TEST_ITEM_INSTANCE_ID_TO_VAULT != "ITEM_INSTANCE_ID_FROM_CHARACTER_INV" and TEST_CHARACTER_ID != "YOUR_CHARACTER_ID_HERE":
        #     print(f"\nTesting move_item_to_vault for item {TEST_ITEM_INSTANCE_ID_TO_VAULT} on char {TEST_CHARACTER_ID}")
        #     success, message = move_item_to_vault(
        #         item_reference_hash=TEST_ITEM_HASH_TO_VAULT, 
        #         item_instance_id=TEST_ITEM_INSTANCE_ID_TO_VAULT, 
        #         stack_size=1, 
        #         character_id=TEST_CHARACTER_ID
        #     )
        #     print(f"Move to Vault Result: {success}, Message: {message}")
        # else:
        #     print("\nSkipping move_item_to_vault test: Placeholder IDs not replaced.")

        # Example: Moving an item from vault to character
        # TEST_ITEM_INSTANCE_ID_FROM_VAULT = "ITEM_INSTANCE_ID_FROM_VAULT_INV"
        # TEST_ITEM_HASH_FROM_VAULT = 0 # ITEM_DEFINITION_HASH_OF_ABOVE_ITEM
        # TARGET_CHARACTER_ID_FOR_VAULT_ITEM = TEST_CHARACTER_ID

        # if TEST_ITEM_INSTANCE_ID_FROM_VAULT != "ITEM_INSTANCE_ID_FROM_VAULT_INV" and TARGET_CHARACTER_ID_FOR_VAULT_ITEM != "YOUR_CHARACTER_ID_HERE":
        #     print(f"\nTesting move_item_to_character for item {TEST_ITEM_INSTANCE_ID_FROM_VAULT} to char {TARGET_CHARACTER_ID_FOR_VAULT_ITEM}")
        #     success, message = move_item_to_character(
        #         item_reference_hash=TEST_ITEM_HASH_FROM_VAULT,
        #         item_instance_id=TEST_ITEM_INSTANCE_ID_FROM_VAULT,
        #         stack_size=1,
        #         target_character_id=TARGET_CHARACTER_ID_FOR_VAULT_ITEM
        #     )
        #     print(f"Move to Character Result: {success}, Message: {message}")
        # else:
        #     print("\nSkipping move_item_to_character test: Placeholder IDs not replaced.")


        # Example: Equipping an item
        # TEST_ITEM_INSTANCE_ID_TO_EQUIP = "UNEQUIPPED_ITEM_INSTANCE_ID_ON_CHARACTER"
        # if TEST_ITEM_INSTANCE_ID_TO_EQUIP != "UNEQUIPPED_ITEM_INSTANCE_ID_ON_CHARACTER" and TEST_CHARACTER_ID != "YOUR_CHARACTER_ID_HERE":
        #     print(f"\nTesting equip_item_on_character for item {TEST_ITEM_INSTANCE_ID_TO_EQUIP} on char {TEST_CHARACTER_ID}")
        #     success, message = equip_item_on_character(
        #         item_instance_id=TEST_ITEM_INSTANCE_ID_TO_EQUIP,
        #         character_id=TEST_CHARACTER_ID
        #     )
        #     print(f"Equip Item Result: {success}, Message: {message}")
        # else:
        #     print("\nSkipping equip_item_on_character test: Placeholder IDs not replaced.")
        
        # Example: Equipping multiple items
        # TEST_ITEM_IDS_TO_EQUIP_LIST = ["INSTANCE_ID_1", "INSTANCE_ID_2"] # Replace with actual instance IDs
        # if TEST_ITEM_IDS_TO_EQUIP_LIST[0] != "INSTANCE_ID_1" and TEST_CHARACTER_ID != "YOUR_CHARACTER_ID_HERE":
        #     print(f"\nTesting equip_multiple_items_on_character for items {TEST_ITEM_IDS_TO_EQUIP_LIST} on char {TEST_CHARACTER_ID}")
        #     success, message = equip_multiple_items_on_character(
        #         item_instance_ids=TEST_ITEM_IDS_TO_EQUIP_LIST,
        #         character_id=TEST_CHARACTER_ID
        #     )
        #     print(f"Equip Multiple Items Result: {success}, Message: {message}")
        # else:
        #     print("\nSkipping equip_multiple_items_on_character test: Placeholder IDs not replaced.")

        print("\nItem actions example finished. Remember to use actual IDs for real tests.")
