import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
import logging
import json
import os
import tkinter as tk

class FluxoCaixaProjetado:
    def __init__(self, contabilidade):
        """
        Inicializa o sistema de fluxo de caixa projetado
        
        Args:
            contabilidade: Instância da classe ContabilidadeAvancada
        """
        self.contabilidade = contabilidade
        self.logger = self._configurar_logger()
        self.previsoes = {
            'receitas': {},
            'despesas': {},
            'saldo': {}
        }
        self.lancamentos_recorrentes = []
        self.carregar_lancamentos_recorrentes()
        
    def _configurar_logger(self):
        """Configura o logger para registrar operações de fluxo de caixa"""
        logger = logging.getLogger('fluxo_caixa')
        logger.setLevel(logging.INFO)
        
        # Criar handler para arquivo
        fh = logging.FileHandler('fluxo_caixa.log')
        fh.setLevel(logging.INFO)
        
        # Criar formatador
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        # Adicionar handler ao logger
        logger.addHandler(fh)
        
        return logger
    
    def carregar_lancamentos_recorrentes(self):
        """Carrega os lançamentos recorrentes do arquivo JSON"""
        try:
            if os.path.exists('lancamentos_recorrentes.json'):
                with open('lancamentos_recorrentes.json', 'r', encoding='utf-8') as f:
                    self.lancamentos_recorrentes = json.load(f)
                    
                    # Converter strings de data para objetos datetime
                    for lanc in self.lancamentos_recorrentes:
                        if 'data_inicio' in lanc:
                            lanc['data_inicio'] = datetime.fromisoformat(lanc['data_inicio'])
                        if 'data_fim' in lanc and lanc['data_fim']:
                            lanc['data_fim'] = datetime.fromisoformat(lanc['data_fim'])
        except Exception as e:
            self.logger.error(f"Erro ao carregar lançamentos recorrentes: {str(e)}")
    
    def salvar_lancamentos_recorrentes(self):
        """Salva os lançamentos recorrentes em arquivo JSON"""
        try:
            # Converter objetos datetime para strings
            lanc_json = []
            for lanc in self.lancamentos_recorrentes:
                lanc_copy = lanc.copy()
                if 'data_inicio' in lanc_copy:
                    lanc_copy['data_inicio'] = lanc_copy['data_inicio'].isoformat()
                if 'data_fim' in lanc_copy and lanc_copy['data_fim']:
                    lanc_copy['data_fim'] = lanc_copy['data_fim'].isoformat()
                lanc_json.append(lanc_copy)
                
            with open('lancamentos_recorrentes.json', 'w', encoding='utf-8') as f:
                json.dump(lanc_json, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar lançamentos recorrentes: {str(e)}")
            return False
    
    def adicionar_lancamento_recorrente(self, descricao, valor, tipo, frequencia, 
                                       data_inicio, data_fim=None, conta_debito=None, 
                                       conta_credito=None, categoria=None):
        """
        Adiciona um novo lançamento recorrente
        
        Args:
            descricao: Descrição do lançamento
            valor: Valor do lançamento
            tipo: Tipo do lançamento ('receita' ou 'despesa')
            frequencia: Frequência do lançamento ('diario', 'semanal', 'mensal', 'trimestral', 'anual')
            data_inicio: Data de início do lançamento
            data_fim: Data de fim do lançamento (opcional)
            conta_debito: Conta de débito (opcional)
            conta_credito: Conta de crédito (opcional)
            categoria: Categoria do lançamento (opcional)
            
        Returns:
            bool: True se adicionado com sucesso, False caso contrário
        """
        try:
            # Validar parâmetros
            if not descricao or not valor or valor <= 0:
                return False
                
            if tipo not in ['receita', 'despesa']:
                return False
                
            if frequencia not in ['diario', 'semanal', 'mensal', 'trimestral', 'anual']:
                return False
            
            # Criar lançamento recorrente
            lancamento = {
                'id': len(self.lancamentos_recorrentes) + 1,
                'descricao': descricao,
                'valor': valor,
                'tipo': tipo,
                'frequencia': frequencia,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'conta_debito': conta_debito,
                'conta_credito': conta_credito,
                'categoria': categoria
            }
            
            self.lancamentos_recorrentes.append(lancamento)
            self.salvar_lancamentos_recorrentes()
            
            self.logger.info(f"Lançamento recorrente adicionado: {descricao}, {valor}, {tipo}, {frequencia}")
            
            return True
        except Exception as e:
            self.logger.error(f"Erro ao adicionar lançamento recorrente: {str(e)}")
            return False
    
    def remover_lancamento_recorrente(self, lancamento_id):
        """
        Remove um lançamento recorrente
        
        Args:
            lancamento_id: ID do lançamento a ser removido
            
        Returns:
            bool: True se removido com sucesso, False caso contrário
        """
        try:
            for i, lanc in enumerate(self.lancamentos_recorrentes):
                if lanc['id'] == lancamento_id:
                    self.lancamentos_recorrentes.pop(i)
                    self.salvar_lancamentos_recorrentes()
                    self.logger.info(f"Lançamento recorrente removido: {lancamento_id}")
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"Erro ao remover lançamento recorrente: {str(e)}")
            return False
    
    def gerar_previsao_fluxo_caixa(self, data_inicio, data_fim, incluir_recorrentes=True, 
                                  incluir_historico=True, metodo='arima'):
        """
        Gera uma previsão de fluxo de caixa para o período especificado
        
        Args:
            data_inicio: Data de início da previsão
            data_fim: Data de fim da previsão
            incluir_recorrentes: Se deve incluir lançamentos recorrentes
            incluir_historico: Se deve usar dados históricos para previsão
            metodo: Método de previsão ('media_movel', 'arima', 'tendencia')
            
        Returns:
            dict: Dicionário com as previsões de receitas, despesas e saldo
        """
        try:
            self.logger.info(f"Gerando previsão de fluxo de caixa de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
            
            # Inicializar dicionários de previsão
            self.previsoes = {
                'receitas': {},
                'despesas': {},
                'saldo': {}
            }
            
            # Gerar datas para o período
            datas = pd.date_range(start=data_inicio, end=data_fim, freq='D')
            for data in datas:
                data_str = data.strftime('%Y-%m-%d')
                self.previsoes['receitas'][data_str] = 0
                self.previsoes['despesas'][data_str] = 0
                self.previsoes['saldo'][data_str] = 0
            
            # 1. Incluir lançamentos recorrentes
            if incluir_recorrentes:
                self._incluir_lancamentos_recorrentes(data_inicio, data_fim)
            
            # 2. Incluir previsões baseadas em dados históricos
            if incluir_historico:
                self._incluir_previsoes_historicas(data_inicio, data_fim, metodo)
            
            # 3. Calcular saldo diário
            saldo_anterior = self._obter_saldo_atual()
            for data in sorted(self.previsoes['receitas'].keys()):
                receita_dia = self.previsoes['receitas'][data]
                despesa_dia = self.previsoes['despesas'][data]
                saldo_dia = saldo_anterior + receita_dia - despesa_dia
                self.previsoes['saldo'][data] = saldo_dia
                saldo_anterior = saldo_dia
            
            self.logger.info(f"Previsão de fluxo de caixa gerada com sucesso")
            
            return self.previsoes
        except Exception as e:
            self.logger.error(f"Erro ao gerar previsão de fluxo de caixa: {str(e)}")
            return None
    
    def _incluir_lancamentos_recorrentes(self, data_inicio, data_fim):
        """
        Inclui os lançamentos recorrentes na previsão
        """
        for lanc in self.lancamentos_recorrentes:
            # Verificar se o lançamento está ativo no período
            if lanc['data_inicio'] > data_fim:
                continue
                
            if lanc['data_fim'] and lanc['data_fim'] < data_inicio:
                continue
            
            # Determinar datas de ocorrência do lançamento no período
            datas_ocorrencia = self._calcular_datas_ocorrencia(
                lanc['data_inicio'], 
                lanc['data_fim'] if lanc['data_fim'] else data_fim,
                lanc['frequencia'],
                data_inicio,
                data_fim
            )
            
            # Adicionar valores às previsões
            for data in datas_ocorrencia:
                data_str = data.strftime('%Y-%m-%d')
                if data_str in self.previsoes[lanc['tipo'] + 's']:
                    self.previsoes[lanc['tipo'] + 's'][data_str] += lanc['valor']
    
    def _calcular_datas_ocorrencia(self, data_inicio, data_fim, frequencia, periodo_inicio, periodo_fim):
        """
        Calcula as datas de ocorrência de um lançamento recorrente dentro de um período
        """
        datas = []
        
        # Ajustar data de início para não ser anterior ao início do período
        data_atual = max(data_inicio, periodo_inicio)
        
        # Ajustar data de fim para não ser posterior ao fim do período
        data_limite = min(data_fim, periodo_fim)
        
        # Calcular datas de ocorrência com base na frequência
        if frequencia == 'diario':
            datas = pd.date_range(start=data_atual, end=data_limite, freq='D')
        
        elif frequencia == 'semanal':
            # Encontrar o próximo dia da semana correspondente
            dia_semana = data_inicio.weekday()
            data_atual = max(data_inicio, periodo_inicio)
            while data_atual <= data_limite:
                if data_atual >= periodo_inicio:
                    datas.append(data_atual)
                data_atual += timedelta(days=7)
        
        elif frequencia == 'mensal':
            # Encontrar o mesmo dia do mês
            dia_mes = data_inicio.day
            data_atual = data_inicio
            while data_atual <= data_limite:
                if data_atual >= periodo_inicio:
                    datas.append(data_atual)
                
                # Avançar para o próximo mês
                mes = data_atual.month + 1
                ano = data_atual.year
                if mes > 12:
                    mes = 1
                    ano += 1
                
                # Ajustar para o último dia do mês se necessário
                try:
                    data_atual = datetime(ano, mes, dia_mes)
                except ValueError:
                    # Se o dia não existir no mês (ex: 31 de fevereiro), usar o último dia
                    if mes == 2:
                        data_atual = datetime(ano, mes, 28)
                        # Verificar se é ano bissexto
                        if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0):
                            data_atual = datetime(ano, mes, 29)
                    elif mes in [4, 6, 9, 11]:
                        data_atual = datetime(ano, mes, 30)
                    else:
                        data_atual = datetime(ano, mes, 31)
        
        elif frequencia == 'trimestral':
            # Encontrar o mesmo dia a cada 3 meses
            dia_mes = data_inicio.day
            data_atual = data_inicio
            while data_atual <= data_limite:
                if data_atual >= periodo_inicio:
                    datas.append(data_atual)
                
                # Avançar 3 meses
                mes = data_atual.month + 3
                ano = data_atual.year
                while mes > 12:
                    mes -= 12
                    ano += 1
                
                # Ajustar para o último dia do mês se necessário
                try:
                    data_atual = datetime(ano, mes, dia_mes)
                except ValueError:
                    # Se o dia não existir no mês, usar o último dia
                    if mes == 2:
                        data_atual = datetime(ano, mes, 28)
                        # Verificar se é ano bissexto
                        if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0):
                            data_atual = datetime(ano, mes, 29)
                    elif mes in [4, 6, 9, 11]:
                        data_atual = datetime(ano, mes, 30)
                    else:
                        data_atual = datetime(ano, mes, 31)
        
        elif frequencia == 'anual':
            # Encontrar o mesmo dia e mês a cada ano
            dia = data_inicio.day
            mes = data_inicio.month
            for ano in range(data_inicio.year, data_limite.year + 1):
                try:
                    data = datetime(ano, mes, dia)
                    if periodo_inicio <= data <= data_limite:
                        datas.append(data)
                except ValueError:
                    # Se o dia não existir no mês (ex: 29 de fevereiro em ano não bissexto)
                    if mes == 2 and dia > 28:
                        # Verificar se é ano bissexto
                        if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0):
                            data = datetime(ano, mes, 29)
                        else:
                            data = datetime(ano, mes, 28)
                        
                        if periodo_inicio <= data <= data_limite:
                            datas.append(data)
        
        return datas
    
    def _incluir_previsoes_historicas(self, data_inicio, data_fim, metodo):
        """
        Inclui previsões baseadas em dados históricos
        """
        # Converter lançamentos para DataFrame
        if not self.contabilidade.lancamentos:
            return
        
        df_lancamentos = self._converter_lancamentos_para_dataframe()
        
        # Separar receitas e despesas
        df_receitas = df_lancamentos[df_lancamentos['tipo'] == 'receita']
        df_despesas = df_lancamentos[df_lancamentos['tipo'] == 'despesa']
        
        # Agrupar por data
        df_receitas_diarias = df_receitas.groupby('data')['valor'].sum().reset_index()
        df_despesas_diarias = df_despesas.groupby('data')['valor'].sum().reset_index()
        
        # Criar séries temporais
        if not df_receitas_diarias.empty:
            serie_receitas = pd.Series(df_receitas_diarias['valor'].values, index=df_receitas_diarias['data'])
            serie_receitas = serie_receitas.asfreq('D', fill_value=0)
        else:
            serie_receitas = pd.Series([], dtype='float64')
        
        if not df_despesas_diarias.empty:
            serie_despesas = pd.Series(df_despesas_diarias['valor'].values, index=df_despesas_diarias['data'])
            serie_despesas = serie_despesas.asfreq('D', fill_value=0)
        else:
            serie_despesas = pd.Series([], dtype='float64')
        
        # Gerar previsões com base no método escolhido
        if metodo == 'media_movel':
            self._prever_media_movel(serie_receitas, serie_despesas, data_inicio, data_fim)
        elif metodo == 'arima':
            self._prever_arima(serie_receitas, serie_despesas, data_inicio, data_fim)
        elif metodo == 'tendencia':
            self._prever_tendencia(serie_receitas, serie_despesas, data_inicio, data_fim)
    
    def _converter_lancamentos_para_dataframe(self):
        """
        Converte os lançamentos contábeis para um DataFrame
        """
        dados = []
        
        for lanc in self.contabilidade.lancamentos:
            # Determinar se é receita ou despesa
            tipo = None
            valor = 0
            
            for movimento in lanc['movimentos']:
                if movimento['conta'].startswith('7'):  # Receitas
                    tipo = 'receita'
                    valor = movimento['credito']
                    break
                elif movimento['conta'].startswith('6'):  # Despesas
                    tipo = 'despesa'
                    valor = movimento['debito']
                    break
            
            # Se não foi possível determinar, verificar pelo valor
            if tipo is None:
                for movimento in lanc['movimentos']:
                    if movimento['conta'].startswith('4'):  # Contas de caixa e bancos
                        if movimento['debito'] > 0:
                            tipo = 'receita'
                            valor = movimento['debito']
                        elif movimento['credito'] > 0:
                            tipo = 'despesa'
                            valor = movimento['credito']
                        break
            
            # Se ainda não foi possível determinar, pular
            if tipo is None:
                continue
            
            dados.append({
                'data': lanc['data'],
                'descricao': lanc['descricao'],
                'valor': valor,
                'tipo': tipo
            })
        
        return pd.DataFrame(dados)
    
    def _prever_media_movel(self, serie_receitas, serie_despesas, data_inicio, data_fim):
        """
        Gera previsões usando média móvel
        """
        # Calcular médias dos últimos 30 dias
        if not serie_receitas.empty:
            media_receitas = serie_receitas[-30:].mean() if len(serie_receitas) >= 30 else serie_receitas.mean()
        else:
            media_receitas = 0
            
        if not serie_despesas.empty:
            media_despesas = serie_despesas[-30:].mean() if len(serie_despesas) >= 30 else serie_despesas.mean()
        else:
            media_despesas = 0
        
        # Aplicar médias aos dias do período de previsão
        datas = pd.date_range(start=data_inicio, end=data_fim, freq='D')
        for data in datas:
            data_str = data.strftime('%Y-%m-%d')
            self.previsoes['receitas'][data_str] += media_receitas
            self.previsoes['despesas'][data_str] += media_despesas
    
    def _prever_arima(self, serie_receitas, serie_despesas, data_inicio, data_fim):
        """
        Gera previsões usando modelo ARIMA
        """
        # Calcular número de dias a prever
        dias_previsao = (data_fim - data_inicio).days + 1
        
        # Prever receitas
        if len(serie_receitas) >= 30:  # Precisamos de dados suficientes para o modelo
            try:
                # Ajustar modelo ARIMA (p,d,q) = (5,1,0) - parâmetros podem ser ajustados
                modelo_receitas = ARIMA(serie_receitas, order=(5,1,0))
                resultado_receitas = modelo_receitas.fit()
                
                # Gerar previsões
                previsao_receitas = resultado_receitas.forecast(steps=dias_previsao)
                
                # Aplicar previsões
                datas = pd.date_range(start=data_inicio, end=data_fim, freq='D')
                for i, data in enumerate(datas):
                    data_str = data.strftime('%Y-%m-%d')
                    # Garantir que a previsão não seja negativa
                    valor_previsto = max(0, previsao_receitas[i])
                    self.previsoes['receitas'][data_str] += valor_previsto
            except Exception as e:
                self.logger.warning(f"Erro ao gerar previsão ARIMA para receitas: {str(e)}")
                # Usar média móvel como fallback
                self._prever_media_movel(serie_receitas, pd.Series(), data_inicio, data_fim)
        else:
            # Usar média móvel se não houver dados suficientes
            self._prever_media_movel(serie_receitas, pd.Series(), data_inicio, data_fim)
        
        # Prever despesas
        if len(serie_despesas) >= 30:
            try:
                # Ajustar modelo ARIMA
                modelo_despesas = ARIMA(serie_despesas, order=(5,1,0))
                resultado_despesas = modelo_despesas.fit()
                
                # Gerar previsões
                previsao_despesas = resultado_despesas.forecast(steps=dias_previsao)
                
                # Aplicar previsões
                datas = pd.date_range(start=data_inicio, end=data_fim, freq='D')
                for i, data in enumerate(datas):
                    data_str = data.strftime('%Y-%m-%d')
                    # Garantir que a previsão não seja negativa
                    valor_previsto = max(0, previsao_despesas[i])
                    self.previsoes['despesas'][data_str] += valor_previsto
            except Exception as e:
                self.logger.warning(f"Erro ao gerar previsão ARIMA para despesas: {str(e)}")
                # Usar média móvel como fallback
                self._prever_media_movel(pd.Series(), serie_despesas, data_inicio, data_fim)
        else:
            # Usar média móvel se não houver dados suficientes
            self._prever_media_movel(pd.Series(), serie_despesas, data_inicio, data_fim)
    
    def _prever_tendencia(self, serie_receitas, serie_despesas, data_inicio, data_fim):
        """
        Gera previsões usando análise de tendência linear
        """
        # Calcular número de dias a prever
        dias_previsao = (data_fim - data_inicio).days + 1
        
        # Prever receitas
        if len(serie_receitas) >= 10:  # Precisamos de dados suficientes
            try:
                # Criar variável independente (dias sequenciais)
                X = np.arange(len(serie_receitas)).reshape(-1, 1)
                y = serie_receitas.values
                
                # Ajustar modelo de regressão linear
                modelo = sm.OLS(y, sm.add_constant(X)).fit()
                
                # Gerar previsões
                X_prev = np.arange(len(serie_receitas), len(serie_receitas) + dias_previsao).reshape(-1, 1)
                previsao_receitas = modelo.predict(sm.add_constant(X_prev))
                
                # Aplicar previsões
                datas = pd.date_range(start=data_inicio, end=data_fim, freq='D')
                for i, data in enumerate(datas):
                    data_str = data.strftime('%Y-%m-%d')
                    # Garantir que a previsão não seja negativa
                    valor_previsto = max(0, previsao_receitas[i])
                    self.previsoes['receitas'][data_str] += valor_previsto
            except Exception as e:
                self.logger.warning(f"Erro ao gerar previsão de tendência para receitas: {str(e)}")
                # Usar média móvel como fallback
                self._prever_media_movel(serie_receitas, pd.Series(), data_inicio, data_fim)
        else:
            # Usar média móvel se não houver dados suficientes
            self._prever_media_movel(serie_receitas, pd.Series(), data_inicio, data_fim)
        
        # Prever despesas
        if len(serie_despesas) >= 10:
            try:
                # Criar variável independente (dias sequenciais)
                X = np.arange(len(serie_despesas)).reshape(-1, 1)
                y = serie_despesas.values
                
                # Ajustar modelo de regressão linear
                modelo = sm.OLS(y, sm.add_constant(X)).fit()
                
                # Gerar previsões
                X_prev = np.arange(len(serie_despesas), len(serie_despesas) + dias_previsao).reshape(-1, 1)
                previsao_despesas = modelo.predict(sm.add_constant(X_prev))
                
                # Aplicar previsões
                datas = pd.date_range(start=data_inicio, end=data_fim, freq='D')
                for i, data in enumerate(datas):
                    data_str = data.strftime('%Y-%m-%d')
                    # Garantir que a previsão não seja negativa
                    valor_previsto = max(0, previsao_despesas[i])
                    self.previsoes['despesas'][data_str] += valor_previsto
            except Exception as e:
                self.logger.warning(f"Erro ao gerar previsão de tendência para despesas: {str(e)}")
                # Usar média móvel como fallback
                self._prever_media_movel(pd.Series(), serie_despesas, data_inicio, data_fim)
        else:
            # Usar média móvel se não houver dados suficientes
            self._prever_media_movel(pd.Series(), serie_despesas, data_inicio, data_fim)
    
    def _obter_saldo_atual(self):
        """
        Obtém o saldo atual das contas de caixa e bancos
        """
        saldo = 0
        
        # Verificar se há lançamentos
        if not self.contabilidade.lancamentos:
            return saldo
        
        # Calcular saldo das contas de caixa e bancos (classe 4)
        for lancamento in self.contabilidade.lancamentos:
            for movimento in lancamento['movimentos']:
                if movimento['conta'].startswith('4'):  # Contas de caixa e bancos
                    saldo += movimento['debito'] - movimento['credito']
        
        return saldo
    
    def gerar_relatorio_fluxo_caixa(self, caminho_saida):
        """
        Gera um relatório de fluxo de caixa projetado
        
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
            elementos.append(Paragraph("Relatório de Fluxo de Caixa Projetado", estilo_titulo))
            elementos.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilo_normal))
            elementos.append(Spacer(1, 0.5*cm))
            
            # Verificar se há previsões
            if not self.previsoes['receitas']:
                elementos.append(Paragraph("Nenhuma previsão de fluxo de caixa disponível.", estilo_normal))
                doc.build(elementos)
                return True
            
            # 1. Resumo mensal
            elementos.append(Paragraph("1. Resumo Mensal", estilo_subtitulo))
            
            # Agrupar por mês
            resumo_mensal = self._agrupar_por_mes()
            
            dados_resumo = [["Mês", "Receitas", "Despesas", "Saldo"]]
            
            for mes, valores in sorted(resumo_mensal.items()):
                dados_resumo.append([
                    mes,
                    f"Kz {valores['receitas']:,.2f}",
                    f"Kz {valores['despesas']:,.2f}",
                    f"Kz {valores['saldo']:,.2f}"
                ])
            
            # Adicionar total
            total_receitas = sum(v['receitas'] for v in resumo_mensal.values())
            total_despesas = sum(v['despesas'] for v in resumo_mensal.values())
            total_saldo = total_receitas - total_despesas
            
            dados_resumo.append([
                "TOTAL",
                f"Kz {total_receitas:,.2f}",
                f"Kz {total_despesas:,.2f}",
                f"Kz {total_saldo:,.2f}"
            ])
            
            tabela_resumo = Table(dados_resumo, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
            tabela_resumo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 1), (3, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elementos.append(tabela_resumo)
            elementos.append(Spacer(1, 0.5*cm))
            
            # 2. Detalhamento diário (primeiros 30 dias)
            elementos.append(Paragraph("2. Detalhamento Diário (Próximos 30 dias)", estilo_subtitulo))
            
            dados_diarios = [["Data", "Receitas", "Despesas", "Saldo Diário", "Saldo Acumulado"]]
            
            # Ordenar datas
            datas_ordenadas = sorted(self.previsoes['receitas'].keys())
            
            # Limitar a 30 dias
            datas_exibir = datas_ordenadas[:30]
            
            saldo_acumulado = self._obter_saldo_atual()
            
            for data_str in datas_exibir:
                data_obj = datetime.fromisoformat(data_str)
                receita_dia = self.previsoes['receitas'][data_str]
                despesa_dia = self.previsoes['despesas'][data_str]
                saldo_dia = receita_dia - despesa_dia
                saldo_acumulado += saldo_dia
                
                dados_diarios.append([
                    data_obj.strftime('%d/%m/%Y'),
                    f"Kz {receita_dia:,.2f}",
                    f"Kz {despesa_dia:,.2f}",
                    f"Kz {saldo_dia:,.2f}",
                    f"Kz {saldo_acumulado:,.2f}"
                ])
            
            tabela_diaria = Table(dados_diarios, colWidths=[3*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
            tabela_diaria.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('ALIGN', (1, 1), (4, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            elementos.append(tabela_diaria)
            elementos.append(Spacer(1, 0.5*cm))
            
            # 3. Lançamentos recorrentes
            elementos.append(Paragraph("3. Lançamentos Recorrentes", estilo_subtitulo))
            
            if self.lancamentos_recorrentes:
                dados_recorrentes = [["Descrição", "Valor", "Tipo", "Frequência", "Próxima Data"]]
                
                for lanc in self.lancamentos_recorrentes:
                    # Calcular próxima data
                    proxima_data = self._calcular_proxima_data(lanc)
                    
                    dados_recorrentes.append([
                        lanc['descricao'],
                        f"Kz {lanc['valor']:,.2f}",
                        lanc['tipo'].capitalize(),
                        lanc['frequencia'].capitalize(),
                        proxima_data.strftime('%d/%m/%Y') if proxima_data else "N/A"
                    ])
                
                tabela_recorrentes = Table(dados_recorrentes, colWidths=[7*cm, 3*cm, 2*cm, 3*cm, 3*cm])
                tabela_recorrentes.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                elementos.append(tabela_recorrentes)
            else:
                elementos.append(Paragraph("Nenhum lançamento recorrente cadastrado.", estilo_normal))
            
            # Gerar PDF
            doc.build(elementos)
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório de fluxo de caixa: {str(e)}")
            return False
    
    def _agrupar_por_mes(self):
        """
        Agrupa as previsões por mês
        """
        resumo_mensal = {}
        
        for data_str in self.previsoes['receitas'].keys():
            data_obj = datetime.fromisoformat(data_str)
            mes_ano = data_obj.strftime('%m/%Y')
            
            if mes_ano not in resumo_mensal:
                resumo_mensal[mes_ano] = {
                    'receitas': 0,
                    'despesas': 0,
                    'saldo': 0
                }
            
            receita_dia = self.previsoes['receitas'][data_str]
            despesa_dia = self.previsoes['despesas'][data_str]
            saldo_dia = receita_dia - despesa_dia
            
            resumo_mensal[mes_ano]['receitas'] += receita_dia
            resumo_mensal[mes_ano]['despesas'] += despesa_dia
            resumo_mensal[mes_ano]['saldo'] += saldo_dia
        
        return resumo_mensal
    
    def _calcular_proxima_data(self, lancamento):
        """
        Calcula a próxima data de ocorrência de um lançamento recorrente
        """
        hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Se a data de início for futura, essa é a próxima data
        if lancamento['data_inicio'] > hoje:
            return lancamento['data_inicio']
        
        # Se tiver data de fim e for no passado, não há próxima data
        if lancamento['data_fim'] and lancamento['data_fim'] < hoje:
            return None
        
        # Calcular próxima data com base na frequência
        if lancamento['frequencia'] == 'diario':
            return hoje
        
        elif lancamento['frequencia'] == 'semanal':
            # Encontrar o próximo dia da semana correspondente
            dia_semana = lancamento['data_inicio'].weekday()
            dias_para_adicionar = (dia_semana - hoje.weekday()) % 7
            if dias_para_adicionar == 0:
                dias_para_adicionar = 7
            return hoje + timedelta(days=dias_para_adicionar)
        
        elif lancamento['frequencia'] == 'mensal':
            # Encontrar o mesmo dia do mês
            dia_mes = lancamento['data_inicio'].day
            
            # Tentar o mês atual
            try:
                proxima_data = hoje.replace(day=dia_mes)
                if proxima_data < hoje:
                    # Se for no passado, tentar o próximo mês
                    if hoje.month == 12:
                        proxima_data = proxima_data.replace(year=hoje.year + 1, month=1)
                    else:
                        proxima_data = proxima_data.replace(month=hoje.month + 1)
                return proxima_data
            except ValueError:
                # Se o dia não existir no mês atual (ex: 31 de fevereiro)
                if hoje.month == 12:
                    mes = 1
                    ano = hoje.year + 1
                else:
                    mes = hoje.month + 1
                    ano = hoje.year
                
                # Ajustar para o último dia do mês
                if mes == 2:
                    ultimo_dia = 28
                    # Verificar se é ano bissexto
                    if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0):
                        ultimo_dia = 29
                elif mes in [4, 6, 9, 11]:
                    ultimo_dia = 30
                else:
                    ultimo_dia = 31
                
                return datetime(ano, mes, min(dia_mes, ultimo_dia))
        
        elif lancamento['frequencia'] == 'trimestral':
            # Encontrar o mesmo dia a cada 3 meses
            dia_mes = lancamento['data_inicio'].day
            
            # Calcular o próximo trimestre
            mes_atual = hoje.month
            mes_proximo = ((mes_atual - 1) // 3 * 3 + 3) % 12 + 1
            ano_proximo = hoje.year + (1 if mes_proximo < mes_atual else 0)
            
            # Ajustar para o último dia do mês se necessário
            try:
                proxima_data = datetime(ano_proximo, mes_proximo, dia_mes)
                if proxima_data < hoje:
                    # Se for no passado, avançar mais um trimestre
                    mes_proximo = (mes_proximo + 2) % 12 + 1
                    ano_proximo = ano_proximo + (1 if mes_proximo < 4 else 0)
                    proxima_data = datetime(ano_proximo, mes_proximo, dia_mes)
                return proxima_data
            except ValueError:
                # Se o dia não existir no mês
                if mes_proximo == 2:
                    ultimo_dia = 28
                    # Verificar se é ano bissexto
                    if ano_proximo % 4 == 0 and (ano_proximo % 100 != 0 or ano_proximo % 400 == 0):
                        ultimo_dia = 29
                elif mes_proximo in [4, 6, 9, 11]:
                    ultimo_dia = 30
                else:
                    ultimo_dia = 31
                
                return datetime(ano_proximo, mes_proximo, min(dia_mes, ultimo_dia))
        
        elif lancamento['frequencia'] == 'anual':
            # Encontrar o mesmo dia e mês a cada ano
            dia = lancamento['data_inicio'].day
            mes = lancamento['data_inicio'].month
            
            # Tentar o ano atual
            try:
                proxima_data = datetime(hoje.year, mes, dia)
                if proxima_data < hoje:
                    # Se for no passado, tentar o próximo ano
                    proxima_data = datetime(hoje.year + 1, mes, dia)
                return proxima_data
            except ValueError:
                # Se o dia não existir no mês (ex: 29 de fevereiro em ano não bissexto)
                if mes == 2:
                    # Verificar se o próximo ano é bissexto
                    ano = hoje.year if datetime(hoje.year, mes, 1) > hoje else hoje.year + 1
                    if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0):
                        return datetime(ano, mes, min(dia, 29))
                    else:
                        return datetime(ano, mes, 28)
                else:
                    return None  # Não deveria chegar aqui
        
        return None
    
    def gerar_grafico_fluxo_caixa(self, canvas, periodo='mensal'):
        """
        Gera um gráfico de fluxo de caixa projetado
        
        Args:
            canvas: Canvas do Tkinter onde o gráfico será exibido
            periodo: Período de agrupamento ('diario', 'semanal', 'mensal')
            
        Returns:
            FigureCanvasTkAgg: Canvas do matplotlib
        """
        try:
            # Verificar se há previsões
            if not self.previsoes['receitas']:
                return None
            
            # Criar figura
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Preparar dados com base no período
            if periodo == 'diario':
                # Usar os primeiros 30 dias
                datas_ordenadas = sorted(self.previsoes['receitas'].keys())[:30]
                datas = [datetime.fromisoformat(d).strftime('%d/%m') for d in datas_ordenadas]
                receitas = [self.previsoes['receitas'][d] for d in datas_ordenadas]
                despesas = [self.previsoes['despesas'][d] for d in datas_ordenadas]
                saldos = [self.previsoes['saldo'][d] for d in datas_ordenadas]
                
                titulo = "Fluxo de Caixa Diário (Próximos 30 dias)"
                
            elif periodo == 'semanal':
                # Agrupar por semana
                dados_semanais = self._agrupar_por_semana()
                datas = [d for d in sorted(dados_semanais.keys())]
                receitas = [dados_semanais[d]['receitas'] for d in datas]
                despesas = [dados_semanais[d]['despesas'] for d in datas]
                saldos = [dados_semanais[d]['saldo'] for d in datas]
                
                titulo = "Fluxo de Caixa Semanal"
                
            else:  # mensal
                # Agrupar por mês
                dados_mensais = self._agrupar_por_mes()
                datas = [d for d in sorted(dados_mensais.keys())]
                receitas = [dados_mensais[d]['receitas'] for d in datas]
                despesas = [dados_mensais[d]['despesas'] for d in datas]
                saldos = [dados_mensais[d]['saldo'] for d in datas]
                
                titulo = "Fluxo de Caixa Mensal"
            
            # Plotar gráfico de barras para receitas e despesas
            x = np.arange(len(datas))
            largura = 0.35
            
            ax.bar(x - largura/2, receitas, largura, label='Receitas', color='green', alpha=0.7)
            ax.bar(x + largura/2, despesas, largura, label='Despesas', color='red', alpha=0.7)
            
            # Plotar linha para saldo
            ax2 = ax.twinx()
            ax2.plot(x, saldos, 'b-', label='Saldo', linewidth=2)
            
            # Configurar eixos e legendas
            ax.set_xlabel('Período')
            ax.set_ylabel('Valor (Kz)')
            ax2.set_ylabel('Saldo (Kz)')
            
            ax.set_title(titulo)
            ax.set_xticks(x)
            ax.set_xticklabels(datas, rotation=45)
            
            # Adicionar legendas
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            # Ajustar layout
            plt.tight_layout()
            
            # Criar canvas para Tkinter
            canvas_fig = FigureCanvasTkAgg(fig, master=canvas)
            canvas_fig.draw()
            canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            return canvas_fig
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar gráfico de fluxo de caixa: {str(e)}")
            return None
    
    def _agrupar_por_semana(self):
        """
        Agrupa as previsões por semana
        """
        resumo_semanal = {}
        
        for data_str in self.previsoes['receitas'].keys():
            data_obj = datetime.fromisoformat(data_str)
            # Calcular o número da semana no ano
            semana = data_obj.strftime('%U')
            ano = data_obj.year
            semana_ano = f"Sem {semana}/{ano}"
            
            if semana_ano not in resumo_semanal:
                resumo_semanal[semana_ano] = {
                    'receitas': 0,
                    'despesas': 0,
                    'saldo': 0
                }
            
            receita_dia = self.previsoes['receitas'][data_str]
            despesa_dia = self.previsoes['despesas'][data_str]
            saldo_dia = receita_dia - despesa_dia
            
            resumo_semanal[semana_ano]['receitas'] += receita_dia
            resumo_semanal[semana_ano]['despesas'] += despesa_dia
            resumo_semanal[semana_ano]['saldo'] += saldo_dia
        
        return resumo_semanal