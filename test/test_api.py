# Para executar este ficheiro de teste, navegar até à raiz do projeto e usar:
# python -m test.test_api
# Isto permite que o Python reconheça a estrutura de módulos (src/) corretamente
# em vez de executar diretamente: python test/test_api.py

# Este arquivo contém testes unitários para o projeto ExoArchive
import unittest
import json
import os
from unittest.mock import patch, MagicMock
from src.api.oauth_manager import get_access_token, load_access_token
from src.api.vendor_manager import get_xur_inventory
from src.api.player_information import get_player_variables, get_player_characters
from src.api.manifest_manager import ensure_manifest_folder
from src.database.database_handler import build_dict
from src.api.item_search import search_items_by_name, get_item_details
from src.config.config import HEADERS, MANIFEST_FOLDER, hash_dict

class TestExoArchive(unittest.TestCase):
    """Classe para testar os módulos do projeto ExoArchive."""
    
    def setUp(self):
        """Configura o ambiente para cada teste."""
        # Define o diretório base do projeto (raiz do ExoArchive)
        # Como test_api.py está em tests/, subimos dois níveis
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.token_file = os.path.join(self.base_dir, "destiny_manifest", "oauth_token.json")
        self.manifest_path = os.path.join(self.base_dir, "destiny_manifest")
        # Dados de exemplo para simular o manifesto
        self.sample_manifest_data = {
            "DestinyInventoryItemDefinition": {
                "1363886209": {
                    "displayProperties": {"name": "Gjallarhorn", "description": "Arma exótica"},
                    "itemTypeDisplayName": "Rocket Launcher",
                    "inventory": {"tierTypeName": "Exotic"}
                }
            }
        }

    # Testes para oauth_manager.py
    @patch("requests.post")
    def test_get_access_token(self, mock_post):
        """Testa a obtenção do token de acesso."""
        # Simula uma resposta da API
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "access_token": "test_access",
            "refresh_token": "test_refresh"
        }
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            result = get_access_token("test_code")
            self.assertEqual(result["access_token"], "test_access")
            mock_file.assert_called_with(self.token_file, "w")

    def test_load_access_token(self):
        """Testa o carregamento de um token salvo."""
        sample_token = {"access_token": "test_access", "refresh_token": "test_refresh"}
        with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(sample_token))):
            with patch("os.path.exists", return_value=True):
                result = load_access_token()
                self.assertEqual(result, sample_token)

    # Testes para vendor_manager.py
    @patch("requests.get")
    def test_get_xur_inventory(self, mock_get):
        """Testa a obtenção do inventário do Xur."""
        # Simula uma resposta da API
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "Response": {"sales": {"data": {"item1": {"itemHash": "1363886209"}}}}
        }
        with patch("src.api.vendor_manager.update_headers_with_token", return_value=HEADERS):
            result = get_xur_inventory(1, "4611686018554152113", "2305843010708964224")
            self.assertIn("sales", result)

    # Testes para player_information.py
    @patch("requests.post")
    def test_get_player_variables(self, mock_post):
        """Testa a obtenção das variáveis do jogador."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "Response": [{"membershipId": "123", "membershipType": 1}]
        }
        with patch("src.api.player_information.update_headers_with_token", return_value=HEADERS):
            result = get_player_variables("cosmy", "0588")
            self.assertEqual(result[0]["membershipId"], "123")

    @patch("requests.get")
    def test_get_player_characters(self, mock_get):
        """Testa a obtenção dos personagens do jogador."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "Response": {"characters": {"data": {"char1": {"classType": 0, "light": 1600}}}}
        }
        with patch("src.api.player_information.update_headers_with_token", return_value=HEADERS):
            result = get_player_characters(1, "123")
            self.assertIn("characters", result)

    # Testes para manifest_manager.py
    @patch("os.makedirs")
    def test_ensure_manifest_folder(self, mock_makedirs):
        """Testa a criação da pasta do manifesto."""
        with patch("os.path.exists", return_value=False):
            result = ensure_manifest_folder()
            self.assertEqual(result, self.manifest_path)
            mock_makedirs.assert_called_once()

    # Testes para database_handler.py
@patch("src.database.database_handler.ensure_manifest_folder")
@patch("src.database.database_handler.sqlite3")
@patch("os.path.exists")
def test_build_dict(self, mock_exists, mock_sqlite, mock_ensure_manifest):
    """Testa a construção do dicionário do manifesto."""
    # Simula o caminho do manifesto
    mock_ensure_manifest.return_value = self.manifest_path
    mock_exists.return_value = True  # Simula que o arquivo do manifesto existe
    
    # Dados de exemplo que serão retornados pela consulta SQL
    mock_data = {
        "hash": "1363886209",
        "displayProperties": {"name": "Gjallarhorn"},
        "itemTypeDisplayName": "Rocket Launcher",
        "inventory": {"tierTypeName": "Exotic"}
    }
    
    # Configura o mock para o cursor e conexão
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    
    # O fetchall deve retornar uma lista de tuplas, onde cada tupla contém o JSON como string
    mock_cursor.fetchall.return_value = [(json.dumps(mock_data),)]
    mock_connection.cursor.return_value = mock_cursor
    
    # Configura o context manager para a conexão
    mock_sqlite.connect.return_value.__enter__.return_value = mock_connection
    mock_sqlite.connect.return_value.__exit__.return_value = None
    
    # Executa o teste
    result = build_dict({"DestinyInventoryItemDefinition": "hash"})
    
    # Debug output
    print(f"Resultados de build_dict: {result}")
    print(f"Mock execute chamado: {mock_cursor.execute.called}")
    print(f"Mock fetchall chamado: {mock_cursor.fetchall.called}")
    
    # Verificações
    self.assertIsInstance(result, dict)
    self.assertIn("DestinyInventoryItemDefinition", result)
    
    # Verifica se o hash está presente no resultado
    if "DestinyInventoryItemDefinition" in result and result["DestinyInventoryItemDefinition"]:
        self.assertIn("1363886209", result["DestinyInventoryItemDefinition"])
        self.assertEqual(
            result["DestinyInventoryItemDefinition"]["1363886209"]["displayProperties"]["name"], 
            "Gjallarhorn"
        )
    else:
        # Se o resultado estiver vazio, o teste deve falhar com uma mensagem clara
        self.fail(f"build_dict retornou resultado vazio ou sem a chave esperada: {result}")

    # Testes para item_search.py
    def test_search_items_by_name(self):
        """Testa a busca de itens por nome."""
        with patch("builtins.print") as mock_print:
            search_items_by_name(self.sample_manifest_data, "Gjallarhorn")
            mock_print.assert_called()

    def test_get_item_details(self):
        """Testa a obtenção de detalhes de um item."""
        result = get_item_details(self.sample_manifest_data, "1363886209")
        self.assertEqual(result["displayProperties"]["name"], "Gjallarhorn")

if __name__ == '__main__':
    unittest.main()