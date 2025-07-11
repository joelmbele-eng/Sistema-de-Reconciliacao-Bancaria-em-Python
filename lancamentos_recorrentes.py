import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime, timedelta
import pandas as pd

class GerenciadorLancamentosRecorrentes:
    def __init__(self, app_principal):
        self.app_principal = app_principal
        self.arquivo_lancamentos = "lancamentos_recorrentes.json"
        self.lancamentos = self.carregar_lancamentos()
        
    def carregar_lancamentos(self):
        """Carrega os lançamentos recorrentes do arquivo JSON"""
        if os.path.exists(self.arquivo_lancamentos):
            try:
                with open(self.arquivo_lancamentos, 'r', encoding='utf-8') as arquivo:
                    return json.load(arquivo)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar lançamentos: {str(e)}")
                return []
        return []
        
    def salvar_lancamentos(self):
        """Salva os lançamentos recorrentes no arquivo JSON"""
        try:
            with open(self.arquivo_lancamentos, 'w', encoding='utf-8') as arquivo:
                json.dump(self.lancamentos, arquivo, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar lançamentos: {str(e)}")
            return False
            
    def adicionar_lancamento(self, descricao, valor, periodicidade, data_inicio, data_fim=None, conta=None):
        """Adiciona um novo lançamento recorrente"""
        novo_lancamento = {
            "id": self.gerar_id(),
            "descricao": descricao,
            "valor": valor,
            "periodicidade": periodicidade,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "conta": conta,
            "ativo": True
        }
        
        self.lancamentos.append(novo_lancamento)
        return self.salvar_lancamentos()
        
    def editar_lancamento(self, id_lancamento, **kwargs):
        """Edita um lançamento recorrente existente"""
        for lancamento in self.lancamentos:
            if lancamento["id"] == id_lancamento:
                for chave, valor in kwargs.items():
                    if chave in lancamento:
                        lancamento[chave] = valor
                return self.salvar_lancamentos()
        return False
        
    def remover_lancamento(self, id_lancamento):
        """Remove um lançamento recorrente"""
        self.lancamentos = [l for l in self.lancamentos if l["id"] != id_lancamento]
        return self.salvar_lancamentos()
        
    def gerar_id(self):
        """Gera um ID único para o lançamento"""
        ids_existentes = [l["id"] for l in self.lancamentos]
        novo_id = 1
        while novo_id in ids_existentes:
            novo_id += 1
        return novo_id
        
    def processar_lancamentos(self, data_inicio, data_fim):
        """Processa os lançamentos recorrentes para um período específico"""
        data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d") if isinstance(data_inicio, str) else data_inicio
        data_fim = datetime.strptime(data_fim, "%Y-%m-%d") if isinstance(data_fim, str) else data_fim
        
        lancamentos_processados = []
        
        for lancamento in self.lancamentos:
            if not lancamento["ativo"]:
                continue
                
            data_inicio_lancamento = datetime.strptime(lancamento["data_inicio"], "%Y-%m-%d")
            data_fim_lancamento = None
            if lancamento["data_fim"]:
                data_fim_lancamento = datetime.strptime(lancamento["data_fim"], "%Y-%m-%d")
                
            # Verificar se o período do lançamento se sobrepõe ao período solicitado
            if data_inicio_lancamento > data_fim:
                continue
                
            if data_fim_lancamento and data_fim_lancamento < data_inicio:
                continue
                
            # Gerar datas de lançamento com base na periodicidade
            datas = self.gerar_datas_lancamento(
                lancamento["periodicidade"],
                data_inicio_lancamento,
                data_fim_lancamento,
                data_inicio,
                data_fim
            )
            
            # Adicionar lançamentos processados
            for data in datas:
                lancamentos_processados.append({
                    "data": data,
                    "descricao": lancamento["descricao"],
                    "valor": lancamento["valor"],
                    "conta": lancamento["conta"],
                    "id_lancamento": lancamento["id"]
                })
                
        return lancamentos_processados
        
    def gerar_datas_lancamento(self, periodicidade, data_inicio, data_fim, periodo_inicio, periodo_fim):
        """Gera as datas de lançamento com base na periodicidade"""
        datas = []
        data_atual = max(data_inicio, periodo_inicio)
        
        # Ajustar data_atual para a primeira ocorrência após data_inicio
        if periodicidade == "mensal":
            # Se for mensal, ajustar para o mesmo dia do mês
            while data_atual.day != data_inicio.day and data_atual.day <= 28:
                data_atual += timedelta(days=1)
                
        elif periodicidade == "trimestral":
            # Se for trimestral, ajustar para o mesmo dia a cada 3 meses
            mes_alvo = ((data_inicio.month - 1) % 3) + 1
            while (data_atual.month - 1) % 3 + 1 != mes_alvo or data_atual.day != data_inicio.day:
                data_atual += timedelta(days=1)
                
        elif periodicidade == "semestral":
            # Se for semestral, ajustar para o mesmo dia a cada 6 meses
            mes_alvo = ((data_inicio.month - 1) % 6) + 1
            while (data_atual.month - 1) % 6 + 1 != mes_alvo or data_atual.day != data_inicio.day:
                data_atual += timedelta(days=1)
                
        elif periodicidade == "anual":
            # Se for anual, ajustar para o mesmo dia e mês
            while data_atual.month != data_inicio.month or data_atual.day != data_inicio.day:
                data_atual += timedelta(days=1)
                
        # Gerar datas até o fim do período
        while data_atual <= periodo_fim:
            if not data_fim or data_atual <= data_fim:
                datas.append(data_atual)
                
            # Avançar para a próxima data com base na periodicidade
            if periodicidade == "diario":
                data_atual += timedelta(days=1)
            elif periodicidade == "semanal":
                data_atual += timedelta(days=7)
            elif periodicidade == "quinzenal":
                data_atual += timedelta(days=15)
            elif periodicidade == "mensal":
                # Avançar um mês mantendo o mesmo dia (ou o último dia do mês)
                ano = data_atual.year + (data_atual.month // 12)
                mes = (data_atual.month % 12) + 1
                dia = min(data_atual.day, [31, 29 if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mes-1])
                data_atual = data_atual.replace(year=ano, month=mes, day=dia)
            elif periodicidade == "trimestral":
                # Avançar três meses
                ano = data_atual.year + (data_atual.month + 2) // 12
                mes = ((data_atual.month + 2) % 12) + 1
                dia = min(data_atual.day, [31, 29 if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mes-1])
                data_atual = data_atual.replace(year=ano, month=mes, day=dia)
            elif periodicidade == "semestral":
                # Avançar seis meses
                ano = data_atual.year + (data_atual.month + 5) // 12
                mes = ((data_atual.month + 5) % 12) + 1
                dia = min(data_atual.day, [31, 29 if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mes-1])
                data_atual = data_atual.replace(year=ano, month=mes, day=dia)
            elif periodicidade == "anual":
                # Avançar um ano
                data_atual = data_atual.replace(year=data_atual.year + 1)
                
        return datas
        
    def abrir_gestor(self):
        """Abre a janela de gestão de lançamentos recorrentes"""
        janela = tk.Toplevel(self.app_principal.root)
        janela.title("Gerenciador de Lançamentos Recorrentes")
        janela.geometry("800x600")
        janela.transient(self.app_principal.root)
        
        # Frame principal
        frame_principal = ttk.Frame(janela, padding="10")
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(frame_principal, text="Gerenciador de Lançamentos Recorrentes", 
                 font=('Helvetica', 14, 'bold')).pack(pady=10)
        
        # Frame de botões
        frame_botoes = ttk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_botoes, text="Adicionar", 
                  command=lambda: self.abrir_formulario_lancamento(janela)).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Editar", 
                  command=lambda: self.editar_lancamento_selecionado(janela, tabela)).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Remover", 
                  command=lambda: self.remover_lancamento_selecionado(janela, tabela)).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Atualizar", 
                  command=lambda: self.atualizar_tabela_lancamentos(tabela)).pack(side=tk.LEFT, padx=5)
        
        # Frame da tabela
        frame_tabela = ttk.Frame(frame_principal)
        frame_tabela.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tabela de lançamentos
        colunas = ('id', 'descricao', 'valor', 'periodicidade', 'data_inicio', 'data_fim', 'conta', 'ativo')
        tabela = ttk.Treeview(frame_tabela, columns=colunas, show='headings')
        
        # Configurar cabeçalhos
        tabela.heading('id', text='ID')
        tabela.heading('descricao', text='Descrição')
        tabela.heading('valor', text='Valor')
        tabela.heading('periodicidade', text='Periodicidade')
        tabela.heading('data_inicio', text='Data Início')
        tabela.heading('data_fim', text='Data Fim')
        tabela.heading('conta', text='Conta')
        tabela.heading('ativo', text='Ativo')
        
        # Configurar larguras
        tabela.column('id', width=50)
        tabela.column('descricao', width=200)
        tabela.column('valor', width=100)
        tabela.column('periodicidade', width=100)
        tabela.column('data_inicio', width=100)
        tabela.column('data_fim', width=100)
        tabela.column('conta', width=100)
        tabela.column('ativo', width=50)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=tabela.yview)
        tabela.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Preencher tabela
        self.atualizar_tabela_lancamentos(tabela)
        
        # Botão de fechar
        ttk.Button(frame_principal, text="Fechar", 
                  command=janela.destroy).pack(pady=10)
                  
    def atualizar_tabela_lancamentos(self, tabela):
        """Atualiza a tabela de lançamentos recorrentes"""
        # Limpar tabela
        for item in tabela.get_children():
            tabela.delete(item)
            
        # Preencher com dados
        for lancamento in self.lancamentos:
            tabela.insert('', 'end', values=(
                lancamento["id"],
                lancamento["descricao"],
                f"Kz {lancamento['valor']:,.2f}",
                lancamento["periodicidade"],
                lancamento["data_inicio"],
                lancamento["data_fim"] if lancamento["data_fim"] else "",
                lancamento["conta"] if lancamento["conta"] else "",
                "Sim" if lancamento["ativo"] else "Não"
            ))
            
    def abrir_formulario_lancamento(self, janela_pai, lancamento=None):
        """Abre o formulário para adicionar ou editar um lançamento recorrente"""
        # Criar janela
        janela = tk.Toplevel(janela_pai)
        janela.title("Adicionar Lançamento" if not lancamento else "Editar Lançamento")
        janela.geometry("400x400")
        janela.transient(janela_pai)
        
        # Frame principal
        frame = ttk.Frame(janela, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos do formulário
        ttk.Label(frame, text="Descrição:").grid(row=0, column=0, sticky=tk.W, pady=5)
        descricao_var = tk.StringVar(value=lancamento["descricao"] if lancamento else "")
        ttk.Entry(frame, textvariable=descricao_var, width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Valor:").grid(row=1, column=0, sticky=tk.W, pady=5)
        valor_var = tk.DoubleVar(value=lancamento["valor"] if lancamento else 0.0)
        ttk.Entry(frame, textvariable=valor_var).grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="Periodicidade:").grid(row=2, column=0, sticky=tk.W, pady=5)
        periodicidade_var = tk.StringVar(value=lancamento["periodicidade"] if lancamento else "mensal")
        ttk.Combobox(frame, textvariable=periodicidade_var, 
                    values=["diario", "semanal", "quinzenal", "mensal", "trimestral", "semestral", "anual"]
                   ).grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="Data Início (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W, pady=5)
        data_inicio_var = tk.StringVar(value=lancamento["data_inicio"] if lancamento else datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(frame, textvariable=data_inicio_var).grid(row=3, column=1, pady=5)
        
        ttk.Label(frame, text="Data Fim (YYYY-MM-DD):").grid(row=4, column=0, sticky=tk.W, pady=5)
        data_fim_var = tk.StringVar(value=lancamento["data_fim"] if lancamento and lancamento["data_fim"] else "")
        ttk.Entry(frame, textvariable=data_fim_var).grid(row=4, column=1, pady=5)
        
        ttk.Label(frame, text="Conta:").grid(row=5, column=0, sticky=tk.W, pady=5)
        conta_var = tk.StringVar(value=lancamento["conta"] if lancamento and lancamento["conta"] else "")
        ttk.Entry(frame, textvariable=conta_var).grid(row=5, column=1, pady=5)
        
        ttk.Label(frame, text="Ativo:").grid(row=6, column=0, sticky=tk.W, pady=5)
        ativo_var = tk.BooleanVar(value=lancamento["ativo"] if lancamento else True)
        ttk.Checkbutton(frame, variable=ativo_var).grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # Função para salvar
        def salvar():
            try:
                descricao = descricao_var.get()
                valor = valor_var.get()
                periodicidade = periodicidade_var.get()
                data_inicio = data_inicio_var.get()
                data_fim = data_fim_var.get() if data_fim_var.get() else None
                conta = conta_var.get() if conta_var.get() else None
                ativo = ativo_var.get()
                
                # Validações
                if not descricao:
                    messagebox.showerror("Erro", "A descrição é obrigatória!")
                    return
                    
                if valor <= 0:
                    messagebox.showerror("Erro", "O valor deve ser maior que zero!")
                    return
                    
                try:
                    datetime.strptime(data_inicio, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Erro", "Data de início inválida! Use o formato YYYY-MM-DD.")
                    return
                    
                if data_fim:
                    try:
                        datetime.strptime(data_fim, "%Y-%m-%d")
                    except ValueError:
                        messagebox.showerror("Erro", "Data de fim inválida! Use o formato YYYY-MM-DD.")
                        return
                
                # Salvar lançamento
                if lancamento:
                    # Editar lançamento existente
                    self.editar_lancamento(
                        lancamento["id"],
                        descricao=descricao,
                        valor=valor,
                        periodicidade=periodicidade,
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                        conta=conta,
                        ativo=ativo
                    )
                    messagebox.showinfo("Sucesso", "Lançamento atualizado com sucesso!")
                else:
                    # Adicionar novo lançamento
                    self.adicionar_lancamento(
                        descricao,
                        valor,
                        periodicidade,
                        data_inicio,
                        data_fim,
                        conta
                    )
                    messagebox.showinfo("Sucesso", "Lançamento adicionado com sucesso!")
                
                janela.destroy()
                
                # Atualizar a tabela na janela principal
                for widget in janela_pai.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Frame):
                                for grandchild in child.winfo_children():
                                    if isinstance(grandchild, ttk.Treeview):
                                        self.atualizar_tabela_lancamentos(grandchild)
                                        
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar lançamento: {str(e)}")
                
        # Botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(frame_botoes, text="Salvar", command=salvar).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Cancelar", command=janela.destroy).pack(side=tk.LEFT, padx=5)
        
    def editar_lancamento_selecionado(self, janela_pai, tabela):
        """Edita o lançamento selecionado na tabela"""
        selecao = tabela.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um lançamento para editar!")
            return
            
        # Obter ID do lançamento selecionado
        id_lancamento = int(tabela.item(selecao[0])['values'][0])
        
        # Encontrar lançamento
        lancamento = None
        for l in self.lancamentos:
            if l["id"] == id_lancamento:
                lancamento = l
                break
                
        if not lancamento:
            messagebox.showerror("Erro", "Lançamento não encontrado!")
            return
            
        # Abrir formulário de edição
        self.abrir_formulario_lancamento(janela_pai, lancamento)
        
    def remover_lancamento_selecionado(self, janela_pai, tabela):
        """Remove o lançamento selecionado na tabela"""
        selecao = tabela.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um lançamento para remover!")
            return
            
        # Obter ID do lançamento selecionado
        id_lancamento = int(tabela.item(selecao[0])['values'][0])
        
        # Confirmar remoção
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja remover este lançamento?"):
            return
            
        # Remover lançamento
        if self.remover_lancamento(id_lancamento):
            messagebox.showinfo("Sucesso", "Lançamento removido com sucesso!")
            self.atualizar_tabela_lancamentos(tabela)
        else:
            messagebox.showerror("Erro", "Erro ao remover lançamento!")