import tkinter as tk
from tkinter import ttk
import json
import os

class GerenciadorTemas:
    """Gerencia os temas da aplicação e configurações de interface"""
    
    TEMAS = {
        "claro": {
            "bg": "#f0f0f0",
            "fg": "#000000",
            "accent": "#1e88e5",
            "button_bg": "#e0e0e0",
            "table_bg": "#ffffff",
            "table_fg": "#000000",
            "header_bg": "#e0e0e0",
            "highlight": "#bbdefb"
        },
        "escuro": {
            "bg": "#303030",
            "fg": "#ffffff",
            "accent": "#2196f3",
            "button_bg": "#424242",
            "table_bg": "#424242",
            "table_fg": "#ffffff",
            "header_bg": "#212121",
            "highlight": "#1565c0"
        },
        "angola": {
            "bg": "#f5f5f5",
            "fg": "#000000",
            "accent": "#ce1126",  # Vermelho da bandeira de Angola
            "button_bg": "#e0e0e0",
            "table_bg": "#ffffff",
            "table_fg": "#000000",
            "header_bg": "#ce1126",  # Vermelho da bandeira de Angola
            "highlight": "#ffcd00"   # Amarelo da bandeira de Angola
        }
    }
    
    def __init__(self):
        self.config_file = "app_config.json"
        self.current_theme = "claro"
        self.load_config()
        
    def load_config(self):
        """Carrega configurações do arquivo"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.current_theme = config.get("theme", "claro")
            except:
                # Se houver erro, usa configuração padrão
                self.current_theme = "claro"
    
    def save_config(self):
        """Salva configurações no arquivo"""
        config = {"theme": self.current_theme}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
    
    def apply_theme(self, root):
        """Aplica o tema atual à interface"""
        style = ttk.Style()
        theme = self.TEMAS[self.current_theme]
        
        # Configurar estilo para widgets ttk
        style.configure("TFrame", background=theme["bg"])
        style.configure("TLabel", background=theme["bg"], foreground=theme["fg"])
        style.configure("TButton", background=theme["button_bg"], foreground=theme["fg"])
        style.configure("Treeview", background=theme["table_bg"], foreground=theme["table_fg"], fieldbackground=theme["table_bg"])
        style.configure("Treeview.Heading", background=theme["header_bg"], foreground=theme["fg"])
        style.map("Treeview", background=[("selected", theme["highlight"])])
        
        # Configurar widgets tk
        root.configure(bg=theme["bg"])
        
        # Retornar o tema para uso em outros widgets
        return theme
    
    def change_theme(self, theme_name, root):
        """Muda o tema atual e aplica à interface"""
        if theme_name in self.TEMAS:
            self.current_theme = theme_name
            self.save_config()
            return self.apply_theme(root)
        return None

class ResponsiveUI:
    """Gerencia a responsividade da interface"""
    
    def __init__(self, root):
        self.root = root
        self.base_width = 1200
        self.base_height = 800
        self.min_width = 800
        self.min_height = 600
        
        # Configurar evento de redimensionamento
        self.root.bind("<Configure>", self.on_resize)
        
        # Definir tamanho mínimo
        self.root.minsize(self.min_width, self.min_height)
        
    def on_resize(self, event):
        """Responde ao redimensionamento da janela"""
        if event.widget == self.root:
            # Calcular fator de escala
            width_scale = event.width / self.base_width
            height_scale = event.height / self.base_height
            
            # Atualizar fonte base
            base_font_size = int(12 * min(width_scale, height_scale))
            self.update_fonts(base_font_size)
            
    def update_fonts(self, base_size):
        """Atualiza tamanhos de fonte com base no tamanho da janela"""
        font_config = {
            "TitleFont": ("Helvetica", int(base_size * 1.5), "bold"),
            "NormalFont": ("Helvetica", base_size),
            "SmallFont": ("Helvetica", int(base_size * 0.8))
        }
        
        # Aplicar configurações de fonte
        for name, font in font_config.items():
            self.root.option_add(f"*{name}", font)
