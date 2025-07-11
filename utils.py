import pandas as pd
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

def formatar_moeda(valor, moeda='Kz'):
    return f"{moeda} {valor:,.2f}"

def calcular_estatisticas(df_banco, df_livro):
    stats = {
        'total_banco': df_banco['valor'].sum() if df_banco is not None else 0,
        'total_livro': df_livro['valor'].sum() if df_livro is not None else 0,
    }
    stats['diferenca'] = stats['total_banco'] - stats['total_livro']
    return stats

def criar_estilo_tabela():
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ])
