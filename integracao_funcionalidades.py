import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import platform
import subprocess

from conciliacao_automatica import ConciliacaoBancariaAutomatica
from fluxo_caixa_projetado import FluxoCaixaProjetado
from auditoria import SistemaAuditoria
from orcamento_realizado import OrcamentoRealizado

class IntegradorFuncionalidades:
    def __init__(self, app):
        """
        Integra as novas funcionalidades ao sistema existente
        
        Args:
            app: Instância da classe ReconciliacaoApp
        """
        self.app = app
        self.contabilidade = app.contabilidade
        
        # Inicializar módulos
        self.conciliacao = ConciliacaoBancariaAutomatica(self.contabilidade)
        self.fluxo_caixa = FluxoCaixaProjetado(self.contabilidade)
        self.auditoria = SistemaAuditoria(self.contabilidade)
        self.orcamento = OrcamentoRealizado(self.contabilidade)
        
        # Adicionar novas opções ao menu
        self._adicionar_menus()
    
    def _adicionar_menus(self):
        """Adiciona novos itens de menu ao sistema"""
        # Verificar se já existe um menu principal
        if hasattr(self.app, 'menu_principal'):
            menu_principal = self.app.menu_principal
        else:
            # Se não existir, criar um novo menu principal
            print("AVISO: Menu principal não encontrado. Criando novo menu.")
            menu_principal = tk.Menu(self.app.root)
            self.app.root.config(menu=menu_principal)
            self.app.menu_principal = menu_principal
        
        # Verificar quais menus já existem para não duplicar
        menus_existentes = {}
        try:
            for i in range(menu_principal.index('end') + 1 if menu_principal.index('end') is not None else 0):
                try:
                    label = menu_principal.entrycget(i, 'label')
                    menus_existentes[label] = i
                except:
                    pass
        except:
            pass
        
        print(f"Menus existentes: {list(menus_existentes.keys())}")
        
        # 1. Menu de Conciliação Bancária
        if "Conciliação Bancária" in menus_existentes:
            # Se o menu já existe, obter referência
            idx = menus_existentes["Conciliação Bancária"]
            menu_conciliacao = menu_principal.entrycget(idx, 'menu')
        else:
            # Se não existe, criar novo
            menu_conciliacao = tk.Menu(menu_principal, tearoff=0)
            menu_principal.add_cascade(label="Conciliação Bancária", menu=menu_conciliacao)
        
        # Adicionar itens ao menu de Conciliação Bancária
        menu_conciliacao.add_command(label="Conciliação Automática", command=self.abrir_conciliacao_automatica)
        menu_conciliacao.add_command(label="Relatório de Conciliação", command=self.gerar_relatorio_conciliacao)
        menu_conciliacao.add_command(label="Resolver Discrepâncias", command=self.resolver_discrepancias)
        
        # 2. Menu de Fluxo de Caixa
        if "Fluxo de Caixa" in menus_existentes:
            idx = menus_existentes["Fluxo de Caixa"]
            menu_fluxo_caixa = menu_principal.entrycget(idx, 'menu')
        else:
            menu_fluxo_caixa = tk.Menu(menu_principal, tearoff=0)
            menu_principal.add_cascade(label="Fluxo de Caixa", menu=menu_fluxo_caixa)
        
        menu_fluxo_caixa.add_command(label="Projeção de Fluxo de Caixa", command=self.abrir_projecao_fluxo_caixa)
        menu_fluxo_caixa.add_command(label="Lançamentos Recorrentes", command=self.gerenciar_lancamentos_recorrentes)
        menu_fluxo_caixa.add_command(label="Relatório de Fluxo de Caixa", command=self.gerar_relatorio_fluxo_caixa)
        
        # 3. Menu de Auditoria
        if "Auditoria" in menus_existentes:
            idx = menus_existentes["Auditoria"]
            menu_auditoria = menu_principal.entrycget(idx, 'menu')
        else:
            menu_auditoria = tk.Menu(menu_principal, tearoff=0)
            menu_principal.add_cascade(label="Auditoria", menu=menu_auditoria)
        
        menu_auditoria.add_command(label="Trilha de Alterações", command=self.abrir_trilha_alteracoes)
        menu_auditoria.add_command(label="Relatório de Auditoria", command=self.gerar_relatorio_auditoria)
        
        # 4. Menu de Orçamento
        if "Orçamento" in menus_existentes:
            idx = menus_existentes["Orçamento"]
            menu_orcamento = menu_principal.entrycget(idx, 'menu')
        else:
            menu_orcamento = tk.Menu(menu_principal, tearoff=0)
            menu_principal.add_cascade(label="Orçamento", menu=menu_orcamento)
        
        menu_orcamento.add_command(label="Definir Orçamento", command=self.definir_orcamento)
        menu_orcamento.add_command(label="Comparar Orçado vs. Realizado", command=self.comparar_orcado_realizado)
        menu_orcamento.add_command(label="Alertas de Desvios", command=self.mostrar_alertas_desvios)
        
        # Chamar a função de diagnóstico para verificar a estrutura final dos menus
        if hasattr(self.app, 'diagnosticar_menus'):
            print("Executando diagnóstico de menus após adicionar novos menus:")
            self.app.diagnosticar_menus()
    
    # ===== Métodos para Conciliação Bancária =====
    
    def abrir_conciliacao_automatica(self):
        """Abre a interface para conciliação bancária automática"""
        # Verificar se há dados carregados
        if self.app.dados_banco is None or self.app.dados_livro is None:
            messagebox.showwarning("Aviso", "Importe os dados bancários e contábeis primeiro!")
            return
        
        # Criar janela
        janela = tk.Toplevel(self.app.root)
        janela.title("Conciliação Bancária Automática")
        janela.geometry("800x600")
        janela.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame_principal = ttk.Frame(janela, padding=10)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Frame de parâmetros
        frame_parametros = ttk.LabelFrame(frame_principal, text="Parâmetros de Conciliação", padding=10)
        frame_parametros.pack(fill=tk.X, pady=10)
        
        # Parâmetros
        ttk.Label(frame_parametros, text="Tolerância de dias:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        tolerancia_dias = ttk.Spinbox(frame_parametros, from_=0, to=10, width=5)
        tolerancia_dias.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        tolerancia_dias.set(3)
        
        ttk.Label(frame_parametros, text="Tolerância de texto (%):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        tolerancia_texto = ttk.Spinbox(frame_parametros, from_=50, to=100, width=5)
        tolerancia_texto.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        tolerancia_texto.set(80)
        
        # Botão de conciliação
        btn_conciliar = ttk.Button(frame_parametros, text="Iniciar Conciliação", 
                                  command=lambda: self._executar_conciliacao(janela, int(tolerancia_dias.get()), 
                                                                           float(tolerancia_texto.get())))
        btn_conciliar.grid(row=0, column=4, padx=20, pady=5)
        
        # Frame de resultados
        frame_resultados = ttk.LabelFrame(frame_principal, text="Resultados da Conciliação", padding=10)
        frame_resultados.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Notebook para abas de resultados
        notebook = ttk.Notebook(frame_resultados)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de transações conciliadas
        tab_conciliadas = ttk.Frame(notebook, padding=10)
        notebook.add(tab_conciliadas, text="Conciliadas")
        
        # Aba de discrepâncias
        tab_discrepancias = ttk.Frame(notebook, padding=10)
        notebook.add(tab_discrepancias, text="Discrepâncias")
        
        # Treeview para transações conciliadas
        colunas_conciliadas = ["id", "data_banco", "descricao_banco", "valor_banco", 
                              "data_livro", "descricao_livro", "valor_livro", "metodo"]
        
        tree_conciliadas = ttk.Treeview(tab_conciliadas, columns=colunas_conciliadas, show="headings")
        tree_conciliadas.pack(fill=tk.BOTH, expand=True)
        
        # Configurar colunas
        tree_conciliadas.heading("id", text="ID")
        tree_conciliadas.heading("data_banco", text="Data Banco")
        tree_conciliadas.heading("descricao_banco", text="Descrição Banco")
        tree_conciliadas.heading("valor_banco", text="Valor Banco")
        tree_conciliadas.heading("data_livro", text="Data Livro")
        tree_conciliadas.heading("descricao_livro", text="Descrição Livro")
        tree_conciliadas.heading("valor_livro", text="Valor Livro")
        tree_conciliadas.heading("metodo", text="Método")
        
        tree_conciliadas.column("id", width=50)
        tree_conciliadas.column("data_banco", width=100)
        tree_conciliadas.column("descricao_banco", width=150)
        tree_conciliadas.column("valor_banco", width=100)
        tree_conciliadas.column("data_livro", width=100)
        tree_conciliadas.column("descricao_livro", width=150)
        tree_conciliadas.column("valor_livro", width=100)
        tree_conciliadas.column("metodo", width=100)
        
        # Scrollbar para transações conciliadas
        scrollbar_conciliadas = ttk.Scrollbar(tab_conciliadas, orient=tk.VERTICAL, command=tree_conciliadas.yview)
        tree_conciliadas.configure(yscrollcommand=scrollbar_conciliadas.set)
        scrollbar_conciliadas.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview para discrepâncias
        colunas_discrepancias = ["id", "data", "descricao", "valor", "origem", "tipo"]
        
        tree_discrepancias = ttk.Treeview(tab_discrepancias, columns=colunas_discrepancias, show="headings")
        tree_discrepancias.pack(fill=tk.BOTH, expand=True)
        
        # Configurar colunas
        tree_discrepancias.heading("id", text="ID")
        tree_discrepancias.heading("data", text="Data")
        tree_discrepancias.heading("descricao", text="Descrição")
        tree_discrepancias.heading("valor", text="Valor")
        tree_discrepancias.heading("origem", text="Origem")
        tree_discrepancias.heading("tipo", text="Tipo")
        
        tree_discrepancias.column("id", width=50)
        tree_discrepancias.column("data", width=100)
        tree_discrepancias.column("descricao", width=250)
        tree_discrepancias.column("valor", width=100)
        tree_discrepancias.column("origem", width=100)
        tree_discrepancias.column("tipo", width=150)
        
        # Scrollbar para discrepâncias
        scrollbar_discrepancias = ttk.Scrollbar(tab_discrepancias, orient=tk.VERTICAL, command=tree_discrepancias.yview)
        tree_discrepancias.configure(yscrollcommand=scrollbar_discrepancias.set)
        scrollbar_discrepancias.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        # Botões
        btn_relatorio = ttk.Button(frame_botoes, text="Gerar Relatório", 
                                  command=self.gerar_relatorio_conciliacao)
        btn_relatorio.pack(side=tk.LEFT, padx=5)
        
        btn_resolver = ttk.Button(frame_botoes, text="Resolver Discrepâncias", 
                                 command=self.resolver_discrepancias)
        btn_resolver.pack(side=tk.LEFT, padx=5)
        
        btn_fechar = ttk.Button(frame_botoes, text="Fechar", command=janela.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=5)
        
        # Armazenar referências
        janela.tree_conciliadas = tree_conciliadas
        janela.tree_discrepancias = tree_discrepancias
    
    def _executar_conciliacao(self, janela, tolerancia_dias, tolerancia_texto):
        """Executa a conciliação bancária automática"""
        try:
            # Limpar treeviews
            janela.tree_conciliadas.delete(*janela.tree_conciliadas.get_children())
            janela.tree_discrepancias.delete(*janela.tree_discrepancias.get_children())
            
            # Executar conciliação
            transacoes_conciliadas, discrepancias = self.conciliacao.conciliar_automaticamente(
                self.app.dados_banco, 
                self.app.dados_livro,
                tolerancia_dias=tolerancia_dias,
                tolerancia_texto=tolerancia_texto
            )
            
            # Preencher treeview de transações conciliadas
            for i, transacao in enumerate(transacoes_conciliadas):
                data_banco = transacao['data_banco'].strftime('%d/%m/%Y') if isinstance(transacao['data_banco'], datetime) else transacao['data_banco']
                data_livro = transacao['data_livro'].strftime('%d/%m/%Y') if isinstance(transacao['data_livro'], datetime) else transacao['data_livro']
                
                janela.tree_conciliadas.insert("", tk.END, values=(
                    transacao['id_conciliacao'],
                    data_banco,
                    transacao['descricao_banco'][:30] + "..." if len(transacao['descricao_banco']) > 30 else transacao['descricao_banco'],
                    f"Kz {transacao['valor_banco']:,.2f}",
                    data_livro,
                    transacao['descricao_livro'][:30] + "..." if len(transacao['descricao_livro']) > 30 else transacao['descricao_livro'],
                    f"Kz {transacao['valor_livro']:,.2f}",
                    transacao['metodo'].replace('_', ' ').title()
                ))
            
            # Preencher treeview de discrepâncias
            for i, discrepancia in enumerate(discrepancias):
                janela.tree_discrepancias.insert("", tk.END, values=(
                    i + 1,
                    discrepancia['data'].strftime('%d/%m/%Y'),
                    discrepancia['descricao'][:50] + "..." if len(discrepancia['descricao']) > 50 else discrepancia['descricao'],
                    f"Kz {discrepancia['valor']:,.2f}",
                    discrepancia['origem'],
                    discrepancia['tipo'].replace('_', ' ').title()
                ))
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo("Conciliação Concluída", 
                               f"Conciliação concluída com sucesso!\n\n"
                               f"Transações conciliadas: {len(transacoes_conciliadas)}\n"
                               f"Discrepâncias encontradas: {len(discrepancias)}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar conciliação: {str(e)}")
    
    def gerar_relatorio_conciliacao(self):
        """Gera um relatório de conciliação bancária"""
        # Verificar se há dados de conciliação
        if not hasattr(self.conciliacao, 'transacoes_conciliadas') or not self.conciliacao.transacoes_conciliadas:
            messagebox.showwarning("Aviso", "Execute a conciliação bancária primeiro!")
            return
        
        # Solicitar caminho para salvar o relatório
        caminho_saida = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf")],
            title="Salvar Relatório de Conciliação"
        )
        
        if not caminho_saida:
            return
        
        # Gerar relatório
        if self.conciliacao.gerar_relatorio_conciliacao(caminho_saida):
            messagebox.showinfo("Sucesso", f"Relatório de conciliação gerado com sucesso!\n\nSalvo em: {caminho_saida}")
            
            # Perguntar se deseja abrir o relatório
            if messagebox.askyesno("Abrir Relatório", "Deseja abrir o relatório agora?"):
                self._abrir_arquivo(caminho_saida)
        else:
            messagebox.showerror("Erro", "Erro ao gerar relatório de conciliação.")
    
    def resolver_discrepancias(self):
        """Abre a interface para resolver discrepâncias"""
        # Verificar se há discrepâncias
        if not hasattr(self.conciliacao, 'discrepancias') or not self.conciliacao.discrepancias:
            messagebox.showwarning("Aviso", "Execute a conciliação bancária primeiro ou não há discrepâncias para resolver!")
            return
        
        # Criar janela
        janela = tk.Toplevel(self.app.root)
        janela.title("Resolver Discrepâncias")
        janela.geometry("900x700")
        janela.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame_principal = ttk.Frame(janela, padding=10)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Frame de discrepâncias
        frame_discrepancias = ttk.LabelFrame(frame_principal, text="Discrepâncias Encontradas", padding=10)
        frame_discrepancias.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview para discrepâncias
        colunas = ["id", "data", "descricao", "valor", "origem", "tipo"]
        
        tree_discrepancias = ttk.Treeview(frame_discrepancias, columns=colunas, show="headings")
        tree_discrepancias.pack(fill=tk.BOTH, expand=True)
        
        # Configurar colunas
        tree_discrepancias.heading("id", text="ID")
        tree_discrepancias.heading("data", text="Data")
        tree_discrepancias.heading("descricao", text="Descrição")
        tree_discrepancias.heading("valor", text="Valor")
        tree_discrepancias.heading("origem", text="Origem")
        tree_discrepancias.heading("tipo", text="Tipo")
        
        tree_discrepancias.column("id", width=50)
        tree_discrepancias.column("data", width=100)
        tree_discrepancias.column("descricao", width=300)
        tree_discrepancias.column("valor", width=100)
        tree_discrepancias.column("origem", width=100)
        tree_discrepancias.column("tipo", width=150)
        
        # Scrollbar para discrepâncias
        scrollbar = ttk.Scrollbar(frame_discrepancias, orient=tk.VERTICAL, command=tree_discrepancias.yview)
        tree_discrepancias.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher treeview
        for i, discrepancia in enumerate(self.conciliacao.discrepancias):
            tree_discrepancias.insert("", tk.END, values=(
                i + 1,
                discrepancia['data'].strftime('%d/%m/%Y'),
                discrepancia['descricao'][:50] + "..." if len(discrepancia['descricao']) > 50 else discrepancia['descricao'],
                f"Kz {discrepancia['valor']:,.2f}",
                discrepancia['origem'],
                discrepancia['tipo'].replace('_', ' ').title()
            ))
        
        # Frame de detalhes
        frame_detalhes = ttk.LabelFrame(frame_principal, text="Detalhes da Discrepância", padding=10)
        frame_detalhes.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Detalhes da discrepância
        lbl_data = ttk.Label(frame_detalhes, text="Data:")
        lbl_data.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        var_data = tk.StringVar()
        entry_data = ttk.Entry(frame_detalhes, textvariable=var_data, state="readonly", width=15)
        entry_data.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        lbl_descricao = ttk.Label(frame_detalhes, text="Descrição:")
        lbl_descricao.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        var_descricao = tk.StringVar()
        entry_descricao = ttk.Entry(frame_detalhes, textvariable=var_descricao, state="readonly", width=50)
        entry_descricao.grid(row=1, column=1, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        
        lbl_valor = ttk.Label(frame_detalhes, text="Valor:")
        lbl_valor.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        var_valor = tk.StringVar()
        entry_valor = ttk.Entry(frame_detalhes, textvariable=var_valor, state="readonly", width=15)
        entry_valor.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        lbl_origem = ttk.Label(frame_detalhes, text="Origem:")
        lbl_origem.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        var_origem = tk.StringVar()
        entry_origem = ttk.Entry(frame_detalhes, textvariable=var_origem, state="readonly", width=15)
        entry_origem.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Frame de sugestões
        frame_sugestoes = ttk.LabelFrame(frame_detalhes, text="Sugestões de Correção", padding=10)
        frame_sugestoes.grid(row=3, column=0, columnspan=4, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=10)
        
        # Listbox para sugestões
        listbox_sugestoes = tk.Listbox(frame_sugestoes, height=5, width=80)
        listbox_sugestoes.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar para sugestões
        scrollbar_sugestoes = ttk.Scrollbar(frame_sugestoes, orient=tk.VERTICAL, command=listbox_sugestoes.yview)
        listbox_sugestoes.configure(yscrollcommand=scrollbar_sugestoes.set)
        scrollbar_sugestoes.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        # Botões
        btn_aplicar = ttk.Button(frame_botoes, text="Aplicar Sugestão", 
                               command=lambda: self._aplicar_sugestao(janela))
        btn_aplicar.pack(side=tk.LEFT, padx=5)
        
        btn_ignorar = ttk.Button(frame_botoes, text="Ignorar Discrepância", 
                               command=lambda: self._ignorar_discrepancia(janela))
        btn_ignorar.pack(side=tk.LEFT, padx=5)
        
        btn_fechar = ttk.Button(frame_botoes, text="Fechar", command=janela.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=5)
        
        # Evento de seleção na treeview
        def ao_selecionar_discrepancia(event):
            # Obter item selecionado
            selecao = tree_discrepancias.selection()
            if not selecao:
                return
            
            # Obter ID da discrepância
            item = tree_discrepancias.item(selecao[0])
            id_discrepancia = int(item['values'][0]) - 1
            
            # Obter discrepância
            discrepancia = self.conciliacao.discrepancias[id_discrepancia]
            
            # Atualizar campos
            var_data.set(discrepancia['data'].strftime('%d/%m/%Y'))
            var_descricao.set(discrepancia['descricao'])
            var_valor.set(f"Kz {discrepancia['valor']:,.2f}")
            var_origem.set(discrepancia['origem'])
            
            # Limpar e preencher listbox de sugestões
            listbox_sugestoes.delete(0, tk.END)
            
            if 'sugestao' in discrepancia and discrepancia['sugestao']:
                for i, sugestao in enumerate(discrepancia['sugestao']):
                    if sugestao['tipo'] == 'generico':
                        listbox_sugestoes.insert(tk.END, f"{i+1}. {sugestao['mensagem']}")
                    else:
                        texto_sugestao = f"{i+1}. {sugestao['tipo'].replace('_', ' ').title()}: "
                        if 'data' in sugestao:
                            texto_sugestao += f"Data: {sugestao['data'].strftime('%d/%m/%Y')}, "
                        texto_sugestao += f"Valor: Kz {sugestao['valor']:,.2f}"
                        if 'similaridade' in sugestao:
                            texto_sugestao += f", Similaridade: {sugestao['similaridade']}%"
                        listbox_sugestoes.insert(tk.END, texto_sugestao)
            else:
                listbox_sugestoes.insert(tk.END, "Nenhuma sugestão disponível.")
        
        tree_discrepancias.bind("<<TreeviewSelect>>", ao_selecionar_discrepancia)
        
        # Armazenar referências
        janela.tree_discrepancias = tree_discrepancias
        janela.listbox_sugestoes = listbox_sugestoes
    
    def _aplicar_sugestao(self, janela):
        """Aplica a sugestão selecionada"""
        # Obter discrepância selecionada
        selecao_discrepancia = janela.tree_discrepancias.selection()
        if not selecao_discrepancia:
            messagebox.showwarning("Aviso", "Selecione uma discrepância primeiro!")
            return
        
        # Obter ID da discrepância
        item = janela.tree_discrepancias.item(selecao_discrepancia[0])
        id_discrepancia = int(item['values'][0]) - 1
        
        # Obter sugestão selecionada
        selecao_sugestao = janela.listbox_sugestoes.curselection()
        if not selecao_sugestao:
            messagebox.showwarning("Aviso", "Selecione uma sugestão primeiro!")
            return
        
        id_sugestao = selecao_sugestao[0]
        
        # Aplicar sugestão
        if self.conciliacao.aplicar_sugestao(id_discrepancia, id_sugestao):
            messagebox.showinfo("Sucesso", "Sugestão aplicada com sucesso!")
            
            # Atualizar treeview
            janela.tree_discrepancias.delete(selecao_discrepancia[0])
            
            # Registrar na auditoria
            self.auditoria.registrar_evento(
                'correcao_discrepancia',
                f"Correção de discrepância aplicada",
                "sistema"
            )
        else:
            messagebox.showerror("Erro", "Erro ao aplicar sugestão.")
    
    def _ignorar_discrepancia(self, janela):
        """Ignora a discrepância selecionada"""
        # Obter discrepância selecionada
        selecao = janela.tree_discrepancias.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione uma discrepância primeiro!")
            return
        
        # Obter ID da discrepância
        item = janela.tree_discrepancias.item(selecao[0])
        id_discrepancia = int(item['values'][0]) - 1
        
        # Confirmar ação
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja ignorar esta discrepância?"):
            return
        
        # Remover discrepância
        self.conciliacao.discrepancias.pop(id_discrepancia)
        
        # Atualizar treeview
        janela.tree_discrepancias.delete(selecao[0])
        
        # Registrar na auditoria
        self.auditoria.registrar_evento(
            'ignorar_discrepancia',
            f"Discrepância ignorada",
            "sistema"
        )
        
        messagebox.showinfo("Sucesso", "Discrepância ignorada com sucesso!")
    
    # ===== Métodos para Fluxo de Caixa =====
    
    def abrir_projecao_fluxo_caixa(self):
        """Abre a interface para projeção de fluxo de caixa"""
        # Criar janela
        janela = tk.Toplevel(self.app.root)
        janela.title("Projeção de Fluxo de Caixa")
        janela.geometry("900x700")
        janela.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame_principal = ttk.Frame(janela, padding=10)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Frame de parâmetros
        frame_parametros = ttk.LabelFrame(frame_principal, text="Parâmetros de Projeção", padding=10)
        frame_parametros.pack(fill=tk.X, pady=10)
        
        # Parâmetros
        ttk.Label(frame_parametros, text="Data Início:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        data_inicio = ttk.Entry(frame_parametros, width=12)
        data_inicio.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        data_inicio.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        ttk.Label(frame_parametros, text="Data Fim:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        data_fim = ttk.Entry(frame_parametros, width=12)
        data_fim.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        data_fim.insert(0, (datetime.now() + timedelta(days=90)).strftime('%d/%m/%Y'))
        
        ttk.Label(frame_parametros, text="Método:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        metodo = ttk.Combobox(frame_parametros, values=["média_movel", "arima", "tendencia"], width=12)
        metodo.grid(row=0, column=5, sticky=tk.W, padx=5, pady=5)
        metodo.current(0)
        
        # Checkboxes
        var_recorrentes = tk.BooleanVar(value=True)
        check_recorrentes = ttk.Checkbutton(frame_parametros, text="Incluir Lançamentos Recorrentes", 
                                          variable=var_recorrentes)
        check_recorrentes.grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        var_historico = tk.BooleanVar(value=True)
        check_historico = ttk.Checkbutton(frame_parametros, text="Usar Dados Históricos", 
                                        variable=var_historico)
        check_historico.grid(row=1, column=3, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # Botão de projeção
        btn_projetar = ttk.Button(frame_parametros, text="Gerar Projeção", 
                                command=lambda: self._executar_projecao_fluxo_caixa(
                                    janela, 
                                    data_inicio.get(), 
                                    data_fim.get(), 
                                    metodo.get(),
                                    var_recorrentes.get(),
                                    var_historico.get()
                                ))
        btn_projetar.grid(row=1, column=6, padx=5, pady=5)
        
        # Frame para gráfico
        frame_grafico = ttk.LabelFrame(frame_principal, text="Gráfico de Projeção", padding=10)
        frame_grafico.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame para tabela
        frame_tabela = ttk.LabelFrame(frame_principal, text="Detalhamento da Projeção", padding=10)
        frame_tabela.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Notebook para abas de detalhamento
        notebook = ttk.Notebook(frame_tabela)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de resumo mensal
        tab_mensal = ttk.Frame(notebook, padding=10)
        notebook.add(tab_mensal, text="Resumo Mensal")
        
        # Aba de detalhamento diário
        tab_diario = ttk.Frame(notebook, padding=10)
        notebook.add(tab_diario, text="Detalhamento Diário")
        
        # Treeview para resumo mensal
        colunas_mensal = ["mes", "receitas", "despesas", "saldo"]
        
        tree_mensal = ttk.Treeview(tab_mensal, columns=colunas_mensal, show="headings")
        tree_mensal.pack(fill=tk.BOTH, expand=True)
        
        # Configurar colunas
        tree_mensal.heading("mes", text="Mês")
        tree_mensal.heading("receitas", text="Receitas")
        tree_mensal.heading("despesas", text="Despesas")
        tree_mensal.heading("saldo", text="Saldo")
        
        tree_mensal.column("mes", width=100)
        tree_mensal.column("receitas", width=150)
        tree_mensal.column("despesas", width=150)
        tree_mensal.column("saldo", width=150)
        
        # Scrollbar para resumo mensal
        scrollbar_mensal = ttk.Scrollbar(tab_mensal, orient=tk.VERTICAL, command=tree_mensal.yview)
        tree_mensal.configure(yscrollcommand=scrollbar_mensal.set)
        scrollbar_mensal.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview para detalhamento diário
        colunas_diario = ["data", "receitas", "despesas", "saldo_dia", "saldo_acumulado"]
        
        tree_diario = ttk.Treeview(tab_diario, columns=colunas_diario, show="headings")
        tree_diario.pack(fill=tk.BOTH, expand=True)
        
        # Configurar colunas
        tree_diario.heading("data", text="Data")
        tree_diario.heading("receitas", text="Receitas")
        tree_diario.heading("despesas", text="Despesas")
        tree_diario.heading("saldo_dia", text="Saldo do Dia")
        tree_diario.heading("saldo_acumulado", text="Saldo Acumulado")
        
        tree_diario.column("data", width=100)
        tree_diario.column("receitas", width=150)
        tree_diario.column("despesas", width=150)
        tree_diario.column("saldo_dia", width=150)
        tree_diario.column("saldo_acumulado", width=150)
        
        # Scrollbar para detalhamento diário
        scrollbar_diario = ttk.Scrollbar(tab_diario, orient=tk.VERTICAL, command=tree_diario.yview)
        tree_diario.configure(yscrollcommand=scrollbar_diario.set)
        scrollbar_diario.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        # Botões
        btn_relatorio = ttk.Button(frame_botoes, text="Gerar Relatório", 
                                  command=self.gerar_relatorio_fluxo_caixa)
        btn_relatorio.pack(side=tk.LEFT, padx=5)
        
        btn_recorrentes = ttk.Button(frame_botoes, text="Gerenciar Lançamentos Recorrentes", 
                                   command=self.gerenciar_lancamentos_recorrentes)
        btn_recorrentes.pack(side=tk.LEFT, padx=5)
        
        btn_fechar = ttk.Button(frame_botoes, text="Fechar", command=janela.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=5)
        
        # Armazenar referências
        janela.frame_grafico = frame_grafico
        janela.tree_mensal = tree_mensal
        janela.tree_diario = tree_diario
    
    def _executar_projecao_fluxo_caixa(self, janela, data_inicio_str, data_fim_str, metodo, 
                                      incluir_recorrentes, incluir_historico):
        """Executa a projeção de fluxo de caixa"""
        try:
            # Converter datas
            data_inicio = datetime.strptime(data_inicio_str, '%d/%m/%Y')
            data_fim = datetime.strptime(data_fim_str, '%d/%m/%Y')
            
            # Validar datas
            if data_inicio > data_fim:
                messagebox.showerror("Erro", "A data de início deve ser anterior à data de fim!")
                return
            
            # Limpar treeviews
            janela.tree_mensal.delete(*janela.tree_mensal.get_children())
            janela.tree_diario.delete(*janela.tree_diario.get_children())
            
            # Limpar frame do gráfico
            for widget in janela.frame_grafico.winfo_children():
                widget.destroy()
            
            # Executar projeção
            previsoes = self.fluxo_caixa.gerar_previsao_fluxo_caixa(
                data_inicio,
                data_fim,
                incluir_recorrentes=incluir_recorrentes,
                incluir_historico=incluir_historico,
                metodo=metodo
            )
            
            if not previsoes:
                messagebox.showerror("Erro", "Erro ao gerar previsão de fluxo de caixa.")
                return
            
            # Gerar gráfico
            canvas_grafico = self.fluxo_caixa.gerar_grafico_fluxo_caixa(janela.frame_grafico, periodo='mensal')
            
            # Preencher resumo mensal
            resumo_mensal = self.fluxo_caixa._agrupar_por_mes()
            
            for mes, valores in sorted(resumo_mensal.items()):
                janela.tree_mensal.insert("", tk.END, values=(
                    mes,
                    f"Kz {valores['receitas']:,.2f}",
                    f"Kz {valores['despesas']:,.2f}",
                    f"Kz {valores['saldo']:,.2f}"
                ))
            
            # Preencher detalhamento diário
            datas_ordenadas = sorted(previsoes['receitas'].keys())
            
            saldo_acumulado = self.fluxo_caixa._obter_saldo_atual()
            
            for data_str in datas_ordenadas:
                data_obj = datetime.fromisoformat(data_str)
                receita_dia = previsoes['receitas'][data_str]
                despesa_dia = previsoes['despesas'][data_str]
                saldo_dia = receita_dia - despesa_dia
                saldo_acumulado += saldo_dia
                
                janela.tree_diario.insert("", tk.END, values=(
                    data_obj.strftime('%d/%m/%Y'),
                    f"Kz {receita_dia:,.2f}",
                    f"Kz {despesa_dia:,.2f}",
                    f"Kz {saldo_dia:,.2f}",
                    f"Kz {saldo_acumulado:,.2f}"
                ))
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo("Projeção Concluída", 
                               "Projeção de fluxo de caixa gerada com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar projeção: {str(e)}")
    
    def gerenciar_lancamentos_recorrentes(self):
        """Abre a interface para gerenciar lançamentos recorrentes"""
        # Criar janela
        janela = tk.Toplevel(self.app.root)
        janela.title("Gerenciar Lançamentos Recorrentes")
        janela.geometry("800x600")
        janela.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame_principal = ttk.Frame(janela, padding=10)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Frame de lançamentos
        frame_lancamentos = ttk.LabelFrame(frame_principal, text="Lançamentos Recorrentes", padding=10)
        frame_lancamentos.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview para lançamentos
        colunas = ["id", "descricao", "valor", "tipo", "frequencia", "data_inicio", "data_fim"]
        
        tree_lancamentos = ttk.Treeview(frame_lancamentos, columns=colunas, show="headings")
        tree_lancamentos.pack(fill=tk.BOTH, expand=True)
        
        # Configurar colunas
        tree_lancamentos.heading("id", text="ID")
        tree_lancamentos.heading("descricao", text="Descrição")
        tree_lancamentos.heading("valor", text="Valor")
        tree_lancamentos.heading("tipo", text="Tipo")
        tree_lancamentos.heading("frequencia", text="Frequência")
        tree_lancamentos.heading("data_inicio", text="Data Início")
        tree_lancamentos.heading("data_fim", text="Data Fim")
        
        tree_lancamentos.column("id", width=50)
        tree_lancamentos.column("descricao", width=200)
        tree_lancamentos.column("valor", width=100)
        tree_lancamentos.column("tipo", width=100)
        tree_lancamentos.column("frequencia", width=100)
        tree_lancamentos.column("data_inicio", width=100)
        tree_lancamentos.column("data_fim", width=100)
        
        # Scrollbar para lançamentos
        scrollbar = ttk.Scrollbar(frame_lancamentos, orient=tk.VERTICAL, command=tree_lancamentos.yview)
        tree_lancamentos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher treeview
        for lanc in self.fluxo_caixa.lancamentos_recorrentes:
            tree_lancamentos.insert("", tk.END, values=(
                lanc['id'],
                lanc['descricao'],
                f"Kz {lanc['valor']:,.2f}",
                lanc['tipo'].capitalize(),
                lanc['frequencia'].capitalize(),
                lanc['data_inicio'].strftime('%d/%m/%Y'),
                lanc['data_fim'].strftime('%d/%m/%Y') if lanc['data_fim'] else "Indefinida"
            ))
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        # Botões
        btn_adicionar = ttk.Button(frame_botoes, text="Adicionar", 
                                  command=lambda: self._adicionar_lancamento_recorrente(janela))
        btn_adicionar.pack(side=tk.LEFT, padx=5)
        
        btn_editar = ttk.Button(frame_botoes, text="Editar", 
                              command=lambda: self._editar_lancamento_recorrente(janela))
        btn_editar.pack(side=tk.LEFT, padx=5)
        
        btn_remover = ttk.Button(frame_botoes, text="Remover", 
                               command=lambda: self._remover_lancamento_recorrente(janela))
        btn_remover.pack(side=tk.LEFT, padx=5)
        
        btn_fechar = ttk.Button(frame_botoes, text="Fechar", command=janela.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=5)
        
        # Armazenar referências
        janela.tree_lancamentos = tree_lancamentos
    
    def _adicionar_lancamento_recorrente(self, janela_pai):
        """Abre a interface para adicionar um lançamento recorrente"""
        # Criar janela
        janela = tk.Toplevel(janela_pai)
        janela.title("Adicionar Lançamento Recorrente")
        janela.geometry("500x350")
        janela.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame = ttk.Frame(janela, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos
        ttk.Label(frame, text="Descrição:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        descricao = ttk.Entry(frame, width=40)
        descricao.grid(row=0, column=1, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        
        ttk.Label(frame, text="Valor:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        valor = ttk.Entry(frame, width=15)
        valor.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="Tipo:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        tipo = ttk.Combobox(frame, values=["receita", "despesa"], width=15)
        tipo.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        tipo.current(0)
        
        ttk.Label(frame, text="Frequência:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        frequencia = ttk.Combobox(frame, values=["diario", "semanal", "mensal", "trimestral", "anual"], width=15)
        frequencia.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        frequencia.current(2)  # Mensal por padrão
        
        ttk.Label(frame, text="Data Início:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        data_inicio = ttk.Entry(frame, width=15)
        data_inicio.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        data_inicio.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        ttk.Label(frame, text="Data Fim (opcional):").grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        data_fim = ttk.Entry(frame, width=15)
        data_fim.grid(row=3, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="Categoria:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        categoria = ttk.Entry(frame, width=20)
        categoria.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="Conta Débito:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        conta_debito = ttk.Entry(frame, width=10)
        conta_debito.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="Conta Crédito:").grid(row=5, column=2, sticky=tk.W, padx=5, pady=5)
        conta_credito = ttk.Entry(frame, width=10)
        conta_credito.grid(row=5, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.grid(row=6, column=0, columnspan=4, pady=20)
        
        # Botões
        btn_salvar = ttk.Button(frame_botoes, text="Salvar", 
                              command=lambda: self._salvar_lancamento_recorrente(
                                  janela,
                                  janela_pai,
                                  descricao.get(),
                                  valor.get(),
                                  tipo.get(),
                                  frequencia.get(),
                                  data_inicio.get(),
                                  data_fim.get(),
                                  categoria.get(),
                                  conta_debito.get(),
                                  conta_credito.get()
                              ))
        btn_salvar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=janela.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)
    
    def _salvar_lancamento_recorrente(self, janela, janela_pai, descricao, valor_str, tipo, frequencia, 
                                    data_inicio_str, data_fim_str, categoria, conta_debito, conta_credito):
        """Salva um lançamento recorrente"""
        try:
            # Validar campos obrigatórios
            if not descricao or not valor_str or not data_inicio_str:
                messagebox.showerror("Erro", "Preencha os campos obrigatórios: Descrição, Valor e Data de Início!")
                return
            
            # Converter valor
            try:
                valor = float(valor_str.replace(".", "").replace(",", "."))
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido!")
                return
            
            # Converter datas
            try:
                data_inicio = datetime.strptime(data_inicio_str, '%d/%m/%Y')
                data_fim = datetime.strptime(data_fim_str, '%d/%m/%Y') if data_fim_str else None
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA.")
                return
            
            # Adicionar lançamento
            if self.fluxo_caixa.adicionar_lancamento_recorrente(
                descricao,
                valor,
                tipo,
                frequencia,
                data_inicio,
                data_fim,
                conta_debito if conta_debito else None,
                conta_credito if conta_credito else None,
                categoria if categoria else None
            ):
                messagebox.showinfo("Sucesso", "Lançamento recorrente adicionado com sucesso!")
                janela.destroy()
                
                # Atualizar treeview
                janela_pai.tree_lancamentos.delete(*janela_pai.tree_lancamentos.get_children())
                
                for lanc in self.fluxo_caixa.lancamentos_recorrentes:
                    janela_pai.tree_lancamentos.insert("", tk.END, values=(
                        lanc['id'],
                        lanc['descricao'],
                        f"Kz {lanc['valor']:,.2f}",
                        lanc['tipo'].capitalize(),
                        lanc['frequencia'].capitalize(),
                        lanc['data_inicio'].strftime('%d/%m/%Y'),
                        lanc['data_fim'].strftime('%d/%m/%Y') if lanc['data_fim'] else "Indefinida"
                    ))
                
                # Registrar na auditoria
                self.auditoria.registrar_evento(
                    'adicao_lancamento_recorrente',
                    f"Adição de lançamento recorrente: {descricao}",
                    "sistema"
                )
            else:
                messagebox.showerror("Erro", "Erro ao adicionar lançamento recorrente!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar lançamento recorrente: {str(e)}")
    
    def _editar_lancamento_recorrente(self, janela):
        """Edita um lançamento recorrente selecionado"""
        # Obter lançamento selecionado
        selecao = janela.tree_lancamentos.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um lançamento para editar!")
            return
        
        # Obter ID do lançamento
        item = janela.tree_lancamentos.item(selecao[0])
        id_lancamento = int(item['values'][0])
        
        # Buscar lançamento
        lancamento = None
        for lanc in self.fluxo_caixa.lancamentos_recorrentes:
            if lanc['id'] == id_lancamento:
                lancamento = lanc
                break
        
        if not lancamento:
            messagebox.showerror("Erro", "Lançamento não encontrado!")
            return
        
        # Criar janela de edição
        janela_edicao = tk.Toplevel(janela)
        janela_edicao.title("Editar Lançamento Recorrente")
        janela_edicao.geometry("500x350")
        janela_edicao.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame = ttk.Frame(janela_edicao, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos
        ttk.Label(frame, text="Descrição:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        descricao = ttk.Entry(frame, width=40)
        descricao.grid(row=0, column=1, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        descricao.insert(0, lancamento['descricao'])
        
        ttk.Label(frame, text="Valor:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        valor = ttk.Entry(frame, width=15)
        valor.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        valor.insert(0, str(lancamento['valor']))
        
        ttk.Label(frame, text="Tipo:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        tipo = ttk.Combobox(frame, values=["receita", "despesa"], width=15)
        tipo.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        tipo.set(lancamento['tipo'])
        
        ttk.Label(frame, text="Frequência:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        frequencia = ttk.Combobox(frame, values=["diario", "semanal", "mensal", "trimestral", "anual"], width=15)
        frequencia.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        frequencia.set(lancamento['frequencia'])
        
        ttk.Label(frame, text="Data Início:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        data_inicio = ttk.Entry(frame, width=15)
        data_inicio.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        data_inicio.insert(0, lancamento['data_inicio'].strftime('%d/%m/%Y'))
        
        ttk.Label(frame, text="Data Fim (opcional):").grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        data_fim = ttk.Entry(frame, width=15)
        data_fim.grid(row=3, column=3, sticky=tk.W, padx=5, pady=5)
        if lancamento['data_fim']:
            data_fim.insert(0, lancamento['data_fim'].strftime('%d/%m/%Y'))
        
        ttk.Label(frame, text="Categoria:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        categoria = ttk.Entry(frame, width=20)
        categoria.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        if 'categoria' in lancamento and lancamento['categoria']:
            categoria.insert(0, lancamento['categoria'])
        
        ttk.Label(frame, text="Conta Débito:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        conta_debito = ttk.Entry(frame, width=10)
        conta_debito.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        if 'conta_debito' in lancamento and lancamento['conta_debito']:
            conta_debito.insert(0, lancamento['conta_debito'])
        
        ttk.Label(frame, text="Conta Crédito:").grid(row=5, column=2, sticky=tk.W, padx=5, pady=5)
        conta_credito = ttk.Entry(frame, width=10)
        conta_credito.grid(row=5, column=3, sticky=tk.W, padx=5, pady=5)
        if 'conta_credito' in lancamento and lancamento['conta_credito']:
            conta_credito.insert(0, lancamento['conta_credito'])
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.grid(row=6, column=0, columnspan=4, pady=20)
        
        # Botões
        btn_salvar = ttk.Button(frame_botoes, text="Salvar", 
                              command=lambda: self._atualizar_lancamento_recorrente(
                                  janela_edicao,
                                  janela,
                                  id_lancamento,
                                  descricao.get(),
                                  valor.get(),
                                  tipo.get(),
                                  frequencia.get(),
                                  data_inicio.get(),
                                  data_fim.get(),
                                  categoria.get(),
                                  conta_debito.get(),
                                  conta_credito.get()
                              ))
        btn_salvar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=janela_edicao.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)
    
    def _atualizar_lancamento_recorrente(self, janela_edicao, janela_pai, id_lancamento, descricao, 
                                       valor_str, tipo, frequencia, data_inicio_str, data_fim_str, 
                                       categoria, conta_debito, conta_credito):
        """Atualiza um lançamento recorrente"""
        try:
            # Validar campos obrigatórios
            if not descricao or not valor_str or not data_inicio_str:
                messagebox.showerror("Erro", "Preencha os campos obrigatórios: Descrição, Valor e Data de Início!")
                return
            
            # Converter valor
            try:
                valor = float(valor_str.replace(".", "").replace(",", "."))
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido!")
                return
            
            # Converter datas
            try:
                data_inicio = datetime.strptime(data_inicio_str, '%d/%m/%Y')
                data_fim = datetime.strptime(data_fim_str, '%d/%m/%Y') if data_fim_str else None
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA.")
                return
            
            # Buscar e atualizar lançamento
            for i, lanc in enumerate(self.fluxo_caixa.lancamentos_recorrentes):
                if lanc['id'] == id_lancamento:
                    # Guardar dados antigos para auditoria
                    dados_antigos = lanc.copy()
                    
                    # Atualizar dados
                    self.fluxo_caixa.lancamentos_recorrentes[i]['descricao'] = descricao
                    self.fluxo_caixa.lancamentos_recorrentes[i]['valor'] = valor
                    self.fluxo_caixa.lancamentos_recorrentes[i]['tipo'] = tipo
                    self.fluxo_caixa.lancamentos_recorrentes[i]['frequencia'] = frequencia
                    self.fluxo_caixa.lancamentos_recorrentes[i]['data_inicio'] = data_inicio
                    self.fluxo_caixa.lancamentos_recorrentes[i]['data_fim'] = data_fim
                    self.fluxo_caixa.lancamentos_recorrentes[i]['categoria'] = categoria if categoria else None
                    self.fluxo_caixa.lancamentos_recorrentes[i]['conta_debito'] = conta_debito if conta_debito else None
                    self.fluxo_caixa.lancamentos_recorrentes[i]['conta_credito'] = conta_credito if conta_credito else None
                    
                    # Salvar alterações
                    self.fluxo_caixa.salvar_lancamentos_recorrentes()
                    
                    # Registrar na auditoria
                    self.auditoria.registrar_evento(
                        'edicao_lancamento_recorrente',
                        f"Edição de lançamento recorrente: {descricao}",
                        "sistema",
                        {
                            'lancamento_id': id_lancamento,
                            'dados_antigos': dados_antigos,
                            'dados_novos': self.fluxo_caixa.lancamentos_recorrentes[i]
                        }
                    )
                    
                    messagebox.showinfo("Sucesso", "Lançamento recorrente atualizado com sucesso!")
                    janela_edicao.destroy()
                    
                    # Atualizar treeview
                    janela_pai.tree_lancamentos.delete(*janela_pai.tree_lancamentos.get_children())
                    
                    for lanc in self.fluxo_caixa.lancamentos_recorrentes:
                        janela_pai.tree_lancamentos.insert("", tk.END, values=(
                            lanc['id'],
                            lanc['descricao'],
                            f"Kz {lanc['valor']:,.2f}",
                            lanc['tipo'].capitalize(),
                            lanc['frequencia'].capitalize(),
                            lanc['data_inicio'].strftime('%d/%m/%Y'),
                            lanc['data_fim'].strftime('%d/%m/%Y') if lanc['data_fim'] else "Indefinida"
                        ))
                    
                    return
            
            messagebox.showerror("Erro", "Lançamento não encontrado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar lançamento recorrente: {str(e)}")
    
    def _remover_lancamento_recorrente(self, janela):
        """Remove um lançamento recorrente selecionado"""
        # Obter lançamento selecionado
        selecao = janela.tree_lancamentos.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um lançamento para remover!")
            return
        
        # Obter ID do lançamento
        item = janela.tree_lancamentos.item(selecao[0])
        id_lancamento = int(item['values'][0])
        
        # Confirmar remoção
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja remover este lançamento recorrente?"):
            return
        
        # Buscar lançamento para auditoria
        lancamento = None
        for lanc in self.fluxo_caixa.lancamentos_recorrentes:
            if lanc['id'] == id_lancamento:
                lancamento = lanc
                break
        
        # Remover lançamento
        if self.fluxo_caixa.remover_lancamento_recorrente(id_lancamento):
            messagebox.showinfo("Sucesso", "Lançamento recorrente removido com sucesso!")
            
            # Atualizar treeview
            janela.tree_lancamentos.delete(selecao[0])
            
            # Registrar na auditoria
            if lancamento:
                self.auditoria.registrar_evento(
                    'remocao_lancamento_recorrente',
                    f"Remoção de lançamento recorrente: {lancamento['descricao']}",
                    "sistema",
                    {'lancamento': lancamento}
                )
        else:
            messagebox.showerror("Erro", "Erro ao remover lançamento recorrente!")
    
    def gerar_relatorio_fluxo_caixa(self):
        """Gera um relatório de fluxo de caixa projetado"""
        # Verificar se há previsões
        if not hasattr(self.fluxo_caixa, 'previsoes') or not self.fluxo_caixa.previsoes['receitas']:
            messagebox.showwarning("Aviso", "Gere uma projeção de fluxo de caixa primeiro!")
            return
        
        # Solicitar caminho para salvar o relatório
        caminho_saida = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf")],
            title="Salvar Relatório de Fluxo de Caixa"
        )
        
        if not caminho_saida:
            return
        
        # Gerar relatório
        if self.fluxo_caixa.gerar_relatorio_fluxo_caixa(caminho_saida):
            messagebox.showinfo("Sucesso", f"Relatório de fluxo de caixa gerado com sucesso!\n\nSalvo em: {caminho_saida}")
            
            # Perguntar se deseja abrir o relatório
            if messagebox.askyesno("Abrir Relatório", "Deseja abrir o relatório agora?"):
                self._abrir_arquivo(caminho_saida)
        else:
            messagebox.showerror("Erro", "Erro ao gerar relatório de fluxo de caixa.")
    
    # ===== Métodos para Auditoria =====
    
    def abrir_trilha_alteracoes(self):
        """Abre a interface para visualizar a trilha de alterações"""
        # Criar janela
        janela = tk.Toplevel(self.app.root)
        janela.title("Trilha de Alterações")
        janela.geometry("900x600")
        janela.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame_principal = ttk.Frame(janela, padding=10)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Frame de filtros
        frame_filtros = ttk.LabelFrame(frame_principal, text="Filtros", padding=10)
        frame_filtros.pack(fill=tk.X, pady=10)
        
        # Filtros
        ttk.Label(frame_filtros, text="Tipo:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        tipo = ttk.Combobox(frame_filtros, values=[
            "",
            "criacao_lancamento",
            "alteracao_lancamento",
            "exclusao_lancamento",
            "correcao_discrepancia",
            "adicao_lancamento_recorrente",
            "edicao_lancamento_recorrente",
            "remocao_lancamento_recorrente"
        ], width=25)
        tipo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Usuário:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        usuario = ttk.Entry(frame_filtros, width=15)
        usuario.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Data Início:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        data_inicio = ttk.Entry(frame_filtros, width=15)
        data_inicio.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Data Fim:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        data_fim = ttk.Entry(frame_filtros, width=15)
        data_fim.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Texto:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        texto = ttk.Entry(frame_filtros, width=40)
        texto.grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        btn_filtrar = ttk.Button(frame_filtros, text="Filtrar", 
                               command=lambda: self._filtrar_registros_auditoria(
                                   janela,
                                   tipo.get(),
                                   usuario.get(),
                                   data_inicio.get(),
                                   data_fim.get(),
                                   texto.get()
                               ))
        btn_filtrar.grid(row=2, column=3, padx=5, pady=5)
        
        # Frame de registros
        frame_registros = ttk.LabelFrame(frame_principal, text="Registros de Auditoria", padding=10)
        frame_registros.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview para registros
        colunas = ["id", "data_hora", "tipo", "usuario", "descricao"]
        
        tree_registros = ttk.Treeview(frame_registros, columns=colunas, show="headings")
        tree_registros.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Configurar colunas
        tree_registros.heading("id", text="ID")
        tree_registros.heading("data_hora", text="Data/Hora")
        tree_registros.heading("tipo", text="Tipo")
        tree_registros.heading("usuario", text="Usuário")
        tree_registros.heading("descricao", text="Descrição")
        
        tree_registros.column("id", width=50)
        tree_registros.column("data_hora", width=150)
        tree_registros.column("tipo", width=150)
        tree_registros.column("usuario", width=100)
        tree_registros.column("descricao", width=400)
        
        # Scrollbar para registros
        scrollbar = ttk.Scrollbar(frame_registros, orient=tk.VERTICAL, command=tree_registros.yview)
        tree_registros.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher treeview com todos os registros
        for registro in self.auditoria.registros_auditoria:
            tree_registros.insert("", tk.END, values=(
                registro['id'],
                registro['data_hora'].strftime('%d/%m/%Y %H:%M:%S'),
                registro['tipo'].replace('_', ' ').title(),
                registro['usuario'],
                registro['descricao']
            ))
        
        # Frame de detalhes
        frame_detalhes = ttk.LabelFrame(frame_principal, text="Detalhes do Registro", padding=10)
        frame_detalhes.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Texto para detalhes
        texto_detalhes = tk.Text(frame_detalhes, height=10, wrap=tk.WORD)
        texto_detalhes.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar para detalhes
        scrollbar_detalhes = ttk.Scrollbar(frame_detalhes, orient=tk.VERTICAL, command=texto_detalhes.yview)
        texto_detalhes.configure(yscrollcommand=scrollbar_detalhes.set)
        scrollbar_detalhes.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Evento de seleção na treeview
        def ao_selecionar_registro(event):
            # Obter item selecionado
            selecao = tree_registros.selection()
            if not selecao:
                return
            
            # Obter ID do registro
            item = tree_registros.item(selecao[0])
            id_registro = int(item['values'][0])
            
            # Buscar registro
            registro = None
            for reg in self.auditoria.registros_auditoria:
                if reg['id'] == id_registro:
                    registro = reg
                    break
            
            if not registro:
                return
            
            # Limpar texto
            texto_detalhes.delete(1.0, tk.END)
            
            # Preencher detalhes
            texto_detalhes.insert(tk.END, f"ID: {registro['id']}\n")
            texto_detalhes.insert(tk.END, f"Data/Hora: {registro['data_hora'].strftime('%d/%m/%Y %H:%M:%S')}\n")
            texto_detalhes.insert(tk.END, f"Tipo: {registro['tipo'].replace('_', ' ').title()}\n")
            texto_detalhes.insert(tk.END, f"Usuário: {registro['usuario']}\n")
            texto_detalhes.insert(tk.END, f"Descrição: {registro['descricao']}\n\n")
            
            if 'detalhes' in registro and registro['detalhes']:
                texto_detalhes.insert(tk.END, "Detalhes:\n")
                
                if 'lancamento_id' in registro['detalhes']:
                    texto_detalhes.insert(tk.END, f"Lançamento ID: {registro['detalhes']['lancamento_id']}\n")
                
                if 'campos_alterados' in registro['detalhes']:
                    texto_detalhes.insert(tk.END, "Campos Alterados:\n")
                    
                    for campo, valores in registro['detalhes']['campos_alterados'].items():
                        if campo == 'movimentos':
                            texto_detalhes.insert(tk.END, "Movimentos:\n")
                            
                            if isinstance(valores, list):
                                for alteracao in valores:
                                    texto_detalhes.insert(tk.END, 
                                        f"  Movimento {alteracao['indice']+1}, Campo {alteracao['campo']}: "
                                        f"{alteracao['antigo']} -> {alteracao['novo']}\n"
                                    )
                            else:
                                texto_detalhes.insert(tk.END, "  Movimentos foram completamente alterados\n")
                        else:
                            texto_detalhes.insert(tk.END, 
                                f"  {campo.capitalize()}: {valores['antigo']} -> {valores['novo']}\n"
                            )
                
                if 'dados_antigos' in registro['detalhes'] and 'dados_novos' in registro['detalhes']:
                    texto_detalhes.insert(tk.END, "\nComparação de Dados:\n")
                    
                    dados_antigos = registro['detalhes']['dados_antigos']
                    dados_novos = registro['detalhes']['dados_novos']
                    
                    for campo in dados_novos:
                        if campo in dados_antigos and dados_antigos[campo] != dados_novos[campo]:
                            valor_antigo = dados_antigos[campo]
                            valor_novo = dados_novos[campo]
                            
                            # Formatar datas
                            if isinstance(valor_antigo, str) and valor_antigo.startswith('20') and 'T' in valor_antigo:
                                try:
                                    valor_antigo = datetime.fromisoformat(valor_antigo).strftime('%d/%m/%Y')
                                except:
                                    pass
                            
                            if isinstance(valor_novo, str) and valor_novo.startswith('20') and 'T' in valor_novo:
                                try:
                                    valor_novo = datetime.fromisoformat(valor_novo).strftime('%d/%m/%Y')
                                except:
                                    pass
                            
                            texto_detalhes.insert(tk.END, f"  {campo}: {valor_antigo} -> {valor_novo}\n")
        
        tree_registros.bind("<<TreeviewSelect>>", ao_selecionar_registro)
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        # Botões
        btn_relatorio = ttk.Button(frame_botoes, text="Gerar Relatório", 
                                  command=self.gerar_relatorio_auditoria)
        btn_relatorio.pack(side=tk.LEFT, padx=5)
        
        btn_fechar = ttk.Button(frame_botoes, text="Fechar", command=janela.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=5)
        
        # Armazenar referências
        janela.tree_registros = tree_registros
        janela.texto_detalhes = texto_detalhes
    
    def _filtrar_registros_auditoria(self, janela, tipo, usuario, data_inicio_str, data_fim_str, texto):
        """Filtra os registros de auditoria"""
        try:
            # Preparar filtros
            filtros = {}
            
            if tipo:
                filtros['tipo'] = tipo
            
            if usuario:
                filtros['usuario'] = usuario
            
            if data_inicio_str:
                try:
                    filtros['data_inicio'] = datetime.strptime(data_inicio_str, '%d/%m/%Y')
                except ValueError:
                    messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA.")
                    return
            
            if data_fim_str:
                try:
                    filtros['data_fim'] = datetime.strptime(data_fim_str, '%d/%m/%Y')
                    # Ajustar para o final do dia
                    filtros['data_fim'] = filtros['data_fim'].replace(hour=23, minute=59, second=59)
                except ValueError:
                    messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA.")
                    return
            
            if texto:
                filtros['texto'] = texto
            
            # Buscar registros
            registros = self.auditoria.buscar_registros(filtros)
            
            # Limpar treeview
            janela.tree_registros.delete(*janela.tree_registros.get_children())
            
            # Preencher treeview
            for registro in registros:
                janela.tree_registros.insert("", tk.END, values=(
                    registro['id'],
                    registro['data_hora'].strftime('%d/%m/%Y %H:%M:%S'),
                    registro['tipo'].replace('_', ' ').title(),
                    registro['usuario'],
                    registro['descricao']
                ))
            
            # Limpar detalhes
            janela.texto_detalhes.delete(1.0, tk.END)
            
            # Mostrar mensagem
            messagebox.showinfo("Filtro Aplicado", f"Foram encontrados {len(registros)} registros.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao filtrar registros: {str(e)}")
    
    def gerar_relatorio_auditoria(self):
        """Gera um relatório de auditoria"""
        # Solicitar filtros
        janela = tk.Toplevel(self.app.root)
        janela.title("Filtros para Relatório de Auditoria")
        janela.geometry("400x250")
        janela.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame = ttk.Frame(janela, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Filtros
        ttk.Label(frame, text="Tipo:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        tipo = ttk.Combobox(frame, values=[
            "",
            "criacao_lancamento",
            "alteracao_lancamento",
            "exclusao_lancamento",
            "correcao_discrepancia",
            "adicao_lancamento_recorrente",
            "edicao_lancamento_recorrente",
            "remocao_lancamento_recorrente"
        ], width=25)
        tipo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="Usuário:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        usuario = ttk.Entry(frame, width=20)
        usuario.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="Data Início:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        data_inicio = ttk.Entry(frame, width=15)
        data_inicio.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="Data Fim:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        data_fim = ttk.Entry(frame, width=15)
        data_fim.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="Texto:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        texto = ttk.Entry(frame, width=30)
        texto.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Botões
        btn_gerar = ttk.Button(frame_botoes, text="Gerar Relatório", 
                             command=lambda: self._executar_relatorio_auditoria(
                                 janela,
                                 tipo.get(),
                                 usuario.get(),
                                 data_inicio.get(),
                                 data_fim.get(),
                                 texto.get()
                             ))
        btn_gerar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=janela.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)
    
    def _executar_relatorio_auditoria(self, janela, tipo, usuario, data_inicio_str, data_fim_str, texto):
        """Executa a geração do relatório de auditoria"""
        try:
            # Preparar filtros
            filtros = {}
            
            if tipo:
                filtros['tipo'] = tipo
            
            if usuario:
                filtros['usuario'] = usuario
            
            if data_inicio_str:
                try:
                    filtros['data_inicio'] = datetime.strptime(data_inicio_str, '%d/%m/%Y')
                except ValueError:
                    messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA.")
                    return
            
            if data_fim_str:
                try:
                    filtros['data_fim'] = datetime.strptime(data_fim_str, '%d/%m/%Y')
                    # Ajustar para o final do dia
                    filtros['data_fim'] = filtros['data_fim'].replace(hour=23, minute=59, second=59)
                except ValueError:
                    messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA.")
                    return
            
            if texto:
                filtros['texto'] = texto
            
            # Solicitar caminho para salvar o relatório
            caminho_saida = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("Arquivos PDF", "*.pdf")],
                title="Salvar Relatório de Auditoria"
            )
            
            if not caminho_saida:
                return
            
            # Gerar relatório
            if self.auditoria.gerar_relatorio_auditoria(filtros, caminho_saida):
                messagebox.showinfo("Sucesso", f"Relatório de auditoria gerado com sucesso!\n\nSalvo em: {caminho_saida}")
                
                # Fechar janela de filtros
                janela.destroy()
                
                # Perguntar se deseja abrir o relatório
                if messagebox.askyesno("Abrir Relatório", "Deseja abrir o relatório agora?"):
                    self._abrir_arquivo(caminho_saida)
            else:
                messagebox.showerror("Erro", "Erro ao gerar relatório de auditoria.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")
    
    # ===== Métodos para Orçamento =====
    
    def definir_orcamento(self):
        """Abre a interface para definir orçamentos"""
        # Criar janela
        janela = tk.Toplevel(self.app.root)
        janela.title("Definir Orçamento")
        janela.geometry("800x600")
        janela.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame_principal = ttk.Frame(janela, padding=10)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Frame de seleção de período
        frame_periodo = ttk.LabelFrame(frame_principal, text="Período", padding=10)
        frame_periodo.pack(fill=tk.X, pady=10)
        
        # Seleção de período
        ttk.Label(frame_periodo, text="Ano:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ano = ttk.Combobox(frame_periodo, values=[str(y) for y in range(datetime.now().year - 2, datetime.now().year + 3)], width=10)
        ano.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ano.set(str(datetime.now().year))
        
        ttk.Label(frame_periodo, text="Mês:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        mes = ttk.Combobox(frame_periodo, values=[
            "1 - Janeiro",
            "2 - Fevereiro",
            "3 - Março",
            "4 - Abril",
            "5 - Maio",
            "6 - Junho",
            "7 - Julho",
            "8 - Agosto",
            "9 - Setembro",
            "10 - Outubro",
            "11 - Novembro",
            "12 - Dezembro"
        ], width=15)
        mes.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        mes.set(f"{datetime.now().month} - {datetime.now().strftime('%B')}")
        
        btn_carregar = ttk.Button(frame_periodo, text="Carregar", 
                                command=lambda: self._carregar_orcamento(
                                    janela,
                                    int(ano.get()),
                                    int(mes.get().split(' - ')[0])
                                ))
        btn_carregar.grid(row=0, column=4, padx=20, pady=5)
        
        # Frame de orçamento
        frame_orcamento = ttk.LabelFrame(frame_principal, text="Orçamento", padding=10)
        frame_orcamento.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Notebook para abas
        notebook = ttk.Notebook(frame_orcamento)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de receitas
        tab_receitas = ttk.Frame(notebook, padding=10)
        notebook.add(tab_receitas, text="Receitas")
        
        # Aba de despesas
        tab_despesas = ttk.Frame(notebook, padding=10)
        notebook.add(tab_despesas, text="Despesas")
        
        # Treeview para receitas
        colunas_receitas = ["categoria", "valor"]
        
        tree_receitas = ttk.Treeview(tab_receitas, columns=colunas_receitas, show="headings")
        tree_receitas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Configurar colunas
        tree_receitas.heading("categoria", text="Categoria")
        tree_receitas.heading("valor", text="Valor Orçado")
        
        tree_receitas.column("categoria", width=300)
        tree_receitas.column("valor", width=150)
        
        # Scrollbar para receitas
        scrollbar_receitas = ttk.Scrollbar(tab_receitas, orient=tk.VERTICAL, command=tree_receitas.yview)
        tree_receitas.configure(yscrollcommand=scrollbar_receitas.set)
        scrollbar_receitas.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de botões para receitas
        frame_botoes_receitas = ttk.Frame(tab_receitas)
        frame_botoes_receitas.pack(fill=tk.X, pady=10)
        
        btn_adicionar_receita = ttk.Button(frame_botoes_receitas, text="Adicionar", 
                                         command=lambda: self._adicionar_orcamento(
                                             janela,
                                             int(ano.get()),
                                             int(mes.get().split(' - ')[0]),
                                             'receita'
                                         ))
        btn_adicionar_receita.pack(side=tk.LEFT, padx=5)
        
        btn_editar_receita = ttk.Button(frame_botoes_receitas, text="Editar", 
                                      command=lambda: self._editar_orcamento(
                                          janela,
                                          int(ano.get()),
                                          int(mes.get().split(' - ')[0]),
                                          'receita'
                                      ))
        btn_editar_receita.pack(side=tk.LEFT, padx=5)
        
        btn_remover_receita = ttk.Button(frame_botoes_receitas, text="Remover", 
                                       command=lambda: self._remover_orcamento(
                                           janela,
                                           int(ano.get()),
                                           int(mes.get().split(' - ')[0]),
                                           'receita'
                                       ))
        btn_remover_receita.pack(side=tk.LEFT, padx=5)
        
        # Treeview para despesas
        colunas_despesas = ["categoria", "valor"]
        
        tree_despesas = ttk.Treeview(tab_despesas, columns=colunas_despesas, show="headings")
        tree_despesas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Configurar colunas
        tree_despesas.heading("categoria", text="Categoria")
        tree_despesas.heading("valor", text="Valor Orçado")
        
        tree_despesas.column("categoria", width=300)
        tree_despesas.column("valor", width=150)
        
        # Scrollbar para despesas
        scrollbar_despesas = ttk.Scrollbar(tab_despesas, orient=tk.VERTICAL, command=tree_despesas.yview)
        tree_despesas.configure(yscrollcommand=scrollbar_despesas.set)
        scrollbar_despesas.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de botões para despesas
        frame_botoes_despesas = ttk.Frame(tab_despesas)
        frame_botoes_despesas.pack(fill=tk.X, pady=10)
        
        btn_adicionar_despesa = ttk.Button(frame_botoes_despesas, text="Adicionar", 
                                         command=lambda: self._adicionar_orcamento(
                                             janela,
                                             int(ano.get()),
                                             int(mes.get().split(' - ')[0]),
                                             'despesa'
                                         ))
        btn_adicionar_despesa.pack(side=tk.LEFT, padx=5)
        
        btn_editar_despesa = ttk.Button(frame_botoes_despesas, text="Editar", 
                                      command=lambda: self._editar_orcamento(
                                          janela,
                                          int(ano.get()),
                                          int(mes.get().split(' - ')[0]),
                                          'despesa'
                                      ))
        btn_editar_despesa.pack(side=tk.LEFT, padx=5)
        
        btn_remover_despesa = ttk.Button(frame_botoes_despesas, text="Remover", 
                                       command=lambda: self._remover_orcamento(
                                           janela,
                                           int(ano.get()),
                                           int(mes.get().split(' - ')[0]),
                                           'despesa'
                                       ))
        btn_remover_despesa.pack(side=tk.LEFT, padx=5)
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        # Botões
        btn_comparar = ttk.Button(frame_botoes, text="Comparar com Realizado", 
                                command=lambda: self.comparar_orcado_realizado(
                                    int(ano.get()),
                                    int(mes.get().split(' - ')[0])
                                ))
        btn_comparar.pack(side=tk.LEFT, padx=5)
        
        btn_fechar = ttk.Button(frame_botoes, text="Fechar", command=janela.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=5)
        
        # Armazenar referências
        janela.tree_receitas = tree_receitas
        janela.tree_despesas = tree_despesas
    
    def _carregar_orcamento(self, janela, ano, mes):
        """Carrega o orçamento para o período selecionado"""
        try:
            # Obter orçamento
            orcamento = self.orcamento.obter_orcamento(ano, mes)
            
            # Limpar treeviews
            janela.tree_receitas.delete(*janela.tree_receitas.get_children())
            janela.tree_despesas.delete(*janela.tree_despesas.get_children())
            
            # Preencher treeview de receitas
            if 'receitas' in orcamento:
                for categoria, valor in orcamento['receitas'].items():
                    janela.tree_receitas.insert("", tk.END, values=(
                        categoria,
                        f"Kz {valor:,.2f}"
                    ))
            
            # Preencher treeview de despesas
            if 'despesas' in orcamento:
                for categoria, valor in orcamento['despesas'].items():
                    janela.tree_despesas.insert("", tk.END, values=(
                        categoria,
                        f"Kz {valor:,.2f}"
                    ))
            
            messagebox.showinfo("Sucesso", f"Orçamento de {mes}/{ano} carregado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar orçamento: {str(e)}")
    
    def _adicionar_orcamento(self, janela_pai, ano, mes, tipo):
        """Abre a interface para adicionar um item ao orçamento"""
        # Criar janela
        janela = tk.Toplevel(janela_pai)
        janela.title(f"Adicionar {tipo.capitalize()} ao Orçamento")
        janela.geometry("400x200")
        janela.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame = ttk.Frame(janela, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos
        ttk.Label(frame, text="Categoria:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Obter categorias disponíveis
        categorias = []
        if tipo == 'receita':
            categorias = [
                "Vendas",
                "Prestação de Serviços",
                "Impostos e Taxas",
                "Subsídios",
                "Receitas Financeiras",
                "Receitas de Imobilizações",
                "Reversões",
                "Receitas Extraordinárias",
                "Outras Receitas"
            ]
        else:  # despesa
            categorias = [
                "Custo de Mercadorias",
                "Fornecimentos e Serviços",
                "Impostos",
                "Custos com Pessoal",
                "Despesas Financeiras",
                "Amortizações",
                "Provisões",
                "Despesas Extraordinárias",
                "Outras Despesas"
            ]
        
        categoria = ttk.Combobox(frame, values=categorias, width=30)
        categoria.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="Valor:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        valor = ttk.Entry(frame, width=15)
        valor.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Botões
        btn_salvar = ttk.Button(frame_botoes, text="Salvar", 
                              command=lambda: self._salvar_orcamento(
                                  janela,
                                  janela_pai,
                                  ano,
                                  mes,
                                  categoria.get(),
                                  valor.get(),
                                  tipo
                              ))
        btn_salvar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=janela.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)
    
    def _salvar_orcamento(self, janela, janela_pai, ano, mes, categoria, valor_str, tipo):
        """Salva um item do orçamento"""
        try:
            # Validar campos
            if not categoria:
                messagebox.showerror("Erro", "Selecione uma categoria!")
                return
            
            # Converter valor
            try:
                valor = float(valor_str.replace(".", "").replace(",", "."))
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido!")
                return
            
            # Definir orçamento
            if self.orcamento.definir_orcamento(ano, mes, categoria, valor, tipo):
                messagebox.showinfo("Sucesso", f"{tipo.capitalize()} adicionado ao orçamento com sucesso!")
                janela.destroy()
                
                # Recarregar orçamento
                self._carregar_orcamento(janela_pai, ano, mes)
                
                # Registrar na auditoria
                self.auditoria.registrar_evento(
                    'definicao_orcamento',
                    f"Definição de orçamento: {tipo}, {categoria}, {valor}, {mes}/{ano}",
                    "sistema"
                )
            else:
                messagebox.showerror("Erro", "Erro ao definir orçamento!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar orçamento: {str(e)}")
    
    def _editar_orcamento(self, janela, ano, mes, tipo):
        """Edita um item do orçamento"""
        # Obter item selecionado
        tree = janela.tree_receitas if tipo == 'receita' else janela.tree_despesas
        selecao = tree.selection()
        
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um item para editar!")
            return
        
        # Obter categoria e valor
        item = tree.item(selecao[0])
        categoria = item['values'][0]
        valor_str = item['values'][1].replace("Kz ", "").replace(".", "").replace(",", ".")
        
        # Criar janela de edição
        janela_edicao = tk.Toplevel(janela)
        janela_edicao.title(f"Editar {tipo.capitalize()} do Orçamento")
        janela_edicao.geometry("400x200")
        janela_edicao.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame = ttk.Frame(janela_edicao, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos
        ttk.Label(frame, text="Categoria:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        categoria_entry = ttk.Entry(frame, width=30)
        categoria_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        categoria_entry.insert(0, categoria)
        categoria_entry.configure(state="readonly")  # Não permitir edição da categoria
        
        ttk.Label(frame, text="Valor:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        valor_entry = ttk.Entry(frame, width=15)
        valor_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        valor_entry.insert(0, valor_str)
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Botões
        btn_salvar = ttk.Button(frame_botoes, text="Salvar", 
                              command=lambda: self._atualizar_orcamento(
                                  janela_edicao,
                                  janela,
                                  ano,
                                  mes,
                                  categoria,
                                  valor_entry.get(),
                                  tipo
                              ))
        btn_salvar.pack(side=tk.LEFT, padx=5)
        
        btn_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=janela_edicao.destroy)
        btn_cancelar.pack(side=tk.LEFT, padx=5)
    
    def _atualizar_orcamento(self, janela_edicao, janela_pai, ano, mes, categoria, valor_str, tipo):
        """Atualiza um item do orçamento"""
        try:
            # Converter valor
            try:
                valor = float(valor_str.replace(".", "").replace(",", "."))
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido!")
                return
            
            # Definir orçamento (sobrescreve o existente)
            if self.orcamento.definir_orcamento(ano, mes, categoria, valor, tipo):
                messagebox.showinfo("Sucesso", f"{tipo.capitalize()} atualizado no orçamento com sucesso!")
                janela_edicao.destroy()
                
                # Recarregar orçamento
                self._carregar_orcamento(janela_pai, ano, mes)
                
                # Registrar na auditoria
                self.auditoria.registrar_evento(
                    'atualizacao_orcamento',
                    f"Atualização de orçamento: {tipo}, {categoria}, {valor}, {mes}/{ano}",
                    "sistema"
                )
            else:
                messagebox.showerror("Erro", "Erro ao atualizar orçamento!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar orçamento: {str(e)}")
    
    def _remover_orcamento(self, janela, ano, mes, tipo):
        """Remove um item do orçamento"""
        # Obter item selecionado
        tree = janela.tree_receitas if tipo == 'receita' else janela.tree_despesas
        selecao = tree.selection()
        
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um item para remover!")
            return
        
        # Obter categoria
        item = tree.item(selecao[0])
        categoria = item['values'][0]
        
        # Confirmar remoção
        if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover {categoria} do orçamento?"):
            return
        
        try:
            # Obter orçamento atual
            orcamento = self.orcamento.obter_orcamento(ano, mes)
            
            # Remover categoria
            if tipo + 's' in orcamento and categoria in orcamento[tipo + 's']:
                del orcamento[tipo + 's'][categoria]
                
                # Atualizar arquivo
                self.orcamento.orcamentos[str(ano)][str(mes)][tipo + 's'] = orcamento[tipo + 's']
                self.orcamento.salvar_orcamentos()
                
                # Atualizar treeview
                tree.delete(selecao[0])
                
                # Registrar na auditoria
                self.auditoria.registrar_evento(
                    'remocao_orcamento',
                    f"Remoção de orçamento: {tipo}, {categoria}, {mes}/{ano}",
                    "sistema"
                )
                
                messagebox.showinfo("Sucesso", f"{tipo.capitalize()} removido do orçamento com sucesso!")
            else:
                messagebox.showerror("Erro", "Categoria não encontrada no orçamento!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao remover orçamento: {str(e)}")
    
    def comparar_orcado_realizado(self, ano=None, mes=None):
        """Abre a interface para comparar orçado vs. realizado"""
        # Se não foram fornecidos ano e mês, solicitar
        if ano is None or mes is None:
            # Criar janela para seleção de período
            janela_periodo = tk.Toplevel(self.app.root)
            janela_periodo.title("Selecionar Período")
            janela_periodo.geometry("300x150")
            janela_periodo.grab_set()  # Torna a janela modal
            
            # Frame principal
            frame = ttk.Frame(janela_periodo, padding=10)
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Campos
            ttk.Label(frame, text="Ano:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            ano_entry = ttk.Combobox(frame, values=[str(y) for y in range(datetime.now().year - 2, datetime.now().year + 3)], width=10)
            ano_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
            ano_entry.set(str(datetime.now().year))
            
            ttk.Label(frame, text="Mês:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            mes_entry = ttk.Combobox(frame, values=[
                "1 - Janeiro",
                "2 - Fevereiro",
                "3 - Março",
                "4 - Abril",
                "5 - Maio",
                "6 - Junho",
                "7 - Julho",
                "8 - Agosto",
                "9 - Setembro",
                "10 - Outubro",
                "11 - Novembro",
                "12 - Dezembro"
            ], width=15)
            mes_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
            mes_entry.set(f"{datetime.now().month} - {datetime.now().strftime('%B')}")
            
            # Frame de botões
            frame_botoes = ttk.Frame(frame)
            frame_botoes.grid(row=2, column=0, columnspan=2, pady=20)
            
            # Botões
            btn_ok = ttk.Button(frame_botoes, text="OK", 
                              command=lambda: self._abrir_comparacao_orcado_realizado(
                                  janela_periodo,
                                  int(ano_entry.get()),
                                  int(mes_entry.get().split(' - ')[0])
                              ))
            btn_ok.pack(side=tk.LEFT, padx=5)
            
            btn_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=janela_periodo.destroy)
            btn_cancelar.pack(side=tk.LEFT, padx=5)
            
            return
        
        # Abrir interface de comparação
        self._abrir_comparacao_orcado_realizado(None, ano, mes)
    
    def _abrir_comparacao_orcado_realizado(self, janela_periodo, ano, mes):
        """Abre a interface de comparação orçado vs. realizado"""
        # Fechar janela de período se existir
        if janela_periodo:
            janela_periodo.destroy()
        
        # Verificar se há orçamento para o período
        orcamento = self.orcamento.obter_orcamento(ano, mes)
        if not orcamento:
            messagebox.showwarning("Aviso", f"Não há orçamento definido para {mes}/{ano}!")
            return
        
        # Criar janela
        janela = tk.Toplevel(self.app.root)
        janela.title(f"Orçado vs. Realizado - {mes}/{ano}")
        janela.geometry("900x700")
        janela.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame_principal = ttk.Frame(janela, padding=10)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Frame de resumo
        frame_resumo = ttk.LabelFrame(frame_principal, text="Resumo", padding=10)
        frame_resumo.pack(fill=tk.X, pady=10)
        
        # Obter comparação
        comparacao = self.orcamento.comparar_orcado_realizado(ano, mes)
        
        # Resumo
        ttk.Label(frame_resumo, text="Receitas:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame_resumo, text=f"Orçado: Kz {comparacao['total_orcado']['receitas']:,.2f}").grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame_resumo, text=f"Realizado: Kz {comparacao['total_realizado']['receitas']:,.2f}").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame_resumo, text=f"Diferença: Kz {comparacao['total_diferenca']['receitas']:,.2f}").grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame_resumo, text=f"% Realização: {comparacao['total_percentual']['receitas']:.1f}%").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame_resumo, text="Despesas:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame_resumo, text=f"Orçado: Kz {comparacao['total_orcado']['despesas']:,.2f}").grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame_resumo, text=f"Realizado: Kz {comparacao['total_realizado']['despesas']:,.2f}").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame_resumo, text=f"Diferença: Kz {comparacao['total_diferenca']['despesas']:,.2f}").grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame_resumo, text=f"% Realização: {comparacao['total_percentual']['despesas']:.1f}%").grid(row=1, column=4, sticky=tk.W, padx=5, pady=5)
        
        resultado_orcado = comparacao['total_orcado']['receitas'] - comparacao['total_orcado']['despesas']
        resultado_realizado = comparacao['total_realizado']['receitas'] - comparacao['total_realizado']['despesas']
        resultado_diferenca = resultado_realizado - resultado_orcado
        
        ttk.Label(frame_resumo, text="Resultado:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame_resumo, text=f"Orçado: Kz {resultado_orcado:,.2f}").grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame_resumo, text=f"Realizado: Kz {resultado_realizado:,.2f}").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(frame_resumo, text=f"Diferença: Kz {resultado_diferenca:,.2f}").grid(row=2, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Frame para gráfico
        frame_grafico = ttk.LabelFrame(frame_principal, text="Gráfico", padding=10)
        frame_grafico.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Gerar gráfico
        canvas_grafico = self.orcamento.gerar_grafico_orcado_realizado(frame_grafico, ano, mes)
        
        # Frame de detalhamento
        frame_detalhamento = ttk.LabelFrame(frame_principal, text="Detalhamento", padding=10)
        frame_detalhamento.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Notebook para abas
        notebook = ttk.Notebook(frame_detalhamento)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de receitas
        tab_receitas = ttk.Frame(notebook, padding=10)
        notebook.add(tab_receitas, text="Receitas")
        
        # Aba de despesas
        tab_despesas = ttk.Frame(notebook, padding=10)
        notebook.add(tab_despesas, text="Despesas")
        
        # Aba de desvios
        tab_desvios = ttk.Frame(notebook, padding=10)
        notebook.add(tab_desvios, text="Desvios Significativos")
        
        # Treeview para receitas
        colunas_receitas = ["categoria", "orcado", "realizado", "diferenca", "percentual"]
        
        tree_receitas = ttk.Treeview(tab_receitas, columns=colunas_receitas, show="headings")
        tree_receitas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Configurar colunas
        tree_receitas.heading("categoria", text="Categoria")
        tree_receitas.heading("orcado", text="Orçado")
        tree_receitas.heading("realizado", text="Realizado")
        tree_receitas.heading("diferenca", text="Diferença")
        tree_receitas.heading("percentual", text="% Realização")
        
        tree_receitas.column("categoria", width=250)
        tree_receitas.column("orcado", width=120)
        tree_receitas.column("realizado", width=120)
        tree_receitas.column("diferenca", width=120)
        tree_receitas.column("percentual", width=120)
        
        # Scrollbar para receitas
        scrollbar_receitas = ttk.Scrollbar(tab_receitas, orient=tk.VERTICAL, command=tree_receitas.yview)
        tree_receitas.configure(yscrollcommand=scrollbar_receitas.set)
        scrollbar_receitas.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher treeview de receitas
        for categoria, valores in comparacao['receitas'].items():
            tree_receitas.insert("", tk.END, values=(
                categoria,
                f"Kz {valores['orcado']:,.2f}",
                f"Kz {valores['realizado']:,.2f}",
                f"Kz {valores['diferenca']:,.2f}",
                f"{valores['percentual']:.1f}%"
            ))
            colunas_despesas = ["categoria", "orcado", "realizado", "diferenca", "percentual"]
        
        tree_despesas = ttk.Treeview(tab_despesas, columns=colunas_despesas, show="headings")
        tree_despesas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Configurar colunas
        tree_despesas.heading("categoria", text="Categoria")
        tree_despesas.heading("orcado", text="Orçado")
        tree_despesas.heading("realizado", text="Realizado")
        tree_despesas.heading("diferenca", text="Diferença")
        tree_despesas.heading("percentual", text="% Realização")
        
        tree_despesas.column("categoria", width=250)
        tree_despesas.column("orcado", width=120)
        tree_despesas.column("realizado", width=120)
        tree_despesas.column("diferenca", width=120)
        tree_despesas.column("percentual", width=120)
        
        # Scrollbar para despesas
        scrollbar_despesas = ttk.Scrollbar(tab_despesas, orient=tk.VERTICAL, command=tree_despesas.yview)
        tree_despesas.configure(yscrollcommand=scrollbar_despesas.set)
        scrollbar_despesas.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher treeview de despesas
        for categoria, valores in comparacao['despesas'].items():
            tree_despesas.insert("", tk.END, values=(
                categoria,
                f"Kz {valores['orcado']:,.2f}",
                f"Kz {valores['realizado']:,.2f}",
                f"Kz {valores['diferenca']:,.2f}",
                f"{valores['percentual']:.1f}%"
            ))
        
        # Identificar desvios significativos
        desvios = self.orcamento.identificar_desvios_significativos(ano, mes)
        
        # Treeview para desvios
        colunas_desvios = ["tipo", "categoria", "orcado", "realizado", "diferenca", "percentual", "situacao"]
        
        tree_desvios = ttk.Treeview(tab_desvios, columns=colunas_desvios, show="headings")
        tree_desvios.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Configurar colunas
        tree_desvios.heading("tipo", text="Tipo")
        tree_desvios.heading("categoria", text="Categoria")
        tree_desvios.heading("orcado", text="Orçado")
        tree_desvios.heading("realizado", text="Realizado")
        tree_desvios.heading("diferenca", text="Diferença")
        tree_desvios.heading("percentual", text="% Desvio")
        tree_desvios.heading("situacao", text="Situação")
        
        tree_desvios.column("tipo", width=80)
        tree_desvios.column("categoria", width=200)
        tree_desvios.column("orcado", width=100)
        tree_desvios.column("realizado", width=100)
        tree_desvios.column("diferenca", width=100)
        tree_desvios.column("percentual", width=80)
        tree_desvios.column("situacao", width=80)
        
        # Scrollbar para desvios
        scrollbar_desvios = ttk.Scrollbar(tab_desvios, orient=tk.VERTICAL, command=tree_desvios.yview)
        tree_desvios.configure(yscrollcommand=scrollbar_desvios.set)
        scrollbar_desvios.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher treeview de desvios
        for desvio in desvios:
            tree_desvios.insert("", tk.END, values=(
                desvio['tipo'].capitalize(),
                desvio['categoria'],
                f"Kz {desvio['orcado']:,.2f}",
                f"Kz {desvio['realizado']:,.2f}",
                f"Kz {desvio['diferenca']:,.2f}",
                f"{desvio['percentual']:.1f}%",
                desvio['situacao'].capitalize()
            ))
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        # Botões
        btn_relatorio = ttk.Button(frame_botoes, text="Gerar Relatório", 
                                  command=lambda: self._gerar_relatorio_orcado_realizado(ano, mes))
        btn_relatorio.pack(side=tk.LEFT, padx=5)
        
        btn_alertas = ttk.Button(frame_botoes, text="Mostrar Alertas", 
                               command=lambda: self.mostrar_alertas_desvios(desvios))
        btn_alertas.pack(side=tk.LEFT, padx=5)
        
        btn_fechar = ttk.Button(frame_botoes, text="Fechar", command=janela.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=5)
    
    def _gerar_relatorio_orcado_realizado(self, ano, mes):
        """Gera um relatório de orçado vs. realizado"""
        # Solicitar caminho para salvar o relatório
        caminho_saida = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf")],
            title="Salvar Relatório de Orçado vs. Realizado"
        )
        
        if not caminho_saida:
            return
        
        # Gerar relatório
        if self.orcamento.gerar_relatorio_orcado_realizado(ano, mes, caminho_saida):
            messagebox.showinfo("Sucesso", f"Relatório de orçado vs. realizado gerado com sucesso!\n\nSalvo em: {caminho_saida}")
            
            # Perguntar se deseja abrir o relatório
            if messagebox.askyesno("Abrir Relatório", "Deseja abrir o relatório agora?"):
                self._abrir_arquivo(caminho_saida)
        else:
            messagebox.showerror("Erro", "Erro ao gerar relatório de orçado vs. realizado.")
    
    def mostrar_alertas_desvios(self, desvios=None):
        """Mostra alertas de desvios significativos"""
        # Se não foram fornecidos desvios, obter do período atual
        if desvios is None:
            ano = datetime.now().year
            mes = datetime.now().month
            desvios = self.orcamento.identificar_desvios_significativos(ano, mes)
        
        # Verificar se há desvios
        if not desvios:
            messagebox.showinfo("Alertas", "Não há desvios significativos para mostrar.")
            return
        
        # Criar janela
        janela = tk.Toplevel(self.app.root)
        janela.title("Alertas de Desvios Significativos")
        janela.geometry("800x600")
        janela.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame_principal = ttk.Frame(janela, padding=10)
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Frame de alertas
        frame_alertas = ttk.LabelFrame(frame_principal, text="Alertas", padding=10)
        frame_alertas.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview para alertas
        colunas = ["tipo", "categoria", "orcado", "realizado", "diferenca", "percentual", "situacao"]
        
        tree_alertas = ttk.Treeview(frame_alertas, columns=colunas, show="headings")
        tree_alertas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Configurar colunas
        tree_alertas.heading("tipo", text="Tipo")
        tree_alertas.heading("categoria", text="Categoria")
        tree_alertas.heading("orcado", text="Orçado")
        tree_alertas.heading("realizado", text="Realizado")
        tree_alertas.heading("diferenca", text="Diferença")
        tree_alertas.heading("percentual", text="% Desvio")
        tree_alertas.heading("situacao", text="Situação")
        
        tree_alertas.column("tipo", width=80)
        tree_alertas.column("categoria", width=200)
        tree_alertas.column("orcado", width=100)
        tree_alertas.column("realizado", width=100)
        tree_alertas.column("diferenca", width=100)
        tree_alertas.column("percentual", width=80)
        tree_alertas.column("situacao", width=80)
        
        # Scrollbar para alertas
        scrollbar_alertas = ttk.Scrollbar(frame_alertas, orient=tk.VERTICAL, command=tree_alertas.yview)
        tree_alertas.configure(yscrollcommand=scrollbar_alertas.set)
        scrollbar_alertas.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher treeview
        for desvio in desvios:
            tree_alertas.insert("", tk.END, values=(
                desvio['tipo'].capitalize(),
                desvio['categoria'],
                f"Kz {desvio['orcado']:,.2f}",
                f"Kz {desvio['realizado']:,.2f}",
                f"Kz {desvio['diferenca']:,.2f}",
                f"{desvio['percentual']:.1f}%",
                desvio['situacao'].capitalize()
            ))
        
        # Frame de recomendações
        frame_recomendacoes = ttk.LabelFrame(frame_principal, text="Recomendações", padding=10)
        frame_recomendacoes.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Texto para recomendações
        texto_recomendacoes = tk.Text(frame_recomendacoes, height=10, wrap=tk.WORD)
        texto_recomendacoes.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar para recomendações
        scrollbar_recomendacoes = ttk.Scrollbar(frame_recomendacoes, orient=tk.VERTICAL, command=texto_recomendacoes.yview)
        texto_recomendacoes.configure(yscrollcommand=scrollbar_recomendacoes.set)
        scrollbar_recomendacoes.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Gerar recomendações
        texto_recomendacoes.insert(tk.END, "Recomendações baseadas nos desvios identificados:\n\n")
        
        for desvio in desvios:
            if desvio['tipo'] == 'receita':
                if desvio['situacao'] == 'abaixo':
                    texto_recomendacoes.insert(tk.END, 
                        f"• A receita de {desvio['categoria']} está {desvio['percentual']:.1f}% abaixo do orçado. "
                        f"Recomenda-se revisar as estratégias de vendas/captação para esta categoria.\n\n"
                    )
                else:
                    texto_recomendacoes.insert(tk.END, 
                        f"• A receita de {desvio['categoria']} está {desvio['percentual']:.1f}% acima do orçado. "
                        f"Considere ajustar o orçamento para refletir este aumento ou investigar se é um evento pontual.\n\n"
                    )
            else:  # despesa
                if desvio['situacao'] == 'acima':
                    texto_recomendacoes.insert(tk.END, 
                        f"• A despesa de {desvio['categoria']} está {desvio['percentual']:.1f}% acima do orçado. "
                        f"Recomenda-se revisar os gastos nesta categoria e implementar medidas de controle.\n\n"
                    )
                else:
                    texto_recomendacoes.insert(tk.END, 
                        f"• A despesa de {desvio['categoria']} está {desvio['percentual']:.1f}% abaixo do orçado. "
                        f"Verifique se há atrasos em pagamentos ou se o orçamento pode ser ajustado.\n\n"
                    )
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        # Botões
        btn_fechar = ttk.Button(frame_botoes, text="Fechar", command=janela.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=5)
    
    # ===== Métodos Utilitários =====
    
    def _abrir_arquivo(self, caminho):
        """Abre um arquivo com o aplicativo padrão do sistema"""
        try:
            if os.path.exists(caminho):
                if platform.system() == 'Windows':
                    os.startfile(caminho)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(['open', caminho])
                else:  # Linux
                    subprocess.call(['xdg-open', caminho])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir arquivo: {str(e)}")