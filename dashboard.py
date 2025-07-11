import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class DashboardAvancado:
    def __init__(self, dados_banco, dados_livro):
        self.dados_banco = dados_banco
        self.dados_livro = dados_livro
        
        self.janela = tk.Toplevel()
        self.janela.title("Dashboard Avançado")
        self.janela.geometry("1200x800")
        
        self.criar_dashboard()
        
    def criar_dashboard(self):
        notebook = ttk.Notebook(self.janela)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Criar abas
        aba_visao_geral = ttk.Frame(notebook)
        aba_tendencias = ttk.Frame(notebook)
        aba_comparativo = ttk.Frame(notebook)
        
        notebook.add(aba_visao_geral, text='Visão Geral')
        notebook.add(aba_tendencias, text='Tendências')
        notebook.add(aba_comparativo, text='Comparativo')
        
        self.criar_visao_geral(aba_visao_geral)
        self.criar_tendencias(aba_tendencias)
        self.criar_comparativo(aba_comparativo)
        
    def criar_visao_geral(self, container):
        frame_superior = ttk.Frame(container)
        frame_superior.pack(fill='x', padx=5, pady=5)
        
        # Estatísticas principais
        total_banco = self.dados_banco['valor'].sum()
        total_livro = self.dados_livro['valor'].sum()
        diferenca = total_banco - total_livro
        
        ttk.Label(frame_superior, 
                 text=f"Total Banco: Kz {total_banco:,.2f}",
                 font=('Helvetica', 12)).pack(side='left', padx=10)
        ttk.Label(frame_superior, 
                 text=f"Total Livro: Kz {total_livro:,.2f}",
                 font=('Helvetica', 12)).pack(side='left', padx=10)
        ttk.Label(frame_superior, 
                 text=f"Diferença: Kz {diferenca:,.2f}",
                 font=('Helvetica', 12)).pack(side='left', padx=10)
        
        # Gráficos
        frame_graficos = ttk.Frame(container)
        frame_graficos.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Gráfico de Pizza para valores positivos
        fig1 = plt.Figure(figsize=(6, 4))
        ax1 = fig1.add_subplot(111)
        
        valores_positivos = [max(0, total_banco), max(0, total_livro)]
        valores_negativos = [abs(min(0, total_banco)), abs(min(0, total_livro))]
        
        if sum(valores_positivos) > 0:
            ax1.pie(valores_positivos, 
                   labels=['Banco', 'Livro'],
                   autopct='%1.1f%%' if sum(valores_positivos) > 0 else None)
            ax1.set_title('Distribuição de Valores Positivos')
        
        canvas1 = FigureCanvasTkAgg(fig1, frame_graficos)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side='left', fill='both', expand=True)
        
    def criar_tendencias(self, container):
        fig = plt.Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        # Evolução temporal
        ax.plot(self.dados_banco['data'], 
               self.dados_banco['valor'].cumsum(),
               label='Banco')
        ax.plot(self.dados_livro['data'], 
               self.dados_livro['valor'].cumsum(),
               label='Livro')
        
        ax.set_title('Evolução Temporal dos Valores')
        ax.set_xlabel('Data')
        ax.set_ylabel('Valor Acumulado (Kz)')
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def criar_comparativo(self, container):
        fig = plt.Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        
        # Análise diária
        datas_unicas = sorted(set(self.dados_banco['data'].unique()) | 
                            set(self.dados_livro['data'].unique()))
        
        valores_banco = []
        valores_livro = []
        
        for data in datas_unicas:
            valor_banco = self.dados_banco[self.dados_banco['data'] == data]['valor'].sum()
            valor_livro = self.dados_livro[self.dados_livro['data'] == data]['valor'].sum()
            
            valores_banco.append(valor_banco)
            valores_livro.append(valor_livro)
        
        x = np.arange(len(datas_unicas))
        largura = 0.35
        
        ax.bar(x - largura/2, valores_banco, largura, label='Banco')
        ax.bar(x + largura/2, valores_livro, largura, label='Livro')
        
        ax.set_title('Comparativo Diário')
        ax.set_xlabel('Data')
        ax.set_ylabel('Valor (Kz)')
        ax.set_xticks(x)
        ax.set_xticklabels([data.strftime('%d/%m') for data in datas_unicas], 
                          rotation=45)
        ax.legend()
        
        canvas = FigureCanvasTkAgg(fig, container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
