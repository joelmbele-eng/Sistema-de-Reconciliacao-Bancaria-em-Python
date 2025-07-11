import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


class Configuracoes:
    """
    Classe para gerenciar as configurações do sistema de reconciliação contábil.
    Permite salvar e carregar configurações de um arquivo JSON.
    """
    
    def __init__(self, app_principal):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            app_principal: Referência à aplicação principal
        """
        self.app_principal = app_principal
        self.arquivo_config = "configuracoes.json"
        self.config = self.carregar_configuracoes()
        
    def carregar_configuracoes(self):
        """
        Carrega as configurações do arquivo JSON.
        
        Returns:
            dict: Dicionário com as configurações carregadas ou configurações padrão
        """
        configuracoes_padrao = {
            "sistema": {
                "tema": "claro",
                "idioma": "pt-BR",
                "diretorio_backup": "",
                "auto_backup": False
            },
            "empresa": {
                "nome": "",
                "nif": "",
                "endereco": "",
                "telefone": "",
                "email": ""
            },
            "contabilidade": {
                "moeda": "Kz",
                "formato_data": "%d/%m/%Y",
                "plano_contas": "PGC-Angola"
            }
        }
        
        if os.path.exists(self.arquivo_config):
            try:
                with open(self.arquivo_config, 'r', encoding='utf-8') as arquivo:
                    return json.load(arquivo)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar configurações: {str(e)}")
                return configuracoes_padrao
        return configuracoes_padrao
        
    def salvar_configuracoes(self):
        """
        Salva as configurações no arquivo JSON.
        
        Returns:
            bool: True se as configurações foram salvas com sucesso, False caso contrário
        """
        try:
            with open(self.arquivo_config, 'w', encoding='utf-8') as arquivo:
                json.dump(self.config, arquivo, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}")
            return False
            
    def obter_config(self, secao, chave):
        """
        Obtém o valor de uma configuração específica.
        
        Args:
            secao (str): Seção da configuração (sistema, empresa, contabilidade)
            chave (str): Chave da configuração
            
        Returns:
            O valor da configuração ou None se não existir
        """
        if secao in self.config and chave in self.config[secao]:
            return self.config[secao][chave]
        return None
        
    def definir_config(self, secao, chave, valor):
        """
        Define o valor de uma configuração específica.
        
        Args:
            secao (str): Seção da configuração (sistema, empresa, contabilidade)
            chave (str): Chave da configuração
            valor: Valor a ser definido
            
        Returns:
            bool: True se a configuração foi definida com sucesso, False caso contrário
        """
        if secao not in self.config:
            self.config[secao] = {}
            
        self.config[secao][chave] = valor
        return self.salvar_configuracoes()
        
    def abrir_gestor(self):
        """Abre a janela de gestão de configurações"""
        janela = tk.Toplevel(self.app_principal.root)
        janela.title("Configurações do Sistema")
        janela.geometry("600x500")
        janela.transient(self.app_principal.root)
        
        # Notebook (abas)
        notebook = ttk.Notebook(janela)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba Sistema
        aba_sistema = ttk.Frame(notebook, padding=10)
        notebook.add(aba_sistema, text="Sistema")
        self.criar_aba_sistema(aba_sistema)
        
        # Aba Empresa
        aba_empresa = ttk.Frame(notebook, padding=10)
        notebook.add(aba_empresa, text="Empresa")
        self.criar_aba_empresa(aba_empresa)
        
        # Aba Contabilidade
        aba_contabilidade = ttk.Frame(notebook, padding=10)
        notebook.add(aba_contabilidade, text="Contabilidade")
        self.criar_aba_contabilidade(aba_contabilidade)
        
        # Botões
        frame_botoes = ttk.Frame(janela)
        frame_botoes.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(frame_botoes, text="Salvar", 
                  command=lambda: self.salvar_e_fechar(janela)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(frame_botoes, text="Cancelar", 
                  command=janela.destroy).pack(side=tk.RIGHT, padx=5)
        
    def criar_aba_sistema(self, frame):
        """
        Cria os controles para a aba Sistema.
        
        Args:
            frame: Frame onde os controles serão adicionados
        """
        # Tema
        ttk.Label(frame, text="Tema:").grid(row=0, column=0, sticky=tk.W, pady=5)
        tema_var = tk.StringVar(value=self.obter_config("sistema", "tema"))
        ttk.Combobox(frame, textvariable=tema_var, 
                    values=["claro", "escuro", "azul", "verde"]).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Idioma
        ttk.Label(frame, text="Idioma:").grid(row=1, column=0, sticky=tk.W, pady=5)
        idioma_var = tk.StringVar(value=self.obter_config("sistema", "idioma"))
        ttk.Combobox(frame, textvariable=idioma_var, 
                    values=["pt-BR", "en-US", "es-ES"]).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Diretório de backup
        ttk.Label(frame, text="Diretório de Backup:").grid(row=2, column=0, sticky=tk.W, pady=5)
        diretorio_var = tk.StringVar(value=self.obter_config("sistema", "diretorio_backup"))
        ttk.Entry(frame, textvariable=diretorio_var, width=30).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        def selecionar_diretorio():
            from tkinter import filedialog
            diretorio = filedialog.askdirectory(title="Selecionar Diretório para Backup")
            if diretorio:
                diretorio_var.set(diretorio)
                
        ttk.Button(frame, text="...", width=3, 
                  command=selecionar_diretorio).grid(row=2, column=2, padx=5, pady=5)
        
        # Auto backup
        auto_backup_var = tk.BooleanVar(value=self.obter_config("sistema", "auto_backup"))
        ttk.Checkbutton(frame, text="Realizar backup automático ao sair", 
                       variable=auto_backup_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Armazenar variáveis para acesso posterior
        self.vars_sistema = {
            "tema": tema_var,
            "idioma": idioma_var,
            "diretorio_backup": diretorio_var,
            "auto_backup": auto_backup_var
        }
        
    def criar_aba_empresa(self, frame):
        """
        Cria os controles para a aba Empresa.
        
        Args:
            frame: Frame onde os controles serão adicionados
        """
        # Nome da empresa
        ttk.Label(frame, text="Nome da Empresa:").grid(row=0, column=0, sticky=tk.W, pady=5)
        nome_var = tk.StringVar(value=self.obter_config("empresa", "nome"))
        ttk.Entry(frame, textvariable=nome_var, width=40).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # NIF
        ttk.Label(frame, text="NIF:").grid(row=1, column=0, sticky=tk.W, pady=5)
        nif_var = tk.StringVar(value=self.obter_config("empresa", "nif"))
        ttk.Entry(frame, textvariable=nif_var, width=20).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Endereço
        ttk.Label(frame, text="Endereço:").grid(row=2, column=0, sticky=tk.W, pady=5)
        endereco_var = tk.StringVar(value=self.obter_config("empresa", "endereco"))
        ttk.Entry(frame, textvariable=endereco_var, width=40).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Telefone
        ttk.Label(frame, text="Telefone:").grid(row=3, column=0, sticky=tk.W, pady=5)
        telefone_var = tk.StringVar(value=self.obter_config("empresa", "telefone"))
        ttk.Entry(frame, textvariable=telefone_var, width=20).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Email
        ttk.Label(frame, text="Email:").grid(row=4, column=0, sticky=tk.W, pady=5)
        email_var = tk.StringVar(value=self.obter_config("empresa", "email"))
        ttk.Entry(frame, textvariable=email_var, width=30).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Armazenar variáveis para acesso posterior
        self.vars_empresa = {
            "nome": nome_var,
            "nif": nif_var,
            "endereco": endereco_var,
            "telefone": telefone_var,
            "email": email_var
        }
        
    def criar_aba_contabilidade(self, frame):
        """
        Cria os controles para a aba Contabilidade.
        
        Args:
            frame: Frame onde os controles serão adicionados
        """
        # Moeda
        ttk.Label(frame, text="Moeda:").grid(row=0, column=0, sticky=tk.W, pady=5)
        moeda_var = tk.StringVar(value=self.obter_config("contabilidade", "moeda"))
        ttk.Combobox(frame, textvariable=moeda_var, 
                    values=["Kz", "R$", "€", "$"]).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Formato de data
        ttk.Label(frame, text="Formato de Data:").grid(row=1, column=0, sticky=tk.W, pady=5)
        formato_data_var = tk.StringVar(value=self.obter_config("contabilidade", "formato_data"))
        ttk.Combobox(frame, textvariable=formato_data_var, 
                    values=["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d"]).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Plano de contas
        ttk.Label(frame, text="Plano de Contas:").grid(row=2, column=0, sticky=tk.W, pady=5)
        plano_contas_var = tk.StringVar(value=self.obter_config("contabilidade", "plano_contas"))
        ttk.Combobox(frame, textvariable=plano_contas_var, 
                    values=["PGC-Angola", "CPC-Brasil", "IFRS"]).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Armazenar variáveis para acesso posterior
        self.vars_contabilidade = {
            "moeda": moeda_var,
            "formato_data": formato_data_var,
            "plano_contas": plano_contas_var
        }
        
    def salvar_e_fechar(self, janela):
        """
        Salva todas as configurações e fecha a janela.
        
        Args:
            janela: Janela a ser fechada após salvar
        """
        # Salvar configurações do sistema
        for chave, var in self.vars_sistema.items():
            self.config["sistema"][chave] = var.get()
            
        # Salvar configurações da empresa
        for chave, var in self.vars_empresa.items():
            self.config["empresa"][chave] = var.get()
            
        # Salvar configurações de contabilidade
        for chave, var in self.vars_contabilidade.items():
            self.config["contabilidade"][chave] = var.get()
            
        # Salvar no arquivo
        if self.salvar_configuracoes():
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            
            # Aplicar tema se foi alterado
            tema_atual = self.obter_config("sistema", "tema")
            if hasattr(self.app_principal, 'gerenciador_temas'):
                self.app_principal.gerenciador_temas.aplicar_tema(tema_atual)
                
            # Fechar janela
            janela.destroy()