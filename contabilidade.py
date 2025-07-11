import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
import json
import os

class ContabilidadeAvancada:
    def __init__(self):
        """Inicializa a classe de contabilidade avançada"""
        self.dados_banco = None
        self.dados_livro = None
        self.lancamentos = []  # Lista para armazenar lançamentos contábeis
        self.bens_amortizaveis = []  # Lista para armazenar bens amortizáveis
        self.plano_contas = self.carregar_plano_contas()  # Carregar plano de contas
        
        # Carregar dados salvos se existirem
        self.carregar_dados_salvos()
    
    def carregar_dados_salvos(self):
        """Carrega dados salvos de arquivos JSON"""
        try:
            # Carregar bens amortizáveis
            if os.path.exists('bens_amortizaveis.json'):
                with open('bens_amortizaveis.json', 'r', encoding='utf-8') as f:
                    self.bens_amortizaveis = json.load(f)
                    # Converter strings de data para objetos datetime
                    for bem in self.bens_amortizaveis:
                        bem['data'] = datetime.fromisoformat(bem['data'])
                        if 'amortizacoes' in bem:
                            for amort in bem['amortizacoes']:
                                amort['data'] = datetime.fromisoformat(amort['data'])
            
            # Carregar lançamentos contábeis
            if os.path.exists('lancamentos_contabeis.json'):
                with open('lancamentos_contabeis.json', 'r', encoding='utf-8') as f:
                    self.lancamentos = json.load(f)
                    # Converter strings de data para objetos datetime
                    for lanc in self.lancamentos:
                        lanc['data'] = datetime.fromisoformat(lanc['data'])
        except Exception as e:
            print(f"Erro ao carregar dados salvos: {str(e)}")
    
    def salvar_dados(self):
        """Salva dados em arquivos JSON"""
        try:
            # Salvar bens amortizáveis
            bens_json = []
            for bem in self.bens_amortizaveis:
                bem_copy = bem.copy()
                bem_copy['data'] = bem_copy['data'].isoformat()
                if 'amortizacoes' in bem_copy:
                    for amort in bem_copy['amortizacoes']:
                        amort['data'] = amort['data'].isoformat()
                bens_json.append(bem_copy)
                
            with open('bens_amortizaveis.json', 'w', encoding='utf-8') as f:
                json.dump(bens_json, f, ensure_ascii=False, indent=2)
            
            # Salvar lançamentos contábeis
            lanc_json = []
            for lanc in self.lancamentos:
                lanc_copy = lanc.copy()
                lanc_copy['data'] = lanc_copy['data'].isoformat()
                lanc_json.append(lanc_copy)
                
            with open('lancamentos_contabeis.json', 'w', encoding='utf-8') as f:
                json.dump(lanc_json, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            print(f"Erro ao salvar dados: {str(e)}")
            return False
    
    def converter_dados_para_lancamentos(self):
        """Converte os dados do banco e livro em lançamentos contábeis estruturados"""
        if self.dados_banco is None and self.dados_livro is None:
            return False
        
        # Não limpar lançamentos existentes, apenas adicionar novos
        lancamentos_existentes = set()
        for lanc in self.lancamentos:
            # Criar uma chave única para cada lançamento
            chave = (lanc['data'].strftime('%Y-%m-%d'), lanc['descricao'], 
                    sum(m['debito'] for m in lanc['movimentos']))
            lancamentos_existentes.add(chave)
        
        novos_lancamentos = 0
        
        # Converter dados do banco se disponíveis
        if self.dados_banco is not None:
            for _, row in self.dados_banco.iterrows():
                # Verificar se o lançamento já existe
                chave = (row['data'].strftime('%Y-%m-%d'), row['descricao'], row['valor'])
                if chave in lancamentos_existentes:
                    continue
                
                # Determinar contas com base na descrição
                conta_debito = self.determinar_conta_debito(row['descricao'])
                conta_credito = self.determinar_conta_credito(row['descricao'])
                
                # Criar lançamento
                lancamento = {
                    'id': f"B{len(self.lancamentos) + novos_lancamentos + 1}",
                    'data': row['data'],
                    'descricao': row['descricao'],
                    'origem': 'BANCO',
                    'movimentos': [
                        {'conta': conta_debito, 'debito': row['valor'], 'credito': 0},
                        {'conta': conta_credito, 'debito': 0, 'credito': row['valor']}
                    ]
                }
                self.lancamentos.append(lancamento)
                novos_lancamentos += 1
                lancamentos_existentes.add(chave)
        
        # Converter dados do livro se disponíveis
        if self.dados_livro is not None:
            for _, row in self.dados_livro.iterrows():
                # Verificar se o lançamento já existe
                chave = (row['data'].strftime('%Y-%m-%d'), row['descricao'], row['valor'])
                if chave in lancamentos_existentes:
                    continue
                
                # Determinar contas com base na descrição
                conta_debito = self.determinar_conta_debito(row['descricao'])
                conta_credito = self.determinar_conta_credito(row['descricao'])
                
                # Criar lançamento
                lancamento = {
                    'id': f"L{len(self.lancamentos) + novos_lancamentos + 1}",
                    'data': row['data'],
                    'descricao': row['descricao'],
                    'origem': 'LIVRO',
                    'movimentos': [
                        {'conta': conta_debito, 'debito': row['valor'], 'credito': 0},
                        {'conta': conta_credito, 'debito': 0, 'credito': row['valor']}
                    ]
                }
                self.lancamentos.append(lancamento)
                novos_lancamentos += 1
                lancamentos_existentes.add(chave)
        
        # Salvar os dados atualizados
        self.salvar_dados()
        
        return novos_lancamentos > 0
    
    def determinar_conta_debito(self, descricao):
        """Determina a conta de débito com base na descrição"""
        descricao_upper = descricao.upper()
        
        # Regras para classificação automática
        if any(termo in descricao_upper for termo in ["VENDA", "RECEITA", "FATURAMENTO"]):
            return "45"  # Caixa
        elif any(termo in descricao_upper for termo in ["TRANSFERÊNCIA", "TRANSFERENCIA", "TED", "DOC"]):
            return "43"  # Depósitos à Ordem
        elif any(termo in descricao_upper for termo in ["SALÁRIO", "SALARIO", "FOLHA", "PAGAMENTO"]):
            return "64"  # Custos com o Pessoal
        elif any(termo in descricao_upper for termo in ["COMPRA", "FORNECEDOR", "MERCADORIA"]):
            return "21"  # Compras
        elif any(termo in descricao_upper for termo in ["IMPOSTO", "TAXA", "TRIBUTO"]):
            return "63"  # Impostos
        elif any(termo in descricao_upper for termo in ["ALUGUEL", "ENERGIA", "ÁGUA", "AGUA", "TELEFONE"]):
            return "62"  # Fornecimentos e Serviços de Terceiros
        
        # Conta padrão para débito
        return "43"  # Depósitos à Ordem
    
    def determinar_conta_credito(self, descricao):
        """Determina a conta de crédito com base na descrição"""
        descricao_upper = descricao.upper()
        
        # Regras para classificação automática
        if any(termo in descricao_upper for termo in ["VENDA", "RECEITA", "FATURAMENTO"]):
            return "71"  # Vendas
        elif any(termo in descricao_upper for termo in ["TRANSFERÊNCIA", "TRANSFERENCIA", "TED", "DOC"]):
            return "37"  # Outros Valores a Receber e a Pagar
        elif any(termo in descricao_upper for termo in ["SALÁRIO", "SALARIO", "FOLHA", "PAGAMENTO"]):
            return "36"  # Pessoal
        elif any(termo in descricao_upper for termo in ["COMPRA", "FORNECEDOR", "MERCADORIA"]):
            return "32"  # Fornecedores
        elif any(termo in descricao_upper for termo in ["IMPOSTO", "TAXA", "TRIBUTO"]):
            return "34"  # Estado
        elif any(termo in descricao_upper for termo in ["ALUGUEL", "ENERGIA", "ÁGUA", "AGUA", "TELEFONE"]):
            return "32"  # Fornecedores
        
        # Conta padrão para crédito
        return "71"  # Vendas
    
    def abrir_classificador_lancamentos(self, root):
        """Abre uma interface para classificar lançamentos em contas contábeis"""
        if self.dados_livro is None and self.dados_banco is None:
            messagebox.showwarning("Aviso", "Importe os dados primeiro!")
            return
        
        # Converter dados para lançamentos preliminares
        self.converter_dados_para_lancamentos()
        
        janela = tk.Toplevel(root)
        janela.title("Classificar Lançamentos Contábeis")
        janela.geometry("900x600")
        
        # Frame para a tabela
        frame_tabela = ttk.Frame(janela)
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Criar tabela
        colunas = ('id', 'data', 'descricao', 'valor', 'origem', 'conta_debito', 'conta_credito')
        tabela = ttk.Treeview(frame_tabela, columns=colunas, show='headings')
        
        # Configurar cabeçalhos
        tabela.heading('id', text='ID')
        tabela.heading('data', text='Data')
        tabela.heading('descricao', text='Descrição')
        tabela.heading('valor', text='Valor')
        tabela.heading('origem', text='Origem')
        tabela.heading('conta_debito', text='Conta Débito')
        tabela.heading('conta_credito', text='Conta Crédito')
        
        # Configurar larguras
        tabela.column('id', width=50)
        tabela.column('data', width=100)
        tabela.column('descricao', width=300)
        tabela.column('valor', width=100)
        tabela.column('origem', width=80)
        tabela.column('conta_debito', width=100)
        tabela.column('conta_credito', width=100)
        
        # Preencher tabela com dados
        for i, lanc in enumerate(self.lancamentos):
            valor = sum(m['debito'] for m in lanc['movimentos'])
            conta_debito = lanc['movimentos'][0]['conta'] if len(lanc['movimentos']) > 0 else ""
            conta_credito = lanc['movimentos'][1]['conta'] if len(lanc['movimentos']) > 1 else ""
            
            tabela.insert('', 'end', iid=i, values=(
                lanc['id'],
                lanc['data'].strftime('%d/%m/%Y'),
                lanc['descricao'],
                f"Kz {valor:,.2f}",
                lanc.get('origem', 'MANUAL'),
                conta_debito,
                conta_credito
            ))
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=tabela.yview)
        tabela.configure(yscrollcommand=scrollbar.set)
        tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para botões
        frame_botoes = ttk.Frame(janela)
        frame_botoes.pack(fill=tk.X, padx=10, pady=10)
        
        # Frame para informações do plano de contas
        frame_info = ttk.LabelFrame(janela, text="Plano de Contas")
        frame_info.pack(fill=tk.X, padx=10, pady=5)
        
        # Texto com informações do plano de contas
        info_text = tk.Text(frame_info, height=6, wrap=tk.WORD)
        info_text.pack(fill=tk.X, padx=5, pady=5)
        info_text.insert(tk.END, "Contas mais comuns:\n")
        info_text.insert(tk.END, "43 - Depósitos à Ordem (débito para entradas)\n")
        info_text.insert(tk.END, "45 - Caixa (débito para entradas em dinheiro)\n")
        info_text.insert(tk.END, "71 - Vendas (crédito para receitas)\n")
        info_text.insert(tk.END, "62 - Fornecimentos e Serviços (débito para despesas)\n")
        info_text.insert(tk.END, "32 - Fornecedores (crédito para compras)\n")
        info_text.configure(state='disabled')
        
        # Função para editar classificação
        def editar_classificacao():
            item_selecionado = tabela.selection()
            if not item_selecionado:
                messagebox.showwarning("Aviso", "Selecione um lançamento primeiro!")
                return
                
            item = item_selecionado[0]
            valores = tabela.item(item, 'values')
            
            # Janela para editar
            janela_edit = tk.Toplevel(janela)
            janela_edit.title("Editar Classificação")
            janela_edit.geometry("400x300")
            
            ttk.Label(janela_edit, text="Conta Débito:").grid(row=0, column=0, padx=5, pady=5)
            conta_debito_var = tk.StringVar(value=valores[5])
            ttk.Entry(janela_edit, textvariable=conta_debito_var).grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(janela_edit, text="Conta Crédito:").grid(row=1, column=0, padx=5, pady=5)
            conta_credito_var = tk.StringVar(value=valores[6])
            ttk.Entry(janela_edit, textvariable=conta_credito_var).grid(row=1, column=1, padx=5, pady=5)
            
            def salvar():
                # Atualizar na tabela
                tabela.item(item, values=(
                    valores[0], valores[1], valores[2], valores[3], valores[4],
                    conta_debito_var.get(), conta_credito_var.get()
                ))
                
                # Atualizar no objeto de lançamentos
                idx = int(item)
                valor = float(valores[3].replace('Kz ', '').replace(',', ''))
                self.lancamentos[idx]['movimentos'] = [
                    {'conta': conta_debito_var.get(), 'debito': valor, 'credito': 0},
                    {'conta': conta_credito_var.get(), 'debito': 0, 'credito': valor}
                ]
                
                janela_edit.destroy()
                
            ttk.Button(janela_edit, text="Salvar", command=salvar).grid(row=2, column=1, pady=10)
        
        # Botões
        ttk.Button(frame_botoes, text="Editar Classificação", command=editar_classificacao).pack(side=tk.LEFT, padx=5)
        
        def salvar_classificacao():
            # Salvar os dados
            if self.salvar_dados():
                messagebox.showinfo("Sucesso", f"{len(self.lancamentos)} lançamentos classificados e salvos com sucesso!")
                janela.destroy()
            else:
                messagebox.showerror("Erro", "Falha ao salvar os lançamentos.")
        
        ttk.Button(frame_botoes, text="Salvar Classificação", command=salvar_classificacao).pack(side=tk.LEFT, padx=5)
        
        # Botão para ver plano de contas completo
        def mostrar_plano_contas():
            janela_plano = tk.Toplevel(janela)
            janela_plano.title("Plano de Contas")
            janela_plano.geometry("600x700")
            
            # Criar texto com scroll
            frame_texto = ttk.Frame(janela_plano)
            frame_texto.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            texto = tk.Text(frame_texto, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(frame_texto, orient=tk.VERTICAL, command=texto.yview)
            texto.configure(yscrollcommand=scrollbar.set)
            texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Preencher com plano de contas
            texto.insert(tk.END, "PLANO DE CONTAS ANGOLANO\n\n")
            for classe, classe_info in self.plano_contas.items():
                texto.insert(tk.END, f"CLASSE {classe}: {classe_info['nome']}\n")
                if 'contas' in classe_info:
                    for codigo, conta_info in classe_info['contas'].items():
                        texto.insert(tk.END, f"  {codigo} - {conta_info['nome']} ({conta_info['tipo']})\n")
                texto.insert(tk.END, "\n")
            
            texto.configure(state='disabled')
            
            ttk.Button(janela_plano, text="Fechar", command=janela_plano.destroy).pack(pady=10)
        
        ttk.Button(frame_botoes, text="Ver Plano de Contas", command=mostrar_plano_contas).pack(side=tk.LEFT, padx=5)
    
    def registrar_bem_amortizavel(self, codigo, descricao, valor, data, vida_util, valor_residual):
        """Registra um novo bem amortizável"""
        # Verificar se o código já existe
        for bem in self.bens_amortizaveis:
            if bem['codigo'] == codigo:
                raise ValueError("Já existe um bem com este código.")
        
        # Criar novo bem
        novo_bem = {
            'codigo': codigo,
            'descricao': descricao,
            'valor': valor,
            'data': data,
            'vida_util': vida_util,
            'valor_residual': valor_residual,
            'amortizacoes': []
        }
        
        # Adicionar à lista
        self.bens_amortizaveis.append(novo_bem)
        
        # Registrar lançamento contábil
        self.registrar_lancamento(
            data,
            f"Aquisição de {descricao}",
            [
                {'conta': '11', 'debito': valor, 'credito': 0},  # Débito em Imobilizações Corpóreas
                {'conta': '32', 'debito': 0, 'credito': valor}   # Crédito em Fornecedores
            ]
        )
        
        # Salvar dados
        self.salvar_dados()
        
        return True
    
    def registrar_lancamento(self, data, descricao, movimentos, origem="MANUAL"):
        """Registra um lançamento contábil manual"""
        # Verificar se os movimentos estão balanceados
        total_debito = sum(m['debito'] for m in movimentos)
        total_credito = sum(m['credito'] for m in movimentos)
        
        if abs(total_debito - total_credito) > 0.01:
            raise ValueError("Lançamento não balanceado. Total de débitos deve ser igual ao total de créditos.")
        
        # Criar novo lançamento
        novo_lancamento = {
            'id': f"M{len(self.lancamentos) + 1}",
            'data': data,
            'descricao': descricao,
            'origem': origem,
            'movimentos': movimentos
        }
        
        # Adicionar à lista
        self.lancamentos.append(novo_lancamento)
        
        # Salvar dados
        self.salvar_dados()
        
        return True
    
    def gerar_balanco_patrimonial(self, data_ref, caminho_saida):
        """
        Gera o Balanço Patrimonial para uma data específica
        Args:
            data_ref: Data de referência
            caminho_saida: Caminho do arquivo PDF de saída
        Returns:
            bool: True se gerado com sucesso, False caso contrário
        """
        try:
            # Converter dados para lançamentos contábeis se necessário
            self.converter_dados_para_lancamentos()
            
            # Filtrar lançamentos até a data de referência
            lancamentos_filtrados = [l for l in self.lancamentos if l['data'] <= data_ref]
            
            # Calcular saldos das contas
            saldos = {}
            for lancamento in lancamentos_filtrados:
                for movimento in lancamento['movimentos']:
                    conta = movimento['conta']
                    if conta not in saldos:
                        saldos[conta] = 0
                    saldos[conta] += movimento['debito'] - movimento['credito']
            
            # Calcular amortizações
            self.calcular_amortizacoes(data_ref)
            
            # Criar documento PDF
            doc = SimpleDocTemplate(caminho_saida, pagesize=A4)
            elementos = []
            
            # Estilos
            estilos = getSampleStyleSheet()
            estilo_titulo = estilos['Heading1']
            estilo_subtitulo = estilos['Heading2']
            estilo_normal = estilos['Normal']
            
            # Título
            elementos.append(Paragraph("Balanço Patrimonial", estilo_titulo))
            elementos.append(Paragraph(f"Data de Referência: {data_ref.strftime('%d/%m/%Y')}", estilo_normal))
            elementos.append(Spacer(1, 0.5*cm))
            
            # Ativo
            elementos.append(Paragraph("ATIVO", estilo_subtitulo))
            
            # Ativo Não Corrente
            dados_ativo_nc = [["Conta", "Descrição", "Valor"]]
            total_ativo_nc = 0
            
            # Adicionar contas do ativo não corrente (classe 1)
            for codigo_conta, saldo in saldos.items():
                if codigo_conta.startswith('1'):
                    # Buscar nome no plano de contas
                    nome_conta = "Conta Desconhecida"
                    for classe, classe_info in self.plano_contas.items():
                        if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                            nome_conta = classe_info['contas'][codigo_conta]['nome']
                            break
                    
                    # Ajustar saldo conforme natureza da conta
                    for classe, classe_info in self.plano_contas.items():
                        if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                            if classe_info['contas'][codigo_conta]['natureza'] == 'credora':
                                saldo = -saldo
                            break
                    
                    dados_ativo_nc.append([codigo_conta, nome_conta, f"Kz {saldo:,.2f}"])
                    total_ativo_nc += saldo
            
            dados_ativo_nc.append(["", "Total do Ativo Não Corrente", f"Kz {total_ativo_nc:,.2f}"])
            
            # Criar tabela
            tabela_ativo_nc = Table(dados_ativo_nc, colWidths=[2*cm, 12*cm, 4*cm])
            tabela_ativo_nc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_ativo_nc)
            elementos.append(Spacer(1, 0.3*cm))
            
            # Ativo Corrente
            dados_ativo_c = [["Conta", "Descrição", "Valor"]]
            total_ativo_c = 0
            
            # Adicionar contas do ativo corrente (classes 2, 3, 4)
            for codigo_conta, saldo in saldos.items():
                if codigo_conta.startswith(('2', '3', '4')):
                    # Verificar se é conta do ativo
                    is_ativo = False
                    for classe, classe_info in self.plano_contas.items():
                        if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                            if classe_info['contas'][codigo_conta]['tipo'] == 'ativo' or (
                                classe_info['contas'][codigo_conta]['tipo'] == 'misto' and saldo > 0):
                                is_ativo = True
                                # Ajustar saldo conforme natureza da conta
                                if classe_info['contas'][codigo_conta]['natureza'] == 'credora':
                                    saldo = -saldo
                            break
                    
                    if is_ativo:
                        # Buscar nome no plano de contas
                        nome_conta = "Conta Desconhecida"
                        for classe, classe_info in self.plano_contas.items():
                            if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                                nome_conta = classe_info['contas'][codigo_conta]['nome']
                                break
                        
                        dados_ativo_c.append([codigo_conta, nome_conta, f"Kz {saldo:,.2f}"])
                        total_ativo_c += saldo
            
            dados_ativo_c.append(["", "Total do Ativo Corrente", f"Kz {total_ativo_c:,.2f}"])
            
            # Criar tabela
            tabela_ativo_c = Table(dados_ativo_c, colWidths=[2*cm, 12*cm, 4*cm])
            tabela_ativo_c.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_ativo_c)
            elementos.append(Spacer(1, 0.3*cm))
            
            # Total do Ativo
            total_ativo = total_ativo_nc + total_ativo_c
            dados_total_ativo = [["", "TOTAL DO ATIVO", f"Kz {total_ativo:,.2f}"]]
            tabela_total_ativo = Table(dados_total_ativo, colWidths=[2*cm, 12*cm, 4*cm])
            tabela_total_ativo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_total_ativo)
            elementos.append(Spacer(1, 0.5*cm))
            
            # Passivo e Capital Próprio
            elementos.append(Paragraph("PASSIVO E CAPITAL PRÓPRIO", estilo_subtitulo))
            
            # Capital Próprio
            dados_capital = [["Conta", "Descrição", "Valor"]]
            total_capital = 0
            
            # Adicionar contas de capital (classe 5)
            for codigo_conta, saldo in saldos.items():
                if codigo_conta.startswith('5'):
                    # Buscar nome no plano de contas
                    nome_conta = "Conta Desconhecida"
                    for classe, classe_info in self.plano_contas.items():
                        if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                            nome_conta = classe_info['contas'][codigo_conta]['nome']
                            break
                    
                    # Ajustar saldo conforme natureza da conta
                    for classe, classe_info in self.plano_contas.items():
                        if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                            if classe_info['contas'][codigo_conta]['natureza'] == 'credora':
                                saldo = -saldo
                            break
                    
                    dados_capital.append([codigo_conta, nome_conta, f"Kz {saldo:,.2f}"])
                    total_capital += saldo
            
            # Calcular resultado do exercício
            resultado_liquido = 0
            for codigo_conta, saldo in saldos.items():
                if codigo_conta.startswith('6'):  # Despesas
                    resultado_liquido -= saldo
                elif codigo_conta.startswith('7'):  # Receitas
                    resultado_liquido += -saldo  # Receitas têm saldo credor (negativo)
            
            dados_capital.append(["88", "Resultado Líquido do Exercício", f"Kz {resultado_liquido:,.2f}"])
            total_capital += resultado_liquido
            
            dados_capital.append(["", "Total do Capital Próprio", f"Kz {total_capital:,.2f}"])
            
            # Criar tabela
            tabela_capital = Table(dados_capital, colWidths=[2*cm, 12*cm, 4*cm])
            tabela_capital.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_capital)
            elementos.append(Spacer(1, 0.3*cm))
            
            # Passivo Não Corrente
            dados_passivo_nc = [["Conta", "Descrição", "Valor"]]
            total_passivo_nc = 0
            
            # Adicionar contas do passivo não corrente (empréstimos de longo prazo)
            for codigo_conta, saldo in saldos.items():
                if codigo_conta.startswith('33'):  # Empréstimos
                    # Verificar se é de longo prazo (simplificação)
                    # Na prática, seria necessário verificar a natureza do empréstimo
                    
                    # Buscar nome no plano de contas
                    nome_conta = "Conta Desconhecida"
                    for classe, classe_info in self.plano_contas.items():
                        if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                            nome_conta = classe_info['contas'][codigo_conta]['nome']
                            break
                    
                    # Ajustar saldo conforme natureza da conta
                    for classe, classe_info in self.plano_contas.items():
                        if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                            if classe_info['contas'][codigo_conta]['natureza'] == 'devedora':
                                saldo = -saldo
                            break
                    
                    dados_passivo_nc.append([codigo_conta, nome_conta, f"Kz {saldo:,.2f}"])
                    total_passivo_nc += saldo
            
            dados_passivo_nc.append(["", "Total do Passivo Não Corrente", f"Kz {total_passivo_nc:,.2f}"])
            
            # Criar tabela
            tabela_passivo_nc = Table(dados_passivo_nc, colWidths=[2*cm, 12*cm, 4*cm])
            tabela_passivo_nc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_passivo_nc)
            elementos.append(Spacer(1, 0.3*cm))
            
            # Passivo Corrente
            dados_passivo_c = [["Conta", "Descrição", "Valor"]]
            total_passivo_c = 0
            
            # Adicionar contas do passivo corrente
            for codigo_conta, saldo in saldos.items():
                if codigo_conta.startswith(('3', '4')) and not codigo_conta.startswith('33'):
                    # Verificar se é conta do passivo
                    is_passivo = False
                    for classe, classe_info in self.plano_contas.items():
                        if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                            if classe_info['contas'][codigo_conta]['tipo'] == 'passivo' or (
                                classe_info['contas'][codigo_conta]['tipo'] == 'misto' and saldo < 0):
                                is_passivo = True
                                # Ajustar saldo conforme natureza da conta
                                if classe_info['contas'][codigo_conta]['natureza'] == 'devedora':
                                    saldo = -saldo
                            break
                    
                    if is_passivo:
                        # Buscar nome no plano de contas
                        nome_conta = "Conta Desconhecida"
                        for classe, classe_info in self.plano_contas.items():
                            if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                                nome_conta = classe_info['contas'][codigo_conta]['nome']
                                break
                        
                        dados_passivo_c.append([codigo_conta, nome_conta, f"Kz {abs(saldo):,.2f}"])
                        total_passivo_c += abs(saldo)
            
            dados_passivo_c.append(["", "Total do Passivo Corrente", f"Kz {total_passivo_c:,.2f}"])
            
            # Criar tabela
            tabela_passivo_c = Table(dados_passivo_c, colWidths=[2*cm, 12*cm, 4*cm])
            tabela_passivo_c.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_passivo_c)
            elementos.append(Spacer(1, 0.3*cm))
            
            # Total do Passivo
            total_passivo = total_passivo_nc + total_passivo_c
            dados_total_passivo = [["", "TOTAL DO PASSIVO", f"Kz {total_passivo:,.2f}"]]
            tabela_total_passivo = Table(dados_total_passivo, colWidths=[2*cm, 12*cm, 4*cm])
            tabela_total_passivo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_total_passivo)
            elementos.append(Spacer(1, 0.3*cm))
            
            # Total do Passivo e Capital Próprio
            total_passivo_capital = total_passivo + total_capital
            dados_total_geral = [["", "TOTAL DO PASSIVO E CAPITAL PRÓPRIO", f"Kz {total_passivo_capital:,.2f}"]]
            tabela_total_geral = Table(dados_total_geral, colWidths=[2*cm, 12*cm, 4*cm])
            tabela_total_geral.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_total_geral)
            
            # Gerar PDF
            doc.build(elementos)
            
            return True
        except Exception as e:
            print(f"Erro ao gerar balanço patrimonial: {str(e)}")
            return False

    def gerar_dre(self, data_inicio, data_fim, caminho_saida):
        """
        Gera a Demonstração de Resultados do Exercício para um período específico
        Args:
            data_inicio: Data de início do período
            data_fim: Data de fim do período
            caminho_saida: Caminho do arquivo PDF de saída
        Returns:
            bool: True se gerado com sucesso, False caso contrário
        """
        try:
            # Converter dados para lançamentos contábeis se necessário
            self.converter_dados_para_lancamentos()
            
            # Filtrar lançamentos do período
            lancamentos_filtrados = [l for l in self.lancamentos
                                    if data_inicio <= l['data'] <= data_fim]
            
            # Calcular saldos das contas
            saldos = {}
            for lancamento in lancamentos_filtrados:
                for movimento in lancamento['movimentos']:
                    conta = movimento['conta']
                    if conta not in saldos:
                        saldos[conta] = 0
                    saldos[conta] += movimento['debito'] - movimento['credito']
            
            # Criar documento PDF
            doc = SimpleDocTemplate(caminho_saida, pagesize=A4)
            elementos = []
            
            # Estilos
            estilos = getSampleStyleSheet()
            estilo_titulo = estilos['Heading1']
            estilo_subtitulo = estilos['Heading2']
            estilo_normal = estilos['Normal']
            
            # Título
            elementos.append(Paragraph("Demonstração de Resultados do Exercício", estilo_titulo))
            elementos.append(Paragraph(f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}", estilo_normal))
            elementos.append(Spacer(1, 0.5*cm))
            
            # Receitas
            elementos.append(Paragraph("RECEITAS", estilo_subtitulo))
            dados_receitas = [["Conta", "Descrição", "Valor"]]
            total_receitas = 0
            
            for codigo_conta, saldo in saldos.items():
                if codigo_conta.startswith('7'):  # Receitas
                    # Para receitas, o saldo é crédito (negativo no nosso cálculo)
                    valor = -saldo
                    
                    # Buscar nome no plano de contas
                    nome_conta = "Conta Desconhecida"
                    for classe, classe_info in self.plano_contas.items():
                        if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                            nome_conta = classe_info['contas'][codigo_conta]['nome']
                            break
                    
                    dados_receitas.append([codigo_conta, nome_conta, f"Kz {valor:,.2f}"])
                    total_receitas += valor
            
            dados_receitas.append(["", "Total de Receitas", f"Kz {total_receitas:,.2f}"])
            
            # Criar tabela
            tabela_receitas = Table(dados_receitas, colWidths=[1.5*cm, 11.5*cm, 4*cm])
            tabela_receitas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_receitas)
            elementos.append(Spacer(1, 0.5*cm))
            
            # Despesas
            elementos.append(Paragraph("DESPESAS", estilo_subtitulo))
            dados_despesas = [["Conta", "Descrição", "Valor"]]
            total_despesas = 0
            
            for codigo_conta, saldo in saldos.items():
                if codigo_conta.startswith('6'):  # Despesas
                    # Para despesas, o saldo é débito (positivo no nosso cálculo)
                    valor = saldo
                    
                    # Buscar nome no plano de contas
                    nome_conta = "Conta Desconhecida"
                    for classe, classe_info in self.plano_contas.items():
                        if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                            nome_conta = classe_info['contas'][codigo_conta]['nome']
                            break
                    
                    dados_despesas.append([codigo_conta, nome_conta, f"Kz {valor:,.2f}"])
                    total_despesas += valor
            
            dados_despesas.append(["", "Total de Despesas", f"Kz {total_despesas:,.2f}"])
            
            # Criar tabela
            tabela_despesas = Table(dados_despesas, colWidths=[1.5*cm, 11.5*cm, 4*cm])
            tabela_despesas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_despesas)
            elementos.append(Spacer(1, 0.5*cm))
            
            # Resultado
            elementos.append(Paragraph("RESULTADO", estilo_subtitulo))
            resultado_liquido = total_receitas - total_despesas
            dados_resultado = [
                ["Descrição", "Valor"],
                ["Total de Receitas", f"Kz {total_receitas:,.2f}"],
                ["Total de Despesas", f"Kz {total_despesas:,.2f}"],
                ["Resultado Líquido do Exercício", f"Kz {resultado_liquido:,.2f}"]
            ]
            
            tabela_resultado = Table(dados_resultado, colWidths=[13*cm, 4*cm])
            tabela_resultado.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_resultado)
            
            # Gerar PDF
            doc.build(elementos)
            
            return True
        except Exception as e:
            print(f"Erro ao gerar DRE: {str(e)}")
            return False

    def gerar_livro_razao(self, data_inicio, data_fim, caminho_saida):
        """
        Gera o Livro Razão para um período específico
        Args:
            data_inicio: Data de início do período
            data_fim: Data de fim do período
            caminho_saida: Caminho do arquivo PDF de saída
        Returns:
            bool: True se gerado com sucesso, False caso contrário
        """
        try:
            # Converter dados para lançamentos contábeis se necessário
            self.converter_dados_para_lancamentos()
            
            # Filtrar lançamentos do período
            lancamentos_filtrados = [l for l in self.lancamentos
                                    if data_inicio <= l['data'] <= data_fim]
            
            # Ordenar por data
            lancamentos_filtrados.sort(key=lambda x: x['data'])
            
            # Agrupar movimentos por conta
            contas = {}
            for lancamento in lancamentos_filtrados:
                for movimento in lancamento['movimentos']:
                    conta = movimento['conta']
                    if conta not in contas:
                        contas[conta] = []
                    
                    contas[conta].append({
                        'data': lancamento['data'],
                        'descricao': lancamento['descricao'],
                        'lancamento_id': lancamento['id'],
                        'debito': movimento['debito'],
                        'credito': movimento['credito']
                    })
            
            # Criar documento PDF
            doc = SimpleDocTemplate(caminho_saida, pagesize=A4)
            elementos = []
            
            # Estilos
            estilos = getSampleStyleSheet()
            estilo_titulo = estilos['Heading1']
            estilo_subtitulo = estilos['Heading2']
            estilo_normal = estilos['Normal']
            
            # Título
            elementos.append(Paragraph("Livro Razão", estilo_titulo))
            elementos.append(Paragraph(f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}", estilo_normal))
            elementos.append(Spacer(1, 0.5*cm))
            
            # Gerar razão para cada conta
            for conta, movimentos in sorted(contas.items()):
                # Buscar nome no plano de contas
                nome_conta = "Conta Desconhecida"
                for classe, classe_info in self.plano_contas.items():
                    if 'contas' in classe_info and conta in classe_info['contas']:
                        nome_conta = classe_info['contas'][conta]['nome']
                        break
                
                elementos.append(Paragraph(f"Conta: {conta} - {nome_conta}", estilo_subtitulo))
                
                # Tabela de movimentos
                dados_movimentos = [["Data", "Descrição", "Lançamento", "Débito", "Crédito", "Saldo"]]
                saldo = 0
                
                for movimento in movimentos:
                    saldo += movimento['debito'] - movimento['credito']
                    dados_movimentos.append([
                        movimento['data'].strftime('%d/%m/%Y'),
                        movimento['descricao'],
                        movimento['lancamento_id'],
                        f"Kz {movimento['debito']:,.2f}" if movimento['debito'] > 0 else "",
                        f"Kz {movimento['credito']:,.2f}" if movimento['credito'] > 0 else "",
                        f"Kz {saldo:,.2f}"
                    ])
                
                # Adicionar linha de total
                total_debitos = sum(m['debito'] for m in movimentos)
                total_creditos = sum(m['credito'] for m in movimentos)
                dados_movimentos.append([
                    "",
                    "TOTAIS",
                    "",
                    f"Kz {total_debitos:,.2f}",
                    f"Kz {total_creditos:,.2f}",
                    f"Kz {saldo:,.2f}"
                ])
                
                # Criar tabela
                tabela_movimentos = Table(dados_movimentos, colWidths=[2*cm, 6*cm, 2*cm, 3*cm, 3*cm, 3*cm])
                tabela_movimentos.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('ALIGN', (3, 1), (5, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elementos.append(tabela_movimentos)
                elementos.append(Spacer(1, 0.5*cm))
            
            # Gerar PDF
            doc.build(elementos)
            
            return True
        except Exception as e:
            print(f"Erro ao gerar livro razão: {str(e)}")
            return False

    def gerar_racu(self, ano, caminho_saida):
        """
        Gera o Relatório Anual de Contas Único (RAÇU) para um ano específico
        Args:
            ano: Ano do relatório
            caminho_saida: Caminho do arquivo PDF de saída
        Returns:
            bool: True se gerado com sucesso, False caso contrário
        """
        try:
            # Converter dados para lançamentos contábeis se necessário
            self.converter_dados_para_lancamentos()
            
            # Definir período
            data_inicio = datetime(ano, 1, 1)
            data_fim = datetime(ano, 12, 31)
            
            # Filtrar lançamentos do período
            lancamentos_filtrados = [l for l in self.lancamentos
                                    if data_inicio <= l['data'] <= data_fim]
            
            # Calcular saldos das contas
            saldos = {}
            for lancamento in lancamentos_filtrados:
                for movimento in lancamento['movimentos']:
                    conta = movimento['conta']
                    if conta not in saldos:
                        saldos[conta] = 0
                    saldos[conta] += movimento['debito'] - movimento['credito']
            
            # Calcular resultado do exercício
            resultado_liquido = 0
            for codigo_conta, saldo in saldos.items():
                if codigo_conta.startswith('6'):  # Despesas
                    resultado_liquido -= saldo
                elif codigo_conta.startswith('7'):  # Receitas
                    resultado_liquido += -saldo  # Receitas têm saldo credor (negativo)
            
            # Criar documento PDF
            doc = SimpleDocTemplate(caminho_saida, pagesize=A4)
            elementos = []
            
            # Estilos
            estilos = getSampleStyleSheet()
            estilo_titulo = estilos['Heading1']
            estilo_subtitulo = estilos['Heading2']
            estilo_normal = estilos['Normal']
            
            # Título
            elementos.append(Paragraph("Relatório Anual de Contas Único (RAÇU)", estilo_titulo))
            elementos.append(Paragraph(f"Exercício: {ano}", estilo_normal))
            elementos.append(Spacer(1, 0.5*cm))
            
            # 1. Identificação da Entidade
            elementos.append(Paragraph("1. IDENTIFICAÇÃO DA ENTIDADE", estilo_subtitulo))
            
            # Dados da empresa (fictícios)
            dados_empresa = [
                ["Nome da Empresa", "Empresa Angolana de Exemplo, Lda."],
                ["NIF", "5417623890"],
                ["Endereço", "Rua Principal, 123, Luanda"],
                ["Telefone", "+244 923 456 789"],
                ["E-mail", "contato@empresaangolana.co.ao"],
                ["Atividade Principal", "Comércio e Serviços"]
            ]
            
            tabela_empresa = Table(dados_empresa, colWidths=[5*cm, 12*cm])
            tabela_empresa.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('PADDING', (0, 0), (-1, -1), 6)
            ]))
            
            elementos.append(tabela_empresa)
            elementos.append(Spacer(1, 0.3*cm))
            
            # 2. Demonstrações Financeiras
            elementos.append(Paragraph("2. DEMONSTRAÇÕES FINANCEIRAS", estilo_subtitulo))
            
            # 2.1 Balanço Patrimonial
            elementos.append(Paragraph("2.1 Balanço Patrimonial", estilo_normal))
            
            # Ativo
            dados_balanco_ativo = [["ATIVO", ""]]
            total_ativo = 0
            
            # Adicionar contas do ativo
            for classe in ["1", "2", "3", "4"]:
                if classe in self.plano_contas:
                    classe_info = self.plano_contas[classe]
                    for codigo_conta, conta_info in classe_info.get('contas', {}).items():
                        if codigo_conta in saldos and (conta_info['tipo'] == 'ativo' or
                                                     (conta_info['tipo'] == 'misto' and saldos[codigo_conta] > 0)):
                            saldo = saldos[codigo_conta]
                            
                            # Ajustar para contas retificadoras
                            if conta_info['natureza'] == 'credora':
                                saldo = -saldo
                            
                            dados_balanco_ativo.append([f"{codigo_conta} - {conta_info['nome']}", f"Kz {abs(saldo):,.2f}"])
                            total_ativo += saldo
            
            # Adicionar total
            dados_balanco_ativo.append(["TOTAL DO ATIVO", f"Kz {total_ativo:,.2f}"])
            
            # Passivo e Capital Próprio
            dados_balanco_passivo = [["PASSIVO E CAPITAL PRÓPRIO", ""]]
            total_passivo_cp = 0
            
            # Adicionar contas do passivo e capital próprio
            for classe in ["3", "5"]:
                if classe in self.plano_contas:
                    classe_info = self.plano_contas[classe]
                    for codigo_conta, conta_info in classe_info.get('contas', {}).items():
                        if codigo_conta in saldos and (conta_info['tipo'] == 'passivo' or
                                                     (conta_info['tipo'] == 'misto' and saldos[codigo_conta] < 0) or
                                                     conta_info['tipo'] == 'capital'):
                            saldo = saldos[codigo_conta]
                            
                            # Ajustar para contas do passivo (crédito é positivo)
                            if conta_info['natureza'] == 'credora':
                                saldo = -saldo
                            
                            dados_balanco_passivo.append([f"{codigo_conta} - {conta_info['nome']}", f"Kz {abs(saldo):,.2f}"])
                            total_passivo_cp += saldo
            
            # Adicionar resultado do exercício
            dados_balanco_passivo.append(["88 - Resultado Líquido do Exercício", f"Kz {abs(resultado_liquido):,.2f}"])
            total_passivo_cp += resultado_liquido
            
            # Adicionar total
            dados_balanco_passivo.append(["TOTAL DO PASSIVO E CAPITAL PRÓPRIO", f"Kz {total_passivo_cp:,.2f}"])
            
            # Criar tabelas
            tabela_balanco_ativo = Table(dados_balanco_ativo, colWidths=[13*cm, 4*cm])
            tabela_balanco_ativo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            tabela_balanco_passivo = Table(dados_balanco_passivo, colWidths=[13*cm, 4*cm])
            tabela_balanco_passivo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_balanco_ativo)
            elementos.append(Spacer(1, 0.3*cm))
            elementos.append(tabela_balanco_passivo)
            elementos.append(Spacer(1, 0.5*cm))
            
            # 2.2 Demonstração de Resultados
            elementos.append(Paragraph("2.2 Demonstração de Resultados", estilo_normal))
            
            dados_dre = [["DEMONSTRAÇÃO DE RESULTADOS", ""]]
            
            # Receitas
            total_receitas = 0
            for codigo_conta, saldo in saldos.items():
                if codigo_conta.startswith('7'):  # Receitas
                    # Para receitas, o saldo é crédito (negativo no nosso cálculo)
                    valor = -saldo
                    
                    # Buscar nome no plano de contas
                    nome_conta = "Conta Desconhecida"
                    for classe, classe_info in self.plano_contas.items():
                        if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                            nome_conta = classe_info['contas'][codigo_conta]['nome']
                            break
                    
                    dados_dre.append([f"{codigo_conta} - {nome_conta}", f"Kz {valor:,.2f}"])
                    total_receitas += valor
            
            dados_dre.append(["Total de Receitas", f"Kz {total_receitas:,.2f}"])
            
            # Despesas
            total_despesas = 0
            for codigo_conta, saldo in saldos.items():
                if codigo_conta.startswith('6'):  # Despesas
                    # Para despesas, o saldo é débito (positivo no nosso cálculo)
                    valor = saldo
                    
                    # Buscar nome no plano de contas
                    nome_conta = "Conta Desconhecida"
                    for classe, classe_info in self.plano_contas.items():
                        if 'contas' in classe_info and codigo_conta in classe_info['contas']:
                            nome_conta = classe_info['contas'][codigo_conta]['nome']
                            break
                    
                    dados_dre.append([f"{codigo_conta} - {nome_conta}", f"Kz {valor:,.2f}"])
                    total_despesas += valor
            
            dados_dre.append(["Total de Despesas", f"Kz {total_despesas:,.2f}"])
            
            # Resultado
            dados_dre.append(["Resultado Líquido do Exercício", f"Kz {resultado_liquido:,.2f}"])
            
            # Criar tabela
            tabela_dre = Table(dados_dre, colWidths=[13*cm, 4*cm])
            tabela_dre.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_dre)
            elementos.append(Spacer(1, 0.5*cm))
            
            # 3. Notas às Demonstrações Financeiras
            elementos.append(Paragraph("3. NOTAS ÀS DEMONSTRAÇÕES FINANCEIRAS", estilo_subtitulo))
            
            # Políticas contábeis
            elementos.append(Paragraph("3.1 Políticas Contábeis", estilo_normal))
            elementos.append(Paragraph("As demonstrações financeiras foram preparadas de acordo com o Plano Geral de Contabilidade Angolano (PGCA) e apresentam a posição financeira, o desempenho financeiro e os fluxos de caixa da entidade.", estilo_normal))
            elementos.append(Spacer(1, 0.3*cm))
            
            # Imobilizações
            elementos.append(Paragraph("3.2 Imobilizações", estilo_normal))
            
            # Tabela de bens amortizáveis
            if self.bens_amortizaveis:
                dados_bens = [["Código", "Descrição", "Valor Original", "Amortização Acumulada", "Valor Líquido"]]
                
                for bem in self.bens_amortizaveis:
                    amortizacao_acumulada = sum(a['valor'] for a in bem.get('amortizacoes', [])
                                              if a['data'].year <= ano)
                    valor_liquido = bem['valor'] - amortizacao_acumulada
                    
                    dados_bens.append([
                        bem['codigo'],
                        bem['descricao'],
                        f"Kz {bem['valor']:,.2f}",
                        f"Kz {amortizacao_acumulada:,.2f}",
                        f"Kz {valor_liquido:,.2f}"
                    ])
                
                tabela_bens = Table(dados_bens, colWidths=[2*cm, 6*cm, 3*cm, 3*cm, 3*cm])
                tabela_bens.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elementos.append(tabela_bens)
            else:
                elementos.append(Paragraph("Não há imobilizações registradas para o período.", estilo_normal))
            
            elementos.append(Spacer(1, 0.3*cm))
            
            # 4. Declaração de Responsabilidade
            elementos.append(Paragraph("4. DECLARAÇÃO DE RESPONSABILIDADE", estilo_subtitulo))
            elementos.append(Paragraph("Os administradores declaram que as demonstrações financeiras apresentam de forma verdadeira e apropriada a posição financeira da entidade em 31 de dezembro de " + str(ano) + " e o resultado das suas operações para o exercício findo naquela data.", estilo_normal))
            elementos.append(Spacer(1, 1*cm))
            
            # Assinaturas
            elementos.append(Paragraph("_______________________________", estilo_normal))
            elementos.append(Paragraph("Diretor Financeiro", estilo_normal))
            elementos.append(Spacer(1, 0.5*cm))
            elementos.append(Paragraph("_______________________________", estilo_normal))
            elementos.append(Paragraph("Contabilista Certificado", estilo_normal))
            
            # Gerar PDF
            doc.build(elementos)
            
            return True
        except Exception as e:
            print(f"Erro ao gerar RAÇU: {str(e)}")
            return False

    def gerar_fluxo_caixa(self, data_inicio, data_fim, caminho_saida):
        """
        Gera a Demonstração dos Fluxos de Caixa para um período específico
        Args:
            data_inicio: Data de início do período
            data_fim: Data de fim do período
            caminho_saida: Caminho do arquivo PDF de saída
        Returns:
            bool: True se gerado com sucesso, False caso contrário
        """
        try:
            # Converter dados para lançamentos contábeis se necessário
            self.converter_dados_para_lancamentos()
            
            # Filtrar lançamentos do período
            lancamentos_filtrados = [l for l in self.lancamentos
                                    if data_inicio <= l['data'] <= data_fim]
            
            # Classificar lançamentos por tipo de atividade
            atividades_operacionais = []
            atividades_investimento = []
            atividades_financiamento = []
            
            for lancamento in lancamentos_filtrados:
                # Classificação simplificada baseada nas contas envolvidas
                tipo_atividade = None
                
                for movimento in lancamento['movimentos']:
                    conta = movimento['conta']
                    
                    # Contas de resultado (6 e 7) e algumas de ativo circulante (2, 3, 4) são operacionais
                    if conta.startswith(('6', '7', '2', '3', '4')):
                        tipo_atividade = 'operacional'
                        break
                    
                    # Contas de imobilizado (1) são de investimento
                    elif conta.startswith('1'):
                        tipo_atividade = 'investimento'
                        break
                    
                    # Contas de capital (5) e empréstimos (33) são de financiamento
                    elif conta.startswith('5') or conta.startswith('33'):
                        tipo_atividade = 'financiamento'
                        break
                
                # Se não foi possível classificar, considerar operacional
                if tipo_atividade is None:
                    tipo_atividade = 'operacional'
                
                # Calcular valor líquido do lançamento
                valor_liquido = 0
                for movimento in lancamento['movimentos']:
                    if movimento['conta'].startswith(('4')):  # Contas de caixa e bancos
                        valor_liquido += movimento['debito'] - movimento['credito']
                
                # Adicionar à lista correspondente
                item = {
                    'data': lancamento['data'],
                    'descricao': lancamento['descricao'],
                    'valor': valor_liquido
                }
                
                if tipo_atividade == 'operacional':
                    atividades_operacionais.append(item)
                elif tipo_atividade == 'investimento':
                    atividades_investimento.append(item)
                elif tipo_atividade == 'financiamento':
                    atividades_financiamento.append(item)
            
            # Calcular totais
            total_operacional = sum(item['valor'] for item in atividades_operacionais)
            total_investimento = sum(item['valor'] for item in atividades_investimento)
            total_financiamento = sum(item['valor'] for item in atividades_financiamento)
            
            # Variação de caixa
            variacao_caixa = total_operacional + total_investimento + total_financiamento
            
            # Criar documento PDF
            doc = SimpleDocTemplate(caminho_saida, pagesize=A4)
            elementos = []
            
            # Estilos
            estilos = getSampleStyleSheet()
            estilo_titulo = estilos['Heading1']
            estilo_subtitulo = estilos['Heading2']
            estilo_normal = estilos['Normal']
            
            # Título
            elementos.append(Paragraph("Demonstração dos Fluxos de Caixa", estilo_titulo))
            elementos.append(Paragraph(f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}", estilo_normal))
            elementos.append(Spacer(1, 0.5*cm))
            
            # 1. Fluxos de Caixa das Atividades Operacionais
            elementos.append(Paragraph("1. FLUXOS DE CAIXA DAS ATIVIDADES OPERACIONAIS", estilo_subtitulo))
            
            dados_operacionais = [["Data", "Descrição", "Valor"]]
            for item in atividades_operacionais:
                dados_operacionais.append([
                    item['data'].strftime('%d/%m/%Y'),
                    item['descricao'],
                    f"Kz {item['valor']:,.2f}"
                ])
            
            dados_operacionais.append(["", "Total das Atividades Operacionais", f"Kz {total_operacional:,.2f}"])
            
            tabela_operacionais = Table(dados_operacionais, colWidths=[2.5*cm, 11.5*cm, 3*cm])
            tabela_operacionais.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_operacionais)
            elementos.append(Spacer(1, 0.5*cm))
            
            # 2. Fluxos de Caixa das Atividades de Investimento
            elementos.append(Paragraph("2. FLUXOS DE CAIXA DAS ATIVIDADES DE INVESTIMENTO", estilo_subtitulo))
            
            if atividades_investimento:
                dados_investimento = [["Data", "Descrição", "Valor"]]
                for item in atividades_investimento:
                    dados_investimento.append([
                        item['data'].strftime('%d/%m/%Y'),
                        item['descricao'],
                        f"Kz {item['valor']:,.2f}"
                    ])
                
                dados_investimento.append(["", "Total das Atividades de Investimento", f"Kz {total_investimento:,.2f}"])
                
                tabela_investimento = Table(dados_investimento, colWidths=[2.5*cm, 11.5*cm, 3*cm])
                tabela_investimento.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elementos.append(tabela_investimento)
            else:
                elementos.append(Paragraph("Não houve fluxos de caixa das atividades de investimento no período.", estilo_normal))
            
            elementos.append(Spacer(1, 0.5*cm))
            
            # 3. Fluxos de Caixa das Atividades de Financiamento
            elementos.append(Paragraph("3. FLUXOS DE CAIXA DAS ATIVIDADES DE FINANCIAMENTO", estilo_subtitulo))
            
            if atividades_financiamento:
                dados_financiamento = [["Data", "Descrição", "Valor"]]
                for item in atividades_financiamento:
                    dados_financiamento.append([
                        item['data'].strftime('%d/%m/%Y'),
                        item['descricao'],
                        f"Kz {item['valor']:,.2f}"
                    ])
                
                dados_financiamento.append(["", "Total das Atividades de Financiamento", f"Kz {total_financiamento:,.2f}"])
                
                tabela_financiamento = Table(dados_financiamento, colWidths=[2.5*cm, 11.5*cm, 3*cm])
                tabela_financiamento.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elementos.append(tabela_financiamento)
            else:
                elementos.append(Paragraph("Não houve fluxos de caixa das atividades de financiamento no período.", estilo_normal))
            
            elementos.append(Spacer(1, 0.5*cm))
            
            # 4. Resumo
            elementos.append(Paragraph("4. RESUMO DOS FLUXOS DE CAIXA", estilo_subtitulo))
            
            dados_resumo = [
                ["Descrição", "Valor"],
                ["Fluxos de Caixa das Atividades Operacionais", f"Kz {total_operacional:,.2f}"],
                ["Fluxos de Caixa das Atividades de Investimento", f"Kz {total_investimento:,.2f}"],
                ["Fluxos de Caixa das Atividades de Financiamento", f"Kz {total_financiamento:,.2f}"],
                ["Variação de Caixa e Equivalentes no Período", f"Kz {variacao_caixa:,.2f}"]
            ]
            
            tabela_resumo = Table(dados_resumo, colWidths=[14*cm, 3*cm])
            tabela_resumo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabela_resumo)
            
            # Gerar PDF
            doc.build(elementos)
            
            return True
        except Exception as e:
            print(f"Erro ao gerar fluxo de caixa: {str(e)}")
            return False

    def calcular_amortizacoes(self, data_referencia):
        """
        Calcula as amortizações dos bens até uma data de referência
        Args:
            data_referencia: Data de referência para o cálculo
        Returns:
            list: Lista de amortizações calculadas
        """
        amortizacoes = []
        
        for bem in self.bens_amortizaveis:
            # Verificar se o bem foi adquirido antes da data de referência
            if bem['data'] > data_referencia:
                continue
            
            # Calcular valor amortizável
            valor_amortizavel = bem['valor'] - bem['valor_residual']
            
            # Calcular taxa anual de amortização
            taxa_anual = 1 / bem['vida_util']
            
            # Calcular valor anual de amortização
            valor_anual = valor_amortizavel * taxa_anual
            
            # Calcular amortizações até a data de referência
            data_inicio = bem['data']
            anos_completos = (data_referencia.year - data_inicio.year)
            
            # Ajustar para anos parciais
            if data_referencia.month < data_inicio.month or (data_referencia.month == data_inicio.month and data_referencia.day < data_inicio.day):
                anos_completos -= 1
            
            # Limitar ao número de anos da vida útil
            anos_completos = min(anos_completos, bem['vida_util'])
            
            # Verificar amortizações já registradas
            anos_registrados = set()
            for amort in bem.get('amortizacoes', []):
                anos_registrados.add(amort['data'].year)
            
            # Registrar amortizações para anos ainda não registrados
            for ano in range(data_inicio.year, data_inicio.year + anos_completos + 1):
                if ano not in anos_registrados:
                    # Para o primeiro ano, calcular proporcionalmente aos meses restantes
                    if ano == data_inicio.year:
                        meses_restantes = 12 - data_inicio.month + 1
                        valor = valor_anual * (meses_restantes / 12)
                    # Para o último ano (se for o ano da data de referência), calcular proporcionalmente
                    elif ano == data_referencia.year:
                        meses_decorridos = data_referencia.month
                        valor = valor_anual * (meses_decorridos / 12)
                    # Para anos completos intermediários
                    else:
                        valor = valor_anual
                    
                    # Criar registro de amortização
                    amortizacao = {
                        'bem_codigo': bem['codigo'],
                        'data': datetime(ano, 12, 31),  # Último dia do ano
                        'valor': valor,
                        'acumulada': sum(a['valor'] for a in bem.get('amortizacoes', [])
                                       if a['data'].year < ano) + valor
                    }
                    
                    amortizacoes.append(amortizacao)
                    
                    # Adicionar à lista de amortizações do bem
                    if 'amortizacoes' not in bem:
                        bem['amortizacoes'] = []
                    
                    bem['amortizacoes'].append({
                        'data': datetime(ano, 12, 31),
                        'valor': valor
                    })
                    
                    # Registrar lançamento contábil
                    self.registrar_lancamento(
                        datetime(ano, 12, 31),
                        f"Amortização anual de {bem['descricao']}",
                        [
                            {'conta': '66', 'debito': valor, 'credito': 0},  # Débito em Amortizações do Exercício
                            {'conta': '19', 'debito': 0, 'credito': valor}   # Crédito em Amortizações Acumuladas
                        ]
                    )
        
        # Salvar dados atualizados
        self.salvar_dados()
        
        return amortizacoes

    def carregar_plano_contas(self):
        """
        Carrega o plano de contas angolano
        Returns:
            dict: Plano de contas estruturado
        """
        # Plano de contas baseado no PGCA (Plano Geral de Contabilidade Angolano)
        return {
            "1": {
                "nome": "Meios Fixos e Investimentos",
                "contas": {
                    "11": {"nome": "Imobilizações Corpóreas", "tipo": "ativo", "natureza": "devedora"},
                    "12": {"nome": "Imobilizações Incorpóreas", "tipo": "ativo", "natureza": "devedora"},
                    "13": {"nome": "Investimentos Financeiros", "tipo": "ativo", "natureza": "devedora"},
                    "14": {"nome": "Obras em Curso", "tipo": "ativo", "natureza": "devedora"},
                    "15": {"nome": "Empréstimos de Financiamento", "tipo": "ativo", "natureza": "devedora"},
                    "19": {"nome": "Amortizações Acumuladas", "tipo": "ativo", "natureza": "credora"}
                }
            },
            "2": {
                "nome": "Existências",
                "contas": {
                    "21": {"nome": "Compras", "tipo": "ativo", "natureza": "devedora"},
                    "22": {"nome": "Matérias-primas, Subsidiárias e de Consumo", "tipo": "ativo", "natureza": "devedora"},
                    "23": {"nome": "Produtos e Trabalhos em Curso", "tipo": "ativo", "natureza": "devedora"},
                    "24": {"nome": "Produtos Acabados e Intermédios", "tipo": "ativo", "natureza": "devedora"},
                    "25": {"nome": "Subprodutos, Desperdícios, Resíduos e Refugos", "tipo": "ativo", "natureza": "devedora"},
                    "26": {"nome": "Mercadorias", "tipo": "ativo", "natureza": "devedora"},
                    "27": {"nome": "Matérias-primas, Mercadorias e Outros Materiais em Trânsito", "tipo": "ativo", "natureza": "devedora"},
                    "28": {"nome": "Adiantamentos por Conta de Compras", "tipo": "ativo", "natureza": "devedora"},
                    "29": {"nome": "Provisões para Depreciação de Existências", "tipo": "ativo", "natureza": "credora"}
                }
            },
            "3": {
                "nome": "Terceiros",
                "contas": {
                    "31": {"nome": "Clientes", "tipo": "ativo", "natureza": "devedora"},
                    "32": {"nome": "Fornecedores", "tipo": "passivo", "natureza": "credora"},
                    "33": {"nome": "Empréstimos", "tipo": "passivo", "natureza": "credora"},
                    "34": {"nome": "Estado", "tipo": "misto", "natureza": "misto"},
                    "35": {"nome": "Entidades Participantes e Participadas", "tipo": "misto", "natureza": "misto"},
                    "36": {"nome": "Pessoal", "tipo": "misto", "natureza": "misto"},
                    "37": {"nome": "Outros Valores a Receber e a Pagar", "tipo": "misto", "natureza": "misto"},
                    "38": {"nome": "Provisões para Cobranças Duvidosas", "tipo": "ativo", "natureza": "credora"},
                    "39": {"nome": "Provisões para Outros Riscos e Encargos", "tipo": "passivo", "natureza": "credora"}
                }
            },
            "4": {
                "nome": "Meios Monetários",
                "contas": {
                    "41": {"nome": "Títulos Negociáveis", "tipo": "ativo", "natureza": "devedora"},
                    "42": {"nome": "Depósitos a Prazo", "tipo": "ativo", "natureza": "devedora"},
                    "43": {"nome": "Depósitos à Ordem", "tipo": "ativo", "natureza": "devedora"},
                    "44": {"nome": "Outros Depósitos", "tipo": "ativo", "natureza": "devedora"},
                    "45": {"nome": "Caixa", "tipo": "ativo", "natureza": "devedora"},
                    "46": {"nome": "Conta no Exterior", "tipo": "ativo", "natureza": "devedora"},
                    "48": {"nome": "Conta de Regularização", "tipo": "misto", "natureza": "misto"},
                    "49": {"nome": "Provisões para Aplicações de Tesouraria", "tipo": "ativo", "natureza": "credora"}
                }
            },
            "5": {
                "nome": "Capital e Reservas",
                "contas": {
                    "51": {"nome": "Capital", "tipo": "capital", "natureza": "credora"},
                    "52": {"nome": "Ações/Quotas Próprias", "tipo": "capital", "natureza": "devedora"},
                    "53": {"nome": "Prémios de Emissão", "tipo": "capital", "natureza": "credora"},
                    "54": {"nome": "Prestações Suplementares", "tipo": "capital", "natureza": "credora"},
                    "55": {"nome": "Reservas Legais", "tipo": "capital", "natureza": "credora"},
                    "56": {"nome": "Reservas de Reavaliação", "tipo": "capital", "natureza": "credora"},
                    "57": {"nome": "Reservas com Fins Especiais", "tipo": "capital", "natureza": "credora"},
                    "58": {"nome": "Reservas Livres", "tipo": "capital", "natureza": "credora"},
                    "59": {"nome": "Resultados Transitados", "tipo": "capital", "natureza": "misto"}
                }
            },
            "6": {
                "nome": "Custos e Perdas",
                "contas": {
                    "61": {"nome": "Custos das Mercadorias Vendidas e das Matérias Consumidas", "tipo": "resultado", "natureza": "devedora"},
                    "62": {"nome": "Fornecimentos e Serviços de Terceiros", "tipo": "resultado", "natureza": "devedora"},
                    "63": {"nome": "Impostos", "tipo": "resultado", "natureza": "devedora"},
                    "64": {"nome": "Custos com o Pessoal", "tipo": "resultado", "natureza": "devedora"},
                    "65": {"nome": "Despesas Financeiras", "tipo": "resultado", "natureza": "devedora"},
                    "66": {"nome": "Amortizações do Exercício", "tipo": "resultado", "natureza": "devedora"},
                    "67": {"nome": "Provisões do Exercício", "tipo": "resultado", "natureza": "devedora"},
                    "68": {"nome": "Custos e Perdas Extraordinários", "tipo": "resultado", "natureza": "devedora"},
                    "69": {"nome": "Outros Custos e Perdas Operacionais", "tipo": "resultado", "natureza": "devedora"}
                }
            },
            "7": {
                "nome": "Proveitos e Ganhos",
                "contas": {
                    "71": {"nome": "Vendas", "tipo": "resultado", "natureza": "credora"},
                    "72": {"nome": "Prestações de Serviços", "tipo": "resultado", "natureza": "credora"},
                    "73": {"nome": "Impostos e Taxas", "tipo": "resultado", "natureza": "credora"},
                    "74": {"nome": "Subsídios à Exploração", "tipo": "resultado", "natureza": "credora"},
                    "75": {"nome": "Receitas Financeiras", "tipo": "resultado", "natureza": "credora"},
                    "76": {"nome": "Receitas de Imobilizações", "tipo": "resultado", "natureza": "credora"},
                    "77": {"nome": "Reversões de Amortizações e Provisões", "tipo": "resultado", "natureza": "credora"},
                    "78": {"nome": "Proveitos e Ganhos Extraordinários", "tipo": "resultado", "natureza": "credora"},
                    "79": {"nome": "Outros Proveitos e Ganhos Operacionais", "tipo": "resultado", "natureza": "credora"}
                }
            },
            "8": {
                "nome": "Resultados",
                "contas": {
                    "81": {"nome": "Resultados Operacionais", "tipo": "resultado", "natureza": "misto"},
                    "82": {"nome": "Resultados Financeiros", "tipo": "resultado", "natureza": "misto"},
                    "83": {"nome": "Resultados Correntes", "tipo": "resultado", "natureza": "misto"},
                    "84": {"nome": "Resultados Extraordinários", "tipo": "resultado", "natureza": "misto"},
                    "85": {"nome": "Resultados Antes de Impostos", "tipo": "resultado", "natureza": "misto"},
                    "86": {"nome": "Imposto Sobre o Rendimento", "tipo": "resultado", "natureza": "devedora"},
                    "88": {"nome": "Resultado Líquido do Exercício", "tipo": "resultado", "natureza": "misto"}
                }
            }
        }