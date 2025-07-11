# Configurações gerais do sistema
CONFIGURACOES = {
    'TITULO': 'Sistema de Reconciliação Contábil - Angola',
    'MOEDA': 'Kz',
    'BANCOS': {
        'BAI': {
            'nome': 'Banco Angolano de Investimentos',
            'colunas': ['Data Valor', 'Descrição', 'Montante'],
            'formato_data': '%d/%m/%Y'
        },
        'BFA': {
            'nome': 'Banco de Fomento Angola',
            'colunas': ['Data', 'Histórico', 'Valor (AOA)'],
            'formato_data': '%d/%m/%Y'
        },
        'BIC': {
            'nome': 'Banco BIC Angola',
            'colunas': ['Data Mov.', 'Descritivo', 'Valor'],
            'formato_data': '%d/%m/%Y'
        }
    }
}
