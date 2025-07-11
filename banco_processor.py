import pandas as pd
from datetime import datetime
from config import CONFIGURACOES

class ProcessadorBanco:
    @staticmethod
    def processar_extrato(arquivo, banco):
        config_banco = CONFIGURACOES['BANCOS'][banco]
        
        if arquivo.endswith('.xlsx'):
            df = pd.read_excel(arquivo)
        else:
            df = pd.read_csv(arquivo, encoding='utf-8')
            
        # Padronização das colunas
        df = df.rename(columns={
            config_banco['colunas'][0]: 'data',
            config_banco['colunas'][1]: 'descricao',
            config_banco['colunas'][2]: 'valor'
        })
        
        # Tratamento de data e valor
        df['data'] = pd.to_datetime(df['data'])
        df['valor'] = pd.to_numeric(df['valor'].astype(str).str.replace(',', '.'))
        
        return df[['data', 'descricao', 'valor']]
