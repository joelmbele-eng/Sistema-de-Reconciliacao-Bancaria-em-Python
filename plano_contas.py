import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import json
import os

class PlanoContasAngolano:
    """Implementa o plano de contas conforme PGCA (Plano Geral de Contabilidade Angolano)"""
    
    def __init__(self, app):
        self.app = app
        self.contas = {}
        self.arquivo_contas = "plano_contas_pgca.json"
        self.carregar_plano_contas()
    
    def carregar_plano_contas(self):
        """Carrega o plano de contas do arquivo ou cria um novo com a estrutura básica"""
        if os.path.exists(self.arquivo_contas):
            try:
                with open(self.arquivo_contas, 'r', encoding='utf-8') as f:
                    self.contas = json.load(f)
            except:
                self.criar_plano_padrao()
        else:
            self.criar_plano_padrao()
    
    def salvar_plano_contas(self):
        """Salva o plano de contas no arquivo"""
        with open(self.arquivo_contas, 'w', encoding='utf-8') as f:
            json.dump(self.contas, f, ensure_ascii=False, indent=4)
    
    def criar_plano_padrao(self):
        """Cria a estrutura básica do plano de contas PGCA"""
        self.contas = {
            # Classe 1 - Meios Fixos e Investimentos
            "1": {
                "nome": "Meios Fixos e Investimentos",
                "subcontas": {
                    "11": {"nome": "Imobilizações Corpóreas", "subcontas": {}},
                    "12": {"nome": "Imobilizações Incorpóreas", "subcontas": {}},
                    "13": {"nome": "Investimentos Financeiros", "subcontas": {}},
                    "14": {"nome": "Imobilizações em Curso", "subcontas": {}},
                    "19": {"nome": "Amortizações Acumuladas", "subcontas": {}}
                }
            },
            # Classe 2 - Existências
            "2": {
                "nome": "Existências",
                "subcontas": {
                    "21": {"nome": "Compras", "subcontas": {}},
                    "22": {"nome": "Matérias-Primas, Subsidiárias e de Consumo", "subcontas": {}},
                    "23": {"nome": "Produtos e Trabalhos em Curso", "subcontas": {}},
                    "24": {"nome": "Produtos Acabados e Intermédios", "subcontas": {}},
                    "25": {"nome": "Subprodutos, Desperdícios, Resíduos e Refugos", "subcontas": {}},
                    "26": {"nome": "Mercadorias", "subcontas": {}},
                    "26": {"nome": "Mercadorias", "subcontas": {}},
                    "27": {"nome": "Matérias-Primas, Mercadorias e Outros Materiais em Trânsito", "subcontas": {}},
                    "28": {"nome": "Adiantamentos por Conta de Compras", "subcontas": {}},
                    "29": {"nome": "Provisões para Depreciação de Existências", "subcontas": {}}
                }
            },
            # Classe 3 - Terceiros
            "3": {
                "nome": "Terceiros",
                "subcontas": {
                    "31": {"nome": "Clientes", "subcontas": {}},
                    "32": {"nome": "Fornecedores", "subcontas": {}},
                    "33": {"nome": "Empréstimos", "subcontas": {}},
                    "34": {"nome": "Estado", "subcontas": {}},
                    "35": {"nome": "Entidades Participantes e Participadas", "subcontas": {}},
                    "36": {"nome": "Pessoal", "subcontas": {}},
                    "37": {"nome": "Outros Valores a Receber e a Pagar", "subcontas": {}},
                    "38": {"nome": "Provisões para Cobranças Duvidosas", "subcontas": {}},
                    "39": {"nome": "Provisões para Outros Riscos e Encargos", "subcontas": {}}
                }
            },
            # Classe 4 - Meios Monetários
            "4": {
                "nome": "Meios Monetários",
                "subcontas": {
                    "41": {"nome": "Títulos Negociáveis", "subcontas": {}},
                    "42": {"nome": "Depósitos a Prazo", "subcontas": {}},
                    "43": {"nome": "Depósitos à Ordem", "subcontas": {}},
                    "44": {"nome": "Outros Depósitos", "subcontas": {}},
                    "45": {"nome": "Caixa", "subcontas": {}},
                    "46": {"nome": "Outros Valores Monetários", "subcontas": {}}
                }
            },
            # Classe 5 - Capital e Reservas
            "5": {
                "nome": "Capital e Reservas",
                "subcontas": {
                    "51": {"nome": "Capital", "subcontas": {}},
                    "52": {"nome": "Acções/Quotas Próprias", "subcontas": {}},
                    "53": {"nome": "Prémios de Emissão", "subcontas": {}},
                    "54": {"nome": "Prestações Suplementares", "subcontas": {}},
                    "55": {"nome": "Reservas Legais", "subcontas": {}},
                    "56": {"nome": "Reservas Estatutárias", "subcontas": {}},
                    "57": {"nome": "Reservas Especiais", "subcontas": {}},
                    "58": {"nome": "Reservas Livres", "subcontas": {}},
                    "59": {"nome": "Resultados Transitados", "subcontas": {}}
                }
            },
            # Classe 6 - Custos e Perdas
            "6": {
                "nome": "Custos e Perdas",
                "subcontas": {
                    "61": {"nome": "Custos das Mercadorias Vendidas e das Matérias Consumidas", "subcontas": {}},
                    "62": {"nome": "Fornecimentos e Serviços de Terceiros", "subcontas": {}},
                    "63": {"nome": "Impostos", "subcontas": {}},
                    "64": {"nome": "Custos com o Pessoal", "subcontas": {}},
                    "65": {"nome": "Despesas Financeiras", "subcontas": {}},
                    "66": {"nome": "Outras Despesas Operacionais", "subcontas": {}},
                    "67": {"nome": "Amortizações e Reintegrações do Exercício", "subcontas": {}},
                    "68": {"nome": "Provisões do Exercício", "subcontas": {}},
                    "69": {"nome": "Custos e Perdas Extraordinários", "subcontas": {}}
                }
            },
            # Classe 7 - Proveitos e Ganhos
            "7": {
                "nome": "Proveitos e Ganhos",
                "subcontas": {
                    "71": {"nome": "Vendas", "subcontas": {}},
                    "72": {"nome": "Prestações de Serviços", "subcontas": {}},
                    "73": {"nome": "Impostos e Taxas", "subcontas": {}},
                    "74": {"nome": "Transferências e Subsídios Correntes Obtidos", "subcontas": {}},
                    "75": {"nome": "Receitas Financeiras", "subcontas": {}},
                    "76": {"nome": "Outras Receitas Operacionais", "subcontas": {}},
                    "77": {"nome": "Reversões de Amortizações e Provisões", "subcontas": {}},
                    "78": {"nome": "Proveitos e Ganhos em Filiais e Associadas", "subcontas": {}},
                    "79": {"nome": "Proveitos e Ganhos Extraordinários", "subcontas": {}}
                }
            },
            # Classe 8 - Resultados
            "8": {
                "nome": "Resultados",
                "subcontas": {
                    "81": {"nome": "Resultados Operacionais", "subcontas": {}},
                    "82": {"nome": "Resultados Financeiros", "subcontas": {}},
                    "83": {"nome": "Resultados Correntes", "subcontas": {}},
                    "84": {"nome": "Resultados Extraordinários", "subcontas": {}},
                    "85": {"nome": "Resultados Antes de Impostos", "subcontas": {}},
                    "86": {"nome": "Imposto Sobre o Rendimento", "subcontas": {}},
                    "88": {"nome": "Resultado Líquido do Exercício", "subcontas": {}},
                    "89": {"nome": "Dividendos Antecipados", "subcontas": {}}
                }
            }
        }
        
        # Adicionar algumas subcontas comuns para exemplo
        self.contas["4"]["subcontas"]["43"]["subcontas"]["431"] = {"nome": "Banco A", "subcontas": {}}
        self.contas["4"]["subcontas"]["43"]["subcontas"]["432"] = {"nome": "Banco B", "subcontas": {}}
        self.contas["4"]["subcontas"]["45"]["subcontas"]["451"] = {"nome": "Caixa Sede", "subcontas": {}}
        
        self.salvar_plano_contas()
    
    def abrir_gestor(self):
        """Abre a janela de gestão do plano de contas"""
        janela = tk.Toplevel(self.app.root)
        janela.title("Plano de Contas PGCA")
        janela.geometry("800x600")
        janela.transient(self.app.root)
        
        # Aplicar tema atual
        if hasattr(self.app, 'gerenciador_temas'):
            tema = self.app.gerenciador_temas.apply_theme(janela)
        
        # Frame principal
        frame_principal = ttk.Frame(janela, padding="10")
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame_principal, text="Plano Geral de Contabilidade Angolano", 
                 font=('Helvetica', 16, 'bold')).pack(pady=10)
        
        # Frame de conteúdo dividido
        frame_conteudo = ttk.Frame(frame_principal)
        frame_conteudo.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Árvore de contas
        frame_arvore = ttk.Frame(frame_conteudo)
        frame_arvore.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(frame_arvore, text="Estrutura de Contas").pack(pady=5)
        
        # Criar Treeview
        colunas = ('codigo', 'nome')
        self.arvore_contas = ttk.Treeview(frame_arvore, columns=colunas, show='tree headings')
        self.arvore_contas.heading('codigo', text='Código')
        self.arvore_contas.heading('nome', text='Nome')
        self.arvore_contas.column('codigo', width=100)
        self.arvore_contas.column('nome', width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_arvore, orient=tk.VERTICAL, command=self.arvore_contas.yview)
        self.arvore_contas.configure(yscrollcommand=scrollbar.set)
        
        self.arvore_contas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Carregar contas na árvore
        self.carregar_contas_na_arvore()
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame_conteudo)
        frame_botoes.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        ttk.Button(frame_botoes, text="Adicionar Conta", 
                  command=self.adicionar_conta).pack(fill=tk.X, pady=5)
        ttk.Button(frame_botoes, text="Editar Conta", 
                  command=self.editar_conta).pack(fill=tk.X, pady=5)
        ttk.Button(frame_botoes, text="Excluir Conta", 
                  command=self.excluir_conta).pack(fill=tk.X, pady=5)
        ttk.Separator(frame_botoes, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Button(frame_botoes, text="Exportar Plano", 
                  command=self.exportar_plano).pack(fill=tk.X, pady=5)
        ttk.Button(frame_botoes, text="Importar Plano", 
                  command=self.importar_plano).pack(fill=tk.X, pady=5)
        
    def carregar_contas_na_arvore(self):
        """Carrega as contas na árvore de visualização"""
        # Limpar árvore
        for item in self.arvore_contas.get_children():
            self.arvore_contas.delete(item)
        
        # Adicionar classes principais
        for codigo, classe in self.contas.items():
            classe_id = self.arvore_contas.insert('', 'end', text=codigo, 
                                               values=(codigo, classe['nome']))
            
            # Adicionar subcontas
            self.adicionar_subcontas_na_arvore(classe_id, codigo, classe['subcontas'])
    
    def adicionar_subcontas_na_arvore(self, parent_id, parent_codigo, subcontas):
        """Adiciona subcontas recursivamente na árvore"""
        for codigo, conta in subcontas.items():
            conta_id = self.arvore_contas.insert(parent_id, 'end', text=codigo, 
                                              values=(codigo, conta['nome']))
            
            if 'subcontas' in conta and conta['subcontas']:
                self.adicionar_subcontas_na_arvore(conta_id, codigo, conta['subcontas'])
    
    def adicionar_conta(self):
        """Adiciona uma nova conta ou subconta"""
        item_selecionado = self.arvore_contas.selection()
        
        if not item_selecionado:
            # Adicionar conta principal (classe)
            codigo = simpledialog.askstring("Novo Código", "Digite o código da nova classe:")
            if not codigo:
                return
                
            if codigo in self.contas:
                messagebox.showerror("Erro", "Este código já existe!")
                return
                
            nome = simpledialog.askstring("Nome da Conta", "Digite o nome da nova classe:")
            if not nome:
                return
                
            self.contas[codigo] = {
                "nome": nome,
                "subcontas": {}
            }
        else:
            # Adicionar subconta
            item_id = item_selecionado[0]
            codigo_pai = self.arvore_contas.item(item_id)['values'][0]
            
            # Encontrar a conta pai
            caminho = self.obter_caminho_conta(codigo_pai)
            if not caminho:
                messagebox.showerror("Erro", "Não foi possível encontrar a conta pai!")
                return
                
            # Solicitar código da nova subconta
            codigo = simpledialog.askstring("Novo Código", 
                                          f"Digite o código da nova subconta (pai: {codigo_pai}):")
            if not codigo:
                return
                
            # Verificar se o código já existe
            conta_pai = self.obter_conta_por_caminho(caminho)
            if codigo in conta_pai['subcontas']:
                messagebox.showerror("Erro", "Este código já existe!")
                return
                
            nome = simpledialog.askstring("Nome da Conta", "Digite o nome da nova subconta:")
            if not nome:
                return
                
            # Adicionar subconta
            conta_pai['subcontas'][codigo] = {
                "nome": nome,
                "subcontas": {}
            }
        
        # Salvar e atualizar
        self.salvar_plano_contas()
        self.carregar_contas_na_arvore()
    
    def editar_conta(self):
        """Edita uma conta existente"""
        item_selecionado = self.arvore_contas.selection()
        
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma conta para editar!")
            return
            
        item_id = item_selecionado[0]
        codigo = self.arvore_contas.item(item_id)['values'][0]
        
        # Encontrar a conta
        caminho = self.obter_caminho_conta(codigo)
        if not caminho:
            messagebox.showerror("Erro", "Não foi possível encontrar a conta!")
            return
            
        conta = self.obter_conta_por_caminho(caminho)
        
        # Solicitar novo nome
        novo_nome = simpledialog.askstring("Editar Conta", 
                                         "Digite o novo nome da conta:", 
                                         initialvalue=conta['nome'])
        if not novo_nome:
            return
            
        # Atualizar nome
        conta['nome'] = novo_nome
        
        # Salvar e atualizar
        self.salvar_plano_contas()
        self.carregar_contas_na_arvore()
    
    def excluir_conta(self):
        """Exclui uma conta existente"""
        item_selecionado = self.arvore_contas.selection()
        
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione uma conta para excluir!")
            return
            
        item_id = item_selecionado[0]
        codigo = self.arvore_contas.item(item_id)['values'][0]
        
        # Confirmar exclusão
        if not messagebox.askyesno("Confirmar Exclusão", 
                                 f"Tem certeza que deseja excluir a conta {codigo}?"):
            return
            
        # Encontrar a conta
        caminho = self.obter_caminho_conta(codigo)
        if not caminho:
            messagebox.showerror("Erro", "Não foi possível encontrar a conta!")
            return
            
        # Excluir conta
        if len(caminho) == 1:
            # Conta principal
            del self.contas[caminho[0]]
        else:
            # Subconta
            conta_pai = self.obter_conta_por_caminho(caminho[:-1])
            del conta_pai['subcontas'][caminho[-1]]
        
        # Salvar e atualizar
        self.salvar_plano_contas()
        self.carregar_contas_na_arvore()
    
    def obter_caminho_conta(self, codigo):
        """Obtém o caminho completo para uma conta pelo seu código"""
        # Verificar se é uma conta principal
        if codigo in self.contas:
            return [codigo]
            
        # Buscar nas subcontas
        for classe_codigo, classe in self.contas.items():
            caminho = self.buscar_subconta(classe_codigo, classe['subcontas'], codigo)
            if caminho:
                return caminho
                
        return None
    
    def buscar_subconta(self, parent_codigo, subcontas, codigo_busca):
        """Busca recursivamente uma subconta pelo código"""
        for codigo, conta in subcontas.items():
            if codigo == codigo_busca:
                return [parent_codigo, codigo]
                
            if 'subcontas' in conta and conta['subcontas']:
                caminho = self.buscar_subconta(codigo, conta['subcontas'], codigo_busca)
                if caminho:
                    return [parent_codigo] + caminho
                    
        return None
    
    def obter_conta_por_caminho(self, caminho):
        """Obtém uma conta pelo seu caminho"""
        if not caminho:
            return None
            
        if len(caminho) == 1:
            return self.contas[caminho[0]]
            
        conta = self.contas[caminho[0]]
        for i in range(1, len(caminho)):
            conta = conta['subcontas'][caminho[i]]
            
        return conta
    
    def exportar_plano(self):
        """Exporta o plano de contas para um arquivo Excel"""
        from tkinter import filedialog
        
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if not arquivo:
            return
            
        # Criar DataFrame para exportação
        dados = []
        
        for classe_codigo, classe in self.contas.items():
            dados.append({
                'Código': classe_codigo,
                'Nome': classe['nome'],
                'Nível': 1
            })
            
            self.adicionar_subcontas_para_exportacao(dados, classe_codigo, classe['subcontas'], 2)
            
        df = pd.DataFrame(dados)
        df.to_excel(arquivo, index=False)
        
        messagebox.showinfo("Sucesso", f"Plano de contas exportado para {arquivo}")
    
    def adicionar_subcontas_para_exportacao(self, dados, parent_codigo, subcontas, nivel):
        """Adiciona subcontas ao DataFrame para exportação"""
        for codigo, conta in subcontas.items():
            dados.append({
                'Código': codigo,
                'Nome': conta['nome'],
                'Nível': nivel
            })
            
            if 'subcontas' in conta and conta['subcontas']:
                self.adicionar_subcontas_para_exportacao(
                    dados, codigo, conta['subcontas'], nivel + 1)
    
    def importar_plano(self):
        """Importa o plano de contas de um arquivo Excel"""
        from tkinter import filedialog
        
        arquivo = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if not arquivo:
            return
            
        try:
            df = pd.read_excel(arquivo)
            
            # Verificar colunas necessárias
            if not all(col in df.columns for col in ['Código', 'Nome', 'Nível']):
                messagebox.showerror("Erro", "O arquivo não contém as colunas necessárias!")
                return
                
            # Confirmar substituição
            if not messagebox.askyesno("Confirmar Importação", 
                                     "Isso substituirá o plano de contas atual. Continuar?"):
                return
                
            # Criar novo plano de contas
            novo_plano = {}
            
            # Processar linhas
            for _, row in df.iterrows():
                codigo = str(row['Código'])
                nome = row['Nome']
                nivel = int(row['Nível'])
                
                if nivel == 1:
                    # Conta principal
                    novo_plano[codigo] = {
                        "nome": nome,
                        "subcontas": {}
                    }
                else:
                    # Subconta - encontrar pai
                    partes_codigo = codigo.split('.')
                    if len(partes_codigo) >= 2:
                        codigo_pai = '.'.join(partes_codigo[:-1])
                        caminho_pai = self.obter_caminho_conta_em_plano(novo_plano, codigo_pai)
                        
                        if caminho_pai:
                            conta_pai = self.obter_conta_por_caminho_em_plano(novo_plano, caminho_pai)
                            conta_pai['subcontas'][codigo] = {
                                "nome": nome,
                                "subcontas": {}
                            }
            
            # Substituir plano atual
            self.contas = novo_plano
            self.salvar_plano_contas()
            self.carregar_contas_na_arvore()
            
            messagebox.showinfo("Sucesso", "Plano de contas importado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar: {str(e)}")
    
    def obter_caminho_conta_em_plano(self, plano, codigo):
        """Obtém o caminho de uma conta em um plano específico"""
        # Verificar se é uma conta principal
        if codigo in plano:
            return [codigo]
            
        # Buscar nas subcontas
        for classe_codigo, classe in plano.items():
            caminho = self.buscar_subconta_em_plano(classe_codigo, classe['subcontas'], codigo)
            if caminho:
                return caminho
                
        return None
    
    def buscar_subconta_em_plano(self, parent_codigo, subcontas, codigo_busca):
        """Busca recursivamente uma subconta em um plano específico"""
        for codigo, conta in subcontas.items():
            if codigo == codigo_busca:
                return [parent_codigo, codigo]
                
            if 'subcontas' in conta and conta['subcontas']:
                caminho = self.buscar_subconta_em_plano(codigo, conta['subcontas'], codigo_busca)
                if caminho:
                    return [parent_codigo] + caminho
                    
        return None
    
    def obter_conta_por_caminho_em_plano(self, plano, caminho):
        """Obtém uma conta pelo seu caminho em um plano específico"""
        if not caminho:
            return None
            
        if len(caminho) == 1:
            return plano[caminho[0]]
            
        conta = plano[caminho[0]]
        for i in range(1, len(caminho)):
            conta = conta['subcontas'][caminho[i]]
            
        return conta