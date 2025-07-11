import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import tkinter as tk

class OrcamentoRealizado:
    def __init__(self, contabilidade):
        """
        Inicializa o sistema de comparação entre orçado e realizado
        
        Args:
            contabilidade: Instância da classe ContabilidadeAvancada
        """
        self.contabilidade = contabilidade
        self.logger = self._configurar_logger()
        self.orcamentos = {}
        self.carregar_orcamentos()
        
    def _configurar_logger(self):
        """Configura o logger para registrar operações de orçamento"""
        logger = logging.getLogger('orcamento')
        logger.setLevel(logging.INFO)
        
        # Criar handler para arquivo
        fh = logging.FileHandler('orcamento.log')
        fh.setLevel(logging.INFO)
        
        # Criar formatador
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        # Adicionar handler ao logger
        logger.addHandler(fh)
        
        return logger
    
    def carregar_orcamentos(self):
        """Carrega os orçamentos do arquivo JSON"""
        try:
            if os.path.exists('orcamentos.json'):
                with open('orcamentos.json', 'r', encoding='utf-8') as f:
                    self.orcamentos = json.load(f)
        except Exception as e:
            self.logger.error(f"Erro ao carregar orçamentos: {str(e)}")
    
    def salvar_orcamentos(self):
        """Salva os orçamentos em arquivo JSON"""
        try:
            with open('orcamentos.json', 'w', encoding='utf-8') as f:
                json.dump(self.orcamentos, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar orçamentos: {str(e)}")
            return False
    
    def definir_orcamento(self, ano, mes, categoria, valor, tipo):
        """
        Define um valor orçado para uma categoria em um determinado mês
        
        Args:
            ano: Ano do orçamento
            mes: Mês do orçamento (1-12)
            categoria: Categoria do orçamento (ex: 'Vendas', 'Salários', etc.)
            valor: Valor orçado
            tipo: Tipo do orçamento ('receita' ou 'despesa')
            
        Returns:
            bool: True se definido com sucesso, False caso contrário
        """
        try:
            # Validar parâmetros
            if not isinstance(ano, int) or ano < 2000 or ano > 2100:
                return False
                
            if not isinstance(mes, int) or mes < 1 or mes > 12:
                return False
                
            if not categoria or not isinstance(categoria, str):
                return False
                
            if not isinstance(valor, (int, float)) or valor < 0:
                return False
                
            if tipo not in ['receita', 'despesa']:
                return False
            
            # Criar estrutura de ano se não existir
            if str(ano) not in self.orcamentos:
                self.orcamentos[str(ano)] = {}
            
            # Criar estrutura de mês se não existir
            if str(mes) not in self.orcamentos[str(ano)]:
                self.orcamentos[str(ano)][str(mes)] = {
                    'receitas': {},
                    'despesas': {}
                }
            
            # Definir valor orçado
            self.orcamentos[str(ano)][str(mes)][tipo + 's'][categoria] = valor
            
            # Salvar alterações
            self.salvar_orcamentos()
            
            self.logger.info(f"Orçamento definido: {ano}/{mes}, {categoria}, {tipo}, {valor}")
            
            return True
        except Exception as e:
            self.logger.error(f"Erro ao definir orçamento: {str(e)}")
            return False
    
    def obter_orcamento(self, ano, mes=None):
        """
        Obtém os valores orçados para um determinado ano/mês
        
        Args:
            ano: Ano do orçamento
            mes: Mês do orçamento (opcional, se não informado retorna todo o ano)
            
        Returns:
            dict: Dicionário com os valores orçados
        """
        try:
            if str(ano) not in self.orcamentos:
                return {}
            
            if mes is not None:
                if str(mes) not in self.orcamentos[str(ano)]:
                    return {}
                return self.orcamentos[str(ano)][str(mes)]
            else:
                return self.orcamentos[str(ano)]
        except Exception as e:
            self.logger.error(f"Erro ao obter orçamento: {str(e)}")
            return {}
    
    def calcular_realizado(self, ano, mes=None):
        """
        Calcula os valores realizados para um determinado ano/mês
        
        Args:
            ano: Ano para cálculo
            mes: Mês para cálculo (opcional, se não informado calcula todo o ano)
            
        Returns:
            dict: Dicionário com os valores realizados
        """
        try:
            # Converter lançamentos para DataFrame
            if not self.contabilidade.lancamentos:
                return {'receitas': {}, 'despesas': {}}
            
            df_lancamentos = self._converter_lancamentos_para_dataframe()
            
            # Filtrar por ano
            df_ano = df_lancamentos[df_lancamentos['data'].dt.year == ano]
            
            # Filtrar por mês se informado
            if mes is not None:
                df_filtrado = df_ano[df_ano['data'].dt.month == mes]
            else:
                df_filtrado = df_ano
            
            # Separar receitas e despesas
            df_receitas = df_filtrado[df_filtrado['tipo'] == 'receita']
            df_despesas = df_filtrado[df_filtrado['tipo'] == 'despesa']
            
            # Agrupar por categoria
            receitas_por_categoria = df_receitas.groupby('categoria')['valor'].sum().to_dict()
            despesas_por_categoria = df_despesas.groupby('categoria')['valor'].sum().to_dict()
            
            return {
                'receitas': receitas_por_categoria,
                'despesas': despesas_por_categoria
            }
        except Exception as e:
            self.logger.error(f"Erro ao calcular realizado: {str(e)}")
            return {'receitas': {}, 'despesas': {}}
    
    def _converter_lancamentos_para_dataframe(self):
        """
        Converte os lançamentos contábeis para um DataFrame
        """
        dados = []
        
        for lanc in self.contabilidade.lancamentos:
            # Determinar se é receita ou despesa
            tipo = None
            valor = 0
            categoria = "Não classificado"
            
            for movimento in lanc['movimentos']:
                if movimento['conta'].startswith('7'):  # Receitas
                    tipo = 'receita'
                    valor = movimento['credito']
                    # Determinar categoria com base na conta
                    categoria = self._determinar_categoria_por_conta(movimento['conta'])
                    break
                elif movimento['conta'].startswith('6'):  # Despesas
                    tipo = 'despesa'
                    valor = movimento['debito']
                    # Determinar categoria com base na conta
                    categoria = self._determinar_categoria_por_conta(movimento['conta'])
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
                'tipo': tipo,
                'categoria': categoria
            })
        
        return pd.DataFrame(dados)
    
    def _determinar_categoria_por_conta(self, codigo_conta):
        """
        Determina a categoria com base no código da conta
        """
        # Mapeamento de códigos de conta para categorias
        mapeamento = {
            # Receitas
            '71': 'Vendas',
            '72': 'Prestação de Serviços',
            '73': 'Impostos e Taxas',
            '74': 'Subsídios',
            '75': 'Receitas Financeiras',
            '76': 'Receitas de Imobilizações',
            '77': 'Reversões',
            '78': 'Receitas Extraordinárias',
            '79': 'Outras Receitas',
            
            # Despesas
            '61': 'Custo de Mercadorias',
            '62': 'Fornecimentos e Serviços',
            '63': 'Impostos',
            '64': 'Custos com Pessoal',
            '65': 'Despesas Financeiras',
            '66': 'Amortizações',
            '67': 'Provisões',
            '68': 'Despesas Extraordinárias',
            '69': 'Outras Despesas'
        }
        
        # Verificar se o código da conta está no mapeamento
        for prefixo, categoria in mapeamento.items():
            if codigo_conta.startswith(prefixo):
                return categoria
        
        return "Não classificado"
    
    def comparar_orcado_realizado(self, ano, mes=None):
        """
        Compara os valores orçados com os realizados
        
        Args:
            ano: Ano para comparação
            mes: Mês para comparação (opcional, se não informado compara todo o ano)
            
        Returns:
            dict: Dicionário com a comparação entre orçado e realizado
        """
        try:
            # Obter valores orçados
            orcado = self.obter_orcamento(ano, mes)
            
            # Obter valores realizados
            realizado = self.calcular_realizado(ano, mes)
            
            # Inicializar resultado
            resultado = {
                'receitas': {},
                'despesas': {},
                'total_orcado': {
                    'receitas': 0,
                    'despesas': 0
                },
                'total_realizado': {
                    'receitas': 0,
                    'despesas': 0
                }
            }
            
            # Processar receitas
            todas_categorias_receitas = set()
            if 'receitas' in orcado:
                todas_categorias_receitas.update(orcado['receitas'].keys())
            todas_categorias_receitas.update(realizado['receitas'].keys())
            
            for categoria in todas_categorias_receitas:
                valor_orcado = orcado.get('receitas', {}).get(categoria, 0)
                valor_realizado = realizado['receitas'].get(categoria, 0)
                diferenca = valor_realizado - valor_orcado
                percentual = (valor_realizado / valor_orcado * 100) if valor_orcado > 0 else 0
                
                resultado['receitas'][categoria] = {
                    'orcado': valor_orcado,
                    'realizado': valor_realizado,
                    'diferenca': diferenca,
                    'percentual': percentual
                }
                
                resultado['total_orcado']['receitas'] += valor_orcado
                resultado['total_realizado']['receitas'] += valor_realizado
            
            # Processar despesas
            todas_categorias_despesas = set()
            if 'despesas' in orcado:
                todas_categorias_despesas.update(orcado['despesas'].keys())
            todas_categorias_despesas.update(realizado['despesas'].keys())
            
            for categoria in todas_categorias_despesas:
                valor_orcado = orcado.get('despesas', {}).get(categoria, 0)
                valor_realizado = realizado['despesas'].get(categoria, 0)
                diferenca = valor_realizado - valor_orcado
                percentual = (valor_realizado / valor_orcado * 100) if valor_orcado > 0 else 0
                
                resultado['despesas'][categoria] = {
                    'orcado': valor_orcado,
                    'realizado': valor_realizado,
                    'diferenca': diferenca,
                    'percentual': percentual
                }
                
                resultado['total_orcado']['despesas'] += valor_orcado
                resultado['total_realizado']['despesas'] += valor_realizado
            
            # Calcular totais
            resultado['total_diferenca'] = {
                'receitas': resultado['total_realizado']['receitas'] - resultado['total_orcado']['receitas'],
                'despesas': resultado['total_realizado']['despesas'] - resultado['total_orcado']['despesas']
            }
            
            resultado['total_percentual'] = {
                'receitas': (resultado['total_realizado']['receitas'] / resultado['total_orcado']['receitas'] * 100) 
                            if resultado['total_orcado']['receitas'] > 0 else 0,
                'despesas': (resultado['total_realizado']['despesas'] / resultado['total_orcado']['despesas'] * 100) 
                            if resultado['total_orcado']['despesas'] > 0 else 0
            }
            
            return resultado
        except Exception as e:
            self.logger.error(f"Erro ao comparar orçado e realizado: {str(e)}")
            return {}
    
    def identificar_desvios_significativos(self, ano, mes=None, limite_percentual=20):
        """
        Identifica desvios significativos entre orçado e realizado
        
        Args:
            ano: Ano para análise
            mes: Mês para análise (opcional, se não informado analisa todo o ano)
            limite_percentual: Percentual limite para considerar um desvio significativo
            
        Returns:
            list: Lista de desvios significativos
        """
        try:
            # Comparar orçado e realizado
            comparacao = self.comparar_orcado_realizado(ano, mes)
            
            desvios = []
            
            # Verificar desvios em receitas
            for categoria, valores in comparacao['receitas'].items():
                if valores['orcado'] > 0:  # Evitar divisão por zero
                    percentual = abs(valores['diferenca'] / valores['orcado'] * 100)
                    
                    if percentual > limite_percentual:
                        desvios.append({
                            'tipo': 'receita',
                            'categoria': categoria,
                            'orcado': valores['orcado'],
                            'realizado': valores['realizado'],
                            'diferenca': valores['diferenca'],
                            'percentual': percentual,
                            'situacao': 'acima' if valores['diferenca'] > 0 else 'abaixo'
                        })
            
            # Verificar desvios em despesas
            for categoria, valores in comparacao['despesas'].items():
                if valores['orcado'] > 0:  # Evitar divisão por zero
                    percentual = abs(valores['diferenca'] / valores['orcado'] * 100)
                    
                    if percentual > limite_percentual:
                        desvios.append({
                            'tipo': 'despesa',
                            'categoria': categoria,
                            'orcado': valores['orcado'],
                            'realizado': valores['realizado'],
                            'diferenca': valores['diferenca'],
                            'percentual': percentual,
                            'situacao': 'acima' if valores['diferenca'] > 0 else 'abaixo'
                        })
            
            # Ordenar por percentual de desvio (decrescente)
            desvios.sort(key=lambda x: x['percentual'], reverse=True)
            
            return desvios
        except Exception as e:
            self.logger.error(f"Erro ao identificar desvios significativos: {str(e)}")
            return []
    
    def gerar_relatorio_orcado_realizado(self, ano, mes, caminho_saida):
        """
        Gera um relatório comparativo entre orçado e realizado
        
        Args:
            ano: Ano do relatório
            mes: Mês do relatório
            caminho_saida: Caminho do arquivo PDF de saída
            
        Returns:
            bool: True se gerado com sucesso, False caso contrário
        """
        try:
            # Obter comparação
            comparacao = self.comparar_orcado_realizado(ano, mes)
            
            # Identificar desvios
            desvios = self.identificar_desvios_significativos(ano, mes)
            
            # Criar documento PDF
            doc = SimpleDocTemplate(caminho_saida, pagesize=landscape(A4))
            elementos = []
            
            # Estilos
            estilos = getSampleStyleSheet()
            estilo_titulo = estilos['Heading1']
            estilo_subtitulo = estilos['Heading2']
            estilo_normal = estilos['Normal']
            
            # Título
            elementos.append(Paragraph("Relatório de Orçado vs. Realizado", estilo_titulo))
            elementos.append(Paragraph(f"Período: {mes}/{ano}", estilo_normal))
            elementos.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilo_normal))
            elementos.append(Spacer(1, 0.5*cm))
            
            # 1. Resumo
            elementos.append(Paragraph("1. Resumo", estilo_subtitulo))
            
            dados_resumo = [
                ["", "Orçado", "Realizado", "Diferença", "% Realização"],
                ["Receitas", f"Kz {comparacao['total_orcado']['receitas']:,.2f}", 
                 f"Kz {comparacao['total_realizado']['receitas']:,.2f}", 
                 f"Kz {comparacao['total_diferenca']['receitas']:,.2f}", 
                 f"{comparacao['total_percentual']['receitas']:.1f}%"],
                ["Despesas", f"Kz {comparacao['total_orcado']['despesas']:,.2f}", 
                 f"Kz {comparacao['total_realizado']['despesas']:,.2f}", 
                 f"Kz {comparacao['total_diferenca']['despesas']:,.2f}", 
                 f"{comparacao['total_percentual']['despesas']:.1f}%"],
                ["Resultado", f"Kz {comparacao['total_orcado']['receitas'] - comparacao['total_orcado']['despesas']:,.2f}", 
                 f"Kz {comparacao['total_realizado']['receitas'] - comparacao['total_realizado']['despesas']:,.2f}", 
                 f"Kz {(comparacao['total_realizado']['receitas'] - comparacao['total_realizado']['despesas']) - (comparacao['total_orcado']['receitas'] - comparacao['total_orcado']['despesas']):,.2f}", 
                 ""]
            ]
            
            tabela_resumo = Table(dados_resumo, colWidths=[4*cm, 5*cm, 5*cm, 5*cm, 3*cm])
            tabela_resumo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 1), (4, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elementos.append(tabela_resumo)
            elementos.append(Spacer(1, 0.5*cm))
            
            # 2. Detalhamento de Receitas
            elementos.append(Paragraph("2. Detalhamento de Receitas", estilo_subtitulo))
            
            if comparacao['receitas']:
                dados_receitas = [["Categoria", "Orçado", "Realizado", "Diferença", "% Realização"]]
                
                for categoria, valores in sorted(comparacao['receitas'].items()):
                    dados_receitas.append([
                        categoria,
                        f"Kz {valores['orcado']:,.2f}",
                        f"Kz {valores['realizado']:,.2f}",
                        f"Kz {valores['diferenca']:,.2f}",
                        f"{valores['percentual']:.1f}%"
                    ])
                
                tabela_receitas = Table(dados_receitas, colWidths=[6*cm, 5*cm, 5*cm, 5*cm, 3*cm])
                tabela_receitas.setStyle(TableStyle([
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
                elementos.append(tabela_receitas)
            else:
                elementos.append(Paragraph("Nenhuma receita orçada ou realizada no período.", estilo_normal))
            
            elementos.append(Spacer(1, 0.5*cm))
            
            # 3. Detalhamento de Despesas
            elementos.append(Paragraph("3. Detalhamento de Despesas", estilo_subtitulo))
            
            if comparacao['despesas']:
                dados_despesas = [["Categoria", "Orçado", "Realizado", "Diferença", "% Realização"]]
                
                for categoria, valores in sorted(comparacao['despesas'].items()):
                    dados_despesas.append([
                        categoria,
                        f"Kz {valores['orcado']:,.2f}",
                        f"Kz {valores['realizado']:,.2f}",
                        f"Kz {valores['diferenca']:,.2f}",
                        f"{valores['percentual']:.1f}%"
                    ])
                
                tabela_despesas = Table(dados_despesas, colWidths=[6*cm, 5*cm, 5*cm, 5*cm, 3*cm])
                tabela_despesas.setStyle(TableStyle([
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
                elementos.append(tabela_despesas)
            else:
                elementos.append(Paragraph("Nenhuma despesa orçada ou realizada no período.", estilo_normal))
            
            elementos.append(Spacer(1, 0.5*cm))
            
            # 4. Desvios Significativos
            elementos.append(Paragraph("4. Desvios Significativos", estilo_subtitulo))
            
            if desvios:
                dados_desvios = [["Tipo", "Categoria", "Orçado", "Realizado", "Diferença", "% Desvio", "Situação"]]
                
                for desvio in desvios:
                    dados_desvios.append([
                        desvio['tipo'].capitalize(),
                        desvio['categoria'],
                        f"Kz {desvio['orcado']:,.2f}",
                        f"Kz {desvio['realizado']:,.2f}",
                        f"Kz {desvio['diferenca']:,.2f}",
                        f"{desvio['percentual']:.1f}%",
                        desvio['situacao'].capitalize()
                    ])
                
                tabela_desvios = Table(dados_desvios, colWidths=[2*cm, 5*cm, 4*cm, 4*cm, 4*cm, 2.5*cm, 2.5*cm])
                tabela_desvios.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('ALIGN', (2, 1), (5, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                elementos.append(tabela_desvios)
                
                # 5. Recomendações
                elementos.append(Spacer(1, 0.5*cm))
                elementos.append(Paragraph("5. Recomendações", estilo_subtitulo))
                
                for desvio in desvios[:5]:  # Limitar às 5 principais recomendações
                    if desvio['tipo'] == 'receita':
                        if desvio['situacao'] == 'abaixo':
                            elementos.append(Paragraph(
                                f"• A receita de {desvio['categoria']} está {desvio['percentual']:.1f}% abaixo do orçado. "
                                f"Recomenda-se revisar as estratégias de vendas/captação para esta categoria.",
                                estilo_normal
                            ))
                        else:
                            elementos.append(Paragraph(
                                f"• A receita de {desvio['categoria']} está {desvio['percentual']:.1f}% acima do orçado. "
                                f"Considere ajustar o orçamento para refletir este aumento ou investigar se é um evento pontual.",
                                estilo_normal
                            ))
                    else:  # despesa
                        if desvio['situacao'] == 'acima':
                            elementos.append(Paragraph(
                                f"• A despesa de {desvio['categoria']} está {desvio['percentual']:.1f}% acima do orçado. "
                                f"Recomenda-se revisar os gastos nesta categoria e implementar medidas de controle.",
                                estilo_normal
                            ))
                        else:
                            elementos.append(Paragraph(
                                f"• A despesa de {desvio['categoria']} está {desvio['percentual']:.1f}% abaixo do orçado. "
                                f"Verifique se há atrasos em pagamentos ou se o orçamento pode ser ajustado.",
                                estilo_normal
                            ))
            else:
                elementos.append(Paragraph("Não foram identificados desvios significativos no período.", estilo_normal))
            
            # Gerar PDF
            doc.build(elementos)
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório de orçado vs. realizado: {str(e)}")
            return False
    
    def gerar_grafico_orcado_realizado(self, canvas, ano, mes=None, tipo='ambos'):
        """
        Gera um gráfico comparativo entre orçado e realizado
        
        Args:
            canvas: Canvas do Tkinter onde o gráfico será exibido
            ano: Ano para o gráfico
            mes: Mês para o gráfico (opcional)
            tipo: Tipo de dados a exibir ('receitas', 'despesas', 'ambos')
            
        Returns:
            FigureCanvasTkAgg: Canvas do matplotlib
        """
        try:
            # Obter comparação
            comparacao = self.comparar_orcado_realizado(ano, mes)
            
            # Verificar se há dados
            if not comparacao:
                return None
            
            # Criar figura
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Configurar dados com base no tipo
            if tipo == 'receitas' or tipo == 'ambos':
                # Preparar dados de receitas
                categorias_receitas = list(comparacao['receitas'].keys())
                orcado_receitas = [comparacao['receitas'][cat]['orcado'] for cat in categorias_receitas]
                realizado_receitas = [comparacao['receitas'][cat]['realizado'] for cat in categorias_receitas]
                
                # Limitar a 10 categorias para melhor visualização
                if len(categorias_receitas) > 10:
                    # Ordenar por valor realizado (decrescente)
                    indices_ordenados = sorted(range(len(realizado_receitas)), key=lambda i: realizado_receitas[i], reverse=True)
                    categorias_receitas = [categorias_receitas[i] for i in indices_ordenados[:10]]
                    orcado_receitas = [orcado_receitas[i] for i in indices_ordenados[:10]]
                    realizado_receitas = [realizado_receitas[i] for i in indices_ordenados[:10]]
            
            if tipo == 'despesas' or tipo == 'ambos':
                # Preparar dados de despesas
                categorias_despesas = list(comparacao['despesas'].keys())
                orcado_despesas = [comparacao['despesas'][cat]['orcado'] for cat in categorias_despesas]
                realizado_despesas = [comparacao['despesas'][cat]['realizado'] for cat in categorias_despesas]
                
                # Limitar a 10 categorias para melhor visualização
                if len(categorias_despesas) > 10:
                    # Ordenar por valor realizado (decrescente)
                    indices_ordenados = sorted(range(len(realizado_despesas)), key=lambda i: realizado_despesas[i], reverse=True)
                    categorias_despesas = [categorias_despesas[i] for i in indices_ordenados[:10]]
                    orcado_despesas = [orcado_despesas[i] for i in indices_ordenados[:10]]
                    realizado_despesas = [realizado_despesas[i] for i in indices_ordenados[:10]]
            
            # Plotar gráficos
            if tipo == 'receitas':
                self._plotar_grafico_barras(ax, categorias_receitas, orcado_receitas, realizado_receitas, "Receitas")
                titulo = "Orçado vs. Realizado - Receitas"
            elif tipo == 'despesas':
                self._plotar_grafico_barras(ax, categorias_despesas, orcado_despesas, realizado_despesas, "Despesas")
                titulo = "Orçado vs. Realizado - Despesas"
            else:  # ambos
                # Criar subplots
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
                
                # Plotar receitas
                if categorias_receitas:
                    self._plotar_grafico_barras(ax1, categorias_receitas, orcado_receitas, realizado_receitas, "Receitas")
                    ax1.set_title("Receitas")
                
                # Plotar despesas
                if categorias_despesas:
                    self._plotar_grafico_barras(ax2, categorias_despesas, orcado_despesas, realizado_despesas, "Despesas")
                    ax2.set_title("Despesas")
                
                titulo = "Orçado vs. Realizado"
            
            # Configurar título
            periodo = f"{mes}/{ano}" if mes else str(ano)
            plt.suptitle(f"{titulo} - {periodo}", fontsize=16)
            
            # Ajustar layout
            plt.tight_layout()
            
            # Criar canvas para Tkinter
            canvas_fig = FigureCanvasTkAgg(fig, master=canvas)
            canvas_fig.draw()
            canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            return canvas_fig
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar gráfico de orçado vs. realizado: {str(e)}")
            return None
    
    def _plotar_grafico_barras(self, ax, categorias, valores_orcados, valores_realizados, titulo):
        """
        Plota um gráfico de barras comparando orçado e realizado
        """
        # Configurar posições das barras
        x = np.arange(len(categorias))
        largura = 0.35
        
        # Plotar barras
        ax.bar(x - largura/2, valores_orcados, largura, label='Orçado', color='blue', alpha=0.7)
        ax.bar(x + largura/2, valores_realizados, largura, label='Realizado', color='green', alpha=0.7)
        
        # Configurar eixos e legendas
        ax.set_ylabel('Valor (Kz)')
        ax.set_xticks(x)
        ax.set_xticklabels(categorias, rotation=45, ha='right')
        ax.legend()
        
        # Adicionar valores nas barras
        for i, v in enumerate(valores_orcados):
            ax.text(i - largura/2, v + 0.1, f"{v:,.0f}", ha='center', va='bottom', fontsize=8, rotation=90)
        
        for i, v in enumerate(valores_realizados):
            ax.text(i + largura/2, v + 0.1, f"{v:,.0f}", ha='center', va='bottom', fontsize=8, rotation=90)
        
        # Ajustar limites do eixo y
        max_valor = max(max(valores_orcados or [0]), max(valores_realizados or [0]))
        ax.set_ylim(0, max_valor * 1.2)  # 20% de margem acima do valor máximo
