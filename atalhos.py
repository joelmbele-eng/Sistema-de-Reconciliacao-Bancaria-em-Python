import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from typing import Dict, Any, Callable, Optional


class GerenciadorAtalhos:
    """Classe para gerenciar atalhos de teclado na aplicação."""
    
    def __init__(self, aplicacao_principal):
        """
        Inicializa o gerenciador de atalhos.
        
        Args:
            aplicacao_principal: A instância principal da aplicação
        """
        self.aplicacao = aplicacao_principal
        self.arquivo_atalhos = "atalhos.json"
        self.atalhos = self.carregar_atalhos()
        
    def carregar_atalhos(self) -> Dict[str, str]:
        """
        Carrega os atalhos do arquivo JSON.
        
        Returns:
            Dict[str, str]: Dicionário com os atalhos configurados
        """
        if os.path.exists(self.arquivo_atalhos):
            try:
                with open(self.arquivo_atalhos, 'r', encoding='utf-8') as arquivo:
                    return json.load(arquivo)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar atalhos: {str(e)}")
                return self.atalhos_padrao()
        return self.atalhos_padrao()
    
    def atalhos_padrao(self) -> Dict[str, str]:
        """
        Define os atalhos padrão da aplicação.
        
        Returns:
            Dict[str, str]: Dicionário com os atalhos padrão
        """
        return {
            "importar_banco": "Ctrl+B",
            "importar_livro": "Ctrl+L",
            "conciliar": "Ctrl+C",
            "gerar_relatorio_diario": "Ctrl+R",
            "gerar_relatorio_mensal": "Ctrl+M",
            "gerar_relatorio_divergencias": "Ctrl+D",
            "mostrar_graficos": "Ctrl+G",
            "limpar_dados": "Ctrl+Del",
            "sair": "Alt+F4"
        }
    
    def salvar_atalhos(self) -> bool:
        """
        Salva os atalhos no arquivo JSON.
        
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            with open(self.arquivo_atalhos, 'w', encoding='utf-8') as arquivo:
                json.dump(self.atalhos, arquivo, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar atalhos: {str(e)}")
            return False
    
    def registrar_atalhos(self, janela: tk.Tk) -> None:
        """
        Registra os atalhos na janela especificada.
        
        Args:
            janela: A janela onde os atalhos serão registrados
        """
        for funcao, atalho in self.atalhos.items():
            metodo = getattr(self.aplicacao, funcao, None)
            if metodo and callable(metodo):
                atalho_convertido = self.converter_atalho(atalho)
                janela.bind(atalho_convertido, lambda event, m=metodo: m())
    
    def converter_atalho(self, atalho: str) -> str:
        """
        Converte a representação do atalho para o formato aceito pelo tkinter.
        
        Args:
            atalho: Representação do atalho (ex: "Ctrl+S")
            
        Returns:
            str: Atalho no formato do tkinter (ex: "<Control-s>")
        """
        atalho = atalho.replace("Ctrl", "Control")
        atalho = atalho.replace("+", "-")
        
        # Converter para minúsculas letras após o último hífen
        partes = atalho.split("-")
        if len(partes) > 1 and len(partes[-1]) == 1:
            partes[-1] = partes[-1].lower()
        atalho = "-".join(partes)
        
        return f"<{atalho}>"
    
    def abrir_configuracao(self) -> None:
        """Abre a janela de configuração de atalhos."""
        janela = tk.Toplevel(self.aplicacao.root)
        janela.title("Configuração de Atalhos")
        janela.geometry("500x400")
        janela.transient(self.aplicacao.root)
        janela.grab_set()  # Torna a janela modal
        
        # Frame principal
        frame = ttk.Frame(janela, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(
            frame, 
            text="Configuração de Atalhos de Teclado", 
            font=('Helvetica', 12, 'bold')
        ).pack(pady=10)
        
        # Frame para os atalhos com scrollbar
        frame_canvas = ttk.Frame(frame)
        frame_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(frame_canvas)
        scrollbar = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
        frame_atalhos = ttk.Frame(canvas)
        
        # Configuração do scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame_atalhos, anchor="nw")
        
        frame_atalhos.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Variáveis para armazenar os valores dos atalhos
        variaveis_atalhos = {}
        
        # Adicionar campos para cada atalho
        for i, (funcao, atalho) in enumerate(sorted(self.atalhos.items())):
            # Nome amigável da função
            nome_funcao = " ".join(palavra.capitalize() for palavra in funcao.split("_"))
            
            ttk.Label(frame_atalhos, text=nome_funcao + ":").grid(
                row=i, column=0, sticky=tk.W, pady=5, padx=5)
            
            # Variável para o atalho
            var_atalho = tk.StringVar(value=atalho)
            variaveis_atalhos[funcao] = var_atalho
            
            # Campo de entrada
            entrada = ttk.Entry(frame_atalhos, textvariable=var_atalho, width=15)
            entrada.grid(row=i, column=1, padx=10, pady=5)
            
            # Botão para redefinir para o padrão
            ttk.Button(
                frame_atalhos, 
                text="Padrão",
                command=lambda f=funcao, v=var_atalho: v.set(self.atalhos_padrao()[f])
            ).grid(row=i, column=2, padx=5, pady=5)
        
        # Função para salvar alterações
        def salvar_alteracoes():
            # Verificar se há atalhos duplicados
            valores = [var.get() for var in variaveis_atalhos.values()]
            if len(valores) != len(set(valores)):
                messagebox.showerror("Erro", "Existem atalhos duplicados. Cada função deve ter um atalho único.")
                return
                
            # Atualizar atalhos com os valores das variáveis
            for funcao, var in variaveis_atalhos.items():
                self.atalhos[funcao] = var.get()
            
            # Salvar no arquivo
            if self.salvar_atalhos():
                messagebox.showinfo("Sucesso", "Atalhos salvos com sucesso!")
                janela.destroy()
        
        # Função para restaurar todos os atalhos para o padrão
        def restaurar_padrao():
            if messagebox.askyesno("Confirmar", "Deseja restaurar todos os atalhos para o padrão?"):
                padrao = self.atalhos_padrao()
                for funcao, var in variaveis_atalhos.items():
                    if funcao in padrao:
                        var.set(padrao[funcao])
        
        # Botões de ação
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(pady=15)
        
        ttk.Button(
            frame_botoes, 
            text="Salvar", 
            command=salvar_alteracoes
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame_botoes, 
            text="Restaurar Padrão", 
            command=restaurar_padrao
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame_botoes, 
            text="Cancelar", 
            command=janela.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def obter_descricao_atalho(self, funcao: str) -> str:
        """
        Retorna a descrição do atalho para uma função específica.
        
        Args:
            funcao: Nome da função
            
        Returns:
            str: Descrição do atalho ou string vazia se não existir
        """
        return self.atalhos.get(funcao, "")
    
    def atualizar_atalho(self, funcao: str, novo_atalho: str) -> bool:
        """
        Atualiza um atalho específico.
        
        Args:
            funcao: Nome da função
            novo_atalho: Novo atalho a ser definido
            
        Returns:
            bool: True se atualizou com sucesso, False caso contrário
        """
        if funcao in self.atalhos:
            self.atalhos[funcao] = novo_atalho
            return self.salvar_atalhos()
        return False
    
    def adicionar_atalho(self, funcao: str, atalho: str) -> bool:
        """
        Adiciona um novo atalho.
        
        Args:
            funcao: Nome da função
            atalho: Atalho a ser definido
            
        Returns:
            bool: True se adicionou com sucesso, False caso contrário
        """
        if atalho in self.atalhos.values():
            return False  # Atalho já existe
        
        self.atalhos[funcao] = atalho
        return self.salvar_atalhos()
    
    def remover_atalho(self, funcao: str) -> bool:
        """
        Remove um atalho.
        
        Args:
            funcao: Nome da função
            
        Returns:
            bool: True se removeu com sucesso, False caso contrário
        """
        if funcao in self.atalhos:
            del self.atalhos[funcao]
            return self.salvar_atalhos()
        return False
