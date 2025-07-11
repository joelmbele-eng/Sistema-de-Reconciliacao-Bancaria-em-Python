from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from datetime import datetime
import pandas as pd
import os

class GeradorRelatorios:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.configurar_estilos()
        
    def configurar_estilos(self):
        """Configura os estilos personalizados para os relatórios"""
        self.estilo_titulo = ParagraphStyle(
            'EstiloTitulo',
            parent=self.styles['Title'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Centralizado
        )
        
        self.estilo_subtitulo = ParagraphStyle(
            'EstiloSubtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.HexColor('#2E5090')
        )
        
    def criar_cabecalho(self, titulo, data_geracao=None):
        """Cria o cabeçalho padrão dos relatórios"""
        elementos = []
        
        # Título principal
        elementos.append(Paragraph(titulo, self.estilo_titulo))
        
        # Data de geração
        if data_geracao is None:
            data_geracao = datetime.now()
        data_texto = f"Gerado em: {data_geracao.strftime('%d/%m/%Y %H:%M')}"
        elementos.append(Paragraph(data_texto, self.styles['Normal']))
        elementos.append(Spacer(1, 20))
        
        return elementos

    def estilo_tabela_padrao(self):
        """Retorna o estilo padrão para tabelas"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5090')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8)
        ])

    def gerar_relatorio_diario(self, dados_banco, dados_livro, caminho_saida):
        """Gera relatório detalhado das movimentações diárias"""
        doc = SimpleDocTemplate(
            caminho_saida,
            pagesize=landscape(A4),
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        elementos = self.criar_cabecalho("Relatório Diário de Reconciliação Contábil")
        
        # Resumo diário
        dados_diarios = []
        for data in sorted(set(dados_banco['data'].dt.date)):
            banco_dia = dados_banco[dados_banco['data'].dt.date == data]['valor'].sum()
            livro_dia = dados_livro[dados_livro['data'].dt.date == data]['valor'].sum()
            diferenca = banco_dia - livro_dia
            status = "OK" if abs(diferenca) < 0.01 else "Divergência"
            
            dados_diarios.append([
                data.strftime('%d/%m/%Y'),
                f"Kz {banco_dia:,.2f}",
                f"Kz {livro_dia:,.2f}",
                f"Kz {diferenca:,.2f}",
                status
            ])
        
        tabela = Table([['Data', 'Total Banco', 'Total Livro', 'Diferença', 'Status']] + dados_diarios)
        tabela.setStyle(self.estilo_tabela_padrao())
        elementos.append(tabela)
        
        doc.build(elementos)

    def gerar_relatorio_mensal(self, dados_mensais, caminho_saida):
        """Gera relatório consolidado mensal"""
        doc = SimpleDocTemplate(
            caminho_saida,
            pagesize=landscape(A4),
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        elementos = self.criar_cabecalho("Relatório Mensal de Reconciliação")
        
        # Dados mensais
        dados_tabela = []
        total_banco = 0
        total_livro = 0
        
        for mes in sorted(dados_mensais['banco'].index):
            banco_mes = dados_mensais['banco'][mes]
            livro_mes = dados_mensais['livro'][mes]
            diferenca = banco_mes - livro_mes
            status = "OK" if abs(diferenca) < 0.01 else "Divergência"
            
            total_banco += banco_mes
            total_livro += livro_mes
            
            dados_tabela.append([
                mes,
                f"Kz {banco_mes:,.2f}",
                f"Kz {livro_mes:,.2f}",
                f"Kz {diferenca:,.2f}",
                status
            ])
        
        # Adicionar totais
        dados_tabela.append([
            'TOTAL',
            f"Kz {total_banco:,.2f}",
            f"Kz {total_livro:,.2f}",
            f"Kz {(total_banco - total_livro):,.2f}",
            ''
        ])
        
        tabela = Table([['Mês', 'Total Banco', 'Total Livro', 'Diferença', 'Status']] + dados_tabela)
        tabela.setStyle(self.estilo_tabela_padrao())
        elementos.append(tabela)
        
        doc.build(elementos)

    def gerar_relatorio_divergencias(self, divergencias, caminho_saida):
        """Gera relatório detalhado de divergências encontradas"""
        doc = SimpleDocTemplate(
            caminho_saida,
            pagesize=landscape(A4),
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        elementos = self.criar_cabecalho("Relatório de Divergências")
        
        # Adicionar resumo
        elementos.append(Paragraph(
            f"Total de divergências encontradas: {len(divergencias)}",
            self.estilo_subtitulo
        ))
        elementos.append(Spacer(1, 20))
        
        # Tabela de divergências
        if divergencias:
            dados_tabela = []
            for div in divergencias:
                dados_tabela.append([
                    div['data'].strftime('%d/%m/%Y'),
                    div['descricao'],
                    f"Kz {div['valor']:,.2f}",
                    div['origem']
                ])
            
            tabela = Table([['Data', 'Descrição', 'Valor', 'Origem']] + dados_tabela)
            tabela.setStyle(self.estilo_tabela_padrao())
            elementos.append(tabela)
        else:
            elementos.append(Paragraph(
                "Não foram encontradas divergências no período analisado.",
                self.styles['Normal']
            ))
        
        doc.build(elementos)
