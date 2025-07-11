import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import difflib
import re
from fuzzywuzzy import fuzz
import logging

class ConciliacaoBancariaAutomatica:
    def __init__(self, contabilidade):
        """
        Inicializa o sistema de conciliação bancária automatizada
        
        Args:
            contabilidade: Instância da classe ContabilidadeAvancada
        """
        self.contabilidade = contabilidade
        self.logger = self._configurar_logger()
        self.transacoes_conciliadas = []
        self.discrepancias = []
        
    def _configurar_logger(self):
        """Configura o logger para registrar operações de conciliação"""
        logger = logging.getLogger('conciliacao_bancaria')
        logger.setLevel(logging.INFO)
        
        # Criar handler para arquivo
        fh = logging.FileHandler('conciliacao_bancaria.log')
        fh.setLevel(logging.INFO)
        
        # Criar formatador
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        # Adicionar handler ao logger
        logger.addHandler(fh)
        
        return logger
    
    def conciliar_automaticamente(self, dados_banco, dados_livro, tolerancia_dias=3, tolerancia_valor=0.01, tolerancia_texto=80):
        """
        Realiza a conciliação automática entre extratos bancários e lançamentos contábeis
        
        Args:
            dados_banco: DataFrame com os dados do extrato bancário
            dados_livro: DataFrame com os dados do livro contábil
            tolerancia_dias: Número de dias de tolerância para matching de datas
            tolerancia_valor: Tolerância para diferenças de valores (em valor absoluto)
            tolerancia_texto: Pontuação mínima (0-100) para considerar descrições similares
            
        Returns:
            tuple: (transacoes_conciliadas, discrepancias)
        """
        self.logger.info(f"Iniciando conciliação automática com {len(dados_banco)} registros bancários e {len(dados_livro)} registros contábeis")
        
        # Resetar listas
        self.transacoes_conciliadas = []
        self.discrepancias = []
        
        # Copiar DataFrames para não modificar os originais
        banco_df = dados_banco.copy()
        livro_df = dados_livro.copy()
        
        # Adicionar colunas de controle
        banco_df['conciliado'] = False
        livro_df['conciliado'] = False
        banco_df['id_conciliacao'] = None
        livro_df['id_conciliacao'] = None
        
        # Algoritmo 1: Matching exato (data, valor e descrição similar)
        self._matching_exato(banco_df, livro_df, tolerancia_texto)
        
        # Algoritmo 2: Matching por valor e data próxima
        self._matching_por_valor_data(banco_df, livro_df, tolerancia_dias)
        
        # Algoritmo 3: Matching por agrupamento (somas iguais)
        self._matching_por_agrupamento(banco_df, livro_df, tolerancia_dias)
        
        # Identificar discrepâncias
        self._identificar_discrepancias(banco_df, livro_df)
        
        self.logger.info(f"Conciliação concluída: {len(self.transacoes_conciliadas)} transações conciliadas, {len(self.discrepancias)} discrepâncias encontradas")
        
        return self.transacoes_conciliadas, self.discrepancias
    
    def _matching_exato(self, banco_df, livro_df, tolerancia_texto):
        """
        Realiza o matching exato entre transações com mesma data, valor e descrição similar
        """
        id_conciliacao = 1
        
        for i, row_banco in banco_df[~banco_df['conciliado']].iterrows():
            for j, row_livro in livro_df[~livro_df['conciliado']].iterrows():
                # Verificar se data e valor são iguais
                if (row_banco['data'].date() == row_livro['data'].date() and 
                    abs(row_banco['valor'] - row_livro['valor']) < 0.01):
                    
                    # Verificar similaridade de texto
                    similaridade = fuzz.token_sort_ratio(
                        self._normalizar_texto(row_banco['descricao']), 
                        self._normalizar_texto(row_livro['descricao'])
                    )
                    
                    if similaridade >= tolerancia_texto:
                        # Marcar como conciliado
                        banco_df.at[i, 'conciliado'] = True
                        livro_df.at[j, 'conciliado'] = True
                        banco_df.at[i, 'id_conciliacao'] = id_conciliacao
                        livro_df.at[j, 'id_conciliacao'] = id_conciliacao
                        
                        # Registrar conciliação
                        self.transacoes_conciliadas.append({
                            'id_conciliacao': id_conciliacao,
                            'data_banco': row_banco['data'],
                            'descricao_banco': row_banco['descricao'],
                            'valor_banco': row_banco['valor'],
                            'data_livro': row_livro['data'],
                            'descricao_livro': row_livro['descricao'],
                            'valor_livro': row_livro['valor'],
                            'metodo': 'matching_exato',
                            'similaridade': similaridade
                        })
                        
                        id_conciliacao += 1
                        break
    
    def _matching_por_valor_data(self, banco_df, livro_df, tolerancia_dias):
        """
        Realiza o matching por valor exato e data próxima
        """
        id_conciliacao = len(self.transacoes_conciliadas) + 1
        
        for i, row_banco in banco_df[~banco_df['conciliado']].iterrows():
            for j, row_livro in livro_df[~livro_df['conciliado']].iterrows():
                # Verificar se o valor é igual
                if abs(row_banco['valor'] - row_livro['valor']) < 0.01:
                    # Verificar se a data está dentro da tolerância
                    dias_diff = abs((row_banco['data'].date() - row_livro['data'].date()).days)
                    
                    if dias_diff <= tolerancia_dias:
                        # Marcar como conciliado
                        banco_df.at[i, 'conciliado'] = True
                        livro_df.at[j, 'conciliado'] = True
                        banco_df.at[i, 'id_conciliacao'] = id_conciliacao
                        livro_df.at[j, 'id_conciliacao'] = id_conciliacao
                        
                        # Registrar conciliação
                        self.transacoes_conciliadas.append({
                            'id_conciliacao': id_conciliacao,
                            'data_banco': row_banco['data'],
                            'descricao_banco': row_banco['descricao'],
                            'valor_banco': row_banco['valor'],
                            'data_livro': row_livro['data'],
                            'descricao_livro': row_livro['descricao'],
                            'valor_livro': row_livro['valor'],
                            'metodo': 'matching_por_valor_data',
                            'dias_diferenca': dias_diff
                        })
                        
                        id_conciliacao += 1
                        break
    
    def _matching_por_agrupamento(self, banco_df, livro_df, tolerancia_dias):
        """
        Realiza o matching por agrupamento de transações que somam o mesmo valor
        """
        id_conciliacao = len(self.transacoes_conciliadas) + 1
        
        # Identificar transações não conciliadas
        banco_nao_conciliado = banco_df[~banco_df['conciliado']]
        livro_nao_conciliado = livro_df[~livro_df['conciliado']]
        
        # Agrupar por data (com tolerância)
        for data_banco in banco_nao_conciliado['data'].dt.date.unique():
            # Definir intervalo de datas para busca
            data_inicio = data_banco - timedelta(days=tolerancia_dias)
            data_fim = data_banco + timedelta(days=tolerancia_dias)
            
            # Filtrar transações do banco na data atual
            banco_data = banco_nao_conciliado[banco_nao_conciliado['data'].dt.date == data_banco]
            
            # Filtrar transações do livro no intervalo de datas
            livro_periodo = livro_nao_conciliado[
                (livro_nao_conciliado['data'].dt.date >= data_inicio) & 
                (livro_nao_conciliado['data'].dt.date <= data_fim)
            ]
            
            # Se não houver transações em algum dos lados, continuar
            if len(banco_data) == 0 or len(livro_periodo) == 0:
                continue
            
            # Tentar encontrar combinações de transações que somam o mesmo valor
            for n_banco in range(1, min(4, len(banco_data) + 1)):  # Limitar a 3 transações para evitar explosão combinatória
                for combinacao_banco in self._gerar_combinacoes(banco_data, n_banco):
                    soma_banco = sum(combinacao_banco['valor'])
                    
                    for n_livro in range(1, min(4, len(livro_periodo) + 1)):
                        for combinacao_livro in self._gerar_combinacoes(livro_periodo, n_livro):
                            soma_livro = sum(combinacao_livro['valor'])
                            
                            # Se as somas forem iguais, conciliar
                            if abs(soma_banco - soma_livro) < 0.01:
                                # Marcar transações como conciliadas
                                for idx in combinacao_banco.index:
                                    banco_df.loc[idx, 'conciliado'] = True
                                    banco_df.loc[idx, 'id_conciliacao'] = id_conciliacao
                                
                                for idx in combinacao_livro.index:
                                    livro_df.loc[idx, 'conciliado'] = True
                                    livro_df.loc[idx, 'id_conciliacao'] = id_conciliacao
                                
                                # Registrar conciliação
                                self.transacoes_conciliadas.append({
                                    'id_conciliacao': id_conciliacao,
                                    'data_banco': data_banco,
                                    'descricao_banco': "Agrupamento de " + str(n_banco) + " transações",
                                    'valor_banco': soma_banco,
                                    'data_livro': combinacao_livro['data'].iloc[0].date(),
                                    'descricao_livro': "Agrupamento de " + str(n_livro) + " transações",
                                    'valor_livro': soma_livro,
                                    'metodo': 'matching_por_agrupamento',
                                    'transacoes_banco': combinacao_banco[['data', 'descricao', 'valor']].to_dict('records'),
                                    'transacoes_livro': combinacao_livro[['data', 'descricao', 'valor']].to_dict('records')
                                })
                                
                                id_conciliacao += 1
                                # Atualizar DataFrames não conciliados
                                banco_nao_conciliado = banco_df[~banco_df['conciliado']]
                                livro_nao_conciliado = livro_df[~livro_df['conciliado']]
                                # Sair dos loops internos
                                break
                            
                        # Se encontrou match, sair do loop
                        if all(banco_df.loc[combinacao_banco.index, 'conciliado']):
                            break
                    
                    # Se encontrou match, sair do loop
                    if all(banco_df.loc[combinacao_banco.index, 'conciliado']):
                        break
    
    def _identificar_discrepancias(self, banco_df, livro_df):
        """
        Identifica discrepâncias entre os extratos bancários e os lançamentos contábeis
        """
        # Transações do banco não conciliadas
        for _, row in banco_df[~banco_df['conciliado']].iterrows():
            self.discrepancias.append({
                'data': row['data'],
                'descricao': row['descricao'],
                'valor': row['valor'],
                'origem': 'BANCO',
                'tipo': 'nao_conciliado',
                'sugestao': self._gerar_sugestao_correcao(row, livro_df)
            })
        
        # Transações do livro não conciliadas
        for _, row in livro_df[~livro_df['conciliado']].iterrows():
            self.discrepancias.append({
                'data': row['data'],
                'descricao': row['descricao'],
                'valor': row['valor'],
                'origem': 'LIVRO',
                'tipo': 'nao_conciliado',
                'sugestao': self._gerar_sugestao_correcao(row, banco_df, origem_livro=True)
            })
    
    def _gerar_sugestao_correcao(self, transacao, df_comparacao, origem_livro=False):
        """
        Gera sugestões de correção para transações não conciliadas
        """
        sugestoes = []
        
        # Buscar por transações com valor similar
        df_valor_similar = df_comparacao[
            (df_comparacao['valor'] > transacao['valor'] * 0.95) & 
            (df_comparacao['valor'] < transacao['valor'] * 1.05)
        ]
        
        if not df_valor_similar.empty:
            for _, row in df_valor_similar.iterrows():
                sugestoes.append({
                    'tipo': 'valor_similar',
                    'data': row['data'],
                    'descricao': row['descricao'],
                    'valor': row['valor'],
                    'diferenca_valor': row['valor'] - transacao['valor'],
                    'dias_diferenca': abs((row['data'].date() - transacao['data'].date()).days)
                })
        
        # Buscar por transações com data igual
        df_data_igual = df_comparacao[df_comparacao['data'].dt.date == transacao['data'].date()]
        
        if not df_data_igual.empty:
            for _, row in df_data_igual.iterrows():
                sugestoes.append({
                    'tipo': 'data_igual',
                    'data': row['data'],
                    'descricao': row['descricao'],
                    'valor': row['valor'],
                    'diferenca_valor': row['valor'] - transacao['valor']
                })
        
        # Buscar por transações com descrição similar
        for _, row in df_comparacao.iterrows():
            similaridade = fuzz.token_sort_ratio(
                self._normalizar_texto(transacao['descricao']), 
                self._normalizar_texto(row['descricao'])
            )
            
            if similaridade >= 70:
                sugestoes.append({
                    'tipo': 'descricao_similar',
                    'data': row['data'],
                    'descricao': row['descricao'],
                    'valor': row['valor'],
                    'similaridade': similaridade,
                    'diferenca_valor': row['valor'] - transacao['valor'],
                    'dias_diferenca': abs((row['data'].date() - transacao['data'].date()).days)
                })
        
        # Ordenar sugestões por relevância
        if sugestoes:
            sugestoes.sort(key=lambda x: (
                -1 if 'similaridade' in x and x['similaridade'] > 85 else 0,
                abs(x['diferenca_valor']),
                x.get('dias_diferenca', 999)
            ))
        
        # Se não houver sugestões, gerar recomendação genérica
        if not sugestoes:
            if origem_livro:
                return [{
                    'tipo': 'generico',
                    'mensagem': 'Lançamento contábil sem correspondência no extrato bancário. Verificar se a transação bancária ainda não ocorreu ou se há erro no lançamento.'
                }]
            else:
                return [{
                    'tipo': 'generico',
                    'mensagem': 'Transação bancária sem correspondência no livro contábil. Registrar o lançamento contábil correspondente.'
                }]
        
        return sugestoes[:3]  # Retornar as 3 melhores sugestões
    
    def _normalizar_texto(self, texto):
        """
        Normaliza o texto para comparação (remove acentos, converte para minúsculas, etc.)
        """
        if not isinstance(texto, str):
            return ""
        
        # Converter para minúsculas
        texto = texto.lower()
        
        # Remover caracteres especiais e números
        texto = re.sub(r'[^\w\s]', ' ', texto)
        
        # Remover espaços extras
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    
    def _gerar_combinacoes(self, df, n):
        """
        Gera todas as combinações possíveis de n linhas do DataFrame
        """
        from itertools import combinations
        
        indices = list(df.index)
        for combo_indices in combinations(indices, n):
            yield df.loc[list(combo_indices)]
    
    def gerar_relatorio_conciliacao(self, caminho_saida):
        """
        Gera um relatório detalhado da conciliação bancária
        
        Args:
            caminho_saida: Caminho do arquivo PDF de saída
        
        Returns:
            bool: True se gerado com sucesso, False caso contrário
        """
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        
        try:
            doc = SimpleDocTemplate(caminho_saida, pagesize=A4)
            elementos = []
            
            # Estilos
            estilos = getSampleStyleSheet()
            estilo_titulo = estilos['Heading1']
            estilo_subtitulo = estilos['Heading2']
            estilo_normal = estilos['Normal']
            
            # Título
            elementos.append(Paragraph("Relatório de Conciliação Bancária Automatizada", estilo_titulo))
            elementos.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilo_normal))
            elementos.append(Spacer(1, 0.5*cm))
            
            # 1. Resumo da conciliação
            elementos.append(Paragraph("1. Resumo da Conciliação", estilo_subtitulo))
            
            dados_resumo = [
                ["Item", "Quantidade", "Valor Total"],
                ["Transações Bancárias Conciliadas", str(len(set([t['id_conciliacao'] for t in self.transacoes_conciliadas]))), 
                 f"Kz {sum([t['valor_banco'] for t in self.transacoes_conciliadas]):,.2f}"],
                ["Discrepâncias Identificadas", str(len(self.discrepancias)), 
                 f"Kz {sum([d['valor'] for d in self.discrepancias]):,.2f}"]
            ]
            
            tabela_resumo = Table(dados_resumo, colWidths=[10*cm, 4*cm, 4*cm])
            tabela_resumo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('ALIGN', (1, 1), (2, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elementos.append(tabela_resumo)
            elementos.append(Spacer(1, 0.5*cm))
            
            # 2. Transações conciliadas
            elementos.append(Paragraph("2. Transações Conciliadas", estilo_subtitulo))
            
            if self.transacoes_conciliadas:
                dados_conciliadas = [["ID", "Data Banco", "Valor Banco", "Data Livro", "Valor Livro", "Método"]]
                
                for transacao in self.transacoes_conciliadas:
                    dados_conciliadas.append([
                        str(transacao['id_conciliacao']),
                        transacao['data_banco'].strftime('%d/%m/%Y') if isinstance(transacao['data_banco'], datetime) else transacao['data_banco'],
                        f"Kz {transacao['valor_banco']:,.2f}",
                        transacao['data_livro'].strftime('%d/%m/%Y') if isinstance(transacao['data_livro'], datetime) else transacao['data_livro'],
                        f"Kz {transacao['valor_livro']:,.2f}",
                        transacao['metodo'].replace('_', ' ').title()
                    ])
                
                tabela_conciliadas = Table(dados_conciliadas, colWidths=[1.5*cm, 3*cm, 3.5*cm, 3*cm, 3.5*cm, 4*cm])
                tabela_conciliadas.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('ALIGN', (0, 1), (0, -1), 'CENTER'),
                    ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                    ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                elementos.append(tabela_conciliadas)
            else:
                elementos.append(Paragraph("Nenhuma transação conciliada no período.", estilo_normal))
            
            elementos.append(Spacer(1, 0.5*cm))
            
            # 3. Discrepâncias identificadas
            elementos.append(Paragraph("3. Discrepâncias Identificadas", estilo_subtitulo))
            
            if self.discrepancias:
                dados_discrepancias = [["Data", "Descrição", "Valor", "Origem", "Tipo"]]
                
                for discrepancia in self.discrepancias:
                    dados_discrepancias.append([
                        discrepancia['data'].strftime('%d/%m/%Y'),
                        discrepancia['descricao'][:30] + "..." if len(discrepancia['descricao']) > 30 else discrepancia['descricao'],
                        f"Kz {discrepancia['valor']:,.2f}",
                        discrepancia['origem'],
                        discrepancia['tipo'].replace('_', ' ').title()
                    ])
                
                tabela_discrepancias = Table(dados_discrepancias, colWidths=[3*cm, 7*cm, 3*cm, 3*cm, 3*cm])
                tabela_discrepancias.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                elementos.append(tabela_discrepancias)
                
                # 4. Sugestões de correção
                elementos.append(Spacer(1, 0.5*cm))
                elementos.append(Paragraph("4. Sugestões de Correção", estilo_subtitulo))
                
                for i, discrepancia in enumerate(self.discrepancias[:10]):  # Limitar a 10 discrepâncias para não deixar o relatório muito grande
                    elementos.append(Paragraph(f"Discrepância {i+1}: {discrepancia['descricao']}", estilos['Heading3']))
                    elementos.append(Paragraph(f"Data: {discrepancia['data'].strftime('%d/%m/%Y')} | Valor: Kz {discrepancia['valor']:,.2f} | Origem: {discrepancia['origem']}", estilo_normal))
                    
                    if discrepancia['sugestao']:
                        for j, sugestao in enumerate(discrepancia['sugestao']):
                            if sugestao['tipo'] == 'generico':
                                elementos.append(Paragraph(f"Sugestão: {sugestao['mensagem']}", estilo_normal))
                            else:
                                elementos.append(Paragraph(f"Sugestão {j+1}: {sugestao['tipo'].replace('_', ' ').title()}", estilo_normal))
                                elementos.append(Paragraph(f"   - Data: {sugestao['data'].strftime('%d/%m/%Y')}", estilo_normal))
                                elementos.append(Paragraph(f"   - Descrição: {sugestao['descricao']}", estilo_normal))
                                elementos.append(Paragraph(f"   - Valor: Kz {sugestao['valor']:,.2f}", estilo_normal))
                                
                                if 'similaridade' in sugestao:
                                    elementos.append(Paragraph(f"   - Similaridade: {sugestao['similaridade']}%", estilo_normal))
                                
                                if 'diferenca_valor' in sugestao:
                                    elementos.append(Paragraph(f"   - Diferença de valor: Kz {sugestao['diferenca_valor']:,.2f}", estilo_normal))
                                
                                if 'dias_diferenca' in sugestao:
                                    elementos.append(Paragraph(f"   - Diferença de dias: {sugestao['dias_diferenca']}", estilo_normal))
                    else:
                        elementos.append(Paragraph("Sem sugestões disponíveis.", estilo_normal))
                    
                    elementos.append(Spacer(1, 0.3*cm))
            else:
                elementos.append(Paragraph("Nenhuma discrepância identificada no período.", estilo_normal))
            
            # Gerar PDF
            doc.build(elementos)
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório de conciliação: {str(e)}")
            return False
    
    def aplicar_sugestao(self, discrepancia_id, sugestao_id):
        """
        Aplica uma sugestão de correção a uma discrepância
        
        Args:
            discrepancia_id: ID da discrepância
            sugestao_id: ID da sugestão a ser aplicada
            
        Returns:
            bool: True se aplicada com sucesso, False caso contrário
        """
        try:
            if discrepancia_id < 0 or discrepancia_id >= len(self.discrepancias):
                return False
            
            discrepancia = self.discrepancias[discrepancia_id]
            
            if sugestao_id < 0 or sugestao_id >= len(discrepancia['sugestao']):
                return False
            
            sugestao = discrepancia['sugestao'][sugestao_id]
            
            # Registrar a aplicação da sugestão
            self.logger.info(f"Aplicando sugestão {sugestao_id} à discrepância {discrepancia_id}: {discrepancia['descricao']}")
            
            # Se a discrepância for do banco e não estiver no livro, criar lançamento contábil
            if discrepancia['origem'] == 'BANCO' and sugestao['tipo'] == 'generico':
                # Determinar contas com base na descrição
                conta_debito = self.contabilidade.determinar_conta_debito(discrepancia['descricao'])
                conta_credito = self.contabilidade.determinar_conta_credito(discrepancia['descricao'])
                
                # Criar lançamento
                lancamento = {
                    'id': f"B{len(self.contabilidade.lancamentos) + 1}",
                    'data': discrepancia['data'],
                    'descricao': discrepancia['descricao'],
                    'origem': 'BANCO',
                    'movimentos': [
                        {'conta': conta_debito, 'debito': discrepancia['valor'], 'credito': 0},
                        {'conta': conta_credito, 'debito': 0, 'credito': discrepancia['valor']}
                    ]
                }
                
                self.contabilidade.lancamentos.append(lancamento)
                self.contabilidade.salvar_dados()
                
                # Remover a discrepância da lista
                self.discrepancias.pop(discrepancia_id)
                
                return True
            
            # Se a sugestão for de valor similar, ajustar o valor
            elif sugestao['tipo'] == 'valor_similar':
                # Encontrar o lançamento correspondente
                for i, lanc in enumerate(self.contabilidade.lancamentos):
                    if (lanc['data'].date() == sugestao['data'].date() and 
                        lanc['descricao'] == sugestao['descricao']):
                        
                        # Ajustar o valor dos movimentos
                        for movimento in lanc['movimentos']:
                            if movimento['debito'] > 0:
                                movimento['debito'] = discrepancia['valor']
                            if movimento['credito'] > 0:
                                movimento['credito'] = discrepancia['valor']
                        
                        self.contabilidade.salvar_dados()
                        
                        # Remover a discrepância da lista
                        self.discrepancias.pop(discrepancia_id)
                        
                        return True
            
            # Se a sugestão for de data igual ou descrição similar, criar novo lançamento
            elif sugestao['tipo'] in ['data_igual', 'descricao_similar']:
                # Determinar contas com base na descrição
                conta_debito = self.contabilidade.determinar_conta_debito(discrepancia['descricao'])
                conta_credito = self.contabilidade.determinar_conta_credito(discrepancia['descricao'])
                
                # Criar lançamento
                lancamento = {
                    'id': f"B{len(self.contabilidade.lancamentos) + 1}",
                    'data': discrepancia['data'],
                    'descricao': discrepancia['descricao'],
                    'origem': 'BANCO',
                    'movimentos': [
                        {'conta': conta_debito, 'debito': discrepancia['valor'], 'credito': 0},
                        {'conta': conta_credito, 'debito': 0, 'credito': discrepancia['valor']}
                    ]
                }
                
                self.contabilidade.lancamentos.append(lancamento)
                self.contabilidade.salvar_dados()
                
                # Remover a discrepância da lista
                self.discrepancias.pop(discrepancia_id)
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar sugestão: {str(e)}")
            return False
