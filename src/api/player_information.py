# Este arquivo lida com as chamadas à API para obter as informações do utilizador
import requests
from src.api.oauth_manager import update_headers_with_token

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
    headers = update_headers_with_token()
    
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
    components = "200"

    url = f"https://www.bungie.net/Platform/Destiny2/{membershipType}/Profile/{membershipId}/?components={components}"

    print(f"A consultar os perfis do utilizador em: {url}")

    # Obtém cabeçalhos com token OAuth
    headers = update_headers_with_token()
    
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