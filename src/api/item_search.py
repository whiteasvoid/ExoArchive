# Este arquivo contém funções para procurar e mostrar detalhes de items
from src.config.config import hash_dict

# Função que procura items pelo nome
def search_items_by_name(tableData, searchValue):
    print(f"\nA procurar items com '{searchValue}'...")
    
    # Verifica se a tabela de items existe
    if 'DestinyInventoryItemDefinition' not in tableData:
        print("Tabela de items não encontrada nos dados do manifesto")
        return
    
    # Obtém todos os items
    items = tableData['DestinyInventoryItemDefinition']
    foundItems = []
    
    # Procura items cujo nome contém o termo de pesquisa
    for id_hash, item in items.items():
        if 'displayProperties' in item and 'name' in item['displayProperties']:
            nome = item['displayProperties']['name']
            if searchValue.lower() in nome.lower():
                foundItems.append((id_hash, item))
    
    # Mostra os resultados
    if foundItems:
        print(f"Encontrados {len(foundItems)} items:")
        # Mostra apenas os primeiros 10 resultados
        for index, (id_hash, item) in enumerate(foundItems[:10]):
            propriedades = item.get('displayProperties', {})
            nome = propriedades.get('name', 'Desconhecido')
            descricao = propriedades.get('description', 'Sem descrição')
            tipo_item = item.get('itemTypeDisplayName', 'Tipo Desconhecido')
            
            print(f"\nNome: {nome}")
            print(f"Hash: {id_hash}")
            print(f"Tipo: {tipo_item}")
            print(f"Descrição: {descricao[:300]}...")
            
            if index < len(foundItems[:10]) - 1:
                print("=" * 20)
    else:
        print("Nenhum item encontrado com esse termo de pesquisa")

# Função que procura items pelo tipo
def search_items_by_type(tableData, searchValue, hasDescription):
    print(f"\nA procurar items com '{searchValue}'...")
    
    # Verifica se a tabela de items existe
    if 'DestinyInventoryItemDefinition' not in tableData:
        print("Tabela de items não encontrada nos dados do manifesto")
        return
    
    # Obtém todos os items
    items = tableData['DestinyInventoryItemDefinition']
    foundItems = []
    
    # Procura items cujo tipo contém o termo de pesquisa
    for id_hash, item in items.items():
        if 'inventory' in item and 'tierTypeName' in item['inventory']:
            tierName = item['inventory']['tierTypeName']
            description = item['displayProperties']['description']
            if searchValue.lower() in tierName.lower():
                if hasDescription:
                    if description != "":
                        foundItems.append((id_hash, item))
                else:
                    foundItems.append((id_hash, item))
    
    # Mostra os resultados
    if foundItems:
        print(f"Encontrados {len(foundItems)} items:")
        # Mostra apenas os primeiros 10 resultados
        for id_hash, item in foundItems[:10]:
            propriedades = item.get('displayProperties', {})
            nome = propriedades.get('name', 'Desconhecido')
            descricao = propriedades.get('description', 'Sem descrição')
            tipo_item = item.get('itemTypeDisplayName', 'Tipo Desconhecido')
            tier_item = item.get('inventory', {}).get('tierTypeName', 'Desconhecido')
            
            print(f"\nNome: {nome}")
            print(f"Hash: {id_hash}")
            print(f"Tipo: {tipo_item}")
            print(f"Raridade: {tier_item}")
            print(f"Descrição: {descricao[:300]}...")
    else:
        print("Nenhum item encontrado com esse termo de pesquisa")

# Função que mostra detalhes de um item específico
def get_item_details(tableData, hash_item):
    # Verifica se a tabela de items existe
    if 'DestinyInventoryItemDefinition' not in tableData:
        print("Tabela de items não encontrada nos dados do manifesto")
        return None
    
    items = tableData['DestinyInventoryItemDefinition']
    
    # Verifica se o item existe
    if hash_item in items:
        item = items[hash_item]
        propriedades = item.get('displayProperties', {})
        
        print(f"\n=== DETALHES DO ITEM ===")
        print(f"Nome: {propriedades.get('name', 'Desconhecido')}")
        print(f"Hash: {hash_item}")
        print(f"Tipo: {item.get('itemTypeDisplayName', 'Tipo Desconhecido')}")
        print(f"Nível: {item.get('inventory', {}).get('tierTypeName', 'Nível Desconhecido')}")
        print(f"Descrição: {propriedades.get('description', 'Sem descrição')}")
        
        return item
    else:
        print(f"Item com hash {hash_item} não encontrado")
        return None