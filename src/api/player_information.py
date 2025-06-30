# Este arquivo lida com as chamadas à API para obter as informações do utilizador
import requests
import os # Added for new functions
from src.api.oauth_manager import update_headers_with_token

# --- New Imports for Enhanced Functionality ---
from .destiny_api_client import get_profile as new_get_profile, get_character_inventory, get_linked_profiles, DestinyComponentType
from src.auth import token_manager # To get current user's membership_id if needed


# Função para obter as informações do utilizador
def get_player_variables(username, tag):
    """
    Obtém as variáveis necessárias relacionadas ao player
    
    Utility: https://bungie-net.github.io/#/components/schemas/User.ExactSearchRequest

    Args:
        username (str): Nome da conta (cosmy).
        tag (int16): Tag da conta (0588).
    
    Returns:
        dict: Informações técnicas relacionadas ao player
    """
    BODY = {
        "displayName": username,
        "displayNameCode": tag
    }
    
    # Para fazer a pesquisa em todas as plataformas
    membership_type = -1

    # URL do endpoint da API para os dados do vendedor
    url = f"https://www.bungie.net/Platform/Destiny2/SearchDestinyPlayerByBungieName/{membership_type}/"
    
    print(f"A consultar os dados do utilizador em: {url}")
    
    # Obtém cabeçalhos com token OAuth
    headers = update_headers_with_token() # This uses the old oauth_manager
    
    # Faz a requisição à API
    response = requests.post(url, headers=headers, json=BODY)
    
    # Verifica se a requisição foi bem-sucedida
    if response.status_code == 200:
        data = response.json()
        if data.get("Response"):
            print("Informações relacionadas ao utilizador obtidas com sucesso!")
            return data["Response"]
        else:
            print("Erro: Resposta da API não contém dados válidos.")
            return None
    else:
        print(f"Erro na requisição: {response.status_code} - {response.text}")
        return None

# Função para obter as informações dos personagens do utilizador
def get_player_characters(membershipType, membershipId):
    """
    Obtém as variáveis necessárias relacionadas ao player
    
    Utility: https://bungie-net.github.io/#Destiny2.GetProfile
    Args:
        membershipType (int32): Informação obtida através da função get_player_variables.
        membershipId (int64): Informação obtida através da função get_player_variables.
    
    Returns:
        dict: Informações técnicas relacionadas ao perfil do player
    """
    # https://bungie-net.github.io/#/components/schemas/Destiny.DestinyComponentType
    components = "200" # Corresponds to DestinyComponentType.CHARACTERS

    url = f"https://www.bungie.net/Platform/Destiny2/{membershipType}/Profile/{membershipId}/?components={components}"

    print(f"A consultar os perfis do utilizador em: {url}")

    # Obtém cabeçalhos com token OAuth
    headers = update_headers_with_token() # This uses the old oauth_manager
    
    # Faz a requisição à API
    response = requests.get(url, headers=headers)

    # Verifica se a requisição foi bem-sucedida
    if response.status_code == 200:
        data = response.json()
        if data.get("Response"):
            print("Informações relacionadas ao utilizador obtidas com sucesso!")
            return data["Response"]
        else:
            print("Erro: Resposta da API não contém dados válidos.")
            return None
    else:
        print(f"Erro na requisição: {response.status_code} - {response.text}")
        return None

# Função para exibir as informações do utilizador
def display_player_variables(username, tag):
    """
    Obtém as variáveis necessárias relacionadas ao player

    Args:
        username (str): Nome da conta (cosmy).
        tag (int16): Tag da conta (0588).
    
    Returns:
        dict: Informações técnicas relacionadas ao player
    """
    # Obtém os dados do utilizador
    player_data = get_player_variables(username, tag)
    
    if not player_data:
        print("Não foi possível obter as informações do utilizador.")
        return
    
    player_data = player_data[0]

    membershipId_data = player_data.get("membershipId", {})
    membershipType_data = player_data.get("membershipType", {})
    if not membershipId_data or not membershipType_data:
        print("Não foi encontrado o membership do utilizador.")
        return
    
    print("\n=== Informações associadas ao utilizador ===")
    
    # Mostra as informações
    print(f"membershipId: {membershipId_data}")
    print(f"membershipType: {membershipType_data}")

