"""
Gestor de estilos
Este módulo carrega e aplica estilos CSS aos widgets da interface
"""

import os
from typing import Dict, Optional

class StyleManager:
    """Classe responsável por carregar e gerir estilos CSS"""
    
    def __init__(self, styles_dir: str = "styles"):
        """
        Inicializa o gestor de estilos
        
        Args:
            styles_dir: Diretório onde estão os arquivos CSS
        """
        # Obtém o diretório do ficheiro style_manager.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.styles_dir = os.path.join(current_dir, styles_dir)
        self._styles_cache: Dict[str, str] = {}
        self._ensure_styles_dir()
    
    def _ensure_styles_dir(self):
        """Verifica se o diretório de estilos existe"""
        if not os.path.exists(self.styles_dir):
            print(f"Aviso: Diretório '{self.styles_dir}' não encontrado")
            print(f"Procurando em: {os.path.abspath(self.styles_dir)}")
            # Tenta criar o diretório se não existir
            try:
                os.makedirs(self.styles_dir, exist_ok=True)
                print(f"Diretório criado: {self.styles_dir}")
            except Exception as e:
                print(f"Erro ao criar diretório: {e}")
    
    def load_style(self, style_name: str) -> str:
        """
        Carrega um estilo específico do cache ou arquivo
        
        Args:
            style_name: Nome do arquivo CSS (sem extensão)
            
        Returns:
            Conteúdo do CSS como string
        """
        if style_name in self._styles_cache:
            return self._styles_cache[style_name]
        
        file_path = os.path.join(self.styles_dir, f"{style_name}.css")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                style_content = file.read()
                self._styles_cache[style_name] = style_content
                return style_content
        except FileNotFoundError:
            print(f"Arquivo de estilo não encontrado: {file_path}")
            return ""
        except Exception as e:
            print(f"Erro ao carregar estilo {style_name}: {e}")
            return ""
    
    def apply_style(self, widget, style_name: str, additional_class: str = ""):
        """
        Aplica um estilo a um widget
        
        Args:
            widget: Widget PyQt5 para aplicar o estilo
            style_name: Nome do arquivo CSS
            additional_class: Classe CSS adicional para aplicar
        """
        style = self.load_style(style_name)
        if style:
            # Se há uma classe adicional, aplicamos apenas essa parte do CSS
            if additional_class:
                # Para PyQt5, precisamos aplicar o estilo completo
                # mas podemos configurar a propriedade de classe
                widget.setProperty("class", additional_class)
            
            widget.setStyleSheet(style)
    
    def get_combined_styles(self, *style_names: str) -> str:
        """
        Combina múltiplos estilos em uma string
        
        Args:
            *style_names: Nomes dos arquivos CSS para combinar
            
        Returns:
            CSS combinado como string
        """
        combined = ""
        for style_name in style_names:
            style = self.load_style(style_name)
            if style:
                combined += f"\n/* {style_name}.css */\n{style}\n"
        return combined
    
    def apply_combined_styles(self, widget, *style_names: str):
        """
        Aplica múltiplos estilos combinados a um widget
        
        Args:
            widget: Widget PyQt5
            *style_names: Nomes dos arquivos CSS para combinar
        """
        combined_style = self.get_combined_styles(*style_names)
        if combined_style:
            widget.setStyleSheet(combined_style)
    
    def clear_cache(self):
        """Limpa o cache de estilos"""
        self._styles_cache.clear()
    
    def reload_style(self, style_name: str) -> str:
        """
        Recarrega um estilo específico (ignora cache)
        
        Args:
            style_name: Nome do arquivo CSS
            
        Returns:
            Conteúdo do CSS atualizado
        """
        if style_name in self._styles_cache:
            del self._styles_cache[style_name]
        return self.load_style(style_name)

# Instância global do gerenciador de estilos
style_manager = StyleManager()

# Funções de conveniência
def load_style(style_name: str) -> str:
    """Função de conveniência para carregar um estilo"""
    return style_manager.load_style(style_name)

def apply_style(widget, style_name: str, css_class: str = ""):
    """Função de conveniência para aplicar um estilo"""
    style_manager.apply_style(widget, style_name, css_class)

def apply_button_style(button, button_type: str = "primary"):
    """
    Aplica estilo específico para botões
    
    Args:
        button: QPushButton
        button_type: Tipo do botão (primary, secondary, success)
    """
    style_manager.apply_style(button, "buttons")
    if button_type != "default":
        button.setProperty("class", f"{button_type}-button")
        # Força a atualização do estilo
        button.style().unpolish(button)
        button.style().polish(button)