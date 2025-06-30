# Este arquivo gere a interface gráfica utilizando PyQt5
import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QLabel, QDialog, QGridLayout, 
                             QTextEdit, QScrollArea, QSpinBox, QTabWidget, QComboBox, QMessageBox,
                             QMenu) # Added QTabWidget, QComboBox, QMessageBox, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from src.database.database_handler import create_manifest_data
# from src.api.manifest_manager import get_manifest # Already used by item_search
from src.api.item_search import search_items_by_name, get_item_details # search_items_by_type not used here yet
# from src.api.vendor_manager import display_xur_items, get_xur_inventory # display_xur_items not used directly by MainWindow
from src.api.vendor_manager import get_xur_inventory # Keep if needed
from src.api.player_information import (display_player_variables, 
                                        display_player_characters, 
                                        get_current_user_primary_destiny_membership, 
                                        get_character_inventories_for_current_user,
                                        get_profile_inventory_for_current_user) # New imports
from src.api import DestinyComponentType, get_profile as api_get_profile # For specifying components and aliased get_profile
from src.api import item_actions # New import for item actions
from src.auth import token_manager # To check auth status
from components.style_manager import apply_style, apply_button_style
import json # For debug printing complex objects

class DebugWindow(QDialog):
    """Janela de debug com uma área de texto para saída"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Janela de Debug")
        self.setMinimumSize(600, 400)

        # Layout principal da janela de debug
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Área de texto para saída de debug
        self.debug_output = QTextEdit()
        self.debug_output.setReadOnly(True)
        self.debug_output.setPlaceholderText("Saída de debug aparecerá aqui...")
        apply_style(self.debug_output, "inputs")
        layout.addWidget(self.debug_output)
        
        # Botão para limpar a área de debug
        self.clear_debug_button = QPushButton("🗑️ Limpar Debug")
        self.clear_debug_button.clicked.connect(self.clear_debug)
        apply_button_style(self.clear_debug_button, "secondary")
        layout.addWidget(self.clear_debug_button)
        
    def clear_debug(self):
        """Limpa a área de debug"""
        self.debug_output.clear()
        self.debug_output.append("✨ Área de debug limpa.")
        
    def append_debug(self, text):
        """Adiciona texto à área de debug"""
        if text.strip():
            self.debug_output.append(text.strip())

class ItemDetailsDialog(QDialog):
    """Janela de diálogo para exibir detalhes de um item"""
    def __init__(self, item, parent=None, icon_cache=None):
        super().__init__(parent)
        self.setWindowTitle("Detalhes do Item")
        self.setGeometry(300, 300, 350, 250)
        self.icon_cache = icon_cache
        
        # Layout principal
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Ícone do item
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(64, 64)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        layout.addWidget(self.icon_label)
        
        # Informações do item
        propriedades = item.get('displayProperties', {})
        nome = propriedades.get('name', 'Desconhecido')
        tipo = item.get('itemTypeDisplayName', 'Tipo Desconhecido')
        nivel = item.get('inventory', {}).get('tierTypeName', 'Nível Desconhecido')
        descricao = propriedades.get('description', 'Sem descrição')
        hash_item = item.get('hash', 'Desconhecido')
        
        self.info_label = QLabel(
            f"<b>Nome:</b> {nome}<br>"
            f"<b>Hash:</b> {hash_item}<br>"
            f"<b>Tipo:</b> {tipo}<br>"
            f"<b>Nível:</b> {nivel}<br>"
            f"<b>Descrição:</b> {descricao}"
        )
        self.info_label.setWordWrap(True)
        apply_style(self.info_label, "labels")
        layout.addWidget(self.info_label)
        
        # Botão para fechar
        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.close)
        apply_button_style(self.close_button, "secondary")
        layout.addWidget(self.close_button)
        
        # Carrega o ícone
        self.load_icon(item.get('icon_url', 'Sem ícone disponível'))
    
    def load_icon(self, icon_url):
        """Carrega e exibe a imagem do ícone a partir do URL"""
        try:
            if icon_url and icon_url != "Sem ícone disponível":
                # Verifica se o ícone está no cache
                if icon_url in self.icon_cache:
                    scaled_pixmap = self.icon_cache[icon_url]
                else:
                    response = requests.get(icon_url)
                    if response.status_code == 200:
                        pixmap = QPixmap()
                        pixmap.loadFromData(response.content)
                        scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio)
                        self.icon_cache[icon_url] = scaled_pixmap  # Armazena no cache
                    else:
                        self.icon_label.setText("Erro")
                        return
                self.icon_label.setPixmap(scaled_pixmap)
            else:
                self.icon_label.setText("Sem ícone")
        except Exception as e:
            self.icon_label.setText("Erro")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Cache para ícones
        self.icon_cache = {}
        
        # Define o título da janela
        self.setWindowTitle("ExoArchive - Destiny 2")
        
        # Define o tamanho inicial da janela
        self.setGeometry(100, 100, 800, 600)
        
        # Aplica o estilo da janela principal
        apply_style(self, "main_window")

        # Cria o widget central e o layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Carrega os dados do manifesto
        self.manifest_data = create_manifest_data()

        # Layout para o título e o botão de debug
        header_layout = QHBoxLayout()
        main_layout.addLayout(header_layout)
        
        # Título principal da aplicação
        self.main_title = QLabel("ExoArchive")
        self.main_title.setProperty("class", "title-label")
        apply_style(self.main_title, "labels")
        header_layout.addWidget(self.main_title)
        
        # Adiciona um espaço expansível para empurrar o botão de debug para a direita
        header_layout.addStretch()
        
        # Botão de debug
        self.debug_button = QPushButton("🐞 Debug")
        self.debug_button.clicked.connect(self.open_debug_window)
        apply_button_style(self.debug_button, "secondary")
        header_layout.addWidget(self.debug_button)

        # Subtítulo
        self.subtitle = QLabel("Explorador de dados do Destiny 2")
        self.subtitle.setProperty("class", "subtitle-label")
        apply_style(self.subtitle, "labels")
        main_layout.addWidget(self.subtitle)

        # Seção de pesquisa
        self.create_search_section(main_layout)
        
        # Seção de botões de ação
        self.create_action_buttons(main_layout)

        # Tab widget for different views
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Search/General Results Tab (existing functionality)
        self.search_tab = QWidget()
        self.tab_widget.addTab(self.search_tab, "🔍 Item Search & General")
        search_tab_layout = QVBoxLayout(self.search_tab)
        self.create_output_section(search_tab_layout) # output_section now part of this tab

        # Character Inventory Tab (New)
        self.character_tab = QWidget()
        self.tab_widget.addTab(self.character_tab, "👤 Character Inventory")
        character_tab_layout = QVBoxLayout(self.character_tab)
        self.create_character_inventory_section(character_tab_layout)
        
        # Vault Tab (New)
        self.vault_tab = QWidget()
        self.tab_widget.addTab(self.vault_tab, "📦 Vault")
        vault_tab_layout = QVBoxLayout(self.vault_tab)
        self.create_vault_section(vault_tab_layout)


        # Variáveis temporárias (substituir)
        self.membership_type = 1
        self.destiny_membership_id = "4611686018554152113"
        self.character_id = "2305843010708964224"
        
        # Inicializa a janela de debug (mas não a exibe)
        self.debug_window = DebugWindow(self)
        
        # Store character data once fetched
        self.characters_data = {} # {character_id: {details}, ...}
        self.current_character_id = None
        self.current_destiny_membership_id = None
        self.current_destiny_membership_type = None


    def create_character_inventory_section(self, layout):
        """Creates the UI section for character inventory."""
        # Character Selector
        char_select_layout = QHBoxLayout()
        layout.addLayout(char_select_layout)

        char_select_label = QLabel("Select Character:")
        apply_style(char_select_label, "labels")
        char_select_layout.addWidget(char_select_label)

        self.character_selector_combo = QComboBox()
        self.character_selector_combo.setPlaceholderText("Load characters first")
        apply_style(self.character_selector_combo, "inputs") # Assuming 'inputs' style is suitable
        self.character_selector_combo.currentIndexChanged.connect(self.on_character_selected)
        char_select_layout.addWidget(self.character_selector_combo)

        load_chars_button = QPushButton("🔄 Load/Refresh Characters")
        apply_button_style(load_chars_button, "primary")
        load_chars_button.clicked.connect(self.load_and_populate_characters)
        char_select_layout.addWidget(load_chars_button)
        
        layout.addStretch(1) # Pushes content below down if needed

        # Equipped Items Section
        equipped_label = QLabel("Equipped Items:")
        apply_style(equipped_label, "labels")
        layout.addWidget(equipped_label)
        self.equipped_scroll_area = QScrollArea()
        self.equipped_scroll_area.setWidgetResizable(True)
        self.equipped_widget = QWidget()
        self.equipped_grid = QGridLayout(self.equipped_widget)
        self.equipped_scroll_area.setWidget(self.equipped_widget)
        apply_style(self.equipped_scroll_area, "images")
        layout.addWidget(self.equipped_scroll_area)

        # Inventory Items Section
        inventory_label = QLabel("Inventory Items:")
        apply_style(inventory_label, "labels")
        layout.addWidget(inventory_label)
        self.char_inventory_scroll_area = QScrollArea()
        self.char_inventory_scroll_area.setWidgetResizable(True)
        self.char_inventory_widget = QWidget()
        self.char_inventory_grid = QGridLayout(self.char_inventory_widget)
        self.char_inventory_scroll_area.setWidget(self.char_inventory_widget)
        apply_style(self.char_inventory_scroll_area, "images")
        layout.addWidget(self.char_inventory_scroll_area)

    def create_vault_section(self, layout):
        """Creates the UI section for the Vault."""
        load_vault_button = QPushButton("🔄 Load/Refresh Vault")
        apply_button_style(load_vault_button, "primary")
        load_vault_button.clicked.connect(self.load_vault_inventory)
        layout.addWidget(load_vault_button)
        
        self.vault_scroll_area = QScrollArea()
        self.vault_scroll_area.setWidgetResizable(True)
        self.vault_widget = QWidget()
        self.vault_grid = QGridLayout(self.vault_widget)
        self.vault_scroll_area.setWidget(self.vault_widget)
        apply_style(self.vault_scroll_area, "images")
        layout.addWidget(self.vault_scroll_area)

    def create_search_section(self, layout):
        """Cria a área de pesquisa de itens"""
        # Layout para a pesquisa
        search_layout = QHBoxLayout()
        layout.addLayout(search_layout)
        
        # Label para a pesquisa
        self.search_label = QLabel("Procurar Item por Nome:")
        apply_style(self.search_label, "labels")
        search_layout.addWidget(self.search_label)

        # Campo de entrada para pesquisa
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ex: Gjallarhorn, Ace of Spades...")
        apply_style(self.search_input, "inputs")
        search_layout.addWidget(self.search_input)

        # Campo para limite de itens
        self.limit_label = QLabel("Limite de Itens:")
        apply_style(self.limit_label, "labels")
        search_layout.addWidget(self.limit_label)
        
        self.limit_input = QSpinBox()
        self.limit_input.setMinimum(1)
        self.limit_input.setMaximum(100)
        self.limit_input.setValue(20)  # Valor padrão
        apply_style(self.limit_input, "inputs")
        search_layout.addWidget(self.limit_input)

        # Botão de pesquisa (estilo primário)
        self.search_button = QPushButton("🔍 Procurar Item")
        self.search_button.clicked.connect(self.search_item)
        apply_button_style(self.search_button, "primary")
        layout.addWidget(self.search_button)

    def create_action_buttons(self, layout):
        """Cria os botões de ação"""
        # Label para ações
        actions_label = QLabel("Ações Disponíveis:")
        apply_style(actions_label, "labels")
        layout.addWidget(actions_label)

        # Botão para informações do jogador
        self.player_button = QPushButton("👤 Informações do Jogador")
        self.player_button.clicked.connect(self.show_player_info)
        apply_button_style(self.player_button, "secondary")
        layout.addWidget(self.player_button)

        # Botão para itens do Xur
        self.xur_button = QPushButton("🛒 Itens do Xur")
        self.xur_button.clicked.connect(self.show_xur_items)
        apply_button_style(self.xur_button, "success")
        layout.addWidget(self.xur_button)

    def create_output_section(self, layout):
        """Cria a área de exibição de resultados"""
        # Label para resultados
        self.output_label = QLabel("Resultados:")
        apply_style(self.output_label, "labels")
        layout.addWidget(self.output_label)

        # Área de rolagem para a grade de ícones
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.output_widget = QWidget()
        self.output_grid = QGridLayout()
        self.output_widget.setLayout(self.output_grid)
        self.scroll_area.setWidget(self.output_widget)
        apply_style(self.scroll_area, "images")  # Aplica estilo do images.css
        layout.addWidget(self.scroll_area)

        # Botão para limpar resultados
        self.clear_button = QPushButton("🗑️ Limpar Resultados")
        self.clear_button.clicked.connect(self.clear_output)
        apply_button_style(self.clear_button, "secondary")
        layout.addWidget(self.clear_button)

    def load_icon_button(self, item, row, col):
        """Carrega um botão com o ícone e nome do item na grade"""
        propriedades = item.get('displayProperties', {})
        nome = propriedades.get('name', 'Desconhecido')
        icon_url = item.get('icon_url', 'Sem ícone disponível')
        
        # Cria um widget para o item
        item_widget = QWidget()
        item_layout = QVBoxLayout()
        item_layout.setSpacing(5)
        item_widget.setLayout(item_layout)
        
        # Botão com o ícone
        icon_button = QPushButton()
        icon_button.setFixedSize(64, 64)
        apply_button_style(icon_button, "icon")  # Aplica estilo icon-button
        try:
            if icon_url and icon_url != "Sem ícone disponível":
                # Verifica se o ícone está no cache
                if icon_url in self.icon_cache:
                    scaled_pixmap = self.icon_cache[icon_url]
                else:
                    response = requests.get(icon_url)
                    if response.status_code == 200:
                        pixmap = QPixmap()
                        pixmap.loadFromData(response.content)
                        scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio)
                        self.icon_cache[icon_url] = scaled_pixmap  # Armazena no cache
                        self.debug_window.append_debug(f"Ícone carregado: {icon_url}")
                    else:
                        icon_button.setText("Erro")
                        self.debug_window.append_debug(f"Erro ao carregar ícone: {response.status_code}")
                        return
                icon_button.setIcon(QIcon(scaled_pixmap))
                icon_button.setIconSize(scaled_pixmap.size())
            else:
                icon_button.setText("Sem ícone")
                self.debug_window.append_debug("Nenhum ícone disponível para exibir")
        except Exception as e:
            icon_button.setText("Erro")
            self.debug_window.append_debug(f"Erro ao carregar ícone: {str(e)}")
        
        # Conecta o clique do botão à exibição dos detalhes
        icon_button.clicked.connect(lambda: self.show_item_details(item))
        item_layout.addWidget(icon_button)
        
        # Nome do item
        name_label = QLabel(nome)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setFixedWidth(80)
        apply_style(name_label, "labels")
        item_layout.addWidget(name_label)
        
        # Adiciona o widget à grade
        self.output_grid.addWidget(item_widget, row, col)

    def show_item_details(self, item):
        """Exibe os detalhes do item em uma janela de diálogo"""
        dialog = ItemDetailsDialog(item, self, self.icon_cache)
        dialog.exec_()

    def open_debug_window(self):
        """Abre a janela de debug"""
        self.debug_window.show()
        # Debug inicial
        self.debug_window.append_debug("Janela de debug aberta.")
        self.debug_window.append_debug(f"Dados do manifesto carregados: {bool(self.manifest_data)}")
        self.debug_window.append_debug(f"Membership Type: {self.membership_type}")
        self.debug_window.append_debug(f"Destiny Membership ID: {self.destiny_membership_id}")
        self.debug_window.append_debug(f"Character ID: {self.character_id}")

    def search_item(self):
        """Procura um item pelo nome e exibe os ícones na grade"""
        # Limpa a grade anterior
        self.clear_output()
        
        search_term = self.search_input.text().strip()
        limit = self.limit_input.value()  # Obtém o limite do QSpinBox
        
        if not search_term:
            self.debug_window.append_debug("⚠️ Por favor, insira um termo de pesquisa.")
            return

        self.debug_window.append_debug(f"Pesquisa iniciada: '{search_term}' (Limite: {limit})")

        # Redireciona a saída padrão para a janela de debug
        sys.stdout = TextRedirector(self.debug_window)
        try:
            found_items = search_items_by_name(self.manifest_data, search_term)
            if found_items:
                self.output_label.setText(f"Resultados: {len(found_items)} itens encontrados (mostrando até {limit})")
                # Adiciona os itens à grade (4 colunas, respeitando o limite)
                for index, (id_hash, item) in enumerate(found_items[:limit]):
                    row = index // 4
                    col = index % 4
                    self.debug_window.append_debug(f"Carregando item {index + 1}/{min(limit, len(found_items))}: {item.get('displayProperties', {}).get('name', 'Desconhecido')}")
                    self.load_icon_button(item, row, col)
            else:
                self.output_label.setText("Resultados: Nenhum item encontrado")
        except Exception as e:
            self.debug_window.append_debug(f"❌ Erro na pesquisa: {str(e)}")
        finally:
            sys.stdout = sys.__stdout__  # Restaura a saída padrão

    def show_player_info(self):
        """Exibe informações do jogador na janela de debug"""
        self.clear_output()
        self.output_label.setText("Resultados: Informações do Jogador")
        self.debug_window.append_debug("Exibindo informações do jogador...")

        # Redireciona a saída padrão para a janela de debug
        sys.stdout = TextRedirector(self.debug_window)
        try:
            display_player_variables("cosmy", "0588")
            display_player_characters(self.membership_type, self.destiny_membership_id)
        except Exception as e:
            self.debug_window.append_debug(f"❌ Erro ao carregar informações: {str(e)}")
        finally:
            sys.stdout = sys.__stdout__  # Restaura a saída padrão

    def show_xur_items(self):
        """Exibe os itens disponíveis do Xur na grade"""
        self.clear_output()
        limit = self.limit_input.value()  # Obtém o limite do QSpinBox
        self.output_label.setText("Resultados: Itens do Xur")
        self.debug_window.append_debug(f"Exibindo itens do Xur (Limite: {limit})")

        # Redireciona a saída padrão para a janela de debug
        sys.stdout = TextRedirector(self.debug_window)
        try:
            xur_data = get_xur_inventory(self.membership_type, self.destiny_membership_id, self.character_id)
            if xur_data and xur_data.get("sales", {}).get("data", {}):
                sales_data = xur_data["sales"]["data"]
                found_items = []
                for sale_item in sales_data.values():
                    item_hash = sale_item.get("itemHash")
                    if item_hash:
                        item = get_item_details(self.manifest_data, item_hash)
                        if item:
                            found_items.append((item_hash, item))
                if found_items:
                    self.output_label.setText(f"Resultados: {len(found_items)} itens do Xur (mostrando até {limit})")
                    # Adiciona os itens à grade (4 colunas, respeitando o limite)
                    for index, (id_hash, item) in enumerate(found_items[:limit]):
                        row = index // 4
                        col = index % 4
                        self.debug_window.append_debug(f"Carregando item {index + 1}/{min(limit, len(found_items))}: {item.get('displayProperties', {}).get('name', 'Desconhecido')}")
                        self.load_icon_button(item, row, col)
                else:
                    self.output_label.setText("Resultados: Nenhum item do Xur encontrado")
            else:
                self.output_label.setText("Resultados: Nenhum item do Xur encontrado")
        except Exception as e:
            self.debug_window.append_debug(f"❌ Erro ao carregar itens do Xur: {str(e)}")
        finally:
            sys.stdout = sys.__stdout__  # Restaura a saída padrão

    def clear_output(self):
        """Limpa a grade de resultados"""
        # Remove todos os widgets da grade
        while self.output_grid.count():
            item = self.output_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.output_label.setText("Resultados:")
        self.debug_window.append_debug("Área de resultados limpa.")

    def load_and_populate_characters(self):
        """Fetches character data and populates the character selector combo box."""
        if not token_manager.get_access_token():
            QMessageBox.warning(self, "Authentication Required", "Please log in first to load character data.")
            self.debug_window.append_debug("🚫 Authentication required to load characters.")
            return

        self.debug_window.append_debug("🔄 Loading character information...")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            # Get primary membership first
            membership_id, membership_type = get_current_user_primary_destiny_membership()
            if not membership_id or membership_type is None:
                QMessageBox.critical(self, "Error", "Could not determine your primary Destiny membership. Ensure you are authenticated and have played Destiny.")
                self.debug_window.append_debug("❌ Failed to get primary Destiny membership.")
                return
            
            self.current_destiny_membership_id = membership_id
            self.current_destiny_membership_type = membership_type

            # Fetch profile with character details
            # We need DestinyComponentType.CHARACTERS (200)
            # and DestinyComponentType.PROFILE_CURRENCIES (103) for currency display (optional here)
            # and DestinyComponentType.ITEM_INSTANCES (300), ITEM_SOCKETS (305) etc for items.
            # For now, just characters to populate the dropdown. Inventory is fetched on selection.
            # Corrected call:
            profile_response = api_get_profile(membership_type, membership_id, [DestinyComponentType.CHARACTERS])


            if not profile_response or "characters" not in profile_response or "data" not in profile_response.get("characters", {}):
                QMessageBox.critical(self, "Error", "Failed to load character data from profile.")
                self.debug_window.append_debug(f"❌ Failed to load character data. Response: {profile_response}")
                return

            self.characters_data = profile_response["characters"]["data"]
            self.character_selector_combo.clear()

            if not self.characters_data:
                self.character_selector_combo.setPlaceholderText("No characters found")
                QMessageBox.information(self, "No Characters", "No characters found for this Destiny account.")
                self.debug_window.append_debug("ℹ️ No characters found for the account.")
                return

            for char_id, char_data in self.characters_data.items():
                class_hash = char_data.get("classHash")
                class_def = get_item_details(self.manifest_data, class_hash) if class_hash else None # Re-use get_item_details for definition lookup
                class_name = class_def.get("displayProperties", {}).get("name", "Unknown Class") if class_def else "Unknown Class"
                
                race_hash = char_data.get("raceHash")
                race_def = get_item_details(self.manifest_data, race_hash) if race_hash else None
                race_name = race_def.get("displayProperties", {}).get("name", "Unknown Race") if race_def else "Unknown Race"
                
                light = char_data.get("light", "N/A")
                label = f"{class_name} ({race_name}) - {light}💡"
                self.character_selector_combo.addItem(label, char_id)
                self.debug_window.append_debug(f"Character added to selector: {label} (ID: {char_id})")
            
            if self.character_selector_combo.count() > 0:
                self.character_selector_combo.setCurrentIndex(0) # Select first character by default
                self.on_character_selected(0) # Trigger inventory load for the first character

            self.debug_window.append_debug("✅ Characters loaded and populated.")

        except Exception as e:
            QMessageBox.critical(self, "Error Loading Characters", f"An error occurred: {str(e)}")
            self.debug_window.append_debug(f"❌ Error loading characters: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()
            
    def on_character_selected(self, index):
        """Handles character selection change."""
        if index < 0: # No character selected or combo is empty
            self.current_character_id = None
            self.clear_character_inventory_display()
            return

        self.current_character_id = self.character_selector_combo.itemData(index)
        self.debug_window.append_debug(f"Selected character ID: {self.current_character_id}")
        self.load_character_inventory()

    def load_character_inventory(self):
        """Loads and displays the inventory for the current_character_id."""
        if not self.current_character_id or not self.current_destiny_membership_id or self.current_destiny_membership_type is None:
            self.debug_window.append_debug("⚠️ Cannot load character inventory: Missing character or membership info.")
            return

        self.clear_character_inventory_display()
        self.debug_window.append_debug(f"🔄 Loading inventory for character: {self.current_character_id}")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            # Fetch detailed inventory including equipment and general inventory
            inventory_data = get_character_inventories_for_current_user() # This fetches for ALL characters

            if not inventory_data or self.current_character_id not in inventory_data:
                QMessageBox.warning(self, "Inventory Data", f"No inventory data found for character {self.current_character_id}.")
                self.debug_window.append_debug(f"⚠️ No inventory data for character {self.current_character_id}.")
                return

            char_specific_inventory = inventory_data[self.current_character_id]

            # Display Equipped Items
            self.debug_window.append_debug(f"Equipped items for {self.current_character_id}: {len(char_specific_inventory.get('equipment', []))}")
            for index, item_instance in enumerate(char_specific_inventory.get("equipment", [])):
                item_hash = item_instance.get("itemHash")
                item_def = get_item_details(self.manifest_data, item_hash) # Fetch definition
                if item_def:
                    # Augment item_def with instance_id for context menu actions
                    item_def['itemInstanceId'] = item_instance.get('itemInstanceId')
                    item_def['isEquipped'] = True # Mark as equipped
                    row = index // 8  # Adjust columns as needed
                    col = index % 8
                    self.load_icon_button_for_inventory(item_def, row, col, self.equipped_grid, "character_equipped")
            
            # Display Character Inventory Items
            self.debug_window.append_debug(f"Inventory items for {self.current_character_id}: {len(char_specific_inventory.get('inventory', []))}")
            for index, item_instance in enumerate(char_specific_inventory.get("inventory", [])):
                item_hash = item_instance.get("itemHash")
                item_def = get_item_details(self.manifest_data, item_hash)
                if item_def:
                    item_def['itemInstanceId'] = item_instance.get('itemInstanceId')
                    item_def['isEquipped'] = False # Mark as unequipped
                    row = index // 8
                    col = index % 8
                    self.load_icon_button_for_inventory(item_def, row, col, self.char_inventory_grid, "character_inventory")
            
            self.debug_window.append_debug("✅ Character inventory displayed.")

        except Exception as e:
            QMessageBox.critical(self, "Error Loading Inventory", f"An error occurred: {str(e)}")
            self.debug_window.append_debug(f"❌ Error loading character inventory: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()

    def load_vault_inventory(self):
        """Loads and displays the vault inventory."""
        if not token_manager.get_access_token():
            QMessageBox.warning(self, "Authentication Required", "Please log in first to load vault data.")
            return
        
        if not self.current_destiny_membership_id or self.current_destiny_membership_type is None:
             # Try to get it if not set (e.g. user directly clicks vault tab)
            membership_id, membership_type = get_current_user_primary_destiny_membership()
            if not membership_id or membership_type is None:
                QMessageBox.critical(self, "Error", "Could not determine your primary Destiny membership for vault.")
                return
            self.current_destiny_membership_id = membership_id
            self.current_destiny_membership_type = membership_type


        self.clear_vault_inventory_display()
        self.debug_window.append_debug("🔄 Loading Vault inventory...")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            vault_data = get_profile_inventory_for_current_user() # Fetches PROFILE_INVENTORIES
            
            if not vault_data or not vault_data.get("items"):
                QMessageBox.information(self, "Vault Empty", "No items found in the Vault.")
                self.debug_window.append_debug("ℹ️ Vault is empty or data not found.")
                return

            self.debug_window.append_debug(f"Vault items: {len(vault_data.get('items', []))}")
            for index, item_instance in enumerate(vault_data.get("items", [])):
                item_hash = item_instance.get("itemHash")
                item_def = get_item_details(self.manifest_data, item_hash)
                if item_def:
                    item_def['itemInstanceId'] = item_instance.get('itemInstanceId')
                    row = index // 10 # Adjust columns for vault display
                    col = index % 10
                    self.load_icon_button_for_inventory(item_def, row, col, self.vault_grid, "vault")
            
            self.debug_window.append_debug("✅ Vault inventory displayed.")
        except Exception as e:
            QMessageBox.critical(self, "Error Loading Vault", f"An error occurred: {str(e)}")
            self.debug_window.append_debug(f"❌ Error loading vault: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()

    def load_icon_button_for_inventory(self, item_def, row, col, target_grid, item_location_type):
        """Loads an item button into a specified grid. item_location_type: 'character_equipped', 'character_inventory', 'vault'"""
        propriedades = item_def.get('displayProperties', {})
        nome = propriedades.get('name', 'Desconhecido')
        icon_url = propriedades.get('icon', None)
        if icon_url:
            icon_url = f"https://www.bungie.net{icon_url}"
        else:
            icon_url = 'Sem ícone disponível'

        item_widget = QWidget()
        item_layout = QVBoxLayout()
        item_layout.setSpacing(2) # Reduced spacing
        item_layout.setContentsMargins(2,2,2,2) # Reduced margins
        item_widget.setLayout(item_layout)
        
        icon_button = QPushButton()
        icon_button.setFixedSize(56, 56) # Slightly smaller icons for denser display
        apply_button_style(icon_button, "icon")
        
        # Store item data directly on the button for context menu
        icon_button.setProperty("item_data", item_def)
        icon_button.setProperty("item_location_type", item_location_type)

        if icon_url and icon_url != 'Sem ícone disponível':
            if icon_url in self.icon_cache:
                scaled_pixmap = self.icon_cache[icon_url]
            else:
                response = requests.get(icon_url)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    scaled_pixmap = pixmap.scaled(52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.icon_cache[icon_url] = scaled_pixmap
                else:
                    icon_button.setText("Err")
                    target_grid.addWidget(item_widget, row, col)
                    return
            icon_button.setIcon(QIcon(scaled_pixmap))
            icon_button.setIconSize(scaled_pixmap.size())
        else:
            icon_button.setText(nome[:3]) # Show first 3 letters if no icon

        # icon_button.clicked.connect(lambda checked, item=item_def: self.show_item_details(item)) # Left click for details
        icon_button.setContextMenuPolicy(Qt.CustomContextMenu)
        icon_button.customContextMenuRequested.connect(
            lambda pos, btn=icon_button: self.show_item_context_menu(pos, btn)
        )
        item_layout.addWidget(icon_button)
        
        # Optional: Smaller name label or tooltip for name if space is tight
        # name_label = QLabel(nome)
        # name_label.setAlignment(Qt.AlignCenter)
        # name_label.setWordWrap(True)
        # name_label.setFixedWidth(60)
        # apply_style(name_label, "labels")
        # item_layout.addWidget(name_label)
        icon_button.setToolTip(nome)


        target_grid.addWidget(item_widget, row, col)

    def show_item_context_menu(self, position, button_widget):
        """Shows a context menu for an inventory item."""
        item_data = button_widget.property("item_data")
        location_type = button_widget.property("item_location_type") # 'character_equipped', 'character_inventory', 'vault'
        
        if not item_data:
            return

        item_instance_id = item_data.get("itemInstanceId")
        item_hash = item_data.get("hash")
        is_equipped = item_data.get("isEquipped", False) # From augmented data

        menu = QMenu()

        # Common action: View Details
        view_details_action = menu.addAction("View Details")
        view_details_action.triggered.connect(lambda: self.show_item_details(item_data))

        if location_type == "character_inventory" and not is_equipped:
            equip_action = menu.addAction("Equip")
            equip_action.triggered.connect(lambda: self.handle_equip_item(item_instance_id))
            
            move_to_vault_action = menu.addAction("Move to Vault")
            move_to_vault_action.triggered.connect(lambda: self.handle_move_to_vault(item_hash, item_instance_id, 1))

        elif location_type == "character_equipped": # Item is equipped
            # No direct "unequip" action in Destiny API, must equip something else or move
            move_to_vault_action = menu.addAction("Move to Vault (will unequip)")
            move_to_vault_action.triggered.connect(lambda: self.handle_move_to_vault(item_hash, item_instance_id, 1))
        
        elif location_type == "vault":
            if self.characters_data and self.current_destiny_membership_id: # Ensure characters are loaded
                move_to_char_menu = menu.addMenu("Move to Character")
                for char_id, char_details in self.characters_data.items():
                    class_def = get_item_details(self.manifest_data, char_details.get("classHash"))
                    class_name = class_def.get("displayProperties", {}).get("name", f"Char {char_id[:5]}")
                    char_action = move_to_char_menu.addAction(f"{class_name} ({char_details.get('light', '')}💡)")
                    char_action.triggered.connect(
                        lambda checked, ch_id=char_id, it_hash=item_hash, it_id=item_instance_id: 
                        self.handle_move_from_vault(it_hash, it_id, 1, ch_id)
                    )
            else:
                 menu.addAction("Move to Character (Load Chars First)").setEnabled(False)


        menu.exec_(button_widget.mapToGlobal(position))

    def handle_equip_item(self, item_instance_id):
        if not self.current_character_id:
            QMessageBox.warning(self, "Error", "No character selected to equip item on.")
            return
        self.debug_window.append_debug(f"🛡️ Attempting to equip item {item_instance_id} on {self.current_character_id}")
        if not self.current_character_id:
            QMessageBox.warning(self, "Error", "No character selected to equip item on.")
            return
        self.debug_window.append_debug(f"🛡️ Attempting to equip item {item_instance_id} on {self.current_character_id}")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            success, message = item_actions.equip_item_on_character(item_instance_id, self.current_character_id)
            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_character_inventory_display() 
            else:
                QMessageBox.critical(self, "Equip Failed", message)
        except Exception as e:
            QMessageBox.critical(self, "Equip Error", f"An unexpected error occurred: {str(e)}")
            self.debug_window.append_debug(f"💥 Unexpected equip error: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()


    def handle_move_to_vault(self, item_hash, item_instance_id, stack_size):
        if not self.current_character_id:
            QMessageBox.warning(self, "Error", "No character selected to move item from.")
            return
        self.debug_window.append_debug(f"📦 Attempting to move item {item_instance_id} (hash: {item_hash}) to vault from {self.current_character_id}")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            success, message = item_actions.move_item_to_vault(item_hash, item_instance_id, stack_size, self.current_character_id)
            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_character_inventory_display()
                self.refresh_vault_inventory_display() 
            else:
                QMessageBox.critical(self, "Move to Vault Failed", message)
        except Exception as e:
            QMessageBox.critical(self, "Move to Vault Error", f"An unexpected error occurred: {str(e)}")
            self.debug_window.append_debug(f"💥 Unexpected move to vault error: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()


    def handle_move_from_vault(self, item_hash, item_instance_id, stack_size, target_character_id):
        self.debug_window.append_debug(f"👤 Attempting to move item {item_instance_id} (hash: {item_hash}) from vault to character {target_character_id}")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            success, message = item_actions.move_item_to_character(item_hash, item_instance_id, stack_size, target_character_id)
            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_vault_inventory_display()
                if self.current_character_id == target_character_id:
                    self.refresh_character_inventory_display()
            else:
                QMessageBox.critical(self, "Move to Character Failed", message)
        except Exception as e:
            QMessageBox.critical(self, "Move to Character Error", f"An unexpected error occurred: {str(e)}")
            self.debug_window.append_debug(f"💥 Unexpected move from vault error: {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()

    def refresh_character_inventory_display(self):
        """Refreshes the current character's inventory display."""
        self.debug_window.append_debug("🔃 Refreshing character inventory display...")
        if self.current_character_id:
            self.load_character_inventory()
        else:
            self.debug_window.append_debug("⚠️ No current character selected to refresh.")
            self.clear_character_inventory_display() # Clear if no char selected

    def refresh_vault_inventory_display(self):
        """Refreshes the vault inventory display."""
        self.debug_window.append_debug("🔃 Refreshing vault inventory display...")
        self.load_vault_inventory()


    def clear_character_inventory_display(self):
        """Clears equipped and character inventory grids."""
        for grid_layout in [self.equipped_grid, self.char_inventory_grid]:
            while grid_layout.count():
                item = grid_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.debug_window.append_debug("Character inventory display cleared.")
        
    def clear_vault_inventory_display(self):
        """Clears the vault inventory grid."""
        while self.vault_grid.count():
            item = self.vault_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.debug_window.append_debug("Vault inventory display cleared.")


# Classe para redirecionar a saída padrão para a área de texto
class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        if text.strip():  # Só adiciona texto não vazio
            # Verifica se o widget é uma DebugWindow e usa append_debug
            if hasattr(self.text_widget, 'append_debug'):
                self.text_widget.append_debug(text.strip())
            else:
                self.text_widget.append(text.strip())

    def flush(self):
        pass

# Classe para redirecionar a saída padrão para duas áreas de texto
class DualTextRedirector:
    def __init__(self, main_widget, debug_widget):
        self.main_widget = main_widget
        self.debug_widget = debug_widget

    def write(self, text):
        if text.strip():  # Só adiciona texto não vazio
            # Verifica se o texto contém palavras-chave de erro
            if any(keyword in text.lower() for keyword in ["erro", "⚠️", "❌"]):
                self.debug_widget.append_debug(text.strip())
            else:
                self.main_widget.append(text.strip())

    def flush(self):
        pass

# Função principal para iniciar a aplicação
def start_ui():
    app = QApplication(sys.argv)
    
    # Aplica fonte padrão da aplicação
    app.setStyleSheet("""
        QApplication {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start_ui()