# Função para exibir as informações do perfil utilizador
def display_player_characters(membershipType, membershipId):
    """
    Obtém as variáveis necessárias relacionadas ao player
    
    Utility: https://bungie-net.github.io/#Destiny2.GetProfile
    Args:
        membershipType (int32): Informação obtida através da função get_player_variables.
        membershipId (int64): Informação obtida através da função get_player_variables.
    
    Returns:
        dict: Informações técnicas relacionadas ao perfil do player
    """
    # Obtém os dados do utilizador
    player_profile_data = get_player_characters(membershipType, membershipId)
    
    if not player_profile_data:
        print("Não foi possível obter as informações do perfil do utilizador.")
        return
    
    characters = player_profile_data.get("characters", {}).get("data", {})

    if not characters:
        print("Nenhum personagem encontrado para este utilizador.")
        return
    
    print("\n=== Informações associadas aos personagens do utilizador ===")

    # Itera sobre os personagens
    for character_id, character_data in characters.items():
        class_type = character_data.get("classType", 0)
        # Converte o classType para o nome da classe
        class_name = {0: "Titan", 1: "Hunter", 2: "Warlock"}.get(class_type, "Desconhecido")
        light_level = character_data.get("light", "Desconhecido")
        race_type = character_data.get("raceType", "Desconhecido")
        # Converte o raceType para o nome da raça
        race_name = {0: "Human", 1: "Awoken", 2: "Exo"}.get(race_type, "Desconhecido")
        gender_type = character_data.get("genderType", "Desconhecido")
        # Converte o genderType para o nome do género
        gender_name = {0: "Male", 1: "Female"}.get(gender_type, "Desconhecido")
        
        print(f"\nCharacter ID: {character_id}")
        print(f"Class: {class_name}")
        print(f"Power Level: {light_level}")
        print(f"Race: {race_name}")
        print(f"Gender: {gender_name}")

# --- New functions using destiny_api_client and token_manager ---

def get_current_user_primary_destiny_membership():
    """
    Retrieves the primary Destiny membership ID and type for the currently authenticated user.
    This is useful for knowing which profile to fetch data for.
    Returns:
        tuple: (destiny_membership_id, destiny_membership_type) or (None, None) if not found.
    """
    bnet_membership_id = token_manager.get_membership_id()
    if not bnet_membership_id:
        print("Error: No authenticated Bungie.net user found (token_manager has no membership_id).")
        return None, None

    try:
        # Assuming the membership_id from token_manager is the Bungie.net membershipId (Type 254)
        linked_profiles_response = get_linked_profiles(bnet_membership_id, membership_type=254)
        
        if linked_profiles_response and linked_profiles_response.get("profiles"):
            primary_profile = None
            # Prefer primary cross-save profile
            primary_profile = next((p for p in linked_profiles_response["profiles"] if p.get("isCrossSavePrimary", False)), None)
            
            if not primary_profile and linked_profiles_response["profiles"]:
                # Fallback: sort by dateLastPlayed if available, to get the most recent
                sorted_profiles = sorted(linked_profiles_response["profiles"], key=lambda p: p.get("dateLastPlayed", ""), reverse=True)
                if sorted_profiles:
                    primary_profile = sorted_profiles[0]

            if primary_profile:
                membership_id = primary_profile.get("membershipId")
                membership_type = primary_profile.get("membershipType")
                if membership_id and membership_type is not None:
                    return membership_id, membership_type
                else:
                    print(f"Found a profile but it's missing membershipId or membershipType: {primary_profile}")
            else:
                print("No suitable Destiny profiles found in linked_profiles_response.")
        else:
            print(f"Could not fetch or parse linked profiles for BungieNet membership ID: {bnet_membership_id}")
            print(f"API Response: {linked_profiles_response}")
            
    except Exception as e:
        print(f"Error getting primary Destiny membership: {e}")
        
    return None, None


