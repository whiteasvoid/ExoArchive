# src/api/__init__.py

from .destiny_api_client import (
    get_linked_profiles,
    get_profile,
    get_character_inventory,
    DestinyComponentType
)
# oauth_manager might be more of an internal auth thing, but if direct access needed:
# from .oauth_manager import ... 
# manifest_manager would be exposed if used directly by UI/main logic
# from .manifest_manager import ...

# item_search, player_information, vendor_manager are likely higher-level
# abstractions that would use destiny_api_client internally.
# They can be exposed here if they are meant to be the primary interface
# for those functionalities from other parts of the application.
# For example:
# from .player_information import get_full_inventory_details # Hypothetical function

__all__ = [
    "get_linked_profiles",
    "get_profile",
    "get_character_inventory",
    "transfer_item", 
    "equip_item",    
    "equip_items",   
    "DestinyComponentType",
)

from .player_information import (
    get_current_user_primary_destiny_membership,
    get_character_inventories_for_current_user,
    get_profile_inventory_for_current_user
)

from .item_actions import ( # Added item_actions
    move_item_to_vault,
    move_item_to_character,
    equip_item_on_character,
    equip_multiple_items_on_character
)

# item_search, vendor_manager are likely higher-level
# abstractions that would use destiny_api_client internally.
# They can be exposed here if they are meant to be the primary interface
# for those functionalities from other parts of the application.
# from .item_search import ...
# from .vendor_manager import ...


__all__ = [
    # destiny_api_client exports
    "get_linked_profiles",
    "get_profile", # This is the one from destiny_api_client
    "get_character_inventory",
    "transfer_item",
    "equip_item",
    "equip_items",
    "DestinyComponentType",

    # player_information exports
    "get_current_user_primary_destiny_membership",
    "get_character_inventories_for_current_user",
    "get_profile_inventory_for_current_user",

    # item_actions exports
    "move_item_to_vault",
    "move_item_to_character",
    "equip_item_on_character",
    "equip_multiple_items_on_character",
]
