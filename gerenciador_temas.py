import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
import os

class GerenciadorTemas:
    """Gerencia os temas visuais da aplicação"""
    
    def __init__(self, app):
        self.app = app
        self.temas = {}
        self.tema_atual = "Padrão"
        self.arquivo_temas = "temas.json"
        self.carregar_temas()
    
    def carregar_temas(self):
        """Carrega os temas do arquivo"""
        # Definir tema padrão
        self.temas = {
            "Padrão": {
                "background": "#f0f0f0",
                "foreground": "#000000",
                "accent": "#0078d7",
                "button_bg": "#e1e1e1",
                "button_fg": "#000000",
                "highlight_bg": "#d1d1d1",
                "highlight_fg": "#000000",
                "font_family": "Helvetica",
                "font_size": 10
            },
            "Escuro": {
                "background": "#2d2d2d",
                "foreground": "#ffffff",
                "accent": "#0078d7",
                "button_bg": "#3d3d3d",
                "button_fg": "#ffffff",
                "highlight_bg": "#4d4d4d",
                "highlight_fg": "#ffffff",
                "font_family": "Helvetica",
                "font_size": 10
            },
            "Azul": {
                "background": "#e6f0ff",
                "foreground": "#000000",
                "accent": "#0050c0",
                "button_bg": "#b3d1ff",
                "button_fg": "#000000",
                "highlight_bg": "#80b3ff",
                "highlight_fg": "#000000",
                "font_family": "Helvetica",
                "font_size": 10
            }
        }
        
        # Carregar temas personalizados
        if os.path.exists(self.arquivo_temas):
            try:
                with open(self.arquivo_temas, 'r', encoding='utf-8') as f:
                    temas_salvos = json.load(f)
                    # Mesclar com os temas padrão
                    for nome, tema in temas_salvos.items():
                        self.temas[nome] = tema
            except:
                pass
    
    def salvar_temas(self):
        """Salva os temas no arquivo"""
        with open(self.arquivo_temas, 'w', encoding='utf-8') as f:
            json.dump(self.temas, f, ensure_ascii=False, indent=4)
    
    def aplicar_tema(self, tema_nome=None):
        """Aplica um tema à aplicação"""
        if tema_nome is None:
            tema_nome = self.tema_atual
        else:
            self.tema_atual = tema_nome
            
        if tema_nome not in self.temas:
            tema_nome = "Padrão"
            
        tema = self.temas[tema_nome]
        
        # Criar estilo personalizado
        style = ttk.Style()
        
        # Configurar cores e fontes
        style.configure("TFrame", background=tema["background"])
        style.configure("TLabel", background=tema["background"], foreground=tema["foreground"],
                      font=(tema["font_family"], tema["font_size"]))
        style.configure("TButton", background=tema["button_bg"], foreground=tema["button_fg"],
                      font=(tema["font_family"], tema["font_size"]))
        style.map("TButton",
                background=[("active", tema["highlight_bg"])],
                foreground=[("active", tema["highlight_fg"])])
        style.configure("TEntry", fieldbackground=tema["background"], foreground=tema["foreground"],
                      font=(tema["font_family"], tema["font_size"]))
        style.configure("TCombobox", fieldbackground=tema["background"], foreground=tema["foreground"],
                      font=(tema["font_family"], tema["font_size"]))
        style.map("TCombobox",
                fieldbackground=[("readonly", tema["background"])],
                foreground=[("readonly", tema["foreground"])])
        style.configure("Treeview", background=tema["background"], foreground=tema["foreground"],
                      font=(tema["font_family"], tema["font_size"]))
        style.map("Treeview",
                background=[("selected", tema["accent"])],
                foreground=[("selected", "#ffffff")])
        
        # Configurar cores da janela principal
        if hasattr(self.app, 'root'):
            self.app.root.configure(background=tema["background"])
            
        return tema
    
    def apply_theme(self, widget):
        """Aplica o tema atual a um widget específico"""
        tema = self.temas[self.tema_atual]
        
        if isinstance(widget, tk.Toplevel):
            widget.configure(background=tema["background"])
            
        return tema
    
    def abrir_gestor(self):
        """Abre a janela de gestão de temas"""
        janela = tk.Toplevel(self.app.root)
        janela.title("Gerenciador de Temas")
        janela.geometry("600x500")
        janela.transient(self.app.root)
        
        # Aplicar tema atual
        tema = self.apply_theme(janela)
        
        # Frame principal
        frame_principal = ttk.Frame(janela, padding="10")
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame_principal, text="Gerenciador de Temas", 
                 font=(tema["font_family"], 16, 'bold')).pack(pady=10)
        
        # Frame de conteúdo dividido
        frame_conteudo = ttk.Frame(frame_principal)
        frame_conteudo.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Lista de temas
        frame_lista = ttk.Frame(frame_conteudo)
        frame_lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(frame_lista, text="Temas Disponíveis").pack(pady=5)
        
        listbox_temas = tk.Listbox(frame_lista, bg=tema["background"], fg=tema["foreground"],
                                 font=(tema["font_family"], tema["font_size"]))
        listbox_temas.pack(fill=tk.BOTH, expand=True)
        
        # Preencher lista de temas
        for nome_tema in self.temas.keys():
            listbox_temas.insert(tk.END, nome_tema)
            if nome_tema == self.tema_atual:
                listbox_temas.selection_set(listbox_temas.size()-1)
        
        # Frame de edição
        frame_edicao = ttk.Frame(frame_conteudo)
        frame_edicao.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(frame_edicao, text="Editar Tema").pack(pady=5)
        
        # Campos de edição
        frame_campos = ttk.Frame(frame_edicao)
        frame_campos.pack(fill=tk.BOTH, expand=True)
        
        # Variáveis para os campos
        var_nome = tk.StringVar()
        var_bg = tk.StringVar()
        var_fg = tk.StringVar()
        var_accent = tk.StringVar()
        var_button_bg = tk.StringVar()
        var_button_fg = tk.StringVar()
        var_highlight_bg = tk.StringVar()
        var_highlight_fg = tk.StringVar()
        var_font_family = tk.StringVar()
        var_font_size = tk.IntVar(value=10)
        
        # Função para selecionar cor
        def selecionar_cor(var):
            cor_atual = var.get()
            cor = colorchooser.askcolor(cor_atual)[1]
            if cor:
                var.set(cor)
                atualizar_preview()
        
        # Função para atualizar preview
        preview_frame = ttk.Frame(frame_edicao, height=100)
        preview_frame.pack(fill=tk.X, pady=10)
        
        def atualizar_preview():
            # Limpar preview
            for widget in preview_frame.winfo_children():
                widget.destroy()
                
            # Criar preview com as cores selecionadas
            preview_bg = var_bg.get()
            preview_fg = var_fg.get()
            preview_button_bg = var_button_bg.get()
            preview_button_fg = var_button_fg.get()
            preview_accent = var_accent.get()
            
            preview = tk.Frame(preview_frame, bg=preview_bg, height=100)
            preview.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(preview, text="Exemplo de Texto", bg=preview_bg, fg=preview_fg,
                   font=(var_font_family.get(), var_font_size.get())).pack(pady=5)
            
            button_frame = tk.Frame(preview, bg=preview_bg)
            button_frame.pack(pady=5)
            
            tk.Button(button_frame, text="Botão Normal", bg=preview_button_bg, fg=preview_button_fg,
                    font=(var_font_family.get(), var_font_size.get())).pack(side=tk.LEFT, padx=5)
            
            tk.Button(button_frame, text="Botão Destaque", bg=preview_accent, fg="#ffffff",
                    font=(var_font_family.get(), var_font_size.get())).pack(side=tk.LEFT, padx=5)
        
        # Campos
        row = 0
        
        ttk.Label(frame_campos, text="Nome do Tema:").grid(row=row, column=0, sticky="w", pady=2)
        ttk.Entry(frame_campos, textvariable=var_nome).grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        ttk.Label(frame_campos, text="Cor de Fundo:").grid(row=row, column=0, sticky="w", pady=2)
        ttk.Entry(frame_campos, textvariable=var_bg).grid(row=row, column=1, sticky="ew", pady=2)
        ttk.Button(frame_campos, text="...", width=3, 
                  command=lambda: selecionar_cor(var_bg)).grid(row=row, column=2, pady=2)
        row += 1
        
        ttk.Label(frame_campos, text="Cor de Texto:").grid(row=row, column=0, sticky="w", pady=2)
        ttk.Entry(frame_campos, textvariable=var_fg).grid(row=row, column=1, sticky="ew", pady=2)
        ttk.Button(frame_campos, text="...", width=3, 
                  command=lambda: selecionar_cor(var_fg)).grid(row=row, column=2, pady=2)
        row += 1
        
        ttk.Label(frame_campos, text="Cor de Destaque:").grid(row=row, column=0, sticky="w", pady=2)
        ttk.Entry(frame_campos, textvariable=var_accent).grid(row=row, column=1, sticky="ew", pady=2)
        ttk.Button(frame_campos, text="...", width=3, 
                  command=lambda: selecionar_cor(var_accent)).grid(row=row, column=2, pady=2)
        row += 1
        
        ttk.Label(frame_campos, text="Cor de Fundo do Botão:").grid(row=row, column=0, sticky="w", pady=2)
        ttk.Entry(frame_campos, textvariable=var_button_bg).grid(row=row, column=1, sticky="ew", pady=2)
        ttk.Button(frame_campos, text="...", width=3, 
                  command=lambda: selecionar_cor(var_button_bg)).grid(row=row, column=2, pady=2)
        row += 1
        
        ttk.Label(frame_campos, text="Cor de Texto do Botão:").grid(row=row, column=0, sticky="w", pady=2)
        ttk.Entry(frame_campos, textvariable=var_button_fg).grid(row=row, column=1, sticky="ew", pady=2)
        ttk.Button(frame_campos, text="...", width=3, 
                  command=lambda: selecionar_cor(var_button_fg)).grid(row=row, column=2, pady=2)
        row += 1
        
        ttk.Label(frame_campos, text="Cor de Destaque do Botão:").grid(row=row, column=0, sticky="w", pady=2)
        ttk.Entry(frame_campos, textvariable=var_highlight_bg).grid(row=row, column=1, sticky="ew", pady=2)
        ttk.Button(frame_campos, text="...", width=3, 
                  command=lambda: selecionar_cor(var_highlight_bg)).grid(row=row, column=2, pady=2)
        row += 1
        
        ttk.Label(frame_campos, text="Cor de Texto Destacado:").grid(row=row, column=0, sticky="w", pady=2)
        ttk.Entry(frame_campos, textvariable=var_highlight_fg).grid(row=row, column=1, sticky="ew", pady=2)
        ttk.Button(frame_campos, text="...", width=3, 
                  command=lambda: selecionar_cor(var_highlight_fg)).grid(row=row, column=2, pady=2)
        row += 1
        
        ttk.Label(frame_campos, text="Família da Fonte:").grid(row=row, column=0, sticky="w", pady=2)
        fonte_combo = ttk.Combobox(frame_campos, textvariable=var_font_family, 
                                 values=["Helvetica", "Arial", "Times", "Courier", "Verdana"])
        fonte_combo.grid(row=row, column=1, sticky="ew", pady=2)
        row += 1
        
        ttk.Label(frame_campos, text="Tamanho da Fonte:").grid(row=row, column=0, sticky="w", pady=2)
        ttk.Spinbox(frame_campos, from_=8, to=16, textvariable=var_font_size, 
                   width=5).grid(row=row, column=1, sticky="w", pady=2)
        row += 1
        
        # Função para carregar tema selecionado
        def carregar_tema_selecionado():
            selecionado = listbox_temas.curselection()
            if not selecionado:
                return
                
            nome_tema = listbox_temas.get(selecionado[0])
            tema = self.temas[nome_tema]
            
            var_nome.set(nome_tema)
            var_bg.set(tema["background"])
            var_fg.set(tema["foreground"])
            var_accent.set(tema["accent"])
            var_button_bg.set(tema["button_bg"])
            var_button_fg.set(tema["button_fg"])
            var_highlight_bg.set(tema["highlight_bg"])
            var_highlight_fg.set(tema["highlight_fg"])
            var_font_family.set(tema["font_family"])
            var_font_size.set(tema["font_size"])
            
            atualizar_preview()
        
        # Vincular seleção da lista
        listbox_temas.bind('<<ListboxSelect>>', lambda e: carregar_tema_selecionado())
        
        # Carregar tema inicial
        carregar_tema_selecionado()
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        # Funções para os botões
        def salvar_tema():
            nome = var_nome.get()
            if not nome:
                messagebox.showerror("Erro", "O nome do tema é obrigatório!")
                return
                
            # Confirmar sobrescrita se já existir
            if nome in self.temas and nome in ["Padrão", "Escuro", "Azul"]:
                messagebox.showerror("Erro", "Não é possível modificar os temas padrão!")
                return
                
            if nome in self.temas:
                if not messagebox.askyesno("Confirmar", f"O tema '{nome}' já existe. Deseja sobrescrevê-lo?"):
                    return
            
            # Criar novo tema
            novo_tema = {
                "background": var_bg.get(),
                "foreground": var_fg.get(),
                "accent": var_accent.get(),
                "button_bg": var_button_bg.get(),
                "button_fg": var_button_fg.get(),
                "highlight_bg": var_highlight_bg.get(),
                "highlight_fg": var_highlight_fg.get(),
                "font_family": var_font_family.get(),
                "font_size": var_font_size.get()
            }
            
            # Salvar tema
            self.temas[nome] = novo_tema
            self.salvar_temas()
            
            # Atualizar lista
            listbox_temas.delete(0, tk.END)
            for nome_tema in self.temas.keys():
                listbox_temas.insert(tk.END, nome_tema)
                if nome_tema == nome:
                    listbox_temas.selection_set(listbox_temas.size()-1)
            
            messagebox.showinfo("Sucesso", f"Tema '{nome}' salvo com sucesso!")
        
        def excluir_tema():
            selecionado = listbox_temas.curselection()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione um tema para excluir!")
                return
                
            nome_tema = listbox_temas.get(selecionado[0])
            
            # Não permitir excluir temas padrão
            if nome_tema in ["Padrão", "Escuro", "Azul"]:
                messagebox.showerror("Erro", "Não é possível excluir os temas padrão!")
                return
                
            # Confirmar exclusão
            if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir o tema '{nome_tema}'?"):
                return
                
            # Excluir tema
            del self.temas[nome_tema]
            self.salvar_temas()
            
            # Se o tema excluído for o atual, mudar para o padrão
            if nome_tema == self.tema_atual:
                self.tema_atual = "Padrão"
                self.aplicar_tema()
            
            # Atualizar lista
            listbox_temas.delete(0, tk.END)
            for nome_tema in self.temas.keys():
                listbox_temas.insert(tk.END, nome_tema)
            
            messagebox.showinfo("Sucesso", f"Tema '{nome_tema}' excluído com sucesso!")
        
        def aplicar_tema_selecionado():
            selecionado = listbox_temas.curselection()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione um tema para aplicar!")
                return
                
            nome_tema = listbox_temas.get(selecionado[0])
            self.aplicar_tema(nome_tema)
            messagebox.showinfo("Sucesso", f"Tema '{nome_tema}' aplicado com sucesso!")
        
        # Botões
        ttk.Button(frame_botoes, text="Novo", 
                  command=lambda: [var_nome.set(""), atualizar_preview()]).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Salvar", 
                  command=salvar_tema).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Excluir", 
                  command=excluir_tema).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Aplicar", 
                  command=aplicar_tema_selecionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Fechar", 
                  command=janela.destroy).pack(side=tk.RIGHT, padx=5)