def get_character_inventories_for_current_user():
    """
    Fetches equipped and unequipped inventory for all characters of the authenticated user.
    Returns:
        dict: {character_id: {"equipment": [], "inventory": [], "item_components": {}}, ...} or None
    """
    destiny_membership_id, destiny_membership_type = get_current_user_primary_destiny_membership()

    if not destiny_membership_id or destiny_membership_type is None:
        return None

    try:
        profile_components = [DestinyComponentType.CHARACTERS]
        # Using the new_get_profile to avoid name collision if old get_profile is kept
        profile_response = new_get_profile(destiny_membership_type, destiny_membership_id, profile_components)
        
        character_ids_data = profile_response.get("characters", {}).get("data", {})
        if not character_ids_data: # Check if character_ids_data itself is None or empty
            print("No characters data found for this profile.")
            return {}
        
        character_ids = list(character_ids_data.keys()) # Get all character IDs
        if not character_ids:
            print("No character IDs found for this profile.")
            return {}


        all_character_inventories = {}
        # Define components needed for detailed inventory view
        inventory_components_list = [
            DestinyComponentType.CHARACTER_EQUIPMENT,    # Equipped items
            DestinyComponentType.CHARACTER_INVENTORIES,  # Unequipped items
            DestinyComponentType.ITEM_INSTANCES,         # For item instance details (level, quality, etc.)
            DestinyComponentType.ITEM_SOCKETS,           # For equipped mods/perks in sockets
            DestinyComponentType.ITEM_STATS,             # For base item stats
            DestinyComponentType.ITEM_PERKS,             # For item perks
            DestinyComponentType.ITEM_REUSABLE_PLUGS,    # For state of reusable plugs
            DestinyComponentType.ITEM_OBJECTIVES,        # For objectives on items like bounties
        ]

        for char_id in character_ids:
            print(f"Fetching detailed inventory for character: {char_id}")
            char_inventory_response = get_character_inventory(
                destiny_membership_type, 
                destiny_membership_id, 
                char_id, 
                inventory_components_list
            )
            
            equipment = char_inventory_response.get("equipment", {}).get("data", {}).get("items", [])
            inventory = char_inventory_response.get("inventory", {}).get("data", {}).get("items", [])
            item_components_data = char_inventory_response.get("itemComponents", {})


            all_character_inventories[char_id] = {
                "equipment": equipment,
                "inventory": inventory,
                "item_instances": item_components_data.get("instances", {}).get("data",{}),
                "item_sockets": item_components_data.get("sockets", {}).get("data",{}),
                "item_stats": item_components_data.get("stats", {}).get("data",{}),
                "item_perks": item_components_data.get("perks", {}).get("data",{}),
                "item_reusable_plugs": item_components_data.get("reusablePlugs", {}).get("data",{}),
                "item_objectives": item_components_data.get("objectives", {}).get("data",{})
            }
            print(f"Character {char_id}: {len(equipment)} equipped, {len(inventory)} unequipped.")

        return all_character_inventories

    except Exception as e:
        print(f"Error fetching character inventories: {e}")
        return None

