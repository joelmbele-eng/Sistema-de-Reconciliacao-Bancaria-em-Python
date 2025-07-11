import json
import os
import logging
from datetime import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

class SistemaAuditoria:
    def __init__(self, contabilidade):
        """
        Inicializa o sistema de auditoria
        
        Args:
            contabilidade: Instância da classe ContabilidadeAvancada
        """
        self.contabilidade = contabilidade
        self.logger = self._configurar_logger()
        self.registros_auditoria = []
        self.carregar_registros()
    
    def _configurar_logger(self):
        """Configura o logger para registrar operações de auditoria"""
        logger = logging.getLogger('auditoria')
        logger.setLevel(logging.INFO)
        
        # Criar handler para arquivo
        fh = logging.FileHandler('auditoria.log')
        fh.setLevel(logging.INFO)
        
        # Criar formatador
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        # Adicionar handler ao logger
        logger.addHandler(fh)
        
        return logger
    
    def carregar_registros(self):
        """Carrega os registros de auditoria do arquivo JSON"""
        try:
            if os.path.exists('auditoria_registros.json'):
                with open('auditoria_registros.json', 'r', encoding='utf-8') as f:
                    self.registros_auditoria = json.load(f)
                    
                    # Converter strings de data para objetos datetime
                    for reg in self.registros_auditoria:
                        reg['data_hora'] = datetime.fromisoformat(reg['data_hora'])
        except Exception as e:
            self.logger.error(f"Erro ao carregar registros de auditoria: {str(e)}")
    
    def salvar_registros(self):
        """Salva os registros de auditoria em arquivo JSON"""
        try:
            # Converter objetos datetime para strings
            registros_json = []
            for reg in self.registros_auditoria:
                reg_copy = reg.copy()
                reg_copy['data_hora'] = reg_copy['data_hora'].isoformat()
                registros_json.append(reg_copy)
                
            with open('auditoria_registros.json', 'w', encoding='utf-8') as f:
                json.dump(registros_json, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar registros de auditoria: {str(e)}")
            return False
    
    def registrar_evento(self, tipo, descricao, usuario, detalhes=None):
        """
        Registra um evento de auditoria
        
        Args:
            tipo: Tipo do evento ('criacao', 'alteracao', 'exclusao', 'login', etc.)
            descricao: Descrição do evento
            usuario: Usuário que realizou a ação
            detalhes: Detalhes adicionais do evento (opcional)
            
        Returns:
            bool: True se registrado com sucesso, False caso contrário
        """
        try:
            registro = {
                'id': len(self.registros_auditoria) + 1,
                'data_hora': datetime.now(),
                'tipo': tipo,
                'descricao': descricao,
                'usuario': usuario,
                'detalhes': detalhes or {}
            }
            
            self.registros_auditoria.append(registro)
            self.salvar_registros()
            
            self.logger.info(f"Evento registrado: {tipo} - {descricao} por {usuario}")
            
            return True
        except Exception as e:
            self.logger.error(f"Erro ao registrar evento: {str(e)}")
            return False
    
    def registrar_alteracao_lancamento(self, lancamento_id, usuario, dados_antigos, dados_novos):
        """
        Registra uma alteração em um lançamento contábil
        
        Args:
            lancamento_id: ID do lançamento alterado
            usuario: Usuário que realizou a alteração
            dados_antigos: Dados do lançamento antes da alteração
            dados_novos: Dados do lançamento após a alteração
            
        Returns:
            bool: True se registrado com sucesso, False caso contrário
        """
        try:
            # Identificar campos alterados
            campos_alterados = {}
            
            # Verificar alterações nos campos básicos
            for campo in ['data', 'descricao']:
                if campo in dados_antigos and campo in dados_novos:
                    valor_antigo = dados_antigos[campo]
                    valor_novo = dados_novos[campo]
                    
                    # Converter datas para string se necessário
                    if campo == 'data' and isinstance(valor_antigo, datetime):
                        valor_antigo = valor_antigo.strftime('%d/%m/%Y')
                    if campo == 'data' and isinstance(valor_novo, datetime):
                        valor_novo = valor_novo.strftime('%d/%m/%Y')
                    
                    if valor_antigo != valor_novo:
                        campos_alterados[campo] = {
                            'antigo': valor_antigo,
                            'novo': valor_novo
                        }
            
            # Verificar alterações nos movimentos
            if 'movimentos' in dados_antigos and 'movimentos' in dados_novos:
                movimentos_antigos = dados_antigos['movimentos']
                movimentos_novos = dados_novos['movimentos']
                
                # Verificar se a quantidade de movimentos mudou
                if len(movimentos_antigos) != len(movimentos_novos):
                    campos_alterados['movimentos'] = {
                        'antigo': movimentos_antigos,
                        'novo': movimentos_novos
                    }
                else:
                    # Verificar alterações em cada movimento
                    for i, (mov_antigo, mov_novo) in enumerate(zip(movimentos_antigos, movimentos_novos)):
                        for campo_mov in ['conta', 'debito', 'credito']:
                            if mov_antigo[campo_mov] != mov_novo[campo_mov]:
                                if 'movimentos' not in campos_alterados:
                                    campos_alterados['movimentos'] = []
                                
                                campos_alterados['movimentos'].append({
                                    'indice': i,
                                    'campo': campo_mov,
                                    'antigo': mov_antigo[campo_mov],
                                    'novo': mov_novo[campo_mov]
                                })
            
            # Se não houver alterações, não registrar
            if not campos_alterados:
                return True
            
            # Registrar evento
            detalhes = {
                'lancamento_id': lancamento_id,
                'campos_alterados': campos_alterados
            }
            
            return self.registrar_evento(
                'alteracao_lancamento',
                f"Alteração no lançamento {lancamento_id}",
                usuario,
                detalhes
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar alteração de lançamento: {str(e)}")
            return False
    
    def registrar_criacao_lancamento(self, lancamento, usuario):
        """
        Registra a criação de um novo lançamento contábil
        
        Args:
            lancamento: Dados do lançamento criado
            usuario: Usuário que criou o lançamento
            
        Returns:
            bool: True se registrado com sucesso, False caso contrário
        """
        try:
            detalhes = {
                'lancamento_id': lancamento['id'],
                'data': lancamento['data'].strftime('%d/%m/%Y') if isinstance(lancamento['data'], datetime) else lancamento['data'],
                'descricao': lancamento['descricao'],
                'movimentos': lancamento['movimentos']
            }
            
            return self.registrar_evento(
                'criacao_lancamento',
                f"Criação do lançamento {lancamento['id']}",
                usuario,
                detalhes
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar criação de lançamento: {str(e)}")
            return False
    
    def registrar_exclusao_lancamento(self, lancamento, usuario):
        """
        Registra a exclusão de um lançamento contábil
        
        Args:
            lancamento: Dados do lançamento excluído
            usuario: Usuário que excluiu o lançamento
            
        Returns:
            bool: True se registrado com sucesso, False caso contrário
        """
        try:
            detalhes = {
                'lancamento_id': lancamento['id'],
                'data': lancamento['data'].strftime('%d/%m/%Y') if isinstance(lancamento['data'], datetime) else lancamento['data'],
                'descricao': lancamento['descricao'],
                'movimentos': lancamento['movimentos']
            }
            
            return self.registrar_evento(
                'exclusao_lancamento',
                f"Exclusão do lançamento {lancamento['id']}",
                usuario,
                detalhes
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar exclusão de lançamento: {str(e)}")
            return False
    
    def buscar_registros(self, filtros=None):
        """
        Busca registros de auditoria com base em filtros
        
        Args:
            filtros: Dicionário com filtros (tipo, usuario, data_inicio, data_fim)
            
        Returns:
            list: Lista de registros que atendem aos filtros
        """
        if filtros is None:
            return self.registros_auditoria
        
        resultados = []
        
        for registro in self.registros_auditoria:
            incluir = True
            
            # Filtrar por tipo
            if 'tipo' in filtros and filtros['tipo'] and registro['tipo'] != filtros['tipo']:
                incluir = False
            
            # Filtrar por usuário
            if 'usuario' in filtros and filtros['usuario'] and registro['usuario'] != filtros['usuario']:
                incluir = False
            
            # Filtrar por data de início
            if 'data_inicio' in filtros and filtros['data_inicio'] and registro['data_hora'] < filtros['data_inicio']:
                incluir = False
            
            # Filtrar por data de fim
            if 'data_fim' in filtros and filtros['data_fim'] and registro['data_hora'] > filtros['data_fim']:
                incluir = False
            
            # Filtrar por texto na descrição
            if 'texto' in filtros and filtros['texto']:
                if filtros['texto'].lower() not in registro['descricao'].lower():
                    incluir = False
            
            if incluir:
                resultados.append(registro)
        
        return resultados
    
    def gerar_relatorio_auditoria(self, filtros, caminho_saida):
        """
        Gera um relatório de auditoria com base em filtros
        
        Args:
            filtros: Dicionário com filtros (tipo, usuario, data_inicio, data_fim)
            caminho_saida: Caminho do arquivo PDF de saída
            
        Returns:
            bool: True se gerado com sucesso, False caso contrário
        """
        try:
            # Buscar registros
            registros = self.buscar_registros(filtros)
            
            # Criar documento PDF
            doc = SimpleDocTemplate(caminho_saida, pagesize=A4)
            elementos = []
            
            # Estilos
            estilos = getSampleStyleSheet()
            estilo_titulo = estilos['Heading1']
            estilo_subtitulo = estilos['Heading2']
            estilo_normal = estilos['Normal']
            
            # Título
            elementos.append(Paragraph("Relatório de Auditoria", estilo_titulo))
            elementos.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilo_normal))
            elementos.append(Spacer(1, 0.5*cm))
            
            # Filtros aplicados
            elementos.append(Paragraph("Filtros Aplicados", estilo_subtitulo))
            
            texto_filtros = []
            if 'tipo' in filtros and filtros['tipo']:
                texto_filtros.append(f"Tipo: {filtros['tipo']}")
            if 'usuario' in filtros and filtros['usuario']:
                texto_filtros.append(f"Usuário: {filtros['usuario']}")
            if 'data_inicio' in filtros and filtros['data_inicio']:
                texto_filtros.append(f"Data Início: {filtros['data_inicio'].strftime('%d/%m/%Y')}")
            if 'data_fim' in filtros and filtros['data_fim']:
                texto_filtros.append(f"Data Fim: {filtros['data_fim'].strftime('%d/%m/%Y')}")
            if 'texto' in filtros and filtros['texto']:
                texto_filtros.append(f"Texto: {filtros['texto']}")
            
            if texto_filtros:
                for texto in texto_filtros:
                    elementos.append(Paragraph(texto, estilo_normal))
            else:
                elementos.append(Paragraph("Nenhum filtro aplicado", estilo_normal))
            
            elementos.append(Spacer(1, 0.5*cm))
            
            # Resumo
            elementos.append(Paragraph("Resumo", estilo_subtitulo))
            elementos.append(Paragraph(f"Total de registros: {len(registros)}", estilo_normal))
            
            # Contagem por tipo
            tipos = {}
            for registro in registros:
                tipo = registro['tipo']
                if tipo not in tipos:
                    tipos[tipo] = 0
                tipos[tipo] += 1
            
            if tipos:
                dados_tipos = [["Tipo", "Quantidade"]]
                for tipo, quantidade in tipos.items():
                    dados_tipos.append([tipo.replace('_', ' ').title(), str(quantidade)])
                
                tabela_tipos = Table(dados_tipos, colWidths=[10*cm, 7*cm])
                tabela_tipos.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elementos.append(tabela_tipos)
            
            elementos.append(Spacer(1, 0.5*cm))
            
            # Detalhamento dos registros
            elementos.append(Paragraph("Detalhamento dos Registros", estilo_subtitulo))
            
            if registros:
                dados_registros = [["ID", "Data/Hora", "Tipo", "Usuário", "Descrição"]]
                
                for registro in registros:
                    dados_registros.append([
                        str(registro['id']),
                        registro['data_hora'].strftime('%d/%m/%Y %H:%M'),
                        registro['tipo'].replace('_', ' ').title(),
                        registro['usuario'],
                        registro['descricao']
                    ])
                
                tabela_registros = Table(dados_registros, colWidths=[1.5*cm, 3.5*cm, 3.5*cm, 3*cm, 6*cm])
                tabela_registros.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('ALIGN', (0, 1), (0, -1), 'CENTER'),
                    ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                elementos.append(tabela_registros)
                
                # Detalhes dos 10 registros mais recentes
                elementos.append(Spacer(1, 0.5*cm))
                elementos.append(Paragraph("Detalhes dos Registros Recentes", estilo_subtitulo))
                
                for registro in sorted(registros, key=lambda x: x['data_hora'], reverse=True)[:10]:
                    elementos.append(Paragraph(f"ID: {registro['id']} - {registro['data_hora'].strftime('%d/%m/%Y %H:%M')}", estilos['Heading3']))
                    elementos.append(Paragraph(f"Tipo: {registro['tipo'].replace('_', ' ').title()}", estilo_normal))
                    elementos.append(Paragraph(f"Usuário: {registro['usuario']}", estilo_normal))
                    elementos.append(Paragraph(f"Descrição: {registro['descricao']}", estilo_normal))
                    
                    if 'detalhes' in registro and registro['detalhes']:
                        elementos.append(Paragraph("Detalhes:", estilo_normal))
                        
                        if 'lancamento_id' in registro['detalhes']:
                            elementos.append(Paragraph(f"Lançamento ID: {registro['detalhes']['lancamento_id']}", estilo_normal))
                        
                        if 'campos_alterados' in registro['detalhes']:
                            elementos.append(Paragraph("Campos Alterados:", estilo_normal))
                            
                            for campo, valores in registro['detalhes']['campos_alterados'].items():
                                if campo == 'movimentos':
                                    elementos.append(Paragraph("Movimentos:", estilo_normal))
                                    
                                    if isinstance(valores, list):
                                        for alteracao in valores:
                                            elementos.append(Paragraph(
                                                f"Movimento {alteracao['indice']+1}, Campo {alteracao['campo']}: "
                                                f"{alteracao['antigo']} -> {alteracao['novo']}",
                                                estilo_normal
                                            ))
                                    else:
                                        elementos.append(Paragraph("Movimentos foram completamente alterados", estilo_normal))
                                else:
                                    elementos.append(Paragraph(
                                        f"{campo.capitalize()}: {valores['antigo']} -> {valores['novo']}",
                                        estilo_normal
                                    ))
                    
                    elementos.append(Spacer(1, 0.3*cm))
            else:
                elementos.append(Paragraph("Nenhum registro encontrado com os filtros aplicados.", estilo_normal))
            
            # Gerar PDF
            doc.build(elementos)
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório de auditoria: {str(e)}")
            return False
    
    def obter_historico_lancamento(self, lancamento_id):
        """
        Obtém o histórico de alterações de um lançamento
        
        Args:
            lancamento_id: ID do lançamento
            
        Returns:
            list: Lista de registros de auditoria relacionados ao lançamento
        """
        historico = []
        
        for registro in self.registros_auditoria:
            if 'detalhes' in registro and 'lancamento_id' in registro['detalhes']:
                if registro['detalhes']['lancamento_id'] == lancamento_id:
                    historico.append(registro)
        
        # Ordenar por data
        historico.sort(key=lambda x: x['data_hora'])
        
        return historico
