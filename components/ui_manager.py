# Este arquivo gere a interface gráfica utilizando PyQt5
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QLabel, QDialog
from PyQt5.QtCore import Qt
from src.database.database_handler import create_manifest_data
from src.api.manifest_manager import get_manifest
from src.api.item_search import search_items_by_name, get_item_details, search_items_by_type
from src.api.vendor_manager import display_xur_items
from src.api.player_information import display_player_variables, display_player_characters
from components.style_manager import StyleManager, apply_button_style

class DebugWindow(QDialog):
    """Janela de debug com uma área de texto para saída"""
    def __init__(self, parent=None, style_manager=None):
        
        super().__init__(parent)
        self.setWindowTitle("Janela de Debug")
        self.setGeometry(200, 200, 600, 400)

        # Armazena o style_manager passado como parâmetro
        self.style_manager = style_manager
        
        # Layout principal da janela de debug
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Área de texto para saída de debug
        self.debug_output = QTextEdit()
        self.debug_output.setReadOnly(True)
        self.debug_output.setPlaceholderText("Saída de debug aparecerá aqui...")
        self.style_manager.apply_style(self.debug_output, "inputs")
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Inicializa o gestor de estilos
        self.style_manager = StyleManager()
        
        # Define o título da janela
        self.setWindowTitle("ExoArchive - Destiny 2")
        
        # Define o tamanho inicial da janela
        self.setGeometry(100, 100, 900, 700)
        
        # Aplica o estilo da janela principal
        self.style_manager.apply_style(self, "main_window")

        # Cria o widget central e o layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)  # Margens da janela

        # Carrega os dados do manifesto
        self.manifest_data = create_manifest_data()

        # Layout para o título e o botão de debug
        header_layout = QHBoxLayout()
        main_layout.addLayout(header_layout)
        
        # Título principal da aplicação
        self.main_title = QLabel("ExoArchive")
        self.main_title.setProperty("class", "title-label")
        self.style_manager.apply_style(self.main_title, "labels")
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
        self.style_manager.apply_style(self.subtitle, "labels")
        main_layout.addWidget(self.subtitle)

        # Seção de pesquisa
        self.create_search_section(main_layout)
        
        # Seção de botões de ação
        self.create_action_buttons(main_layout)

        # Área de resultados
        self.create_output_section(main_layout)

        # Variáveis temporárias (substituir)
        self.membership_type = 1
        self.destiny_membership_id = "4611686018554152113"
        self.character_id = "2305843010708964224"
        
        # Inicializa a janela de debug (mas não a exibe)
        self.debug_window = DebugWindow(self, self.style_manager)

    def create_search_section(self, layout):
        """Cria a seção de pesquisa de itens"""
        # Label para a pesquisa
        self.search_label = QLabel("Procurar Item por Nome:")
        self.style_manager.apply_style(self.search_label, "labels")
        layout.addWidget(self.search_label)

        # Campo de entrada para pesquisa
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ex: Gjallarhorn, Ace of Spades...")
        self.style_manager.apply_style(self.search_input, "inputs")
        layout.addWidget(self.search_input)

        # Botão de pesquisa (estilo primário)
        self.search_button = QPushButton("🔍 Procurar Item")
        self.search_button.clicked.connect(self.search_item)
        apply_button_style(self.search_button, "primary")
        layout.addWidget(self.search_button)

    def create_action_buttons(self, layout):
        """Cria os botões de ação"""
        # Label para ações
        actions_label = QLabel("Ações Disponíveis:")
        self.style_manager.apply_style(actions_label, "labels")
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
        output_label = QLabel("Resultados:")
        self.style_manager.apply_style(output_label, "labels")
        layout.addWidget(output_label)

        # Área de texto para resultados
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setPlaceholderText("Os resultados das suas pesquisas aparecerão aqui...")
        self.style_manager.apply_style(self.output_area, "inputs")
        layout.addWidget(self.output_area)

        # Botão para limpar resultados
        self.clear_button = QPushButton("🗑️ Limpar Resultados")
        self.clear_button.clicked.connect(self.clear_output)
        apply_button_style(self.clear_button, "secondary")
        layout.addWidget(self.clear_button)

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
        """Procura um item pelo nome"""
        self.output_area.clear()
        search_term = self.search_input.text().strip()
        
        if not search_term:
            self.output_area.append("⚠️ Por favor, insira um termo de pesquisa.")
            return

        self.output_area.append(f"🔍 Procurando por: '{search_term}'...")
        self.output_area.append("=" * 50)
        self.debug_window.append_debug(f"Pesquisa iniciada: '{search_term}'")

        # Redireciona a saída padrão para ambas as áreas de texto
        sys.stdout = DualTextRedirector(self.output_area, self.debug_window)
        try:
            search_items_by_name(self.manifest_data, search_term)
        except Exception as e:
            self.output_area.append(f"❌ Erro na pesquisa: {str(e)}")
            self.debug_window.append_debug(f"Erro na pesquisa: {str(e)}")
        finally:
            sys.stdout = sys.__stdout__  # Restaura a saída padrão

    def show_player_info(self):
        """Exibe informações do jogador"""
        self.output_area.clear()
        self.output_area.append("👤 Carregando informações do jogador...")
        self.output_area.append("=" * 50)
        self.debug_window.append_debug("Exibindo informações do jogador...")

        # Redireciona a saída padrão para ambas as áreas de texto
        sys.stdout = DualTextRedirector(self.output_area, self.debug_window)
        try:
            display_player_variables("cosmy", "0588")
            display_player_characters(self.membership_type, self.destiny_membership_id)
        except Exception as e:
            self.output_area.append(f"❌ Erro ao carregar informações: {str(e)}")
            self.debug_window.append_debug(f"Erro ao carregar informações: {str(e)}")
        finally:
            sys.stdout = sys.__stdout__  # Restaura a saída padrão

    def show_xur_items(self):
        """Exibe os itens disponíveis do Xur"""
        self.output_area.clear()
        self.output_area.append("🛒 Carregando itens do Xur...")
        self.output_area.append("=" * 50)
        self.debug_window.append_debug("Exibindo itens do Xur...")

        # Redireciona a saída padrão para ambas as áreas de texto
        sys.stdout = DualTextRedirector(self.output_area, self.debug_window)
        try:
            display_xur_items(self.manifest_data, self.membership_type, 
                            self.destiny_membership_id, self.character_id)
        except Exception as e:
            self.output_area.append(f"❌ Erro ao carregar itens do Xur: {str(e)}")
            self.debug_window.append_debug(f"Erro ao carregar itens do Xur: {str(e)}")
        finally:
            sys.stdout = sys.__stdout__  # Restaura a saída padrão

    def clear_output(self):
        """Limpa a área de resultados"""
        self.output_area.clear()
        self.output_area.append("✨ Área de resultados limpa.")
        self.debug_window.append_debug("Área de resultados limpa.")

# Classe para redirecionar a saída padrão para a área de texto
class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        if text.strip():  # Só adiciona texto não vazio
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
            self.main_widget.append(text.strip())
            self.debug_widget.append_debug(text.strip())

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