def get_profile_inventory_for_current_user():
    """
    Fetches profile-wide inventory (e.g., Vault) for the authenticated user.
    Returns:
        dict: {"items": [], "item_components": {}} or None if an error occurs.
    """
    destiny_membership_id, destiny_membership_type = get_current_user_primary_destiny_membership()

    if not destiny_membership_id or destiny_membership_type is None:
        return None
    
    try:
        profile_inventory_components_list = [
            DestinyComponentType.PROFILE_INVENTORIES,
            DestinyComponentType.ITEM_INSTANCES,
            DestinyComponentType.ITEM_SOCKETS,
            DestinyComponentType.ITEM_STATS,
            DestinyComponentType.ITEM_PERKS,
            DestinyComponentType.ITEM_REUSABLE_PLUGS,
            DestinyComponentType.ITEM_OBJECTIVES,
        ]
        # Using the new_get_profile to avoid name collision
        profile_inv_response = new_get_profile(destiny_membership_type, destiny_membership_id, profile_inventory_components_list)
        
        inventory_items = profile_inv_response.get("profileInventory", {}).get("data", {}).get("items", [])
        item_components_data = profile_inv_response.get("itemComponents", {})
        
        return {
            "items": inventory_items,
            "item_instances": item_components_data.get("instances", {}).get("data",{}),
            "item_sockets": item_components_data.get("sockets", {}).get("data",{}),
            "item_stats": item_components_data.get("stats", {}).get("data",{}),
            "item_perks": item_components_data.get("perks", {}).get("data",{}),
            "item_reusable_plugs": item_components_data.get("reusablePlugs", {}).get("data",{}),
            "item_objectives": item_components_data.get("objectives", {}).get("data",{})
        }

    except Exception as e:
        print(f"Error fetching profile inventory: {e}")
        return None


if __name__ == '__main__':
    # Example Usage (requires tokens to be stored via auth_ui.py or similar)
    # Ensure BUNGIE_API_KEY is set
    if not os.getenv("BUNGIE_API_KEY"):
        print("BUNGIE_API_KEY not set. Please set it in your environment or .env file.")
    elif not token_manager.get_access_token(): # Uses the new token_manager
        print("No access token found. Run auth_ui.py to authenticate first.")
    else:
        print("Fetching primary Destiny membership using new functions...")
        primary_id, primary_type = get_current_user_primary_destiny_membership()
        if primary_id and primary_type is not None:
            print(f"Primary Destiny Membership: ID={primary_id}, Type={primary_type}")

            print("\nFetching character inventories using new functions...")
            char_inventories = get_character_inventories_for_current_user()
            if char_inventories is not None:
                print(f"Found inventories for {len(char_inventories)} character(s).")
                for char_id, data in char_inventories.items():
                    print(f"  Character {char_id}: {len(data.get('equipment', []))} equipped, {len(data.get('inventory',[]))} unequipped items.")
                    # Example: Accessing item instance data for the first equipped item, if any
                    # if data.get('equipment'):
                    #     first_equipped_item_hash = data['equipment'][0].get('itemHash')
                    #     first_equipped_item_instance_id = data['equipment'][0].get('itemInstanceId')
                    #     if first_equipped_item_instance_id and data.get('item_instances'):
                    #        instance_data = data['item_instances'].get(str(first_equipped_item_instance_id))
                    #        if instance_data:
                    #            print(f"    First equipped item ({first_equipped_item_hash}) primary stat: {instance_data.get('primaryStat', {}).get('value')}")


            print("\nFetching profile inventory (Vault) using new functions...")
            profile_inventory_data = get_profile_inventory_for_current_user()
            if profile_inventory_data and profile_inventory_data.get("items"):
                print(f"Found {len(profile_inventory_data['items'])} items in profile inventory (Vault).")
                # Example: Accessing item instance data for the first vault item, if any and instanced
                # if profile_inventory_data['items']:
                #     first_vault_item_instance_id = profile_inventory_data['items'][0].get('itemInstanceId')
                #     if first_vault_item_instance_id and profile_inventory_data.get('item_instances'):
                #         instance_data = profile_inventory_data['item_instances'].get(str(first_vault_item_instance_id))
                #         if instance_data:
                #             print(f"    First vault item primary stat: {instance_data.get('primaryStat', {}).get('value')}")
            elif profile_inventory_data is not None:
                 print("Profile inventory (Vault) is empty or data structure unexpected.")
            else:
                print("Failed to fetch profile inventory.")
        else:
            print("Could not determine primary Destiny membership using new functions.")

    print("\nPlayer Information module example finished.")