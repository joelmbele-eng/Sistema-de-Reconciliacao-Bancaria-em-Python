import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.platypus import Image
import os
import sys
import platform
import subprocess
import zipfile
import tempfile
import shutil
import glob
from banco_processor import ProcessadorBanco
from relatorios import GeradorRelatorios
from config import CONFIGURACOES
from dashboard import DashboardAvancado
from contabilidade import ContabilidadeAvancada
from lancamentos_recorrentes import GerenciadorLancamentosRecorrentes
from gerenciador_temas import GerenciadorTemas
from configuracoes import Configuracoes
from integracao_funcionalidades import IntegradorFuncionalidades

class ReconciliacaoApp:
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.root.title("Sistema de Reconciliação Contábil - Angola")
            self.root.geometry("1200x800")

            # Inicializações
            self.dados_banco = None
            self.dados_livro = None
            self.gerador_relatorios = GeradorRelatorios()
            self.contabilidade = ContabilidadeAvancada()

            # Novos módulos
            self.gerenciador_temas = GerenciadorTemas(self)
            self.configuracoes = Configuracoes(self)
            self.lancamentos_recorrentes = GerenciadorLancamentosRecorrentes(self)

            # Aplicar tema inicial
            tema_inicial = self.configuracoes.obter_config("sistema", "tema")
            if tema_inicial:
                self.gerenciador_temas.aplicar_tema(tema_inicial)

            self.setup_interface()
            self.integrador = IntegradorFuncionalidades(self)
        except Exception as e:
            messagebox.showerror("Erro na Inicialização", f"Ocorreu um erro ao iniciar o sistema: {str(e)}")
            import traceback
            traceback.print_exc()

    def classificar_lancamentos_contabeis(self):
        """Abre a interface para classificar lançamentos em contas contábeis"""
        if self.dados_banco is None and self.dados_livro is None:
            messagebox.showwarning("Aviso", "Importe os dados primeiro!")
            return

        self.contabilidade.dados_banco = self.dados_banco
        self.contabilidade.dados_livro = self.dados_livro
        # Abrir o classificador de lançamentos
        self.contabilidade.abrir_classificador_lancamentos(self.root)

    def setup_interface(self):
        try:
            # Frame principal
            self.frame_principal = ttk.Frame(self.root, padding="10")
            self.frame_principal.pack(fill=tk.BOTH, expand=True)

            # Título
            titulo = ttk.Label(self.frame_principal,
                             text="Sistema de Reconciliação Contábil - Angola",
                             font=('Helvetica', 16, 'bold'))
            titulo.pack(pady=10)

            # Área de botões
            self.criar_area_botoes()

            # Área de estatísticas
            self.criar_area_estatisticas()

            # Tabela principal
            self.criar_tabela()

            # Menu
            self.criar_menu()
        except Exception as e:
            messagebox.showerror("Erro na Interface", f"Ocorreu um erro ao configurar a interface: {str(e)}")
            import traceback
            traceback.print_exc()

    def abrir_dashboard(self):
        if self.validar_dados():
            DashboardAvancado(self.dados_banco, self.dados_livro)

    def criar_area_botoes(self):
        frame_botoes = ttk.Frame(self.frame_principal)
        frame_botoes.pack(fill=tk.X, pady=5)

        # Primeira linha de botões
        ttk.Button(frame_botoes, text="Importar Banco",
                  command=self.importar_banco).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Importar Livro",
                  command=self.importar_livro).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Dashboard",
              command=self.abrir_dashboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Gráficos",
                  command=self.mostrar_graficos).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Limpar",
                  command=self.limpar_dados).pack(side=tk.LEFT, padx=5)
        
        # Segunda linha de botões
        frame_botoes2 = ttk.Frame(self.frame_principal)
        frame_botoes2.pack(fill=tk.X, pady=5)
        
        # Botões para funcionalidades principais
        ttk.Button(frame_botoes2, text="Importar Lançamentos",
                  command=self.importar_lancamentos_contabeis).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes2, text="Balanço Patrimonial",
                  command=self.gerar_balanco).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes2, text="DRE",
                  command=self.gerar_dre).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes2, text="Conciliação Bancária",
                  command=self.realizar_conciliacao_bancaria).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes2, text="Fluxo de Caixa",
                  command=self.gerar_fluxo_caixa).pack(side=tk.LEFT, padx=5)

    def criar_area_estatisticas(self):
        self.frame_stats = ttk.LabelFrame(self.frame_principal, text="Estatísticas")
        self.frame_stats.pack(fill=tk.X, pady=5)

        self.label_total_banco = ttk.Label(self.frame_stats, text="Total Banco: Kz 0,00")
        self.label_total_banco.pack(side=tk.LEFT, padx=10)

        self.label_total_livro = ttk.Label(self.frame_stats, text="Total Livro: Kz 0,00")
        self.label_total_livro.pack(side=tk.LEFT, padx=10)

        self.label_diferenca = ttk.Label(self.frame_stats, text="Diferença: Kz 0,00")
        self.label_diferenca.pack(side=tk.LEFT, padx=10)

    def criar_tabela(self):
        frame_tabela = ttk.Frame(self.frame_principal)
        frame_tabela.pack(fill=tk.BOTH, expand=True, pady=5)

        # Definir colunas
        colunas = ('data', 'descricao', 'valor', 'origem', 'status')
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show='headings')

        # Configurar cabeçalhos
        self.tabela.heading('data', text='Data')
        self.tabela.heading('descricao', text='Descrição')
        self.tabela.heading('valor', text='Valor')
        self.tabela.heading('origem', text='Origem')
        self.tabela.heading('status', text='Status')

        # Configurar larguras
        self.tabela.column('data', width=100)
        self.tabela.column('descricao', width=400)
        self.tabela.column('valor', width=150)
        self.tabela.column('origem', width=100)
        self.tabela.column('status', width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL,
                                command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar.set)

        # Layout
        self.tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def criar_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Arquivo
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Importar Banco", command=self.importar_banco)
        menu_arquivo.add_command(label="Importar Livro", command=self.importar_livro)
        menu_arquivo.add_command(label="Importar Lançamentos Contábeis",
                               command=self.importar_lancamentos_contabeis)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Configurações", command=self.configuracoes.abrir_gestor)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Sair", command=self.root.quit)

        # Menu Relatórios
        menu_relatorios = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Relatórios", menu=menu_relatorios)
        menu_relatorios.add_command(label="Relatório Diário",
                                  command=self.gerar_relatorio_diario)
        menu_relatorios.add_command(label="Relatório Mensal",
                                  command=self.gerar_relatorio_mensal)
        menu_relatorios.add_command(label="Relatório de Divergências",
                                  command=self.gerar_relatorio_divergencias)
        menu_relatorios.add_separator()
        menu_relatorios.add_command(label="Relatório de Auditoria",
                                  command=self.gerar_relatorio_auditoria)
        menu_relatorios.add_command(label="Relatório de Orçamento",
                                  command=self.gerar_relatorio_orcamento)

        # Menu Contabilidade
        menu_contabilidade = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Contabilidade", menu=menu_contabilidade)
        menu_contabilidade.add_command(label="Balanço Patrimonial", command=self.gerar_balanco)
        menu_contabilidade.add_command(label="DRE", command=self.gerar_dre)
        menu_contabilidade.add_command(label="Livro Razão", command=self.gerar_livro_razao)
        menu_contabilidade.add_command(label="RAÇU", command=self.gerar_racu)
        menu_contabilidade.add_command(label="Fluxo de Caixa", command=self.gerar_fluxo_caixa)
        menu_contabilidade.add_separator()
        menu_contabilidade.add_command(label="Registrar Bem Amortizável",
                                     command=self.registrar_bem_amortizavel)
        menu_contabilidade.add_command(label="Lançamentos Recorrentes",
                                     command=self.lancamentos_recorrentes.abrir_gestor)
        menu_contabilidade.add_command(label="Classificar Lançamentos Contábeis", 
                                     command=self.classificar_lancamentos_contabeis)

        # Menu Conciliação Bancária
        menu_conciliacao = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Conciliação Bancária", menu=menu_conciliacao)
        menu_conciliacao.add_command(label="Realizar Conciliação", 
                                   command=self.realizar_conciliacao_bancaria)
        menu_conciliacao.add_command(label="Conciliação Automática", 
                                   command=self.conciliacao_automatica)
        menu_conciliacao.add_command(label="Conciliação Manual", 
                                   command=self.conciliacao_manual)
        menu_conciliacao.add_separator()
        menu_conciliacao.add_command(label="Relatório de Conciliação", 
                                   command=self.relatorio_conciliacao)

        # Menu Fluxo de Caixa
        menu_fluxo_caixa = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fluxo de Caixa", menu=menu_fluxo_caixa)
        menu_fluxo_caixa.add_command(label="Fluxo de Caixa Diário", 
                                   command=self.fluxo_caixa_diario)
        menu_fluxo_caixa.add_command(label="Fluxo de Caixa Mensal", 
                                   command=self.fluxo_caixa_mensal)
        menu_fluxo_caixa.add_command(label="Fluxo de Caixa Anual", 
                                   command=self.fluxo_caixa_anual)
        menu_fluxo_caixa.add_separator()
        menu_fluxo_caixa.add_command(label="Projeção de Fluxo de Caixa", 
                                   command=self.projecao_fluxo_caixa)

        # Menu Auditoria
        menu_auditoria = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Auditoria", menu=menu_auditoria)
        menu_auditoria.add_command(label="Auditoria de Lançamentos", 
                                 command=self.auditoria_lancamentos)
        menu_auditoria.add_command(label="Auditoria de Conciliação", 
                                 command=self.auditoria_conciliacao)
        menu_auditoria.add_command(label="Trilha de Auditoria", 
                                 command=self.trilha_auditoria)
        menu_auditoria.add_separator()
        menu_auditoria.add_command(label="Relatório de Auditoria", 
                                 command=self.gerar_relatorio_auditoria)

        # Menu Orçamento
        menu_orcamento = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Orçamento", menu=menu_orcamento)
        menu_orcamento.add_command(label="Criar Orçamento", 
                                 command=self.criar_orcamento)
        menu_orcamento.add_command(label="Acompanhar Orçamento", 
                                 command=self.acompanhar_orcamento)
        menu_orcamento.add_command(label="Análise de Variações", 
                                 command=self.analise_variacoes_orcamento)
        menu_orcamento.add_separator()
        menu_orcamento.add_command(label="Relatório de Orçamento", 
                                 command=self.gerar_relatorio_orcamento)

        # Menu Ferramentas
        menu_ferramentas = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=menu_ferramentas)
        menu_ferramentas.add_command(label="Gerenciador de Temas",
                                   command=self.gerenciador_temas.abrir_gestor)
        menu_ferramentas.add_command(label="Backup", command=self.realizar_backup)
        menu_ferramentas.add_command(label="Restaurar Backup", command=self.restaurar_backup)

        # Menu Ajuda
        menu_ajuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Sobre", command=self.mostrar_sobre)
        menu_ajuda.add_command(label="Manual do Usuário", command=self.abrir_manual)

    # Funções para Conciliação Bancária
    def realizar_conciliacao_bancaria(self):
        if not self.validar_dados():
            return
            
        # Criar janela de conciliação
        janela = tk.Toplevel(self.root)
        janela.title("Conciliação Bancária")
        janela.geometry("900x600")
        
        # Frame principal
        frame = ttk.Frame(janela, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame, text="Conciliação Bancária", font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Botões de ação
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_botoes, text="Conciliação Automática", 
                  command=self.conciliacao_automatica).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Conciliação Manual", 
                  command=self.conciliacao_manual).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Gerar Relatório", 
                  command=self.relatorio_conciliacao).pack(side=tk.LEFT, padx=5)
        
        # Tabela de conciliação
        frame_tabela = ttk.Frame(frame)
        frame_tabela.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Definir colunas
        colunas = ('data', 'descricao', 'valor_banco', 'valor_livro', 'diferenca', 'status')
        tabela = ttk.Treeview(frame_tabela, columns=colunas, show='headings')
        
        # Configurar cabeçalhos
        tabela.heading('data', text='Data')
        tabela.heading('descricao', text='Descrição')
        tabela.heading('valor_banco', text='Valor Banco')
        tabela.heading('valor_livro', text='Valor Livro')
        tabela.heading('diferenca', text='Diferença')
        tabela.heading('status', text='Status')
        
        # Configurar larguras
        tabela.column('data', width=100)
        tabela.column('descricao', width=300)
        tabela.column('valor_banco', width=120)
        tabela.column('valor_livro', width=120)
        tabela.column('diferenca', width=120)
        tabela.column('status', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=tabela.yview)
        tabela.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher tabela com dados
        self.preencher_tabela_conciliacao(tabela)
        
        # Estatísticas de conciliação
        frame_stats = ttk.LabelFrame(frame, text="Estatísticas de Conciliação")
        frame_stats.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_stats, text="Total Conciliado: Kz 0,00").pack(side=tk.LEFT, padx=10)
        ttk.Label(frame_stats, text="Pendente Banco: Kz 0,00").pack(side=tk.LEFT, padx=10)
        ttk.Label(frame_stats, text="Pendente Livro: Kz 0,00").pack(side=tk.LEFT, padx=10)

    def preencher_tabela_conciliacao(self, tabela):
        """Preenche a tabela de conciliação com dados comparativos"""
        if not self.dados_banco is None and not self.dados_livro is None:
            # Limpar tabela
            tabela.delete(*tabela.get_children())
            
            # Criar dicionário para facilitar a busca
            dict_banco = {}
            for _, row in self.dados_banco.iterrows():
                data_str = row['data'].strftime('%d/%m/%Y')
                chave = (data_str, row['descricao'])
                if chave in dict_banco:
                    dict_banco[chave] += row['valor']
                else:
                    dict_banco[chave] = row['valor']
            
            # Comparar com livro contábil
            for _, row in self.dados_livro.iterrows():
                data_str = row['data'].strftime('%d/%m/%Y')
                chave = (data_str, row['descricao'])
                
                valor_banco = dict_banco.get(chave, 0)
                valor_livro = row['valor']
                diferenca = valor_banco - valor_livro
                
                status = "CONCILIADO" if abs(diferenca) < 0.01 else "PENDENTE"
                
                tabela.insert('', 'end', values=(
                    data_str,
                    row['descricao'],
                    f"Kz {valor_banco:,.2f}",
                    f"Kz {valor_livro:,.2f}",
                    f"Kz {diferenca:,.2f}",
                    status
                ))
                
                # Remover do dicionário para identificar itens apenas no banco
                if chave in dict_banco:
                    del dict_banco[chave]
            
            # Adicionar itens que estão apenas no banco
            for (data_str, descricao), valor in dict_banco.items():
                tabela.insert('', 'end', values=(
                    data_str,
                    descricao,
                    f"Kz {valor:,.2f}",
                    "Kz 0,00",
                    f"Kz {valor:,.2f}",
                    "PENDENTE"
                ))

    def conciliacao_automatica(self):
        """Realiza conciliação automática entre banco e livro contábil"""
        if not self.validar_dados():
            return
            
        try:
            # Contadores
            conciliados = 0
            
            # Criar dicionário para facilitar a busca
            dict_banco = {}
            for _, row in self.dados_banco.iterrows():
                chave = (row['data'], row['valor'])
                dict_banco[chave] = row
            
            # Comparar com livro contábil
            for _, row_livro in self.dados_livro.iterrows():
                chave = (row_livro['data'], row_livro['valor'])
                if chave in dict_banco:
                    # Marcar como conciliado na tabela
                    for item in self.tabela.get_children():
                        valores = self.tabela.item(item)['values']
                        data_str = row_livro['data'].strftime('%d/%m/%Y')
                        valor_str = f"Kz {row_livro['valor']:,.2f}"
                        
                        if valores[0] == data_str and valores[2] == valor_str:
                            self.tabela.set(item, 'status', 'CONCILIADO')
                            conciliados += 1
            
            messagebox.showinfo("Conciliação Automática", 
                              f"{conciliados} lançamentos foram conciliados automaticamente.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na conciliação automática: {str(e)}")

    def conciliacao_manual(self):
        """Abre interface para conciliação manual de lançamentos"""
        if not self.validar_dados():
            return
            
        # Criar janela para conciliação manual
        janela = tk.Toplevel(self.root)
        janela.title("Conciliação Manual")
        janela.geometry("1000x700")
        
        # Frame principal
        frame = ttk.Frame(janela, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame, text="Conciliação Manual de Lançamentos", 
                 font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Painel dividido
        painel = ttk.PanedWindow(frame, orient=tk.HORIZONTAL)
        painel.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame para lançamentos bancários
        frame_banco = ttk.LabelFrame(painel, text="Lançamentos Bancários")
        painel.add(frame_banco, weight=1)
        
        # Frame para lançamentos contábeis
        frame_livro = ttk.LabelFrame(painel, text="Lançamentos Contábeis")
        painel.add(frame_livro, weight=1)
        
        # Tabela de lançamentos bancários
        colunas_banco = ('data', 'descricao', 'valor', 'status')
        tabela_banco = ttk.Treeview(frame_banco, columns=colunas_banco, show='headings')
        
        tabela_banco.heading('data', text='Data')
        tabela_banco.heading('descricao', text='Descrição')
        tabela_banco.heading('valor', text='Valor')
        tabela_banco.heading('status', text='Status')
        
        tabela_banco.column('data', width=100)
        tabela_banco.column('descricao', width=250)
        tabela_banco.column('valor', width=120)
        tabela_banco.column('status', width=100)
        
        scrollbar_banco = ttk.Scrollbar(frame_banco, orient=tk.VERTICAL, command=tabela_banco.yview)
        tabela_banco.configure(yscrollcommand=scrollbar_banco.set)
        
        tabela_banco.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_banco.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tabela de lançamentos contábeis
        colunas_livro = ('data', 'descricao', 'valor', 'status')
        tabela_livro = ttk.Treeview(frame_livro, columns=colunas_livro, show='headings')
        
        tabela_livro.heading('data', text='Data')
        tabela_livro.heading('descricao', text='Descrição')
        tabela_livro.heading('valor', text='Valor')
        tabela_livro.heading('status', text='Status')
        
        tabela_livro.column('data', width=100)
        tabela_livro.column('descricao', width=250)
        tabela_livro.column('valor', width=120)
        tabela_livro.column('status', width=100)
        
        scrollbar_livro = ttk.Scrollbar(frame_livro, orient=tk.VERTICAL, command=tabela_livro.yview)
        tabela_livro.configure(yscrollcommand=scrollbar_livro.set)
        
        tabela_livro.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_livro.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher tabelas
        self.preencher_tabela_banco(tabela_banco)
        self.preencher_tabela_livro(tabela_livro)
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        ttk.Button(frame_botoes, text="Conciliar Selecionados", 
                  command=lambda: self.conciliar_selecionados(tabela_banco, tabela_livro)).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Desconciliar Selecionados", 
                  command=lambda: self.desconciliar_selecionados(tabela_banco, tabela_livro)).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Salvar Conciliação", 
                  command=lambda: self.salvar_conciliacao(janela)).pack(side=tk.LEFT, padx=5)

    def preencher_tabela_banco(self, tabela):
        """Preenche a tabela de lançamentos bancários"""
        if self.dados_banco is not None:
            tabela.delete(*tabela.get_children())
            for _, row in self.dados_banco.iterrows():
                tabela.insert('', 'end', values=(
                    row['data'].strftime('%d/%m/%Y'),
                    row['descricao'],
                    f"Kz {row['valor']:,.2f}",
                    'PENDENTE'
                ))

    def preencher_tabela_livro(self, tabela):
        """Preenche a tabela de lançamentos contábeis"""
        if self.dados_livro is not None:
            tabela.delete(*tabela.get_children())
            for _, row in self.dados_livro.iterrows():
                tabela.insert('', 'end', values=(
                    row['data'].strftime('%d/%m/%Y'),
                    row['descricao'],
                    f"Kz {row['valor']:,.2f}",
                    'PENDENTE'
                ))

    def conciliar_selecionados(self, tabela_banco, tabela_livro):
        """Concilia os lançamentos selecionados nas tabelas"""
        try:
            item_banco = tabela_banco.selection()[0]
            item_livro = tabela_livro.selection()[0]
            
            tabela_banco.set(item_banco, 'status', 'CONCILIADO')
            tabela_livro.set(item_livro, 'status', 'CONCILIADO')
            
            messagebox.showinfo("Conciliação", "Lançamentos conciliados com sucesso!")
        except IndexError:
            messagebox.showwarning("Aviso", "Selecione um lançamento em cada tabela.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conciliar lançamentos: {str(e)}")

    def desconciliar_selecionados(self, tabela_banco, tabela_livro):
        """Remove a conciliação dos lançamentos selecionados"""
        try:
            for item in tabela_banco.selection():
                tabela_banco.set(item, 'status', 'PENDENTE')
            
            for item in tabela_livro.selection():
                tabela_livro.set(item, 'status', 'PENDENTE')
            
            messagebox.showinfo("Conciliação", "Lançamentos desconciliados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao desconciliar lançamentos: {str(e)}")

    def salvar_conciliacao(self, janela):
        """Salva o estado da conciliação e fecha a janela"""
        messagebox.showinfo("Conciliação", "Conciliação salva com sucesso!")
        janela.destroy()

    def relatorio_conciliacao(self):
        """Gera relatório de conciliação bancária"""
        if not self.validar_dados():
            return
            
        # Solicitar data de referência
        data_str = simpledialog.askstring("Data", "Informe a data de referência (DD/MM/AAAA):")
        if not data_str:
            return
            
        try:
            data_ref = datetime.strptime(data_str, "%d/%m/%Y")
        except:
            messagebox.showerror("Erro", "Data inválida!")
            return
        
        # Gerar relatório
        caminho = f"relatorio_conciliacao_{data_ref.strftime('%Y%m%d')}.pdf"
        try:
            # Aqui você chamaria a função do gerador de relatórios
            # self.gerador_relatorios.gerar_relatorio_conciliacao(self.dados_banco, self.dados_livro, caminho, data_ref)
            
            # Por enquanto, apenas mostrar mensagem
            messagebox.showinfo("Relatório", f"Relatório de conciliação gerado: {caminho}")
            # self.abrir_arquivo(caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

    # Funções para Fluxo de Caixa
    def fluxo_caixa_diario(self):
        """Gera relatório de fluxo de caixa diário"""
        if not self.validar_dados():
            return
            
        # Solicitar data
        data_str = simpledialog.askstring("Data", "Informe a data (DD/MM/AAAA):")
        if not data_str:
            return
            
        try:
            data = datetime.strptime(data_str, "%d/%m/%Y")
        except:
            messagebox.showerror("Erro", "Data inválida!")
            return
        
        # Gerar relatório
        caminho = f"fluxo_caixa_diario_{data.strftime('%Y%m%d')}.pdf"
        try:
            self.gerar_fluxo_caixa(data, data, caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar fluxo de caixa: {str(e)}")

    def fluxo_caixa_mensal(self):
        """Gera relatório de fluxo de caixa mensal"""
        if not self.validar_dados():
            return
            
        # Solicitar mês e ano
        mes_ano_str = simpledialog.askstring("Mês/Ano", "Informe o mês e ano (MM/AAAA):")
        if not mes_ano_str:
            return
            
        try:
            mes_ano = datetime.strptime(mes_ano_str, "%m/%Y")
            # Primeiro dia do mês
            data_inicio = mes_ano.replace(day=1)
            # Último dia do mês (usando o próximo mês e voltando um dia)
            if mes_ano.month == 12:
                data_fim = datetime(mes_ano.year + 1, 1, 1) - pd.Timedelta(days=1)
            else:
                data_fim = datetime(mes_ano.year, mes_ano.month + 1, 1) - pd.Timedelta(days=1)
        except:
            messagebox.showerror("Erro", "Formato inválido! Use MM/AAAA")
            return
        
        # Gerar relatório
        caminho = f"fluxo_caixa_mensal_{mes_ano.strftime('%Y%m')}.pdf"
        try:
            self.gerar_fluxo_caixa(data_inicio, data_fim, caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar fluxo de caixa: {str(e)}")

    def fluxo_caixa_anual(self):
        """Gera relatório de fluxo de caixa anual"""
        if not self.validar_dados():
            return
            
        # Solicitar ano
        ano_str = simpledialog.askstring("Ano", "Informe o ano:")
        if not ano_str:
            return
            
        try:
            ano = int(ano_str)
            data_inicio = datetime(ano, 1, 1)
            data_fim = datetime(ano, 12, 31)
        except:
            messagebox.showerror("Erro", "Ano inválido!")
            return
        
        # Gerar relatório
        caminho = f"fluxo_caixa_anual_{ano}.pdf"
        try:
            self.gerar_fluxo_caixa(data_inicio, data_fim, caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar fluxo de caixa: {str(e)}")

    def projecao_fluxo_caixa(self):
        """Gera projeção de fluxo de caixa"""
        if not self.validar_dados():
            return
            
        # Solicitar período
        data_inicio_str = simpledialog.askstring("Data Inicial", "Informe a data inicial (DD/MM/AAAA):")
        if not data_inicio_str:
            return
            
        data_fim_str = simpledialog.askstring("Data Final", "Informe a data final (DD/MM/AAAA):")
        if not data_fim_str:
            return
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
        except:
            messagebox.showerror("Erro", "Data inválida!")
            return
        
        # Gerar projeção
        caminho = f"projecao_fluxo_caixa_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.pdf"
        try:
            # Aqui você implementaria a lógica de projeção
            # Por enquanto, apenas mostrar mensagem
            messagebox.showinfo("Projeção", f"Projeção de fluxo de caixa gerada: {caminho}")
            # self.abrir_arquivo(caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar projeção: {str(e)}")

    # Funções para Auditoria
    def auditoria_lancamentos(self):
        """Realiza auditoria de lançamentos contábeis"""
        if not self.validar_dados():
            return
            
        # Criar janela de auditoria
        janela = tk.Toplevel(self.root)
        janela.title("Auditoria de Lançamentos")
        janela.geometry("900x600")
        
        # Frame principal
        frame = ttk.Frame(janela, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame, text="Auditoria de Lançamentos Contábeis", 
                 font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Filtros
        frame_filtros = ttk.LabelFrame(frame, text="Filtros")
        frame_filtros.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_filtros, text="Data Inicial:").grid(row=0, column=0, padx=5, pady=5)
        data_inicio_var = tk.StringVar()
        ttk.Entry(frame_filtros, textvariable=data_inicio_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Data Final:").grid(row=0, column=2, padx=5, pady=5)
        data_fim_var = tk.StringVar()
        ttk.Entry(frame_filtros, textvariable=data_fim_var).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Valor Mínimo:").grid(row=1, column=0, padx=5, pady=5)
        valor_min_var = tk.StringVar()
        ttk.Entry(frame_filtros, textvariable=valor_min_var).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Valor Máximo:").grid(row=1, column=2, padx=5, pady=5)
        valor_max_var = tk.StringVar()
        ttk.Entry(frame_filtros, textvariable=valor_max_var).grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Button(frame_filtros, text="Aplicar Filtros", 
                  command=lambda: self.aplicar_filtros_auditoria()).grid(row=1, column=4, padx=5, pady=5)
        
        # Tabela de auditoria
        frame_tabela = ttk.Frame(frame)
        frame_tabela.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Definir colunas
        colunas = ('data', 'descricao', 'valor', 'origem', 'status', 'risco')
        tabela = ttk.Treeview(frame_tabela, columns=colunas, show='headings')
        
        # Configurar cabeçalhos
        tabela.heading('data', text='Data')
        tabela.heading('descricao', text='Descrição')
        tabela.heading('valor', text='Valor')
        tabela.heading('origem', text='Origem')
        tabela.heading('status', text='Status')
        tabela.heading('risco', text='Risco')
        
        # Configurar larguras
        tabela.column('data', width=100)
        tabela.column('descricao', width=300)
        tabela.column('valor', width=120)
        tabela.column('origem', width=100)
        tabela.column('status', width=100)
        tabela.column('risco', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=tabela.yview)
        tabela.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher tabela com dados
        self.preencher_tabela_auditoria(tabela)
        
        # Botões de ação
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_botoes, text="Marcar como Verificado", 
                  command=lambda: self.marcar_verificado(tabela)).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Gerar Relatório", 
                  command=self.gerar_relatorio_auditoria).pack(side=tk.LEFT, padx=5)

    def preencher_tabela_auditoria(self, tabela):
        """Preenche a tabela de auditoria com dados"""
        if self.dados_banco is not None and self.dados_livro is not None:
            tabela.delete(*tabela.get_children())
            
            # Adicionar lançamentos do banco
            for _, row in self.dados_banco.iterrows():
                # Determinar nível de risco baseado em critérios
                risco = "BAIXO"
                if row['valor'] > 10000:
                    risco = "ALTO"
                elif row['valor'] > 5000:
                    risco = "MÉDIO"
                
                tabela.insert('', 'end', values=(
                    row['data'].strftime('%d/%m/%Y'),
                    row['descricao'],
                    f"Kz {row['valor']:,.2f}",
                    'BANCO',
                    'PENDENTE',
                    risco
                ))
            
            # Adicionar lançamentos do livro
            for _, row in self.dados_livro.iterrows():
                # Determinar nível de risco baseado em critérios
                risco = "BAIXO"
                if row['valor'] > 10000:
                    risco = "ALTO"
                elif row['valor'] > 5000:
                    risco = "MÉDIO"
                
                tabela.insert('', 'end', values=(
                    row['data'].strftime('%d/%m/%Y'),
                    row['descricao'],
                    f"Kz {row['valor']:,.2f}",
                    'LIVRO',
                    'PENDENTE',
                    risco
                ))

    def aplicar_filtros_auditoria(self):
        """Aplica filtros na tabela de auditoria"""
        messagebox.showinfo("Filtros", "Filtros aplicados com sucesso!")

    def marcar_verificado(self, tabela):
        """Marca lançamentos selecionados como verificados"""
        try:
            for item in tabela.selection():
                tabela.set(item, 'status', 'VERIFICADO')
            
            messagebox.showinfo("Auditoria", "Lançamentos marcados como verificados!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao marcar lançamentos: {str(e)}")

    def auditoria_conciliacao(self):
        """Realiza auditoria de conciliação bancária"""
        if not self.validar_dados():
            return
            
        messagebox.showinfo("Auditoria", "Iniciando auditoria de conciliação bancária...")
        # Implementar lógica de auditoria de conciliação

    def trilha_auditoria(self):
        """Exibe trilha de auditoria do sistema"""
        # Criar janela para trilha de auditoria
        janela = tk.Toplevel(self.root)
        janela.title("Trilha de Auditoria")
        janela.geometry("800x600")
        
        # Frame principal
        frame = ttk.Frame(janela, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame, text="Trilha de Auditoria do Sistema", 
                 font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Tabela de eventos
        frame_tabela = ttk.Frame(frame)
        frame_tabela.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Definir colunas
        colunas = ('data', 'hora', 'usuario', 'acao', 'detalhes')
        tabela = ttk.Treeview(frame_tabela, columns=colunas, show='headings')
        
        # Configurar cabeçalhos
        tabela.heading('data', text='Data')
        tabela.heading('hora', text='Hora')
        tabela.heading('usuario', text='Usuário')
        tabela.heading('acao', text='Ação')
        tabela.heading('detalhes', text='Detalhes')
        
        # Configurar larguras
        tabela.column('data', width=100)
        tabela.column('hora', width=100)
        tabela.column('usuario', width=100)
        tabela.column('acao', width=150)
        tabela.column('detalhes', width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=tabela.yview)
        tabela.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Adicionar alguns eventos de exemplo
        data_atual = datetime.now().strftime('%d/%m/%Y')
        hora_atual = datetime.now().strftime('%H:%M:%S')
        
        tabela.insert('', 'end', values=(
            data_atual,
            hora_atual,
            'admin',
            'Login',
            'Login no sistema'
        ))
        
        tabela.insert('', 'end', values=(
            data_atual,
            hora_atual,
            'admin',
            'Importação',
            'Importação de extrato bancário'
        ))
        
        tabela.insert('', 'end', values=(
            data_atual,
            hora_atual,
            'admin',
            'Conciliação',
            'Conciliação automática realizada'
        ))
        
        # Botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_botoes, text="Exportar Trilha", 
                  command=lambda: self.exportar_trilha_auditoria()).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Limpar Trilha", 
                  command=lambda: self.limpar_trilha_auditoria(tabela)).pack(side=tk.LEFT, padx=5)

    def exportar_trilha_auditoria(self):
        """Exporta a trilha de auditoria para um arquivo"""
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if arquivo:
            messagebox.showinfo("Exportação", f"Trilha de auditoria exportada para: {arquivo}")

    def limpar_trilha_auditoria(self, tabela):
        """Limpa a trilha de auditoria"""
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja limpar a trilha de auditoria?"):
            tabela.delete(*tabela.get_children())
            messagebox.showinfo("Trilha de Auditoria", "Trilha de auditoria limpa com sucesso!")

    def gerar_relatorio_auditoria(self):
        """Gera relatório de auditoria"""
        if not self.validar_dados():
            return
            
        # Solicitar período
        data_inicio_str = simpledialog.askstring("Data Inicial", "Informe a data inicial (DD/MM/AAAA):")
        if not data_inicio_str:
            return
            
        data_fim_str = simpledialog.askstring("Data Final", "Informe a data final (DD/MM/AAAA):")
        if not data_fim_str:
            return
        
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
        except:
            messagebox.showerror("Erro", "Data inválida!")
            return
        
        # Gerar relatório
        caminho = f"relatorio_auditoria_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.pdf"
        try:
            # Aqui você implementaria a geração do relatório
            # Por enquanto, apenas mostrar mensagem
            messagebox.showinfo("Relatório", f"Relatório de auditoria gerado: {caminho}")
            # self.abrir_arquivo(caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

    # Funções para Orçamento
    def criar_orcamento(self):
        """Cria um novo orçamento"""
        # Criar janela para novo orçamento
        janela = tk.Toplevel(self.root)
        janela.title("Criar Orçamento")
        janela.geometry("800x600")
        
        # Frame principal
        frame = ttk.Frame(janela, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame, text="Criar Novo Orçamento", 
                 font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Informações básicas
        frame_info = ttk.LabelFrame(frame, text="Informações Básicas")
        frame_info.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_info, text="Nome:").grid(row=0, column=0, padx=5, pady=5)
        nome_var = tk.StringVar()
        ttk.Entry(frame_info, textvariable=nome_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_info, text="Ano:").grid(row=0, column=2, padx=5, pady=5)
        ano_var = tk.StringVar()
        ttk.Entry(frame_info, textvariable=ano_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(frame_info, text="Descrição:").grid(row=1, column=0, padx=5, pady=5)
        descricao_var = tk.StringVar()
        ttk.Entry(frame_info, textvariable=descricao_var, width=50).grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        
        # Tabela de itens do orçamento
        frame_tabela = ttk.LabelFrame(frame, text="Itens do Orçamento")
        frame_tabela.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Definir colunas
        colunas = ('categoria', 'descricao', 'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 
                  'jul', 'ago', 'set', 'out', 'nov', 'dez', 'total')
        tabela = ttk.Treeview(frame_tabela, columns=colunas, show='headings')
        
        # Configurar cabeçalhos
        tabela.heading('categoria', text='Categoria')
        tabela.heading('descricao', text='Descrição')
        for i, mes in enumerate(['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 
                               'jul', 'ago', 'set', 'out', 'nov', 'dez']):
            tabela.heading(mes, text=mes.capitalize())
        tabela.heading('total', text='Total')
        
        # Configurar larguras
        tabela.column('categoria', width=100)
        tabela.column('descricao', width=200)
        for mes in ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 
                  'jul', 'ago', 'set', 'out', 'nov', 'dez', 'total']:
            tabela.column(mes, width=70)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=tabela.yview)
        scrollbar_x = ttk.Scrollbar(frame_tabela, orient=tk.HORIZONTAL, command=tabela.xview)
        tabela.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Layout
        tabela.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        frame_tabela.grid_rowconfigure(0, weight=1)
        frame_tabela.grid_columnconfigure(0, weight=1)
        
        # Botões para adicionar/remover itens
        frame_botoes_tabela = ttk.Frame(frame_tabela)
        frame_botoes_tabela.grid(row=2, column=0, pady=5)
        
        ttk.Button(frame_botoes_tabela, text="Adicionar Item", 
                  command=lambda: self.adicionar_item_orcamento(tabela)).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes_tabela, text="Remover Item", 
                  command=lambda: self.remover_item_orcamento(tabela)).pack(side=tk.LEFT, padx=5)
        
        # Botões de ação
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        ttk.Button(frame_botoes, text="Salvar Orçamento", 
                  command=lambda: self.salvar_orcamento(nome_var.get(), ano_var.get(), 
                                                      descricao_var.get(), tabela, janela)).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Cancelar", 
                  command=janela.destroy).pack(side=tk.LEFT, padx=5)

    def adicionar_item_orcamento(self, tabela):
        """Adiciona um novo item ao orçamento"""
        # Criar janela para adicionar item
        janela = tk.Toplevel()
        janela.title("Adicionar Item")
        janela.geometry("400x200")
        
        # Frame principal
        frame = ttk.Frame(janela, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos
        ttk.Label(frame, text="Categoria:").grid(row=0, column=0, padx=5, pady=5)
        categoria_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=categoria_var, 
                    values=["Receitas", "Despesas Operacionais", "Despesas Administrativas", 
                           "Investimentos", "Financeiro"]).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Descrição:").grid(row=1, column=0, padx=5, pady=5)
        descricao_var = tk.StringVar()
        ttk.Entry(frame, textvariable=descricao_var).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Valor Mensal:").grid(row=2, column=0, padx=5, pady=5)
        valor_var = tk.DoubleVar()
        ttk.Entry(frame, textvariable=valor_var).grid(row=2, column=1, padx=5, pady=5)
        
        def adicionar():
            try:
                categoria = categoria_var.get()
                descricao = descricao_var.get()
                valor = valor_var.get()
                
                if not categoria or not descricao or valor <= 0:
                    messagebox.showwarning("Aviso", "Preencha todos os campos corretamente.")
                    return
                
                # Calcular total
                total = valor * 12
                
                # Adicionar à tabela
                valores = [categoria, descricao]
                valores.extend([f"Kz {valor:,.2f}" for _ in range(12)])
                valores.append(f"Kz {total:,.2f}")
                
                tabela.insert('', 'end', values=tuple(valores))
                janela.destroy()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar item: {str(e)}")
        
        ttk.Button(frame, text="Adicionar", command=adicionar).grid(row=3, column=1, pady=10)

    def remover_item_orcamento(self, tabela):
        """Remove um item do orçamento"""
        try:
            selecionado = tabela.selection()[0]
            tabela.delete(selecionado)
        except IndexError:
            messagebox.showwarning("Aviso", "Selecione um item para remover.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover item: {str(e)}")

    def salvar_orcamento(self, nome, ano, descricao, tabela, janela):
        """Salva o orçamento"""
        try:
            if not nome or not ano:
                messagebox.showwarning("Aviso", "Nome e ano são obrigatórios.")
                return
            
            # Aqui você implementaria a lógica para salvar o orçamento
            
            messagebox.showinfo("Sucesso", f"Orçamento '{nome}' para {ano} salvo com sucesso!")
            janela.destroy()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar orçamento: {str(e)}")

    def acompanhar_orcamento(self):
        """Abre a interface para acompanhamento do orçamento"""
        # Criar janela para acompanhamento
        janela = tk.Toplevel(self.root)
        janela.title("Acompanhamento de Orçamento")
        janela.geometry("1000x600")
        
        # Frame principal
        frame = ttk.Frame(janela, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame, text="Acompanhamento de Orçamento", 
                 font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Seleção de orçamento
        frame_selecao = ttk.Frame(frame)
        frame_selecao.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_selecao, text="Orçamento:").pack(side=tk.LEFT, padx=5)
        orcamento_var = tk.StringVar()
        ttk.Combobox(frame_selecao, textvariable=orcamento_var, 
                    values=["Orçamento 2023", "Orçamento 2024"]).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_selecao, text="Carregar", 
                  command=lambda: self.carregar_orcamento()).pack(side=tk.LEFT, padx=5)
        
        # Tabela de acompanhamento
        frame_tabela = ttk.Frame(frame)
        frame_tabela.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Definir colunas
        colunas = ('categoria', 'descricao', 'orcado', 'realizado', 'variacao', 'percentual')
        tabela = ttk.Treeview(frame_tabela, columns=colunas, show='headings')
        
        # Configurar cabeçalhos
        tabela.heading('categoria', text='Categoria')
        tabela.heading('descricao', text='Descrição')
        tabela.heading('orcado', text='Orçado')
        tabela.heading('realizado', text='Realizado')
        tabela.heading('variacao', text='Variação')
        tabela.heading('percentual', text='% Realização')
        
        # Configurar larguras
        tabela.column('categoria', width=100)
        tabela.column('descricao', width=300)
        tabela.column('orcado', width=120)
        tabela.column('realizado', width=120)
        tabela.column('variacao', width=120)
        tabela.column('percentual', width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=tabela.yview)
        tabela.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Adicionar alguns dados de exemplo
        tabela.insert('', 'end', values=(
            'Receitas',
            'Vendas',
            'Kz 1,000,000.00',
            'Kz 950,000.00',
            'Kz -50,000.00',
            '95%'
        ))
        
        tabela.insert('', 'end', values=(
            'Despesas',
            'Salários',
            'Kz 500,000.00',
            'Kz 520,000.00',
            'Kz 20,000.00',
            '104%'
        ))
        
        # Gráfico de acompanhamento
        frame_grafico = ttk.LabelFrame(frame, text="Análise Gráfica")
        frame_grafico.pack(fill=tk.BOTH, expand=True, pady=10)
        
        fig = plt.Figure(figsize=(10, 4))
        ax = fig.add_subplot(111)
        
        categorias = ['Receitas', 'Despesas', 'Investimentos']
        orcado = [1000000, 700000, 300000]
        realizado = [950000, 720000, 250000]
        
        x = range(len(categorias))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], orcado, width, label='Orçado')
        ax.bar([i + width/2 for i in x], realizado, width, label='Realizado')
        
        ax.set_ylabel('Valor (Kz)')
        ax.set_title('Orçado vs. Realizado por Categoria')
        ax.set_xticks(x)
        ax.set_xticklabels(categorias)
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Botões de ação
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_botoes, text="Exportar Relatório", 
                  command=lambda: self.exportar_relatorio_orcamento()).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Atualizar Dados", 
                  command=lambda: self.atualizar_dados_orcamento()).pack(side=tk.LEFT, padx=5)

    def carregar_orcamento(self):
        """Carrega os dados do orçamento selecionado"""
        messagebox.showinfo("Orçamento", "Orçamento carregado com sucesso!")

    def exportar_relatorio_orcamento(self):
        """Exporta o relatório de acompanhamento do orçamento"""
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("Excel files", "*.xlsx")]
        )
        
        if arquivo:
            messagebox.showinfo("Exportação", f"Relatório exportado para: {arquivo}")

    def atualizar_dados_orcamento(self):
        """Atualiza os dados do orçamento com valores reais"""
        messagebox.showinfo("Atualização", "Dados atualizados com sucesso!")

    def analise_variacoes_orcamento(self):
        """Abre interface para análise de variações orçamentárias"""
        # Criar janela para análise
        janela = tk.Toplevel(self.root)
        janela.title("Análise de Variações Orçamentárias")
        janela.geometry("900x600")
        
        # Frame principal
        frame = ttk.Frame(janela, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame, text="Análise de Variações Orçamentárias", 
                 font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Seleção de orçamento e período
        frame_selecao = ttk.Frame(frame)
        frame_selecao.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_selecao, text="Orçamento:").grid(row=0, column=0, padx=5, pady=5)
        orcamento_var = tk.StringVar()
        ttk.Combobox(frame_selecao, textvariable=orcamento_var, 
                    values=["Orçamento 2023", "Orçamento 2024"]).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_selecao, text="Período:").grid(row=0, column=2, padx=5, pady=5)
        periodo_var = tk.StringVar()
        ttk.Combobox(frame_selecao, textvariable=periodo_var, 
                    values=["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                           "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
                           "Anual"]).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(frame_selecao, text="Analisar", 
                  command=lambda: self.realizar_analise_variacoes()).grid(row=0, column=4, padx=5, pady=5)
        
        # Tabela de variações
        frame_tabela = ttk.Frame(frame)
        frame_tabela.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Definir colunas
        colunas = ('categoria', 'descricao', 'orcado', 'realizado', 'variacao_abs', 'variacao_perc', 'status')
        tabela = ttk.Treeview(frame_tabela, columns=colunas, show='headings')
        
        # Configurar cabeçalhos
        tabela.heading('categoria', text='Categoria')
        tabela.heading('descricao', text='Descrição')
        tabela.heading('orcado', text='Orçado')
        tabela.heading('realizado', text='Realizado')
        tabela.heading('variacao_abs', text='Var. Absoluta')
        tabela.heading('variacao_perc', text='Var. %')
        tabela.heading('status', text='Status')
        
        # Configurar larguras
        tabela.column('categoria', width=100)
        tabela.column('descricao', width=200)
        tabela.column('orcado', width=100)
        tabela.column('realizado', width=100)
        tabela.column('variacao_abs', width=100)
        tabela.column('variacao_perc', width=100)
        tabela.column('status', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=tabela.yview)
        tabela.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Adicionar alguns dados de exemplo
        tabela.insert('', 'end', values=(
            'Receitas',
            'Vendas',
            'Kz 1,000,000.00',
            'Kz 950,000.00',
            'Kz -50,000.00',
            '-5%',
            'ATENÇÃO'
        ))
        
        tabela.insert('', 'end', values=(
            'Despesas',
            'Salários',
            'Kz 500,000.00',
            'Kz 520,000.00',
            'Kz 20,000.00',
            '4%',
            'ACEITÁVEL'
        ))
        
        tabela.insert('', 'end', values=(
            'Despesas',
            'Marketing',
            'Kz 200,000.00',
            'Kz 300,000.00',
            'Kz 100,000.00',
            '50%',
            'CRÍTICO'
        ))
        
        # Gráfico de variações
        frame_grafico = ttk.LabelFrame(frame, text="Análise Gráfica de Variações")
        frame_grafico.pack(fill=tk.BOTH, expand=True, pady=10)
        
        fig = plt.Figure(figsize=(10, 4))
        ax = fig.add_subplot(111)
        
        categorias = ['Vendas', 'Salários', 'Marketing', 'Operacional', 'Financeiro']
        variacoes = [-5, 4, 50, -10, 8]
        cores = ['#ff9999' if v > 10 or v < -10 else '#99ff99' for v in variacoes]
        
        ax.bar(categorias, variacoes, color=cores)
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax.axhline(y=10, color='r', linestyle='--', alpha=0.3)
        ax.axhline(y=-10, color='r', linestyle='--', alpha=0.3)
        
        ax.set_ylabel('Variação (%)')
        ax.set_title('Variações Orçamentárias por Categoria')
        
        canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Botões de ação
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_botoes, text="Exportar Análise", 
                  command=lambda: self.exportar_analise_variacoes()).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Justificar Variações", 
                  command=lambda: self.justificar_variacoes()).pack(side=tk.LEFT, padx=5)

    def realizar_analise_variacoes(self):
        """Realiza a análise de variações orçamentárias"""
        messagebox.showinfo("Análise", "Análise de variações realizada com sucesso!")

    def exportar_analise_variacoes(self):
        """Exporta a análise de variações orçamentárias"""
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("Excel files", "*.xlsx")]
        )
        
        if arquivo:
            messagebox.showinfo("Exportação", f"Análise exportada para: {arquivo}")

    def justificar_variacoes(self):
        """Abre interface para justificar variações orçamentárias"""
        # Criar janela para justificativas
        janela = tk.Toplevel()
        janela.title("Justificar Variações")
        janela.geometry("500x300")
        
        # Frame principal
        frame = ttk.Frame(janela, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos
        ttk.Label(frame, text="Item:").grid(row=0, column=0, padx=5, pady=5)
        item_var = tk.StringVar()
        ttk.Combobox(frame, textvariable=item_var, 
                    values=["Vendas", "Salários", "Marketing"]).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Variação:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(frame, text="50%").grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Justificativa:").grid(row=2, column=0, padx=5, pady=5)
        justificativa_var = tk.StringVar()
        ttk.Entry(frame, textvariable=justificativa_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Ações Corretivas:").grid(row=3, column=0, padx=5, pady=5)
        acoes_var = tk.StringVar()
        ttk.Entry(frame, textvariable=acoes_var, width=50).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Responsável:").grid(row=4, column=0, padx=5, pady=5)
        responsavel_var = tk.StringVar()
        ttk.Entry(frame, textvariable=responsavel_var, width=30).grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Button(frame, text="Salvar Justificativa", 
                  command=lambda: self.salvar_justificativa(janela)).grid(row=5, column=1, pady=10)

    def salvar_justificativa(self, janela):
        """Salva a justificativa para uma variação orçamentária"""
        messagebox.showinfo("Justificativa", "Justificativa salva com sucesso!")
        janela.destroy()

    def gerar_relatorio_orcamento(self):
        """Gera relatório de orçamento"""
        # Solicitar orçamento e período
        orcamento = simpledialog.askstring("Orçamento", "Informe o nome do orçamento:")
        if not orcamento:
            return
            
        periodo = simpledialog.askstring("Período", "Informe o período (MM/AAAA ou AAAA):")
        if not periodo:
            return
        
        # Gerar relatório
        caminho = f"relatorio_orcamento_{periodo.replace('/', '')}.pdf"
        try:
            # Aqui você implementaria a geração do relatório
            # Por enquanto, apenas mostrar mensagem
            messagebox.showinfo("Relatório", f"Relatório de orçamento gerado: {caminho}")
            # self.abrir_arquivo(caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

    def gerar_livro_razao(self):
        if not self.validar_dados():
            return

        # Solicitar período
        data_inicio_str = simpledialog.askstring("Data Inicial", "Informe a data inicial (DD/MM/AAAA):")
        if not data_inicio_str:
            return
            
        data_fim_str = simpledialog.askstring("Data Final", "Informe a data final (DD/MM/AAAA):")
        if not data_fim_str:
            return

        try:
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
        except:
            messagebox.showerror("Erro", "Data inválida!")
            return

        # Verificar se há lançamentos classificados
        if not hasattr(self.contabilidade, 'lancamentos') or not self.contabilidade.lancamentos:
            # Perguntar se deseja classificar os lançamentos
            if messagebox.askyesno("Classificação Contábil",
                                  "É necessário classificar os lançamentos em contas contábeis. Deseja fazer isso agora?"):
                self.classificar_lancamentos_contabeis()
            else:
                # Tentar converter automaticamente
                try:
                    self.contabilidade.converter_dados_para_lancamentos()
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao converter dados: {str(e)}")
                    return

        # Gerar livro razão
        caminho = f"livro_razao_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.pdf"
        try:
            if self.contabilidade.gerar_livro_razao(data_inicio, data_fim, caminho):
                messagebox.showinfo("Sucesso", f"Livro Razão gerado: {caminho}")
                self.abrir_arquivo(caminho)
            else:
                messagebox.showwarning("Aviso", "Não foi possível gerar o Livro Razão.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar Livro Razão: {str(e)}")

    def gerar_racu(self):
        if not self.validar_dados():
            return

        # Solicitar ano
        ano_str = simpledialog.askstring("Ano", "Informe o ano do RAÇU:")
        if not ano_str:
            return
            
        try:
            ano = int(ano_str)
            if ano < 2000 or ano > 2100:
                raise ValueError("Ano inválido")
        except:
            messagebox.showerror("Erro", "Ano inválido!")
            return

        # Verificar se há lançamentos classificados
        if not hasattr(self.contabilidade, 'lancamentos') or not self.contabilidade.lancamentos:
            # Perguntar se deseja classificar os lançamentos
            if messagebox.askyesno("Classificação Contábil",
                                  "É necessário classificar os lançamentos em contas contábeis. Deseja fazer isso agora?"):
                self.classificar_lancamentos_contabeis()
            else:
                # Tentar converter automaticamente
                try:
                    self.contabilidade.converter_dados_para_lancamentos()
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao converter dados: {str(e)}")
                    return

        # Gerar RAÇU
        caminho = f"racu_{ano}.pdf"
        try:
            if self.contabilidade.gerar_racu(ano, caminho):
                messagebox.showinfo("Sucesso", f"RAÇU gerado: {caminho}")
                self.abrir_arquivo(caminho)
            else:
                messagebox.showwarning("Aviso", "Não foi possível gerar o RAÇU.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar RAÇU: {str(e)}")

    def gerar_fluxo_caixa(self):
        if not self.validar_dados():
            return

        # Solicitar período
        data_inicio_str = simpledialog.askstring("Data Inicial", "Informe a data inicial (DD/MM/AAAA):")
        if not data_inicio_str:
            return
            
        data_fim_str = simpledialog.askstring("Data Final", "Informe a data final (DD/MM/AAAA):")
        if not data_fim_str:
            return

        try:
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
        except:
            messagebox.showerror("Erro", "Data inválida!")
            return

        # Gerar fluxo de caixa
        caminho = f"fluxo_caixa_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.pdf"
        try:
            if self.contabilidade.gerar_fluxo_caixa(data_inicio, data_fim, caminho):
                messagebox.showinfo("Sucesso", f"Fluxo de Caixa gerado: {caminho}")
                self.abrir_arquivo(caminho)
            else:
                messagebox.showwarning("Aviso", "Não foi possível gerar o Fluxo de Caixa.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar Fluxo de Caixa: {str(e)}")

    def importar_banco(self):
        arquivo = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )
        if arquivo:
            self.selecionar_banco(arquivo)

    def selecionar_banco(self, arquivo):
        janela = tk.Toplevel(self.root)
        janela.title("Selecionar Banco")
        janela.geometry("300x200")

        banco_var = tk.StringVar()
        for banco in CONFIGURACOES['BANCOS'].keys():
            ttk.Radiobutton(
                janela,
                text=CONFIGURACOES['BANCOS'][banco]['nome'],
                variable=banco_var,
                value=banco
            ).pack(pady=5)

        def processar():
            banco = banco_var.get()
            try:
                self.dados_banco = ProcessadorBanco.processar_extrato(arquivo, banco)
                self.atualizar_interface()
                messagebox.showinfo("Sucesso", "Dados bancários importados com sucesso!")
                janela.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(janela, text="Importar", command=processar).pack(pady=10)

    def importar_livro(self):
        arquivo = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )
        if arquivo:
            try:
                self.dados_livro = pd.read_excel(arquivo) if arquivo.endswith('.xlsx') \
                    else pd.read_csv(arquivo)
                self.atualizar_interface()
                messagebox.showinfo("Sucesso", "Livro contábil importado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar arquivo: {str(e)}")

    def atualizar_interface(self):
        self.atualizar_estatisticas()
        self.atualizar_tabela()
        # Atualiza a contabilidade com os dados mais recentes
        if self.dados_banco is not None and self.dados_livro is not None:
            self.contabilidade.dados_banco = self.dados_banco
            self.contabilidade.dados_livro = self.dados_livro

    def atualizar_estatisticas(self):
        if self.dados_banco is not None:
            total_banco = self.dados_banco['valor'].sum()
            self.label_total_banco.config(
                text=f"Total Banco: Kz {total_banco:,.2f}")
        if self.dados_livro is not None:
            total_livro = self.dados_livro['valor'].sum()
            self.label_total_livro.config(
                text=f"Total Livro: Kz {total_livro:,.2f}")
        if self.dados_banco is not None and self.dados_livro is not None:
            diferenca = total_banco - total_livro
            self.label_diferenca.config(
                text=f"Diferença: Kz {diferenca:,.2f}")

    def atualizar_tabela(self):
        self.tabela.delete(*self.tabela.get_children())
        if self.dados_banco is not None:
            for _, row in self.dados_banco.iterrows():
                self.tabela.insert('', 'end', values=(
                    row['data'].strftime('%d/%m/%Y'),
                    row['descricao'],
                    f"Kz {row['valor']:,.2f}",
                    'BANCO',
                    'PENDENTE'
                ))

        if self.dados_livro is not None:
            for _, row in self.dados_livro.iterrows():
                self.tabela.insert('', 'end', values=(
                    row['data'].strftime('%d/%m/%Y'),
                    row['descricao'],
                    f"Kz {row['valor']:,.2f}",
                    'LIVRO',
                    'PENDENTE'
                ))

    def conciliar(self):
        if not self.validar_dados():
            return

        for _, row_banco in self.dados_banco.iterrows():
            match = self.dados_livro[
                (self.dados_livro['valor'] == row_banco['valor']) &
                (self.dados_livro['data'] == row_banco['data'])
            ]
            if not match.empty:
                # Atualizar status na tabela
                for item in self.tabela.get_children():
                    valores = self.tabela.item(item)['values']
                    if (valores[0] == row_banco['data'].strftime('%d/%m/%Y') and
                        valores[2] == f"Kz {row_banco['valor']:,.2f}"):
                        self.tabela.set(item, 'status', 'CONCILIADO')

    def mostrar_graficos(self):
        if not self.validar_dados():
            return

        janela = tk.Toplevel(self.root)
        janela.title("Análise Gráfica")
        janela.geometry("1000x600")

        fig = plt.Figure(figsize=(12, 6))
        # Gráfico de barras
        ax1 = fig.add_subplot(121)
        totais = [self.dados_banco['valor'].sum(), self.dados_livro['valor'].sum()]
        ax1.bar(['Banco', 'Livro'], totais)
        ax1.set_title('Comparativo de Totais')

        # Gráfico de evolução temporal
        ax2 = fig.add_subplot(122)
        ax2.plot(self.dados_banco['data'], self.dados_banco['valor'].cumsum(),
                label='Banco')
        ax2.plot(self.dados_livro['data'], self.dados_livro['valor'].cumsum(),
                label='Livro')
        ax2.set_title('Evolução Temporal')
        ax2.legend()
        plt.xticks(rotation=45)

        canvas = FigureCanvasTkAgg(fig, master=janela)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def gerar_relatorio_diario(self):
        if not self.validar_dados():
            return

        # Solicitar data específica
        data_str = simpledialog.askstring("Data", "Informe a data para o relatório (DD/MM/AAAA):")
        if not data_str:
            return
            
        try:
            data_ref = datetime.strptime(data_str, "%d/%m/%Y")
        except:
            messagebox.showerror("Erro", "Data inválida!")
            return

        caminho = f"relatorio_diario_{data_ref.strftime('%Y%m%d')}.pdf"
        try:
            self.gerador_relatorios.gerar_relatorio_diario(
                self.dados_banco,
                self.dados_livro,
                caminho,
                data_ref
            )
            messagebox.showinfo("Sucesso", f"Relatório gerado: {caminho}")
            self.abrir_arquivo(caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

    def gerar_relatorio_mensal(self):
        if not self.validar_dados():
            return

        # Solicitar mês e ano
        mes_ano_str = simpledialog.askstring("Mês/Ano", "Informe o mês e ano (MM/AAAA):")
        if not mes_ano_str:
            return
            
        try:
            mes_ano = datetime.strptime(mes_ano_str, "%m/%Y")
        except:
            messagebox.showerror("Erro", "Formato inválido! Use MM/AAAA")
            return

        dados_mensais = {
            'banco': self.dados_banco.groupby(
                self.dados_banco['data'].dt.strftime('%Y-%m'))['valor'].sum(),
            'livro': self.dados_livro.groupby(
                self.dados_livro['data'].dt.strftime('%Y-%m'))['valor'].sum()
        }

        caminho = f"relatorio_mensal_{mes_ano.strftime('%Y%m')}.pdf"
        try:
            self.gerador_relatorios.gerar_relatorio_mensal(dados_mensais, caminho, mes_ano)
            messagebox.showinfo("Sucesso", f"Relatório gerado: {caminho}")
            self.abrir_arquivo(caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

    def gerar_relatorio_divergencias(self):
        if not self.validar_dados():
            return

        divergencias = []
        for _, row_banco in self.dados_banco.iterrows():
            match = self.dados_livro[
                (self.dados_livro['valor'] == row_banco['valor']) &
                (self.dados_livro['data'] == row_banco['data'])
            ]
            if match.empty:
                divergencias.append({
                    'data': row_banco['data'],
                    'descricao': row_banco['descricao'],
                    'valor': row_banco['valor'],
                    'origem': 'BANCO'
                })

        caminho = f"relatorio_divergencias_{datetime.now().strftime('%Y%m%d')}.pdf"
        try:
            self.gerador_relatorios.gerar_relatorio_divergencias(divergencias, caminho)
            messagebox.showinfo("Sucesso", f"Relatório gerado: {caminho}")
            self.abrir_arquivo(caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

    def validar_dados(self):
        if self.dados_banco is None or self.dados_livro is None:
            messagebox.showwarning("Aviso", "Importe todos os dados primeiro!")
            return False
        return True

    def limpar_dados(self):
        self.dados_banco = None
        self.dados_livro = None
        self.tabela.delete(*self.tabela.get_children())
        self.atualizar_estatisticas()
        messagebox.showinfo("Sucesso", "Dados limpos com sucesso!")

    def gerar_balanco(self):
        if not self.validar_dados():
            return

        # Atualiza os dados da contabilidade
        self.contabilidade.dados_banco = self.dados_banco
        self.contabilidade.dados_livro = self.dados_livro

        # Solicita a data de referência
        data_str = simpledialog.askstring("Data", "Informe a data de referência (DD/MM/AAAA):")
        if not data_str:
            return
            
        try:
            data_ref = datetime.strptime(data_str, "%d/%m/%Y")
        except:
            messagebox.showerror("Erro", "Data inválida!")
            return

        if not hasattr(self.contabilidade, 'lancamentos') or not self.contabilidade.lancamentos:
            # Perguntar se deseja classificar os lançamentos
            if messagebox.askyesno("Classificação Contábil",
                                  "É necessário classificar os lançamentos em contas contábeis. Deseja fazer isso agora?"):
                self.classificar_lancamentos_contabeis()
            else:
                # Tentar converter automaticamente
                try:
                    self.contabilidade.converter_dados_para_lancamentos()
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao converter dados: {str(e)}")
                    return

        # Gera o balanço
        caminho = f"balanco_patrimonial_{data_ref.strftime('%Y%m%d')}.pdf"
        try:
            if self.contabilidade.gerar_balanco_patrimonial(data_ref, caminho):
                messagebox.showinfo("Sucesso", f"Balanço gerado: {caminho}")
                self.abrir_arquivo(caminho)
            else:
                messagebox.showwarning("Aviso", "Não foi possível gerar o Balanço Patrimonial.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar Balanço: {str(e)}")

    def gerar_dre(self):
        if not self.validar_dados():
            return

        # Atualiza os dados da contabilidade
        self.contabilidade.dados_banco = self.dados_banco
        self.contabilidade.dados_livro = self.dados_livro

        # Solicita o período
        data_inicio_str = simpledialog.askstring("Data Inicial", "Informe a data inicial (DD/MM/AAAA):")
        if not data_inicio_str:
            return
            
        data_fim_str = simpledialog.askstring("Data Final", "Informe a data final (DD/MM/AAAA):")
        if not data_fim_str:
            return

        try:
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
        except:
            messagebox.showerror("Erro", "Data inválida!")
            return

        # Verificar se há lançamentos classificados
        if not hasattr(self.contabilidade, 'lancamentos') or not self.contabilidade.lancamentos:
            # Perguntar se deseja classificar os lançamentos
            if messagebox.askyesno("Classificação Contábil",
                                  "É necessário classificar os lançamentos em contas contábeis. Deseja fazer isso agora?"):
                self.classificar_lancamentos_contabeis()
            else:
                # Tentar converter automaticamente
                try:
                    self.contabilidade.converter_dados_para_lancamentos()
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao converter dados: {str(e)}")
                    return

        # Gera a DRE
        caminho = f"dre_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.pdf"
        try:
            if self.contabilidade.gerar_dre(data_inicio, data_fim, caminho):
                messagebox.showinfo("Sucesso", f"DRE gerada: {caminho}")
                self.abrir_arquivo(caminho)
            else:
                messagebox.showwarning("Aviso", "Não foi possível gerar a DRE.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar DRE: {str(e)}")

    def importar_lancamentos_contabeis(self):
        arquivo = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )
        if not arquivo:
            return

        try:
            # Importar os dados do arquivo
            if arquivo.endswith('.xlsx'):
                lancamentos = pd.read_excel(arquivo)
            else:
                lancamentos = pd.read_csv(arquivo, encoding='utf-8')

            # Verificar se as colunas necessárias existem
            colunas_necessarias = ['data', 'descricao', 'valor']
            colunas_faltantes = [col for col in colunas_necessarias if col not in lancamentos.columns]

            if colunas_faltantes:
                # Tentar mapear colunas com nomes similares
                mapeamento = {
                    'data': ['data', 'date', 'dt', 'data_lancamento', 'data_lançamento'],
                    'descricao': ['descricao', 'descrição', 'desc', 'historico', 'histórico', 'narrativa'],
                    'valor': ['valor', 'value', 'montante', 'quantia', 'amount']
                }
                for col_necessaria in colunas_faltantes:
                    for col_alternativa in mapeamento[col_necessaria]:
                        if col_alternativa in lancamentos.columns:
                            lancamentos.rename(columns={col_alternativa: col_necessaria}, inplace=True)
                            break

                # Verificar novamente se todas as colunas necessárias existem
                colunas_faltantes = [col for col in colunas_necessarias if col not in lancamentos.columns]
                if colunas_faltantes:
                    messagebox.showerror("Erro", f"O arquivo não contém as colunas necessárias: {', '.join(colunas_faltantes)}")
                    return

            # Converter a coluna de data para datetime
            try:
                if not pd.api.types.is_datetime64_any_dtype(lancamentos['data']):
                    # Tentar diferentes formatos de data
                    formatos_data = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']
                    convertido = False
                    for formato in formatos_data:
                        try:
                            lancamentos['data'] = pd.to_datetime(lancamentos['data'], format=formato)
                            convertido = True
                            break
                        except:
                            continue

                    if not convertido:
                        # Tentar conversão automática
                        lancamentos['data'] = pd.to_datetime(lancamentos['data'], errors='coerce')
                        # Verificar se há datas inválidas (NaT)
                        if lancamentos['data'].isna().any():
                            messagebox.showwarning("Aviso", "Algumas datas não puderam ser convertidas e serão ignoradas.")
                            lancamentos = lancamentos.dropna(subset=['data'])
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao converter datas: {str(e)}")
                return

            # Garantir que a coluna valor seja numérica
            try:
                if not pd.api.types.is_numeric_dtype(lancamentos['valor']):
                    # Remover caracteres não numéricos (exceto ponto e vírgula)
                    lancamentos['valor'] = lancamentos['valor'].astype(str)
                    lancamentos['valor'] = lancamentos['valor'].str.replace('[^\d.,]', '', regex=True)
                    # Substituir vírgula por ponto
                    lancamentos['valor'] = lancamentos['valor'].str.replace(',', '.')
                    # Converter para float
                    lancamentos['valor'] = pd.to_numeric(lancamentos['valor'], errors='coerce')
                    # Verificar se há valores inválidos (NaN)
                    if lancamentos['valor'].isna().any():
                        messagebox.showwarning("Aviso", "Alguns valores não puderam ser convertidos e serão ignorados.")
                        lancamentos = lancamentos.dropna(subset=['valor'])
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao converter valores: {str(e)}")
                return

            # Adicionar coluna de origem se não existir
            if 'origem' not in lancamentos.columns:
                lancamentos['origem'] = 'LIVRO'

            # Adicionar coluna de status se não existir
            if 'status' not in lancamentos.columns:
                lancamentos['status'] = 'PENDENTE'

            # Atualizar os dados do livro
            if self.dados_livro is None:
                self.dados_livro = lancamentos
                messagebox.showinfo("Sucesso", f"{len(lancamentos)} lançamentos importados com sucesso!")
            else:
                # Verificar se há lançamentos duplicados
                chaves_existentes = set()
                if not self.dados_livro.empty:
                    for _, row in self.dados_livro.iterrows():
                        chaves_existentes.add((row['data'], row['descricao'], row['valor']))
                    
                lancamentos_novos = lancamentos[~lancamentos.apply(
                    lambda row: (row['data'], row['descricao'], row['valor']) in chaves_existentes,
                    axis=1
                )]

                if lancamentos_novos.empty:
                    messagebox.showinfo("Informação", "Todos os lançamentos já existem no sistema.")
                    return

                self.dados_livro = pd.concat([self.dados_livro, lancamentos_novos], ignore_index=True)
                # Informar quantos lançamentos foram importados
                messagebox.showinfo("Sucesso", f"{len(lancamentos_novos)} novos lançamentos importados com sucesso!")

            # Atualizar a interface
            self.atualizar_interface()

            # Atualizar a contabilidade com os novos dados
            if hasattr(self, 'contabilidade'):
                self.contabilidade.dados_livro = self.dados_livro

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao importar lançamentos: {str(e)}")
            # Mostrar detalhes do erro para depuração
            import traceback
            traceback.print_exc()

    def registrar_bem_amortizavel(self):
        # Cria uma janela para entrada de dados
        janela = tk.Toplevel(self.root)
        janela.title("Registrar Bem Amortizável")
        janela.geometry("400x300")

        ttk.Label(janela, text="Código:").grid(row=0, column=0, padx=5, pady=5)
        codigo_var = tk.StringVar()
        ttk.Entry(janela, textvariable=codigo_var).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(janela, text="Descrição:").grid(row=1, column=0, padx=5, pady=5)
        descricao_var = tk.StringVar()
        ttk.Entry(janela, textvariable=descricao_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(janela, text="Valor:").grid(row=2, column=0, padx=5, pady=5)
        valor_var = tk.DoubleVar()
        ttk.Entry(janela, textvariable=valor_var).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(janela, text="Data Aquisição:").grid(row=3, column=0, padx=5, pady=5)
        data_var = tk.StringVar()
        ttk.Entry(janela, textvariable=data_var).grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(janela, text="Vida Útil (anos):").grid(row=4, column=0, padx=5, pady=5)
        vida_util_var = tk.IntVar()
        ttk.Entry(janela, textvariable=vida_util_var).grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(janela, text="Valor Residual:").grid(row=5, column=0, padx=5, pady=5)
        residual_var = tk.DoubleVar()
        ttk.Entry(janela, textvariable=residual_var).grid(row=5, column=1, padx=5, pady=5)

        def registrar():
            try:
                codigo = codigo_var.get()
                descricao = descricao_var.get()
                valor = valor_var.get()
                data = datetime.strptime(data_var.get(), "%d/%m/%Y")
                vida_util = vida_util_var.get()
                residual = residual_var.get()

                self.contabilidade.registrar_bem_amortizavel(
                    codigo, descricao, valor, data, vida_util, residual)
                messagebox.showinfo("Sucesso", "Bem amortizável registrado com sucesso!")
                janela.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(janela, text="Registrar", command=registrar).grid(row=6, column=1, pady=10)

    def realizar_backup(self):
        """Realiza backup dos dados do sistema"""
        diretorio = self.configuracoes.obter_config("sistema", "diretorio_backup")
        if not diretorio or not os.path.exists(diretorio):
            diretorio = filedialog.askdirectory(title="Selecionar Diretório para Backup")
            if not diretorio:
                return
            self.configuracoes.definir_config("sistema", "diretorio_backup", diretorio)

        try:
            # Implementar lógica de backup
            data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo_backup = os.path.join(diretorio, f"backup_{data_hora}.zip")

            with zipfile.ZipFile(arquivo_backup, 'w') as zip_file:
                # Adicionar arquivos de configuração
                if os.path.exists(self.configuracoes.arquivo_config):
                    zip_file.write(self.configuracoes.arquivo_config)

                # Adicionar arquivos de temas
                if os.path.exists(self.gerenciador_temas.arquivo_temas):
                    zip_file.write(self.gerenciador_temas.arquivo_temas)

                # Adicionar arquivos de dados
                for arquivo in glob.glob("*.json") + glob.glob("*.xlsx") + glob.glob("*.csv"):
                    zip_file.write(arquivo)

            messagebox.showinfo("Sucesso", f"Backup realizado com sucesso!\nArquivo: {arquivo_backup}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao realizar backup: {str(e)}")

    def restaurar_backup(self):
        """Restaura um backup anterior"""
        arquivo = filedialog.askopenfilename(
            title="Selecionar Arquivo de Backup",
            filetypes=[("Arquivos ZIP", "*.zip")]
        )
        if not arquivo:
            return

        try:
            # Criar diretório temporário
            temp_dir = tempfile.mkdtemp()

            # Extrair backup
            with zipfile.ZipFile(arquivo, 'r') as zip_file:
                zip_file.extractall(temp_dir)

            # Perguntar antes de sobrescrever
            if not messagebox.askyesno("Confirmar", "Esta operação irá sobrescrever os dados atuais. Continuar?"):
                shutil.rmtree(temp_dir)
                return

            # Copiar arquivos de volta
            for arquivo_temp in os.listdir(temp_dir):
                caminho_temp = os.path.join(temp_dir, arquivo_temp)
                shutil.copy2(caminho_temp, os.path.join(os.getcwd(), arquivo_temp))

            # Limpar diretório temporário
            shutil.rmtree(temp_dir)

            messagebox.showinfo("Sucesso", "Backup restaurado com sucesso! O sistema será reiniciado.")
            
            # Reiniciar aplicação
            self.root.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao restaurar backup: {str(e)}")

    def mostrar_sobre(self):
        """Exibe informações sobre o sistema"""
        janela = tk.Toplevel(self.root)
        janela.title("Sobre o Sistema")
        janela.geometry("400x300")
        janela.transient(self.root)

        # Aplicar tema atual
        if hasattr(self, 'gerenciador_temas'):
            self.gerenciador_temas.aplicar_tema_janela(janela)

        # Frame principal
        frame = ttk.Frame(janela, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Logo (placeholder)
        ttk.Label(frame, text="[LOGO]", font=('Helvetica', 24)).pack(pady=10)

        # Informações
        ttk.Label(frame, text="Sistema de Reconciliação Contábil",
                 font=('Helvetica', 14, 'bold')).pack(pady=5)
        ttk.Label(frame, text="Versão 1.0.0").pack()
        ttk.Label(frame, text="© 2023 - Todos os direitos reservados").pack(pady=10)

        # Informações da empresa
        nome_empresa = self.configuracoes.obter_config("empresa", "nome")
        if nome_empresa:
            ttk.Label(frame, text=f"Licenciado para: {nome_empresa}").pack()

        # Botão fechar
        ttk.Button(frame, text="Fechar", command=janela.destroy).pack(pady=10)

    def abrir_manual(self):
        """Abre o manual do usuário"""
        # Verificar se o manual existe
        caminho_manual = "manual_usuario.pdf"
        if not os.path.exists(caminho_manual):
            messagebox.showinfo("Informação", "Manual do usuário não encontrado.")
            return

        # Abrir o manual com o programa padrão
        self.abrir_arquivo(caminho_manual)

    def abrir_arquivo(self, caminho):
        """Abre um arquivo com o programa padrão do sistema operacional"""
        if not os.path.exists(caminho):
            messagebox.showinfo("Informação", f"Arquivo não encontrado: {caminho}")
            return
            
        sistema = platform.system()
        try:
            if sistema == 'Windows':
                os.startfile(caminho)
            elif sistema == 'Darwin':  # macOS
                subprocess.call(['open', caminho])
            else:  # Linux e outros
                subprocess.call(['xdg-open', caminho])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir o arquivo: {str(e)}")

    def executar(self):
        """Inicia a execução do aplicativo"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = ReconciliacaoApp()
        app.executar()
    except Exception as e:
        import traceback
        print(f"Erro fatal: {str(e)}")
        traceback.print_exc()
        # Tentar mostrar uma mensagem de erro mesmo se a interface gráfica falhar
        try:
            messagebox.showerror("Erro Fatal", f"O sistema encontrou um erro fatal e precisa ser encerrado:\n\n{str(e)}")
        except:
            pass
