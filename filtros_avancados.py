import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pandas as pd

class FiltrosAvancados:
    """Implementa filtros avançados para a tabela principal"""
    
    def __init__(self, app):
        self.app = app
        self.filtros_ativos = {}
    
    def abrir(self):
        """Abre a janela de filtros avançados"""
        self.janela = tk.Toplevel(self.app.root)
        self.janela.title("Filtros Avançados")
        self.janela.geometry("600x500")
        self.janela.transient(self.app.root)
        self.janela.grab_set()
        
        # Aplicar tema atual
        if hasattr(self.app, 'gerenciador_temas'):
            tema = self.app.gerenciador_temas.apply_theme(self.janela)
        
        # Frame principal
        frame_principal = ttk.Frame(self.janela, padding="10")
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame_principal, text="Filtros Avançados", 
                 font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Criar controles de filtro
        self.criar_filtros(frame_principal)
        
        # Botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        ttk.Button(frame_botoes, text="Aplicar Filtros", 
                  command=self.aplicar_filtros).pack(side=tk.RIGHT, padx=5)
        ttk.Button(frame_botoes, text="Limpar Filtros", 
                  command=self.limpar_filtros).pack(side=tk.RIGHT, padx=5)
    
    def criar_filtros(self, parent):
        """Cria os controles para os diferentes tipos de filtro"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Filtro por data
        frame_data = ttk.Frame(notebook, padding="10")
        notebook.add(frame_data, text="Data")
        self.criar_filtro_data(frame_data)
        
        # Filtro por valor
        frame_valor = ttk.Frame(notebook, padding="10")
        notebook.add(frame_valor, text="Valor")
        self.criar_filtro_valor(frame_valor)
        
        # Filtro por descrição
        frame_descricao = ttk.Frame(notebook, padding="10")
        notebook.add(frame_descricao, text="Descrição")
        self.criar_filtro_descricao(frame_descricao)
        
        # Filtro por origem
        frame_origem = ttk.Frame(notebook, padding="10")
        notebook.add(frame_origem, text="Origem")
        self.criar_filtro_origem(frame_origem)
        
        # Filtro por status
        frame_status = ttk.Frame(notebook, padding="10")
        notebook.add(frame_status, text="Status")
        self.criar_filtro_status(frame_status)
    
    def criar_filtro_data(self, parent):
        """Cria filtros para o campo de data"""
        ttk.Label(parent, text="Período:").grid(row=0, column=0, sticky="w", pady=5)
        
        # Data inicial
        frame_data_inicio = ttk.Frame(parent)
        frame_data_inicio.grid(row=1, column=0, sticky="w", pady=5)
        
        ttk.Label(frame_data_inicio, text="De:").pack(side=tk.LEFT, padx=5)
        self.data_inicio_var = tk.StringVar()
        ttk.Entry(frame_data_inicio, textvariable=self.data_inicio_var, width=12).pack(side=tk.LEFT)
        ttk.Label(frame_data_inicio, text="(DD/MM/AAAA)").pack(side=tk.LEFT, padx=5)
        
        # Data final
        frame_data_fim = ttk.Frame(parent)
        frame_data_fim.grid(row=2, column=0, sticky="w", pady=5)
        
        ttk.Label(frame_data_fim, text="Até:").pack(side=tk.LEFT, padx=5)
        self.data_fim_var = tk.StringVar()
        ttk.Entry(frame_data_fim, textvariable=self.data_fim_var, width=12).pack(side=tk.LEFT)
        ttk.Label(frame_data_fim, text="(DD/MM/AAAA)").pack(side=tk.LEFT, padx=5)
    
    def criar_filtro_valor(self, parent):
        """Cria filtros para o campo de valor"""
        ttk.Label(parent, text="Faixa de Valor:").grid(row=0, column=0, sticky="w", pady=5)
        
        # Valor mínimo
        frame_valor_min = ttk.Frame(parent)
        frame_valor_min.grid(row=1, column=0, sticky="w", pady=5)
        
        ttk.Label(frame_valor_min, text="Mínimo:").pack(side=tk.LEFT, padx=5)
        self.valor_min_var = tk.StringVar()
        ttk.Entry(frame_valor_min, textvariable=self.valor_min_var, width=15).pack(side=tk.LEFT)
        ttk.Label(frame_valor_min, text="Kz").pack(side=tk.LEFT, padx=5)
        
        # Valor máximo
        frame_valor_max = ttk.Frame(parent)
        frame_valor_max.grid(row=2, column=0, sticky="w", pady=5)
        
        ttk.Label(frame_valor_max, text="Máximo:").pack(side=tk.LEFT, padx=5)
        self.valor_max_var = tk.StringVar()
        ttk.Entry(frame_valor_max, textvariable=self.valor_max_var, width=15).pack(side=tk.LEFT)
        ttk.Label(frame_valor_max, text="Kz").pack(side=tk.LEFT, padx=5)
        
        # Tipo de valor
        frame_tipo_valor = ttk.Frame(parent)
        frame_tipo_valor.grid(row=3, column=0, sticky="w", pady=10)
        
        ttk.Label(frame_tipo_valor, text="Tipo:").pack(side=tk.LEFT, padx=5)
        self.tipo_valor_var = tk.StringVar(value="todos")
        ttk.Radiobutton(frame_tipo_valor, text="Todos", variable=self.tipo_valor_var, 
                       value="todos").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_tipo_valor, text="Positivos", variable=self.tipo_valor_var, 
                       value="positivos").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(frame_tipo_valor, text="Negativos", variable=self.tipo_valor_var, 
                       value="negativos").pack(side=tk.LEFT, padx=5)
    
    def criar_filtro_descricao(self, parent):
        """Cria filtros para o campo de descrição"""
        ttk.Label(parent, text="Texto na Descrição:").grid(row=0, column=0, sticky="w", pady=5)
        
        self.descricao_var = tk.StringVar()
        ttk.Entry(parent, textvariable=self.descricao_var, width=40).grid(row=1, column=0, sticky="w", pady=5)
        
        # Opções de busca
        frame_opcoes = ttk.Frame(parent)
        frame_opcoes.grid(row=2, column=0, sticky="w", pady=10)
        
        self.descricao_exata_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame_opcoes, text="Correspondência exata", 
                       variable=self.descricao_exata_var).pack(anchor="w")
        
        self.descricao_case_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame_opcoes, text="Diferenciar maiúsculas/minúsculas", 
                       variable=self.descricao_case_var).pack(anchor="w", pady=5)
    
    def criar_filtro_origem(self, parent):
        """Cria filtros para o campo de origem"""
        ttk.Label(parent, text="Origem:").grid(row=0, column=0, sticky="w", pady=5)
        
        self.origem_var = tk.StringVar(value="todas")
        ttk.Radiobutton(parent, text="Todas", variable=self.origem_var, 
                       value="todas").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Radiobutton(parent, text="Banco", variable=self.origem_var, 
                       value="BANCO").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Radiobutton(parent, text="Livro", variable=self.origem_var, 
                       value="LIVRO").grid(row=3, column=0, sticky="w", pady=2)
    
    def criar_filtro_status(self, parent):
        """Cria filtros para o campo de status"""
        ttk.Label(parent, text="Status:").grid(row=0, column=0, sticky="w", pady=5)
        
        self.status_var = tk.StringVar(value="todos")
        ttk.Radiobutton(parent, text="Todos", variable=self.status_var, 
                       value="todos").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Radiobutton(parent, text="Pendentes", variable=self.status_var, 
                       value="PENDENTE").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Radiobutton(parent, text="Conciliados", variable=self.status_var, 
                       value="CONCILIADO").grid(row=3, column=0, sticky="w", pady=2)
    
    def aplicar_filtros(self):
        """Aplica os filtros definidos à tabela"""
        self.filtros_ativos = {}
        
        # Filtro de data
        if self.data_inicio_var.get():
            try:
                data_inicio = datetime.strptime(self.data_inicio_var.get(), "%d/%m/%Y")
                self.filtros_ativos['data_inicio'] = data_inicio
            except:
                pass
                
        if self.data_fim_var.get():
            try:
                data_fim = datetime.strptime(self.data_fim_var.get(), "%d/%m/%Y")
                self.filtros_ativos['data_fim'] = data_fim
            except:
                pass
        
        # Filtro de valor
        if self.valor_min_var.get():
            try:
                valor_min = float(self.valor_min_var.get().replace(".", "").replace(",", "."))
                self.filtros_ativos['valor_min'] = valor_min
            except:
                pass
                
        if self.valor_max_var.get():
            try:
                valor_max = float(self.valor_max_var.get().replace(".", "").replace(",", "."))
                self.filtros_ativos['valor_max'] = valor_max
            except:
                pass
        
        if self.tipo_valor_var.get() != "todos":
            self.filtros_ativos['tipo_valor'] = self.tipo_valor_var.get()
        
        # Filtro de descrição
        if self.descricao_var.get():
            self.filtros_ativos['descricao'] = self.descricao_var.get()
            self.filtros_ativos['descricao_exata'] = self.descricao_exata_var.get()
            self.filtros_ativos['descricao_case'] = self.descricao_case_var.get()
        
        # Filtro de origem
        if self.origem_var.get() != "todas":
            self.filtros_ativos['origem'] = self.origem_var.get()
        
        # Filtro de status
        if self.status_var.get() != "todos":
            self.filtros_ativos['status'] = self.status_var.get()
        
        # Aplicar filtros à tabela
        self.filtrar_tabela()
        self.janela.destroy()
    
    def filtrar_tabela(self):
        """Filtra os itens da tabela com base nos filtros ativos"""
        # Limpar tabela
        self.app.tabela.delete(*self.app.tabela.get_children())
        
        # Aplicar filtros aos dados do banco
        if self.app.dados_banco is not None:
            dados_filtrados_banco = self.aplicar_filtros_dataframe(self.app.dados_banco, "BANCO")
            for _, row in dados_filtrados_banco.iterrows():
                status = self.obter_status_item(row, "BANCO")
                if 'status' in self.filtros_ativos and status != self.filtros_ativos['status']:
                    continue
                    
                self.app.tabela.insert('', 'end', values=(
                    row['data'].strftime('%d/%m/%Y'),
                    row['descricao'],
                    f"Kz {row['valor']:,.2f}",
                    'BANCO',
                    status
                ))
        
        # Aplicar filtros aos dados do livro
        if self.app.dados_livro is not None:
            dados_filtrados_livro = self.aplicar_filtros_dataframe(self.app.dados_livro, "LIVRO")
            for _, row in dados_filtrados_livro.iterrows():
                status = self.obter_status_item(row, "LIVRO")
                if 'status' in self.filtros_ativos and status != self.filtros_ativos['status']:
                    continue
                    
                self.app.tabela.insert('', 'end', values=(
                    row['data'].strftime('%d/%m/%Y'),
                    row['descricao'],
                    f"Kz {row['valor']:,.2f}",
                    'LIVRO',
                    status
                ))
    
    def aplicar_filtros_dataframe(self, df, origem):
        """Aplica os filtros a um DataFrame"""
        df_filtrado = df.copy()
        
        # Filtro de data
        if 'data_inicio' in self.filtros_ativos:
            df_filtrado = df_filtrado[df_filtrado['data'] >= self.filtros_ativos['data_inicio']]
            
        if 'data_fim' in self.filtros_ativos:
            df_filtrado = df_filtrado[df_filtrado['data'] <= self.filtros_ativos['data_fim']]
        
        # Filtro de valor
        if 'valor_min' in self.filtros_ativos:
            df_filtrado = df_filtrado[df_filtrado['valor'] >= self.filtros_ativos['valor_min']]
            
        if 'valor_max' in self.filtros_ativos:
            df_filtrado = df_filtrado[df_filtrado['valor'] <= self.filtros_ativos['valor_max']]
        
        if 'tipo_valor' in self.filtros_ativos:
            if self.filtros_ativos['tipo_valor'] == 'positivos':
                df_filtrado = df_filtrado[df_filtrado['valor'] > 0]
            elif self.filtros_ativos['tipo_valor'] == 'negativos':
                df_filtrado = df_filtrado[df_filtrado['valor'] < 0]
        
        # Filtro de descrição
        if 'descricao' in self.filtros_ativos:
            texto = self.filtros_ativos['descricao']
            
            if self.filtros_ativos['descricao_exata']:
                if self.filtros_ativos['descricao_case']:
                    df_filtrado = df_filtrado[df_filtrado['descricao'] == texto]
                else:
                    df_filtrado = df_filtrado[df_filtrado['descricao'].str.lower() == texto.lower()]
            else:
                if self.filtros_ativos['descricao_case']:
                    df_filtrado = df_filtrado[df_filtrado['descricao'].str.contains(texto, regex=False)]
                else:
                    df_filtrado = df_filtrado[df_filtrado['descricao'].str.lower().str.contains(texto.lower(), regex=False)]
        
        # Filtro de origem já é aplicado na chamada da função
        
        return df_filtrado
    
    def obter_status_item(self, row, origem):
        """Determina o status de um item (conciliado ou pendente)"""
        if origem == "BANCO" and self.app.dados_livro is not None:
            match = self.app.dados_livro[
                (self.app.dados_livro['valor'] == row['valor']) &
                (self.app.dados_livro['data'] == row['data'])
            ]
            return "CONCILIADO" if not match.empty else "PENDENTE"
        
        elif origem == "LIVRO" and self.app.dados_banco is not None:
            match = self.app.dados_banco[
                (self.app.dados_banco['valor'] == row['valor']) &
                (self.app.dados_banco['data'] == row['data'])
            ]
            return "CONCILIADO" if not match.empty else "PENDENTE"
        
        return "PENDENTE"
    
    def limpar_filtros(self):
        """Limpa todos os filtros e restaura a visualização original"""
        self.filtros_ativos = {}
        self.app.atualizar_tabela()
        self.janela.destroy()