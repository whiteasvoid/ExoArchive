# Este é o arquivo principal que inicia o programa
# Importamos as funções necessárias de outros arquivos
from src.database.database_handler import create_manifest_data
from src.api.manifest_manager import get_manifest
from src.api.item_search import search_items_by_name, get_item_details, search_items_by_type
from src.api.vendor_manager import display_xur_items
from src.api.player_information import display_player_variables, display_player_characters

# Função principal que executa o programa
def main():
    # Variáveis temporárias
    membership_type = 1
    destiny_membership_id = "4611686018554152113"
    character_id = "2305843010708964224"

    # Carrega ou cria os dados do manifesto
    manifest_data = create_manifest_data()
    
    # Mostra as tabelas disponíveis no manifesto
    print("\n" + "="*50)
    print("Tabelas disponíveis no manifesto:")
    for table_name in manifest_data.keys():
        print(f"- {table_name}: {len(manifest_data[table_name])} entradas")

    # Mostra as informações técnicas do utilizador
    display_player_variables("cosmy", '0588')

    # Mostra as informações técnicas dos personagens do utilizador
    display_player_characters(membership_type, destiny_membership_id)

    # Exemplo: Procurar itens com o nome "Gjallarhorn"
    search_items_by_name(manifest_data, "Gjallarhorn")

    # Exemplo: Procurar itens com a hash "1363886209"
    get_item_details(manifest_data, 1363886209)

    # Exemplo: Procurar itens com o tipo "Exotic" e com descrição
    search_items_by_type(manifest_data, "Exotic", True)

    # Exemplo: Mostrar itens do Xur
    display_xur_items(manifest_data, membership_type, destiny_membership_id, character_id)

# Verifica se este arquivo está sendo executado diretamente
if __name__ == "__main__":
    main()