# Este arquivo lida com as chamadas à API para obter os itens do vendedor Xur
import requests
from src.api.oauth_manager import update_headers_with_token

# Função para obter os itens que o Xur está vendendo
def get_xur_inventory(membership_type, destiny_membership_id, character_id):
    """
    Obtém os itens que o Xur está vendendo para um personagem específico.
    
    Args:
        membership_type (int): Tipo de associação (ex.: 3 para Steam).
        destiny_membership_id (str): ID da associação do jogador.
        character_id (str): ID do personagem do jogador.
    
    Returns:
        dict: Dados do inventário do Xur, ou None se houver erro.
    """
    # Hash do Xur
    xur_vendor_hash = "2190858386"

    # https://bungie-net.github.io/#/components/schemas/Destiny.DestinyComponentType
    components = "402"

    # https://bungie-net.github.io/#/components/schemas/Destiny.DestinyVendorFilter
    filter = "0"

    query_params = f"components={components}"
    if filter is not None:
        query_params += f"&filter={filter}"
    
    # URL do endpoint da API para os dados do vendedor
    url = f"https://www.bungie.net/Platform/Destiny2/{membership_type}/Profile/{destiny_membership_id}/Character/{character_id}/Vendors/{xur_vendor_hash}/?{query_params}"
    
    print(f"A consultar inventário do Xur em: {url}")
    
    # Obtém cabeçalhos com token OAuth
    headers = update_headers_with_token()
    
    # Faz a requisição à API
    response = requests.get(url, headers=headers)
    
    # Verifica se a requisição foi bem-sucedida
    if response.status_code == 200:
        data = response.json()
        if data.get("Response"):
            print("Inventário do Xur obtido com sucesso!")
            return data["Response"]
        else:
            print("Erro: Resposta da API não contém dados válidos.")
            return None
    else:
        print(f"Erro na requisição: {response.status_code} - {response.text}")
        return None

# Função para exibir os itens do Xur usando o manifesto
def display_xur_items(manifest_data, membership_type, destiny_membership_id, character_id):
    """
    Exibe os itens que o Xur está vendendo, usando os dados do manifesto.
    
    Args:
        manifest_data (dict): Dados do manifesto carregados.
        membership_type (int): Tipo de associação (ex.: 3 para Steam).
        destiny_membership_id (str): ID da associação do jogador.
        character_id (str): ID do personagem do jogador.
    """
    from item_search import get_item_details
    
    # Obtém os dados do inventário do Xur
    xur_data = get_xur_inventory(membership_type, destiny_membership_id, character_id)
    
    if not xur_data:
        print("Não foi possível obter os itens do Xur.")
        return
    
    # Acessa a seção de vendas do Xur
    sales_data = xur_data.get("sales", {}).get("data", {})
    if not sales_data:
        print("Nenhum item à venda encontrado para o Xur.")
        return
    
    print("\n=== ITENS À VENDA PELO XUR ===")
    
    # Itera sobre os itens à venda
    for sale_item in sales_data.values():
        item_hash = sale_item.get("itemHash")
        if item_hash:
            print("\n" + "-"*50)
            # Usa a função existente para exibir detalhes do item
            get_item_details(manifest_data, item_hash)
        else:
            print("Item sem hash encontrado, ignorando...")