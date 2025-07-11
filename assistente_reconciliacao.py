import tkinter as tk
from tkinter import ttk, messagebox
import time

class AssistenteReconciliacao:
    """Assistente passo a passo para guiar o usuário no processo de reconciliação"""
    
    def __init__(self, app):
        self.app = app
        self.passos = [
            {
                "titulo": "Bem-vindo ao Assistente de Reconciliação",
                "descricao": "Este assistente irá guiá-lo através do processo de reconciliação contábil passo a passo. Clique em 'Próximo' para continuar.",
                "acao": None
            },
            {
                "titulo": "Passo 1: Importar Extrato Bancário",
                "descricao": "Primeiro, precisamos importar o extrato bancário. Clique em 'Importar Banco' para selecionar o arquivo do extrato.",
                "acao": self.app.importar_banco
            },
            {
                "titulo": "Passo 2: Importar Livro Contábil",
                "descricao": "Agora, vamos importar o livro contábil. Clique em 'Importar Livro' para selecionar o arquivo do livro.",
                "acao": self.app.importar_livro
            },
            {
                "titulo": "Passo 3: Verificar Totais",
                "descricao": "Verifique os totais exibidos na área de estatísticas. A diferença entre o banco e o livro indica possíveis discrepâncias.",
                "acao": None
            },
            {
                "titulo": "Passo 4: Conciliar Transações",
                "descricao": "Vamos conciliar as transações automaticamente. Clique em 'Conciliar' para identificar transações correspondentes.",
                "acao": self.app.conciliar
            },
            {
                "titulo": "Passo 5: Analisar Divergências",
                "descricao": "Analise as transações marcadas como 'PENDENTE'. Estas são as que não possuem correspondência e precisam ser investigadas.",
                "acao": None
            },
            {
                "titulo": "Passo 6: Gerar Relatório",
                "descricao": "Para finalizar, vamos gerar um relatório de divergências. Clique em 'Gerar Relatório' para criar o documento.",
                "acao": self.app.gerar_relatorio_divergencias
            },
            {
                "titulo": "Reconciliação Concluída!",
                "descricao": "Parabéns! Você completou o processo de reconciliação contábil. Você pode agora explorar outras funcionalidades do sistema.",
                "acao": None
            }
        ]
    
    def iniciar(self):
        """Inicia o assistente de reconciliação"""
        self.passo_atual = 0
        self.criar_janela()
        self.atualizar_conteudo()
    
    def criar_janela(self):
        """Cria a janela do assistente"""
        self.janela = tk.Toplevel(self.app.root)
        self.janela.title("Assistente de Reconciliação")
        self.janela.geometry("700x500")
        self.janela.transient(self.app.root)
        
        # Aplicar tema atual
        if hasattr(self.app, 'gerenciador_temas'):
            tema = self.app.gerenciador_temas.apply_theme(self.janela)
        
        # Frame principal
        self.frame_principal = ttk.Frame(self.janela, padding="20")
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Área de título
        self.label_titulo = ttk.Label(self.frame_principal, text="", font=('Helvetica', 16, 'bold'))
        self.label_titulo.pack(pady=(0, 20))
        
        # Área de conteúdo
        self.frame_conteudo = ttk.Frame(self.frame_principal)
        self.frame_conteudo.pack(fill=tk.BOTH, expand=True)
        
        self.label_descricao = ttk.Label(self.frame_conteudo, text="", wraplength=650, justify="left")
        self.label_descricao.pack(pady=10)
        
        # Área de botões
        self.frame_botoes = ttk.Frame(self.frame_principal)
        self.frame_botoes.pack(fill=tk.X, pady=20)
        
        self.btn_anterior = ttk.Button(self.frame_botoes, text="Anterior", 
                                     command=self.passo_anterior)
        self.btn_anterior.pack(side=tk.LEFT, padx=5)
        
        self.btn_acao = ttk.Button(self.frame_botoes, text="Executar Ação", 
                                  command=self.executar_acao)
        self.btn_acao.pack(side=tk.LEFT, padx=5)
        
        self.btn_proximo = ttk.Button(self.frame_botoes, text="Próximo", 
                                     command=self.passo_proximo)
        self.btn_proximo.pack(side=tk.LEFT, padx=5)
        
        self.btn_fechar = ttk.Button(self.frame_botoes, text="Fechar", 
                                    command=self.janela.destroy)
        self.btn_fechar.pack(side=tk.RIGHT, padx=5)
        
        # Barra de progresso
        self.progresso = ttk.Progressbar(self.frame_principal, orient="horizontal", 
                                       length=100, mode="determinate")
        self.progresso.pack(fill=tk.X, pady=10)
    
    def atualizar_conteudo(self):
        """Atualiza o conteúdo da janela com base no passo atual"""
        passo = self.passos[self.passo_atual]
        
        self.label_titulo.config(text=passo["titulo"])
        self.label_descricao.config(text=passo["descricao"])
        
        # Atualizar botões
        self.btn_anterior.config(state=tk.NORMAL if self.passo_atual > 0 else tk.DISABLED)
        self.btn_proximo.config(state=tk.NORMAL if self.passo_atual < len(self.passos) - 1 else tk.DISABLED)
        self.btn_acao.config(state=tk.NORMAL if passo["acao"] is not None else tk.DISABLED)
        
        # Atualizar barra de progresso
        progresso_percentual = (self.passo_atual / (len(self.passos) - 1)) * 100
        self.progresso["value"] = progresso_percentual
    
    def passo_anterior(self):
        """Navega para o passo anterior"""
        if self.passo_atual > 0:
            self.passo_atual -= 1
            self.atualizar_conteudo()
    
    def passo_proximo(self):
        """Navega para o próximo passo"""
        if self.passo_atual < len(self.passos) - 1:
            self.passo_atual += 1
            self.atualizar_conteudo()
    
    def executar_acao(self):
        """Executa a ação associada ao passo atual"""
        passo = self.passos[self.passo_atual]
        if passo["acao"] is not None:
            # Minimizar a janela do assistente temporariamente
            self.janela.withdraw()
            
            try:
                passo["acao"]()
                messagebox.showinfo("Assistente de Reconciliação", 
                                   "Ação executada com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
            
            # Restaurar a janela do assistente
            self.janela.deiconify()
