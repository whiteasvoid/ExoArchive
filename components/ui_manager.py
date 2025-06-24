# Este arquivo gere a interface gráfica utilizando PyQt5
import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QDialog, QGridLayout, QTextEdit, QScrollArea, QSpinBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from src.database.database_handler import create_manifest_data
from src.api.manifest_manager import get_manifest
from src.api.item_search import search_items_by_name, get_item_details, search_items_by_type
from src.api.vendor_manager import display_xur_items, get_xur_inventory
from src.api.player_information import display_player_variables, display_player_characters
from components.style_manager import apply_style, apply_button_style

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

        # Seção de resultados
        self.create_output_section(main_layout)

        # Variáveis temporárias (substituir)
        self.membership_type = 1
        self.destiny_membership_id = "4611686018554152113"
        self.character_id = "2305843010708964224"
        
        # Inicializa a janela de debug (mas não a exibe)
        self.debug_window = DebugWindow(self)

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