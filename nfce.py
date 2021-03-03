import re, os, datetime, util, sys, logging, shutil, csv
import dateutil.parser
#import mysql.connector
from bs4 import BeautifulSoup
#from bs4.element import NavigableString, Tag
from nfce.nfce_db import PRODUCT_NO_CLASSIFIED
from nfce.nfce_models import Session,\
                        NotaFiscal,\
                        Emitente,\
                        NotaFiscalFormaPagamento,\
                        NotaFiscalTotais,\
                        NotaFiscalTransporte, \
                        ProdutoServico,\
                        ProdutosProdServSemGtin,\
                        ProdutosNcm,\
                        ProdutoProdutoGtin,\
                        ProdutoGtin, \
                        ProdutoServicoAjuste
#formatação da chave de acesso
#https://tdn.totvs.com/pages/releaseview.action?pageId=351383045
FORMATO_CD_ACESSO =     {'cd_uf':(0, 2),   
                         'ano_mes':(2, 6),         
                         'cnpj':(6, 20), 
                         'cd_modelo':(20, 22), 
                         'serie':(22, 25), 
                         'numero':(25, 34), 
                         'cd_forma_emissao':(34, 35), 
                         'nu_nfce':(35, 43), 
                         'digito_verificador':(43, 44)   
                        } 

LABELS_EMITENTE =   {
                    'Nome / Razão Social':'razao_social', 
                    'Nome Fantasia':'nm_fantasia', 
                    'CNPJ':'cnpj', 
                    'Endereço':'endereco', 
                    'Bairro / Distrito':'bairro', 
                    'Município':'cd_municipio', 
                    'Telefone':'telefone', 
                    'UF':'sg_uf', 
                    'CEP':'cep', 
                    'País':'cd_pais', 
                    'Inscrição Estadual':'insc_estadual', 
                    'Inscrição Estadual do Substituto Tributário':'insc_estadual_substituto', 
                    'Inscrição Municipal':'insc_municipal', 
                    'Município da Ocorrência do Fato Gerador do ICMS':'cd_municipio_ocorrencia', 
                    'CNAE Fiscal':'cnae_fiscal', 
                    'Código de Regime Tributário':'ds_regime_tributario', 
                    }


class NfceArquivoInvalido(Exception):
    pass
    
def decodificar_codigo_acesso(codigo_acesso):
    dados_nfce = {}
    cd_acesso = util.retirar_pontuacao(codigo_acesso)
    for chave,  item in FORMATO_CD_ACESSO.items():
        pos = FORMATO_CD_ACESSO[chave]
        valor = cd_acesso[ pos[0]:pos[1]]
        dados_nfce[chave] = valor
    dados_nfce['chave_acesso'] = cd_acesso
    return dados_nfce
    
    
class NfceParseGovBr():
    '''
        Classe para leitura de nota fiscais eletronicas do site
        https://www.nfe.fazenda.gov.br/portal/consultaRecaptcha.aspx?tipoConsulta=resumo&tipoConteudo=d09fwabTnLk=
    '''
    def __init__(self,  arquivo_nfce, 
                    aj_texto = True,  
                    aj_data = False,
                    aj_valor = False,
                    log_file_name = '',
                    verbose_log = False, 
                    logNivel = logging.INFO):
    
        self.file_nfce = arquivo_nfce
        self.log_file_name = log_file_name
        self.verbose_log = verbose_log
        
        if not log_file_name:
            logging.basicConfig(level       = logNivel, \
                                format      = '%(levelname)s;%(asctime)s;%(name)s;%(message)s')
        else:
            logging.basicConfig(level       = logNivel, \
                                filename    = log_file_name, \
                                format      = '%(levelname)s;%(asctime)s;%(name)s;%(message)s')
            
        self.log = logging.getLogger(__name__)    
        
        try:
            self.gravar_msq_log('-;Abrindo arquivo {}'.format(arquivo_nfce))
            arq = open(arquivo_nfce,'r', encoding='utf-8')            
            
        except Exception as e:
            self.gravar_msq_log('-;Erro ao abrir {}'.format(arquivo_nfce))
            raise e
            
        self.dados_nota_fiscal = BeautifulSoup(arq.read(),'lxml')
        arq.close()
        
        self.aj_texto = aj_texto            #indica se as string do html vão ser ajustadas (retirar multiplos espaços, etc)    
        self.aj_data = aj_data              #indica que vai converter a datas (string) em datetime, campos iniciando com 'dt_'
        self.aj_valor = aj_valor
        
        #pega as chaves da nota fiscal
        span = self.dados_nota_fiscal.find('span', {'id':'lblChaveAcesso'})
        if span:
            nfce = decodificar_codigo_acesso(span.get_text())
            self.chaves_nota_fiscal = {}
            self.chaves_nota_fiscal['cnpj'] = nfce['cnpj']
            self.chaves_nota_fiscal['serie'] = nfce['serie']
            self.chaves_nota_fiscal['cd_modelo'] = nfce['cd_modelo']
            self.chaves_nota_fiscal['cd_uf'] = nfce['cd_uf']
            self.chaves_nota_fiscal['nu_nfce'] = nfce['nu_nfce']
            self.chave_acesso = nfce['chave_acesso']
            self.numero_nota = nfce['numero']
        else:
            self.gravar_msq_log('-;Arquivo de Nota Fiscal Inválido: {}'.format(arquivo_nfce))
            raise NfceArquivoInvalido


    def gravar_msq_log(self, msg):
        if self.log_file_name != '' or self.verbose_log:
            self.log.info(msg)


    def obter_dados_cobranca(self):
        emitente = {}
        div_emitente = self.dados_nota_fiscal.find('div', {'id':'Cobranca'})
        if div_emitente:
            emitente = self.obter_dados_labels(div_emitente, LABELS_EMITENTE)
            emitente = ajustar_dados_emitente(emitente)
        return emitente


    def obter_dados_emitente(self):
        emitente = {}
        div_emitente = self.dados_nota_fiscal.find('div', {'id':'Emitente'})
        if div_emitente:
            emitente = self.obter_dados_labels(div_emitente, LABELS_EMITENTE)
            emitente = ajustar_dados_emitente(emitente)
        return emitente
    
    def obter_chave_acesso(self):
        return self.chave_acesso


    def obter_dados_nfe_codigo_acesso(self, chave_acesso): 
        #o parametro chave_acesso não é usado, esta função é uma adaptação para que o objeto NfcdParseGovBr possa ser utilizado no módulo import_invoice com se fosse uma NfceParser
        return self.obter_dados_nota()


    def obter_dados_nota(self):
        dados_nota = {}
        dados_nota['cnpj'] = self.chaves_nota_fiscal['cnpj']
        dados_nota['serie'] = self.chaves_nota_fiscal['serie']
        dados_nota['cd_modelo'] = self.chaves_nota_fiscal['cd_modelo']
        dados_nota['cd_uf'] = self.chaves_nota_fiscal['cd_uf'] 
        dados_nota['nu_nfce'] = self.chaves_nota_fiscal['nu_nfce']
        dados_nota['chave_acesso'] = self.chave_acesso
        pos = FORMATO_CD_ACESSO['cd_forma_emissao']
        dados_nota['cd_forma_emissao'] = self.chave_acesso[pos[0]:pos[1]]
        dados_nota['dt_emissao'] = self.obter_data_emissao()
        dados_nota['dt_saida'] = self.obter_data_saida()
        dados_nota['vl_total'] = self.obter_valor_total()
        dados_nota['ds_informacoes_complementares'] = self.obter_informacoes_complementares()
        dados_nota['numero'] = self.numero_nota
        return dados_nota
        
    def obter_informacoes_complementares(self):
        id = self.dados_nota_fiscal.find('div', id = 'Inf')
        legend_inf_contrib = id.find('legend', text='Informações Complementares de Interesse do Contribuinte')
        return legend_inf_contrib.parent.div.get_text().strip()
    
    def obter_dados_toggable_box(self, table, dados_produto):
        
        dado = table.find('label', text='Código do Produto').parent.span.get_text().strip()  
        dados_produto['cd_prod_serv'] = dado
        dado = table.find('label', text='Código NCM').parent.span.get_text().strip()  
        dados_produto['cd_ncm_prod_serv'] = dado
        dado = table.find('label', text='Código CEST').parent.span.get_text().strip()  
        dados_produto['cest_prod_serv'] = dado
        dado = table.find('label', text='Código EX da TIPI').parent.span.get_text().strip()  
        dados_produto['cd_ex_tipi_prod_serv'] = dado
        dado = table.find('label', text='CFOP').parent.span.get_text().strip() 
        dados_produto['cfop_prod_serv'] = dado
        dado = table.find('label', text='Outras Despesas Acessórias').parent.span.get_text().strip()  
        if dado.strip()=='':
            dado = 0
        dados_produto['vl_out_desp_acess'] =  util.converte_monetario_float(dado)
        dado = table.find('label', text='Valor do Desconto').parent.span.get_text().strip() 
        if dado.strip()=='':
            dado = 0
        dados_produto['vl_desconto_prod_serv'] = util.converte_monetario_float(dado)
        dado = table.find('label', text='Valor Total do Frete').parent.span.get_text().strip()  
        if dado.strip()=='':
            dado = 0
        dados_produto['vl_frete_prod_serv'] = util.converte_monetario_float(dado)
        dado = table.find('label', text='Valor do Seguro').parent.span.get_text().strip()  
        if dado.strip()=='':
            dado = 0
        dados_produto['vl_seguro_prod_serv'] = util.converte_monetario_float(dado)
        
        #table = div_prod.find('table', class_="box")
        dado = table.find('label', text='                          Indicador de Composição do Valor Total da NF-e').parent.span.get_text().strip()  
        dados_produto['ind_composicao_prod_serv'] = dado
        dado = table.find('label', text='Código EAN Comercial').parent.span.get_text().strip()  
        dados_produto['cd_ean_prod_serv'] = dado
        dado = table.find('label', text='Unidade Comercial').parent.span.get_text().strip()  
        dados_produto['un_comercial_prod_serv'] = dado
        dado = table.find('label', text='Quantidade Comercial').parent.span.get_text().strip()  
        if dado.strip()=='':
            dado = 0
        dados_produto['qt_comercial_prod_serv'] = util.converte_monetario_float(dado)
        dado = table.find('label', text='Código EAN Tributável').parent.span.get_text().strip() 
        dados_produto['cd_ean_tributavel_prod_serv'] = dado
        dado = table.find('label', text='Unidade Tributável').parent.span.get_text().strip()  
        dados_produto['un_tributavel_prod_serv'] = dado
        dado = table.find('label', text='Quantidade Tributável').parent.span.get_text().strip()  
        if dado.strip()=='':
            dado = 0
        dados_produto['qt_tributavel_prod_serv'] = util.converte_monetario_float(dado)
        dado = table.find('label', text='Valor unitário de comercialização').parent.span.get_text().strip()  
        if dado.strip()=='':
            dado = 0
        dados_produto['vl_unit_comerc_prod_serv'] = util.converte_monetario_float(dado)
        dado = table.find('label', text='Valor unitário de tributação').parent.span.get_text().strip()  
        if dado.strip()=='':
            dado = 0
        dados_produto['vl_unit_tribut_prod_serv'] = util.converte_monetario_float(dado)                
        dado = table.find('label', text='Número do pedido de compra').parent.span.get_text().strip()  
        dados_produto['nu_pedido_compra_prod_serv'] = dado[0:10]              
        dado = table.find('label', text='Item do pedido de compra').parent.span.get_text().strip()  
        dados_produto['item_pedido_prod_serv'] = dado                
        dado = table.find('label', text='Valor Aproximado dos Tributos').parent.span.get_text().strip()  
        dados_produto['vl_aprox_tributos_prod_serv'] = util.converte_monetario_float(dado)                
        dado = table.find('label', text='Número da FCI').parent.span.get_text()  
        dados_produto['nu_fci_prod_serv'] = dado
        
        dado = table.find('label', text=re.compile('\s*Origem da Mercadoria\s*')).parent.span.get_text().strip()  
        dados_produto['ds_origem_mercadoria'] = dado  
        tag = table.find('label', text=re.compile('\s*Tributação do ICMS\s*'))
        if tag: #para o caso de tributação pelo simples
            dado = table.find('label', text=re.compile('\s*Tributação do ICMS\s*')).parent.span.get_text().strip() 
            dados_produto['ds_tributacao_icms'] = dado           
#            tag = table.find('label', text=re.compile('\s*Valor da BC do ICMS ST\s*'))
#            if tag: #se existir uma label com conteúdo "Valor da BC do ICMS ST"
#                dado = tag.parent.span.get_text().strip()  #pega o valor da base de calculo do ICMS  
#                #dado = table.find('label', text=re.compile('\s*Valor da BC do ICMS ST\s*')).parent.span.get_text().strip()  
#            else:     
#                   pass
#            dados_produto['ds_modal_defini_bc_icm'] = util.converte_monetario_float(dado)                
#            dado = table.find('label', text=re.compile('\s*Valor da base de cálculo efetiva\s*')).parent.span.get_text().strip() 
#            dados_produto['vl_base_calculo_icms_normal'] = util.converte_monetario_float(dado)                
#            dado = table.find('label', text=re.compile('\s*Alíquota do ICMS efetiva\s*')).parent.span.get_text().strip() 
#            dados_produto['vl_aliquota_icms_normal'] = util.converte_monetario_float(dado)                
#            dado = table.find('label', text=re.compile('\s*Valor do ICMS efetivo\s*')).parent.span.get_text().strip()
#            dados_produto['vl_icms_normal'] = util.converte_monetario_float(dado)   
        else:
            dados_produto['ds_tributacao_icms'] = 'Simples Nacional / ICMS Não incluído'   
#            dados_produto['ds_modal_defini_bc_icm'] = ''
#            dados_produto['vl_base_calculo_icms_normal'] = 0.0                
#            dados_produto['vl_aliquota_icms_normal'] = 0.0
#            dados_produto['vl_icms_normal'] = 0.0 
        
    def obter_dados_toggle_box(self, table, dados_produto):
        ''' Obtem os dados do produto contido na tabela "'toggle blox" '''
        dado = table.find('td', class_='fixo-prod-serv-numero').span.get_text().strip()
        dados_produto['nu_prod_serv'] = dado
        dado = table.find('td', class_='fixo-prod-serv-descricao').span.get_text().strip()
        dados_produto['ds_prod_serv'] = dado
        dado = table.find('td', class_='fixo-prod-serv-qtd').span.get_text().strip()  
        dados_produto['qt_prod_serv'] = util.converte_monetario_float(dado)
        dado = table.find('td', class_='fixo-prod-serv-vb').span.get_text().strip()  
        dados_produto['vl_prod_serv'] = util.converte_monetario_float(dado)                
        dado = table.find('td', class_='fixo-prod-serv-uc').span.get_text().strip()  
        dados_produto['un_comercial_prod_serv'] = dado
        return dados_produto
    
    
    def obter_dados_produtos_e_servicos(self):       
        dados_prod_serv = []
        div = self.dados_nota_fiscal.find('div', id = 'Prod')
        toggle_boxs = div.fieldset.div.findAll('table', class_='toggle box')
        for table in toggle_boxs:
            dado_prod_serv = {}
            dado_prod_serv = self.obter_dados_toggle_box(table, dado_prod_serv)
            togglable_box = table.nextSibling.nextSibling
            if togglable_box['class'][0] == "toggable":
                self.obter_dados_toggable_box(togglable_box, dado_prod_serv)
            dados_prod_serv.append(dado_prod_serv)
        return dados_prod_serv


    def obter_data_saida(self):
        label_saida = self.dados_nota_fiscal.find('label', text = re.compile('\s*Data/Hora de Saída ou da Entrada\s*'))
        if label_saida:
            return dateutil.parser.parse(label_saida.parent.span.get_text(),dayfirst=True)
        else:
            label_saida = self.dados_nota_fiscal.find('label', text = re.compile('\s*Data Saída/Entrada\s*'))
            if label_saida:
                if label_saida.parent.span.get_text().strip() != '':
                    return dateutil.parser.parse(label_saida.parent.span.get_text(),dayfirst=True)
        return None
                

    def obter_data_emissao(self):
        label_emissao = self.dados_nota_fiscal.find('label', text = re.compile('Data de Emissão'))
        return dateutil.parser.parse(label_emissao.parent.span.get_text(),dayfirst=True)


    def obter_valor_total(self):
        label_valor = self.dados_nota_fiscal.find('label', text = re.compile('Valor\s*Total\s*da\s*Nota\s*Fiscal\s*'))
        return util.converte_monetario_float(label_valor.parent.span.get_text())


    def obter_dados_labels(self, tag, dict_labels):
        if tag:
            dados = {}
            for texto_label in dict_labels.keys():
                label = tag.find('label', text = texto_label)
                if label:
                    dado_label = label.parent.span.get_text()
                    if self.aj_texto:
                        dados[dict_labels[texto_label]] = ajustar_texto(dado_label)
                    else:
                        dados[dict_labels[texto_label]] = dado_label
                    if dict_labels[texto_label][:3] == 'cd_' and not dados[dict_labels[texto_label]]:
                        dados[dict_labels[texto_label]]  = 0
                    if self.aj_data:
                        if dict_labels[texto_label][:3] == 'dt_':         #compara os 3 primeiros caracters do campo para saber se é um campo de data.
                            dados[dict_labels[texto_label]] = converter_data(dados[dict_labels[texto_label]])
                    if self.aj_valor:
                        if dict_labels[texto_label][:3] == 'vl_' or dict_labels[texto_label][:3] == 'qt_':         #compara os 3 primeiros caracters do campo para saber se é um campo de data.
                            dados[dict_labels[texto_label]] = util.converte_monetario_float(dados[dict_labels[texto_label]])
                else:
                    dados[dict_labels[texto_label]]  = None
            return dados
        else:
            return None
class NfceParse():
    #'nt.fiscal.eletronica.2.html'
    
    _dados_nfc_e  = {
                       # 'Modelo':'cd_modelo', 
                       # 'Série':'serie',
                       # 'Número':'nu_nfce',
                        'Data de Emissão':'dt_emissao',
                        'Data Saída/Entrada':'dt_saida',
                        'Valor Total da Nota Fiscal  ':'vl_total'
                    }
                    
                     
                                
    _dados_produtos_e_servicos_1 =  {
                                        'Número':'nu_prod_serv', 
                                        'Descrição':'ds_prod_serv',
                                        'Qtd.':'qt_prod_serv',
                                        'Unidade Comercial':'un_comercial_prod_serv', 
                                        'Valor (R$)':'vl_prod_serv'
                                    }
                                                            
    _dados_produtos_e_servicos_2 =  {
                                        'Código do Produto':'cd_prod_serv',
                                        'Código NCM':'cd_ncm_prod_serv', 
                                        'Código EX da TIPI':'cd_ex_tipi_prod_serv',
                                        'CFOP':'cfop_prod_serv',
                                        'Outras Despesas Acessórias':'vl_out_desp_acess', 
                                        'Valor do Desconto':'vl_desconto_prod_serv',
                                        'Valor Total do Frete':'vl_frete_prod_serv',
                                        'Valor do Seguro':'vl_seguro_prod_serv', 
                                        '\n                              Indicador de Composição do Valor Total da NF-e\n                            ':'ind_composicao_prod_serv',
                                        'Código EAN Comercial':'cd_ean_prod_serv',                                                             
                                        'Quantidade Comercial':'qt_comercial_prod_serv',
                                        'Código EAN Tributável':'cd_ean_tributavel_prod_serv',
                                        'Unidade Tributável':'un_tributavel_prod_serv', 
                                        'Quantidade Tributável':'qt_tributavel_prod_serv',
                                        'Valor unitário de comercialização':'vl_unit_comerc_prod_serv',
                                        'Valor unitário de tributação':'vl_unit_tribut_prod_serv', 
                                        'Número do pedido de compra':'nu_pedido_compra_prod_serv',
                                        'Item do pedido de compra':'item_pedido_prod_serv',
                                        'Valor Aproximado dos Tributos':'vl_aprox_tributos_prod_serv', 
                                        'Número da FCI':'nu_fci_prod_serv',
                                        'CEST':'cest_prod_serv', 
                                    }
                                                        
    _dados_icms_normal =    {
                                'Origem da Mercadoria':'ds_origem_mercadoria', 
                                'Tributação do ICMS':'ds_tributacao_icms', 
                                'Modalidade Definição da BC ICMS NORMAL':'ds_modal_defini_bc_icms', 
                                'Base de Cálculo do ICMS Normal':'vl_base_calculo_icms_normal', 
                                'Alíquota do ICMS Normal':'vl_aliquota_icms_normal', 
                                'Valor do ICMS Normal':'vl_icms_normal', 
                                'Valor do ICMS ST retido':'vl_icms_st_retido'
                            }
                                            
    _dados_pis =    {
                        'CST':'ds_cst_pis',  
                        'Base de Cálculo':'vl_base_calculo_pis',  
                        'Alíquota (%)':'vl_aliquota_pis',   
                        'Alíquota':'vl_aliquota_pis',
                        'Valor':'vl_pis' 
                    }
                    
    _dados_cobranca =   {
                            'Forma de Pagamento':'forma_pagamento',
                            'Valor do Pagamento':'valor_pagamento',
                            'CNPJ da Credenciadora':'cnpj_credenciadora',
                            'Bandeira da operadora':'bandeira_operacao',  
                            'Número de autorização':'numero_autorizacao'
                        }
                            
    _dados_cofins = {
                        'CST':'ds_cst_cofins',  
                        'Base de Cálculo':'vl_base_calculo_cofins',  
                        'Alíquota (%)':'vl_aliquota_cofins',   
                        'Alíquota':'vl_aliquota_cofins',  
                        'Valor':'vl_cofins' 
                    }
                                
    _dados_transporte =    {
                                'Modalidade do Frete': 'ds_modalidade_frete'
                            }
                                         
    _dados_formas_de_pagamento =   {
                                        'Forma de Pagamento' : 'ds_forma_pagamento', 
                                        'Valor do Pagamento' : 'vl_pagamento', 
                                        'CNPJ da Credenciadora' : 'cnpj_credenciadora'
                                    }
                                    
    _dados_emitente =   {
                            'Nome / Razão Social':'razao_social', 
                            'Nome Fantasia':'nm_fantasia', 
                            'CNPJ':'cnpj', 
                            'Endereço':'endereco', 
                            'Bairro / Distrito':'bairro', 
                            'Município':'cd_municipio', 
                            'Telefone':'telefone', 
                            'UF':'sg_uf', 
                            'CEP':'cep', 
                            'País':'cd_pais', 
                            'Inscrição Estadual':'insc_estadual', 
                            'Inscrição Estadual do Substituto Tributário':'insc_estadual_substituto', 
                            'Inscrição Municipal':'insc_municipal', 
                            'Município da Ocorrência do Fato Gerador do ICMS':'cd_municipio_ocorrencia', 
                            'CNAE Fiscal':'cnae_fiscal', 
                            'Código de Regime Tributário':'ds_regime_tributario', 
                        }
    _dados_totais =  {
                        'Base de Cálculo ICMS':'vl_base_calculo_icms', 
                        'Valor do ICMS':'vl_icms',
                        'Valor do ICMS Desonerado':'vl_icms_desonerado', 
                        'Base de Cálculo ICMS ST':'vl_base_calculo_icms_st',
                        'Valor ICMS Substituição':'vl_icms_substituicao', 
                        '\n                  Valor Total dos Produtos\n                ':'vl_total_produtos',
                        'Valor do Frete':'vl_frete', 
                        'Valor do Seguro':'vl_seguro',
                        'Outras Despesas Acessórias':'vl_outras_despesas_acesso', 
                        'Valor Total do IPI':'vl_total_ipi',
                        'Valor Total da NFe':'vl_total_nfe', 
                        'Valor Total dos Descontos':'vl_total_descontos',
                        'Valor Total do II':'vl_total_ii', 
                        'Valor do PIS':'vl_pis',
                        'Valor da COFINS':'vl_cofins', 
                        'Valor Aproximado dos Tributos':'vl_aproximado_tributos'
                    }
    
    
    def __init__(self,  arquivo_nfce ='NFC-e.tintas.html', 
                        aj_texto = False,  
                        aj_data = False,
                        aj_valor = False,
                        log_file_name = '',
                        logNivel = logging.INFO):
        
        self.file_nfce = arquivo_nfce
        
        if not log_file_name:
            
            nome_base = os.path.basename(arquivo_nfce)
            log_file_name = make_logs_path() + '/' + nome_base + '.log'
            
            logging.basicConfig(level       = logNivel, \
                                filename    = log_file_name, \
                                filemode    = 'w', \
                                format      = '%(levelname)s;%(asctime)s;%(name)s;%(funcName)s;%(message)s')
        else:
            logging.basicConfig(level       = logNivel, \
                                filename    = log_file_name, \
                                format      = '%(levelname)s;%(asctime)s;%(name)s;%(funcName)s;%(message)s')
            
        self.log = logging.getLogger(__name__)                    
        try:
            self.log.info('-;Abrindo arquivo {}'.format(arquivo_nfce))
            arq = open(arquivo_nfce,'r', encoding='utf-8')            
            
        except Exception as e:
            self.log.info('-;Erro ao abrir {}'.format(arquivo_nfce))
            raise e
            
        self.dados_nota_fiscal = BeautifulSoup(arq.read(),'lxml')
        arq.close()
        
        self.aj_texto = aj_texto            #indica se as string do html vão ser ajustadas (retirar multiplos espaços, etc)    
        self.aj_data = aj_data              #indica que vai converter a datas (string) em datetime, campos iniciando com 'dt_'
        self.aj_valor = aj_valor
        
        #pega as chaves da nota fiscal
        chave_acesso = self.obter_chave_acesso() 
        
        if chave_acesso:
            nfce = self.obter_dados_nfe_codigo_acesso(chave_acesso)
            self.chaves_nota_fiscal = {}
            self.chaves_nota_fiscal['cnpj'] = nfce['cnpj']
            self.chaves_nota_fiscal['serie'] = nfce['serie']
            self.chaves_nota_fiscal['cd_modelo'] = nfce['cd_modelo']
            self.chaves_nota_fiscal['cd_uf'] = nfce['cd_uf']
            self.chaves_nota_fiscal['nu_nfce'] = nfce['nu_nfce']            
        else:
            self.log.info('-;Arquivo de Nota Fiscal Inválido: {}'.format(arquivo_nfce))
            raise NfceArquivoInvalido
    
    def obter_chave_acesso(self):
        chave_acesso = self._obter_informacao_por_id('lbl_cod_chave_acesso', 'Chave de Acesso')
        if chave_acesso:
            return chave_acesso.get_text()
        else:
            return None
            
    def obter_dados_nfe_codigo_acesso(self, codigo_acesso, dados_completos = True):
        ''' Obtem dados da nota fiscal a partir do número de código de acesso
            Parametros(obj:string) Número do código de acesso
                      (obj:Boolean) Indica se vai obter todos os dados ou só aqueles constantes na chave
            Retorno (dicionario) Dicionario com os dados da nota fiscal
        '''
        self.log.info('-;Obtendo dados sobre Nota Fiscal')
        
        try:
            dados_nota = {}
            str_log = ''
            
            #retirado da declaração da variavel formato_codigo_acesso não vão ser utilizados,  por enquanto
            formato_codigo_acesso = {                   'cd_uf':(0, 2),   
                                                        #'ano_mes':(2, 6),         
                                                        'cnpj':(6, 20), 
                                                        'cd_modelo':(20, 22), 
                                                        'serie':(22, 25), 
                                                        'numero':(25, 34), 
                                                        'cd_forma_emissao':(34, 35), 
                                                        'nu_nfce':(35, 43)
                                                        #'digito_verificador':(43, 44)   
                                                       } 
            codigo_acesso = re.sub(' ', '', codigo_acesso)
            for chave,  item in formato_codigo_acesso.items():
                pos = formato_codigo_acesso[chave]
                valor = codigo_acesso[ pos[0]:pos[1]]
                dados_nota[chave] = valor
                str_log += str(chave)+ ' = ' + str(valor) + ' '
                dados_nota['chave_acesso'] = codigo_acesso
                #inclui outros dados da nota
                ntfce = self.obter_dados_nfc_e()
                if ntfce:
                    for chave, valor in ntfce.items():
                        if chave not in dados_nota.keys():
                            dados_nota[chave]= valor
            
            self.log.info('nota_fiscal;' + str(dados_nota))    
            
            
            return dados_nota
        except Exception as e:
            self.log.error('-;' + str(e))
            raise(e)
        
    def obter_dados_nfc_e(self):
        '''
            Obtém os dados da nota fiscal a partir dos dados contindos em <div id="NFe">
             (dt_emissao,dt_saida,vl_total)
        '''
        div = self._obter_informacao_por_id('NFe', 'Núḿero da Nota')
        
        if div:
            dados_nfc = obter_texto_labels(NfceParse._dados_nfc_e, div,  self.aj_texto,  self.aj_data, self.aj_valor)
            return  dados_nfc
            
        else:
            return None
            
   
    def obter_dados_icms_normal(self,dados_nota_fiscal): 
        ''' Obtem Dados do Icms Normal'''
        #procura uma tag <td> no html da nota fiscal(passada em parametro) que contenha class='table-titulo-aba-interna' e text='ICMS Normal e ST'
        td = dados_nota_fiscal.find('td', {'class': 'table-titulo-aba-interna'},  text = 'ICMS Normal e ST')
        if td:            
           #obtem a tag <table> que contém a <td> procurada, a estrutura do html esta assim <table> <tbory><tr><td> 
            if td.parent.parent.name == 'tbody':
                
                tabela = td.parent.parent.parent                
            else:                
                tabela = td.parent.parent                
            #pega a proxima tabela irmã que contém os labels relativos ao ICMS normal
            tabela = tabela.next_sibling
            dados_icms_normal = obter_texto_labels(NfceParse._dados_icms_normal, tabela,  self.aj_texto, self.aj_data,  self.aj_valor)
           
            return dados_icms_normal
        else:
            return None
            
            
    def obter_dados_pis(self, dados_nota_fiscal): 
        ''' Obtem Dados do PIS'''
        #procura uma tag <td> no html da nota fiscal que contenha class='table-titulo-aba-interna' e text='ICMS Normal e ST'
        #td = self.dados_nota_fiscal.find('td', {'class': 'table-titulo-aba-interna'},  text = 'PIS')
        td = dados_nota_fiscal.find('td', {'class': 'table-titulo-aba-interna'},  text = 'PIS')
        if td:
           #obtem a tag <table> que contém a <td> procurada, a estrutura do html esta assim <table> <tbory><tr><td> 
            if td.parent.parent.name == 'tbody':
                tabela = td.parent.parent.parent
            else:
                tabela = td.parent.parent
            #pega a proxima div irmã que contém os labels relativos ao ICMS normal
            div = tabela.next_sibling
            dados_pis = obter_texto_labels(NfceParse._dados_pis, div,  self.aj_texto, self.aj_data, self.aj_valor)
           
            return dados_pis
        else:
            return None
            
    def obter_dados_cofins(self, dados_nota_fiscal): 
        ''' Obtem Dados do Cofins'''
        #procura uma tag <td> no html da nota fiscal que contenha class='table-titulo-aba-interna' e text='ICMS Normal e ST'
        # td = self.dados_nota_fiscal.find('td', {'class': 'table-titulo-aba-interna'},  text = 'COFINS')
        td = dados_nota_fiscal.find('td', {'class': 'table-titulo-aba-interna'},  text = 'COFINS')
        if td:
           #obtem a tag <table> que contém a <td> procurada, a estrutura do html esta assim <table> <tbory><tr><td> 
           
           if td.parent.parent.name == 'tbody':
                tabela = td.parent.parent.parent
           else:
                tabela = td.parent.parent
           #pega a proxima div irmã que contém os labels relativos ao ICMS normal
           div = tabela.next_sibling
           dados_cofins = obter_texto_labels(NfceParse._dados_cofins, div,  self.aj_texto, self.aj_data, self.aj_valor)
           return dados_cofins
        else:
            return None
    
    def obter_dados_produtos_e_servicos(self):
        ''' Obtem dados sobre produtos e serviços da Nota Fiscais'''
        try:
            self.log.info('-;Obtendo dados sobre produtos e serviços')
            
            dados_produtos_servicos = []
            #str_log = ''
            tabelas = self.dados_nota_fiscal.findAll('table', {'id': re.compile('table-\d+')})
            
            if tabelas:
                #loop nas tag tables encontradas no html da nota
                for indice_tabela,  tabela in enumerate(tabelas):
                    tr = tabela.previous_sibling
                    
                    dado_produtos_servicos_1 = obter_texto_labels(NfceParse._dados_produtos_e_servicos_1, tr,  self.aj_texto, self.aj_data, self.aj_valor)
                    dado_produtos_servicos_2 = obter_texto_labels(NfceParse._dados_produtos_e_servicos_2, tabela,  self.aj_texto, self.aj_data, self.aj_valor)
                    
                    dados_produtos_icms = self.obter_dados_icms_normal(tabela)
                    dados_produtos_pis = self.obter_dados_pis(tabela)
                    dados_produtos_cofins = self.obter_dados_cofins(tabela)
                    
                    if dado_produtos_servicos_1:
                        dado_produtos_servicos = {}
                        for chave,  campo  in dado_produtos_servicos_1.items():
                            dado_produtos_servicos[chave] = campo
                            
                        if dado_produtos_servicos_2:
                            for chave,  campo  in dado_produtos_servicos_2.items():
                                dado_produtos_servicos[chave] = campo
                                
                        dados_produtos_servicos.append(dado_produtos_servicos)
                        
                    if dados_produtos_icms:
                        for chave,  valor in dados_produtos_icms.items():
                            dado_produtos_servicos[chave] = valor
                            
                    if dados_produtos_cofins:   
                        for chave,  valor in dados_produtos_cofins.items():
                            dado_produtos_servicos[chave] = valor
                        
                    if dados_produtos_pis:   
                        for chave,  valor in dados_produtos_pis.items():
                            dado_produtos_servicos[chave] = valor
                            
                    self.log.info('produtos_servicos;' + str(dado_produtos_servicos))
            else:
                    self.log.info('-;produtos e serviços da nota, não foram encontradas')
                    return None
            
            return dados_produtos_servicos
        except Exception as e:
            self.log.error('-;' + str(e))
            raise(e)
            
    def obter_numero_nota(self):
        numero_nota = self._obter_informacao_por_id('lbl_numero_nfe', 'Núḿero da Nota')
        if numero_nota:
            return numero_nota.get_text()
        else:
            return None
    
    
    def obter_dados_transporte(self):
        try:
            self.log.info('-;Obtendo dados sobre transporte')
            id = self.dados_nota_fiscal.find('div', {'id': 'Transporte'})
            #str_log = ''       
            if id:          
               dados_transporte = obter_texto_labels(NfceParse._dados_transporte, id,  self.aj_texto)               
               self.log.info('nota_fiscal_transporte;' + str(dados_transporte))           
               return dados_transporte
            else:
                self.log.info('-;Dados do transporte não encontrados')
                return None            
        except Exception as e:
            self.error('-;' + str(e))
            raise(e)
            
            
    def obter_informacoes_complementares(self):
        ''' Obtem Dados complementares da Nota'''
        try:    
            self.log.info('-;Obtendo dados sobre informações complementares')
            #procura uma tag <td> no html da nota fiscal que contenha class='table-titulo-aba-interna' e text='Informações Complementares de Interesse do Contribuinte'
            td = self.dados_nota_fiscal.find('td', {'class': 'table-titulo-aba-interna'},  text = 'Informações Complementares de Interesse do Contribuinte')
            if td:                
                if td.parent.parent.name =='table': #caso a estrutura seja <table><tr><td>
                    inf_complementar = td.parent.parent.next_sibling.next_sibling.get_text() 
                    self.log.info('nota_fiscal;ds_informacoes_complementares:' + inf_complementar)
                    return inf_complementar
                elif td.parent.parent.parent.name == 'table': #caso a estrutura seja <table><tbody><tr><td>
                    inf_complementar = td.parent.parent.parent.next_sibling.next_sibling.get_text()
                    self.log.info('nota_fiscal;ds_informacoes_complementares:' + inf_complementar)
                    return inf_complementar
                else:
                    self.log.info('-;Informações complementares da Nota não foram encontradas')
                    return None
            else:
                self.log.info('-;Informações complementares da Nota não foram encontradas')
        except Exception as e:
            self.log.error('-;' + str(e))
            raise(e)
            
            
    def obter_data_emissao(self):
        data_emissao = self._obter_informacao_por_id('lbl_dt_emissao', 'Data Emissão')
        
        if data_emissao:
            return data_emissao.get_text()
        else:
            return ''
            
    def teste_label_mercadoria(self):
        tabelas = self.dados_nota_fiscal.findAll('table', {'id': re.compile('table-\d+')})
        if tabelas:
            #loop nas tag tables encontradas no html da nota
            for indice_tabela,  tabela in enumerate(tabelas):
                print('*' * 10)
                #os dados das mercadorias estão em tag 'span'
                #pega na tabela anterior à tabela achada ('table-1' por exemplo) todos os span (relativos da mercadoria)
                spans1 = tabela.previous_sibling.tbody.tr.findAll('span')
                #dentro da tabela achada pega todos os span
                spans2 = tabela.tbody.findAll('span')
                #se achar spans na tabele anterior, coleta os dados da mercadoria em um dicionario
                if spans1:
                   # mercadoria = {}     #dicionario para coletar os dados da mercadoria
                    
                    for indice_span1,  span in enumerate(spans1):           #loop para coletar os dados da tabela anterior
                        print(span.previous_sibling.get_text(), " :",  span.get_text())
                    
                    indice_span1 = indice_span1 + 1             #soma mais um para poder utilizar o indice no próximo loop
                    
                    for indice_span2,  span in enumerate(spans2):   #loop para coletar os dados restantes que estão na tabela achada                    
                       print(span.previous_sibling.get_text(), " :",  span.get_text())
                
                print('*' * 10)    
                    #mercadorias.append(mercadoria)
        
    def obter_dados_mercadorias(self):
        ''' Obtem os dados das mercadorias na nota fiscal
            retorno:
                    (obj:list) - retorna uma lista contendo um dicionario com os dados das mercadorias
        '''
        #lista para guardar as mercadorias
        mercadorias = []
        #campos relativos a mercadoria presentes na nota fiscal
        campos=('numero',  'descricao',  'quantidade',  'unidade_comercial',  \
                        'valor',  'codigo_produto',  'codigo_ncm',  'codigo_ex_tipi', \
                        'cfop',  'outras_despesas_acessorias',  'valor_desconto',  \
                        'valor_total_frete',  'valor_seguro',  'indicador_composicao_valor_total', \
                        'codigo_ean',  'unidade_comercial_2',  'quantidade_comercial',  'codigo_ean_tributavel',  \
                        'unidade_tributavel',  'quantidade_tributavel',  'valor_unitario_comercializacao',  \
                        'valor_unitario_tributacao',  'numero_pedido_compra',  'item_pedido_compra',  \
                        'valor_aproximado_tributos',  'numero_fci',  'cest', 'origem_mercadoria',  'tributacao_icms',  \
                        'modalidade_bc_definicao_icms_normal',  'base_calculo_icms_normal',  'aliquota_icms_normal', \
                        'valor_icms_normal', 'cst_pis',  'base_calculo_pis',  'aliquota_pis', 'valor_pis', 'cts_confins',  \
                         'base_calculo_cofins',  'aliquota_confins',  'valor_confins'  )
        #procura por tag table como id's iguais a 'table-1', 'table-2', etc.
        tabelas = self.dados_nota_fiscal.findAll('table', {'id': re.compile('table-\d+')})
        
        if tabelas:
            #loop nas tag tables encontradas no html da nota
            for indice_tabela,  tabela in enumerate(tabelas):
                #os dados das mercadorias estão em tag 'span'
                #pega na tabela anterior à tabela achada ('table-1' por exemplo) todos os span (relativos da mercadoria)
                spans1 = tabela.previous_sibling.tbody.tr.findAll('span')
                #dentro da tabela achada pega todos os span
                spans2 = tabela.tbody.findAll('span')
                #se achar spans na tabele anterior, coleta os dados da mercadoria em um dicionario
                if spans1:
                    mercadoria = {}     #dicionario para coletar os dados da mercadoria
                    
                    for indice_span1,  span in enumerate(spans1):           #loop para coletar os dados da tabela anterior
                        mercadoria[campos[indice_span1]] = span.get_text()
                    
                    indice_span1 = indice_span1 + 1             #soma mais um para poder utilizar o indice no próximo loop
                    
                    for indice_span2,  span in enumerate(spans2):   #loop para coletar os dados restantes que estão na tabela achada                    
                        mercadoria[campos[indice_span1 + indice_span2]] = span.get_text()
                    
                    mercadorias.append(mercadoria)
                    
            if len(mercadorias):
                return mercadorias
                
        #não encontrou as tag tables            
        return None        
    
    def obter_dados_valores_totais(self):
        ''' Obtém os dados sobre os valores totais da Nota Fiscal'''
        try:
            self.log.info('-;Obtendo dados sobre valores totais da Nota')
            div = self.dados_nota_fiscal.find('div', {'id': 'Totais'})
            if div:         
               #str_log = '' 
                dados_totais = obter_texto_labels(NfceParse._dados_totais, div, self.aj_texto, self.aj_data, self.aj_valor)
    #           for chave, valor in dados_totais.items():
    #               str_log += str(chave) + ' = ' + str(valor) + '  '
                self.log.info('nota_fiscal_totais;' + str(dados_totais))
                return dados_totais
            else:
                self.log.info('-;Dados totais da nota, não foram encontrados')
                return None
        except Exception as e:
            self.info.error('-;' + str(e))
            raise(e)
        
    
    def obter_dados_cobranca(self):
        ''' Obtem os dados da cobrança do arquivo html relativo a Notas Fiscais'''
        
        #formato da cobrança mudou: 22.10.2020. Rever rotina. Retirada!!!
        try:
            self.log.info('-;Obtendo dados sobre Cobrança')
            
            campos = (  'ds_forma_pagamento',  'vl_pagamento',  'cnpj_credenciadora',  'bandeira_operacao',  \
                                'numero_autorizacao')
                                
            #não foi possivel utilizar a função obter_texto_labels, pois os <span> não ficam ao lodo do <label>
            id = self.dados_nota_fiscal.find('div', {'id': 'Cobranca'})
            spans = id.findAll('span')
            
            if spans:
                #str_log = ''
                cobranca = {}
                for indice,  span in enumerate(spans):  
                    valor = span.get_text().strip()
                    
                    if indice < len(campos): #começou a aparecer um span (o último) a mais no grupo da cobrança. Não deixando que de o erro de index out of range (rever depois)
                        if campos[indice] == 'vl_':   #compara os 3 primeiros caracters do campo para saber se é um campo numerico.
                            cobranca[campos[indice]] = util.converte_monetario_float(valor)
                        else:
                            cobranca[campos[indice]] = valor
                    #str_log += str(campos[indice]) + ' = ' + str(valor) + ' '
                    
                self.log.info('nota_fiscal_formas_pagamentos;' + str(cobranca))
                return cobranca
            else:
                self.log.info('-;Dados da cobrança da nota não foram encontrados')
                return None
        except Exception as e:
            self.info.error('-;' + str(e))
            raise(e)


    def obter_dados_emitente(self):
        try:
            self.log.info('-;Obtendo dados sobre Emitente')            
            div = self.dados_nota_fiscal.find('div', {'id': 'Emitente'})            
            if div:
                #str_log = ''
                dados_emitente = obter_texto_labels(NfceParse._dados_emitente, div,  self.aj_texto, self.aj_data, self.aj_valor)
                if dados_emitente:
                   for chave, valor in dados_emitente.items():
                        if chave in ('cd_municipio', 'cd_pais'):         #para dados do tipo '1-descricao' pega somente o dado antes do '-'
                            if isinstance(valor, str):
                                dados_emitente[chave] = valor.split('-')[0]
                                if not dados_emitente[chave].strip():
                                    dados_emitente[chave] = '0'
                        if chave in  ('cnpj', 'cep', 'telefone') :
                            dados_emitente[chave] = util.retirar_pontuacao(valor)
                        
                self.log.info('emitente;' + str(dados_emitente))
                return dados_emitente
            else:
                self.log.info('-;Dados sobre Emitente não encontrados')
                return None
        except Exception as e:
            self.log.error('-;' + str(e))
            raise(e)

    def _obter_informacao_por_id(self, id, nome_informacao): 
        dados = self.dados_nota_fiscal.findAll(id = id)
        qt_dados = len(dados)
        if qt_dados != 1:                                   
            if qt_dados > 1:          #esta buca deveria retornar um só dado
                print('Encontrado mais de um(a) {} na nota fiscal retornand o(a) primeiro(a)'.format(nome_informacao))
            return None            
        else:
            return  dados[0]           

    
class NfceBd():
    def __init__(self, logger=None):
        self.session = Session(autocommit=False)
        self.logger = logger
        
    def __write_info_log(self,msg):
        if self.logger:
            self.logger.info(msg)


    def __write_error_log(self, msg):
        if self.logger:
            self.logger.error(msg)

    
    def insert_full_invoice_in_db(self, invoice_parser):
        '''
            Grava na base de dados informações sobre a nota fiscal que vai ser lida de invoice_parser
            parâmetros:
                (invoice_parser:object NfceParse) objeto responsável por ler o html de nota fiscal
        
        '''
        
        supplier_data = invoice_parser.obter_dados_emitente()   #lê os dados do emitente da nota 
        self.insert_supplier_data_in_db(supplier_data, self.session) #grava na base de dados 
        
        acess_key = invoice_parser.obter_chave_acesso()  #pega a chave de acesso da nota fiscal
        invoice_data = invoice_parser.obter_dados_nfe_codigo_acesso(acess_key) #pega os dados da nota a partir da chave
        extra_data = invoice_parser.obter_informacoes_complementares() #pega as informações complementares da nota fiscal 
        invoice_data['ds_informacoes_complementares'] = extra_data
        self.insert_invoice_data_in_db(invoice_data, self.session) #grava na base de dados a nota fiscal
        
        ## 22.10.2020. retirado. houve alteração do layout. analisar!!!
        #payment_data = invoice_parser.obter_dados_cobranca()    #pega os dados da cobrança da nota fiscal 
        #self.__include_keys(payment_data, invoice_parser) #inclui as chaves primárias da nota fiscal
        #self.insert_payment_data_in_db(payment_data, self.session) #grava na base de dados os dados relativos ao pagamento da nota
        
      #com a inclusão das notas fiscais de gov.br, foi retirado toda a parte de dados totais da nota 
#        total_data = invoice_parser.obter_dados_valores_totais()  #pega os dados relativos ao total da nota fiscal
#        self.__include_keys(total_data, invoice_parser)        #inclui as chaves primárias da nota fiscal
#        self.insert_total_data_in_db(total_data, self.session) #grava na base de dados os dados relativos ao total da nota
     
        
        products_data = invoice_parser.obter_dados_produtos_e_servicos() #pega os dados relativos aos produtos e serviços
        for product_data in products_data:
            self.__include_keys(product_data, invoice_parser)  #inclui as chaves primárias da nota fiscal
        self.insert_products_data_in_db(products_data, self.session)  #grava na base de dados os dados relativos aos produtos
        
    def insert_supplier_data_in_db(self, supplier_data, session):
        try:
            if supplier_data:
                query = session.query(Emitente).filter(Emitente.cnpj == supplier_data['cnpj'])    
                if query.count() == 0:
                    emitente = Emitente()
                    emitente.cnpj = supplier_data['cnpj']
                    emitente.razao_social = supplier_data['razao_social']
                    emitente.nm_fantasia = supplier_data['nm_fantasia']
                    emitente.endereco = supplier_data['endereco']
                    emitente.bairro = supplier_data['bairro']
                    emitente.cep = supplier_data['cep']
                    emitente.cd_municipio = supplier_data['cd_municipio']
                    emitente.cd_municipio_ocorrencia = supplier_data['cd_municipio_ocorrencia']
                    emitente.telefone = supplier_data['telefone']
                    emitente.sg_uf = supplier_data['sg_uf']
                    emitente.cd_pais = supplier_data['cd_pais']
                    emitente.insc_estadual = supplier_data['insc_estadual']
                    emitente.cnae_fiscal = supplier_data['cnae_fiscal']
                    emitente.ds_regime_tributario = supplier_data['ds_regime_tributario']
                    emitente.insc_estadual_substituto = supplier_data['insc_estadual_substituto']
                    emitente.insc_municipal = supplier_data['insc_municipal'] 
                    session.add(emitente)
                    self.__write_info_log(f'-;insert emitente cnpj: {emitente.cnpj} razao_social: {emitente.razao_social}')
                else:
                    self.__write_info_log(f'-;Emitente existente cnpj: {supplier_data["cnpj"]} razao_social: {supplier_data["razao_social"]}')
            else:
                self.__write_info_log('-;Emitente não inserido - Sem Dados')
        except Exception as e:
            self.__write_error_log(f'-;Erro: {sys.exc_info()[0]} ao inserir dados do fornecedor da nota_fiscal: ' + str(e))
            raise(e)


    def insert_invoice_data_in_db(self, invoice_data, session):
        try:
            if invoice_data:
                query = session.query(NotaFiscal)
                query = query.filter(NotaFiscal.nu_nfce == invoice_data['nu_nfce'], 
                                          NotaFiscal.cd_uf == invoice_data['cd_uf'], 
                                          NotaFiscal.serie == invoice_data['serie'], 
                                          NotaFiscal.cnpj == invoice_data['cnpj'], 
                                          NotaFiscal.cd_modelo == invoice_data['cd_modelo'])
                if query.count() == 0:
                    nt = NotaFiscal()
                    nt.nu_nfce = invoice_data['nu_nfce']
                    nt.cd_uf = invoice_data['cd_uf']
                    nt.serie = invoice_data['serie']
                    nt.cnpj = invoice_data['cnpj']
                    nt.cd_modelo = invoice_data['cd_modelo']
                    nt.cd_forma_emissao = invoice_data['cd_forma_emissao']
                    nt.dt_emissao = invoice_data['dt_emissao']
                    nt.chave_acesso = invoice_data['chave_acesso']            
                    nt.numero = invoice_data['numero']
                    nt.dt_saida = None
                    nt. vl_total = invoice_data['vl_total']
                    nt.ds_informacoes_complementares = invoice_data['ds_informacoes_complementares']            
                    session.add(nt)
                    self.__write_info_log(f'-;Inserida Ntfe: {invoice_data["nu_nfce"]} valor: {invoice_data["vl_total"]}')
                else:
                    self.__write_info_log(f'-;Ntfe: {invoice_data["nu_nfce"]} valor: {invoice_data["vl_total"]} já incluída')
            else:
                self.__write_info_log('-;Nota Fiscal não inserida - Sem Dados')
        except Exception as e:
            self.__write_error_log(f'-;Erro: {sys.exc_info()[0]} ao inserir dados da nota_fiscal: ' + str(e))
            raise(e)


    def insert_payment_data_in_db(self, bill_data, session):
        try:
            if bill_data['ds_forma_pagamento']:
                query = session.query(NotaFiscalFormaPagamento)
                query = query.filter(NotaFiscalFormaPagamento.nu_nfce == bill_data['nu_nfce'], 
                                     NotaFiscalFormaPagamento.cd_uf == bill_data['cd_uf'], 
                                     NotaFiscalFormaPagamento.serie == bill_data['serie'], 
                                     NotaFiscalFormaPagamento.cnpj == bill_data['cnpj'], 
                                     NotaFiscalFormaPagamento.cd_modelo == bill_data['cd_modelo'])
                if query.count() == 0:
                    nt = NotaFiscalFormaPagamento()
                    nt.cd_uf = bill_data['cd_uf']
                    nt.cnpj = bill_data['cnpj']
                    nt.nu_nfce = bill_data['nu_nfce']
                    nt.serie = bill_data['serie']
                    nt.cd_modelo = bill_data['cd_modelo']
                    nt.ds_forma_pagamento = bill_data['ds_forma_pagamento']
                    nt.vl_pagamento = bill_data['vl_pagamento']
                    nt.cnpj_credenciadora = bill_data['cnpj_credenciadora']
                    nt.bandeira_operacao = bill_data['bandeira_operacao']
                    session.add(nt)
                    self.__write_info_log(f'-;Inserida Forma de Pagamento Ntfe: {bill_data["nu_nfce"]} - {bill_data["ds_forma_pagamento"]}')
                else:
                    self.__write_info_log(f'-;Forma de Pagamento Ntfe: {bill_data["nu_nfce"]} já incluída')
            else:
                self.__write_info_log('-;Forma de Pagamento Ntfe não inserida - Sem Dados')
        except Exception as e:
            self.__write_error_log(f'-;Erro: {sys.exc_info()[0]} ao inserir dados do pagamento da nota fiscal: ' + str(e))
            raise(e)
    

    def insert_total_data_in_db(self, total_data, session):
        try:
            query = session.query(NotaFiscalTotais)
            query = query.filter(NotaFiscalTotais.nu_nfce == total_data['nu_nfce'], 
                                 NotaFiscalTotais.cd_uf == total_data['cd_uf'], 
                                 NotaFiscalTotais.serie == total_data['serie'], 
                                 NotaFiscalTotais.cnpj == total_data['cnpj'], 
                                 NotaFiscalTotais.cd_modelo == total_data['cd_modelo'])
            if query.count() == 0:
                nt = NotaFiscalTotais()
                nt.nu_nfce = total_data['nu_nfce']
                nt.cd_uf = total_data['cd_uf']
                nt.serie = total_data['serie']
                nt.cnpj = total_data['cnpj']
                nt.cd_modelo = total_data['cd_modelo']
                nt.vl_base_calculo_icms = total_data['vl_base_calculo_icms']
                nt.vl_icms = total_data['vl_icms']
                nt.vl_icms_desonerado = total_data['vl_icms_desonerado'] 
                nt.vl_base_calculo_icms_st = total_data['vl_base_calculo_icms_st']
                nt.vl_icms_substituicao = total_data['vl_icms_substituicao'] 
                nt.vl_total_produtos = total_data['vl_total_produtos']
                nt.vl_frete = total_data['vl_frete']
                nt.vl_seguro = total_data['vl_seguro']
                nt.vl_outras_despesas_acesso = total_data['vl_outras_despesas_acesso'] 
                nt.vl_total_ipi = total_data['vl_total_ipi']
                nt.vl_total_nfe = total_data['vl_total_nfe']
                nt.vl_total_descontos = total_data['vl_total_descontos']
                nt.vl_total_ii = total_data['vl_total_ii'] 
                nt.vl_pis = total_data['vl_pis']
                nt.vl_cofins = total_data['vl_cofins'] 
                nt.vl_aproximado_tributos = total_data['vl_aproximado_tributos']
                session.add(nt)
                self.__write_info_log(f'-;Inseridos Totais da Ntfe: {total_data["nu_nfce"]}')
            else:
                self.__write_info_log(f'-;Totais da Ntfe: {total_data["nu_nfce"]} já incluídos')
            
        except Exception as e:
            self.__write_error_log(f'-;Erro: {sys.exc_info()[0]} ao inserir dados dos totais da nota fiscal: ' + str(e))
            raise(e)


    def insert_delivery_data_in_db(self, delivery_data, session):
        try:
            query = session.query(NotaFiscalTransporte)
            query = query.filter(NotaFiscalTransporte.nu_nfce == delivery_data['nu_nfce'], 
                                 NotaFiscalTransporte.cd_uf == delivery_data['cd_uf'], 
                                 NotaFiscalTransporte.serie == delivery_data['serie'], 
                                 NotaFiscalTransporte.cnpj == delivery_data['cnpj'], 
                                 NotaFiscalTransporte.cd_modelo == delivery_data['cd_modelo'])
            if query.count() == 0:
                nt = NotaFiscalTransporte()
                nt.nu_nfce = delivery_data['nu_nfce']
                nt.cd_uf = delivery_data['cd_uf']
                nt.serie = delivery_data['serie']
                nt.cnpj = delivery_data['cnpj']
                nt.cd_modelo = delivery_data['cd_modelo']
                nt.ds_modalidade_frete =delivery_data['ds_modalidade_frete']
                session.add(nt)
                self.__write_info_log(f'-;Transporte da Ntfe: {delivery_data["nu_nfce"]} - {delivery_data["ds_modalidade_frete"]}')            
            else:
                self.__write_info_log(f'-;Transporte da Ntfe: {delivery_data["nu_nfce"]} já incluído')            
        except Exception as e:
            self.__write_error_log(f'-;Erro: {sys.exc_info()[0]} ao inserir dados sobre o transporte da nota fiscal: ' + str(e))
            raise(e)

   
    def insert_products_data_in_db(self, products_data, session): 
        try:
            if products_data:
                query = session.query(ProdutoServico)                
                for product_data in products_data:
                    
                    query = query.filter( ProdutoServico.nu_nfce == product_data['nu_nfce'], 
                                          ProdutoServico.cd_uf == product_data['cd_uf'], 
                                          ProdutoServico.serie == product_data['serie'], 
                                          ProdutoServico.cnpj == product_data['cnpj'], 
                                          ProdutoServico.cd_modelo == product_data['cd_modelo'], 
                                          ProdutoServico.nu_prod_serv == product_data['nu_prod_serv'])
                    if query.count() == 0:   #ProdutoServico não encontrado?(inseri!)
                        
                        self.insert_product_gtin_data(product_data, session) #inseri produtos com códigos de barras
                        self.adjust_prod_serv(product_data, session)    #ajuste de produtos e serviços
                        produto = ProdutoServico()
                        produto.nu_nfce = product_data['nu_nfce']
                        produto.cd_uf = product_data['cd_uf']
                        produto.serie = product_data['serie']
                        produto.cnpj = product_data['cnpj']
                        produto.cd_modelo = product_data['cd_modelo']
                        produto.nu_prod_serv = product_data['nu_prod_serv']        
                        produto.ds_prod_serv = product_data['ds_prod_serv']
                        produto.qt_prod_serv = product_data['qt_prod_serv']
                        produto.un_comercial_prod_serv = product_data['un_comercial_prod_serv']
                        produto.vl_prod_serv = product_data['vl_prod_serv']            
                        produto.cd_prod_serv = product_data['cd_prod_serv'] 
                        produto.cd_ncm_prod_serv = product_data['cd_ncm_prod_serv']
                        produto.cd_ex_tipi_prod_serv = product_data['cd_ex_tipi_prod_serv'] 
                        produto.cfop_prod_serv = product_data['cfop_prod_serv']
                        produto.vl_out_desp_acess = product_data['vl_out_desp_acess']
                        produto.vl_desconto_prod_serv = product_data['vl_desconto_prod_serv']
                        produto.vl_frete_prod_serv = product_data['vl_frete_prod_serv'] 
                        produto.vl_seguro_prod_serv = product_data['vl_seguro_prod_serv']
                        produto.ind_composicao_prod_serv = product_data['ind_composicao_prod_serv']
                        produto.cd_ean_prod_serv = product_data['cd_ean_prod_serv']
                        produto.qt_comercial_prod_serv = product_data['qt_comercial_prod_serv']
                        produto.cd_ean_tributavel_prod_serv = product_data['cd_ean_tributavel_prod_serv']
                        produto.un_tributavel_prod_serv = product_data['un_tributavel_prod_serv']
                        produto.qt_tributavel_prod_serv = product_data['qt_tributavel_prod_serv'] 
                        produto.vl_unit_comerc_prod_serv = product_data['vl_unit_comerc_prod_serv']
                        produto.vl_unit_tribut_prod_serv= product_data['vl_unit_tribut_prod_serv']
                        produto.nu_pedido_compra_prod_serv = product_data['nu_pedido_compra_prod_serv']
                        produto.item_pedido_prod_serv = product_data['item_pedido_prod_serv']
                        produto.vl_aprox_tributos_prod_serv = product_data['vl_aprox_tributos_prod_serv']
                        produto.nu_fci_prod_serv = product_data['nu_fci_prod_serv']
                        produto.cest_prod_serv = product_data['cest_prod_serv']
                        produto.cd_ean_prod_serv_original = product_data['cd_ean_prod_serv']
                        session.add(produto)
                        self.__write_info_log('-;Inserido Produto: {}-{} Gtin:{} Ncm:{}'.\
                            format(product_data['nu_prod_serv'], 
                                   product_data['ds_prod_serv'], 
                                   product_data['cd_ean_prod_serv'], 
                                   product_data['cd_ncm_prod_serv']))     
                        self.match_id_produto(product_data, session)                        
                    else:
                        #self.__write_info_log(f'-;Produto: {product_data["nu_prod_serv"]} - {product_data["ds_prod_serv"]} já incluído')     
                        self.__write_info_log('-;Produto: {}-{} Gtin:{} Ncm:{} já inserido'.\
                            format(product_data['nu_prod_serv'], 
                                   product_data['ds_prod_serv'], 
                                   product_data['cd_ean_prod_serv'], 
                                   product_data['cd_ncm_prod_serv']))
                    query = session.query(ProdutoServico)
            else:
                self.__write_info_log('-;Produto não inseridos - sem dados')         
        except Exception as e:
            self.__write_error_log(f'-;Erro: {sys.exc_info()[0]} ao inserir dados dos produtos da nota_fiscal: ' + str(e))
            raise(e)


    def insert_product_gtin_data(self, product_data, session):
        ''' 
            Inclue um produto na tabela produto_gtim
        '''
        if product_data:
            if product_data['cd_ean_prod_serv'] != 'SEM GTIN': #produto sem código de barras?
                query = session.query(ProdutoGtin)
                query = query.filter( ProdutoGtin.cd_ean_produto == product_data['cd_ean_prod_serv'])
                if query.count() == 0:
                    produto = ProdutoGtin()
                    produto.cd_ean_produto = product_data['cd_ean_prod_serv']
                    produto.ds_produto = product_data['ds_prod_serv']
                    produto.cd_ncm_produto = product_data['cd_ncm_prod_serv']
                    produto.cd_ean_interno = product_data['cd_ean_prod_serv']
                    produto.qt_item_embalagem = 1
                    session.add(produto)
                    self.__write_info_log(f'-;Inserido Produto Gtin: {product_data["cd_ean_prod_serv"]} - {product_data["ds_prod_serv"]}')     
                    



    def match_id_produto(self, product_data, session):

        query_ean = None
        query_no_ean = None
        if product_data: #tem dados?
            if product_data['cd_ean_prod_serv'] == 'SEM GTIN': #produto sem código de barras?
                query_no_ean = session.query(ProdutosProdServSemGtin)
                query_no_ean = query_no_ean.filter(ProdutosProdServSemGtin.cnpj == product_data['cnpj'], 
                                      ProdutosProdServSemGtin.cd_prod_serv == product_data['cd_prod_serv']) #verifica se esta na tabela de_para
                if query_no_ean.count() > 0: #se estiver, nada a fazer
                   return
            else: #produto com código de barras.
                query_ean = session.query(ProdutoProdutoGtin)
                query_ean = query_ean.filter(ProdutoProdutoGtin.cd_ean_produto == product_data['cd_ean_prod_serv']) #verifica se esta na tabela de_para
                if query_ean.count() == 1: #se estiver nada a fazer
                    return
            query = session.query(ProdutosNcm) #não achou o produto na tabela de_para. verifica na tabela de_para ncm_padrões x produto.
            query = query.filter(ProdutosNcm.cd_ncm == product_data['cd_ncm_prod_serv'])
            if query.count() != 0: #encontrou o produto?
                result = query.all()
                if query_ean:   #produto com código de barras?
                    pp_gtin = ProdutoProdutoGtin()
                    pp_gtin.cd_ean_produto = product_data['cd_ean_prod_serv']
                    pp_gtin.id_produto = result[0].id_produto
                    session.add(pp_gtin)    #nova entrada na tabela de_para
                   #self.__write_info_log(f'-;Inserido Produto x Produto Gtin: {product_data["cd_ean_prod_serv"]} - {product_data["ds_prod_serv"]} id_produto: {result[0].id_produto}')     
                    self.__write_info_log('-;Inserido Produto x Produto Gtin: {} - {} id_produto: {}'\
                            .format(product_data['cd_ean_prod_serv'], 
                                    product_data["ds_prod_serv"], 
                                    result[0].id_produto))     
                else:#produto sem código de barras
                    p_no_gtin = ProdutosProdServSemGtin()
                    p_no_gtin.cnpj = product_data['cnpj']
                    p_no_gtin.cd_prod_serv = product_data['cd_prod_serv']
                    p_no_gtin.id_produto = result[0].id_produto #nova entrada na tabela de_para
                    session.add(p_no_gtin)
                    #self.__write_info_log(f'-;Inserido Produto x Prod Serv sem Gtin - cnpj: {product_data["cnpj"]} cd_prod_serv: {product_data["cd_prod_serv"]} id_produto: {result[0].id_produto}')     
                    self.__write_info_log('-;Inserido Produto x Prod Serv sem Gtin - cnpj: {} cd_prod_serv: {} id_produto: {} ds_prod_serv: {}'\
                            .format(product_data['cnpj'], 
                                    product_data["cd_prod_serv"], 
                                    result[0].id_produto, 
                                    product_data["ds_prod_serv"])) 
                    
            else: #não encontrou produto na tabela de ncm padrões. cria uma estrada nesta tabela e nas outras de_para com o produto 'a classificar'
                p_ncm = ProdutosNcm()
                p_ncm.cd_ncm = product_data['cd_ncm_prod_serv']
                p_ncm.id_produto = PRODUCT_NO_CLASSIFIED
                session.add(p_ncm)
                #self.__write_info_log(f'-;Inserido Produto Ncm - Ncm: {product_data["cd_ncm_prod_serv"]} Produto não classificado : {PRODUCT_NO_CLASSIFIED}')     
                self.__write_info_log('-;Inserido Produto Ncm: {} Produto não classificado : {} ds_prod_serv: {}'\
                            .format(product_data['cd_ncm_prod_serv'],
                                    PRODUCT_NO_CLASSIFIED, 
                                    product_data["ds_prod_serv"])) 
                if query_ean:
                    pp_gtin = ProdutoProdutoGtin()
                    pp_gtin.cd_ean_produto = product_data['cd_ean_prod_serv']
                    pp_gtin.id_produto = PRODUCT_NO_CLASSIFIED
                    session.add(pp_gtin)
                    #self.__write_info_log(f'-;Inserido Produto x Produto Gtim : {product_data["cd_ean_prod_serv"]} Produto não classificado : {PRODUCT_NO_CLASSIFIED}')     
                    self.__write_info_log('-;Inserido Produto x Produto Gtim : {} Produto não classificado : {} ds_prod_serv: {}'\
                            .format(product_data['cd_ean_prod_serv'],
                                    PRODUCT_NO_CLASSIFIED, 
                                    product_data["ds_prod_serv"])) 
                else:
                    p_no_gtin = ProdutosProdServSemGtin()
                    p_no_gtin.cnpj = product_data['cnpj']
                    p_no_gtin.cd_prod_serv = product_data['cd_prod_serv']
                    p_no_gtin.id_produto = PRODUCT_NO_CLASSIFIED
                    session.add(p_no_gtin)
                    #self.__write_info_log(f'-;Inserido Produto x Prod Serv Sem Gtim : Inserido Produto x Prod Serv sem Gtin - cnpj: {product_data["cnpj"]} cd_prod_serv: {product_data["cd_prod_serv"]} Produto não classificado : {PRODUCT_NO_CLASSIFIED}')     
                    self.__write_info_log('-;Inserido Produto x Prod Serv sem Gtin - cnpj: {} cd_prod_serv: {} Produto não classificado: {} ds_prod_serv: {}'\
                            .format(product_data['cnpj'], 
                                    product_data["cd_prod_serv"], 
                                    PRODUCT_NO_CLASSIFIED, 
                                    product_data["ds_prod_serv"])) 


    def inserir_nfce(self):
        chave_acesso = self.nota_fiscal.obter_chave_acesso()  
        dados_nfe = self.nota_fiscal.obter_dados_nfe_codigo_acesso(chave_acesso)
        
#        cursor = self.conexao.cursor()
        
        chave_acesso = self.nota_fiscal.obter_chave_acesso()  
        dados_nfe = self.nota_fiscal.obter_dados_nfe_codigo_acesso(chave_acesso)
      
        
#        sql =   'select nu_nfce                     \
#                from nota_fiscal                    \
#                where   cd_uf = %s and              \
#                        cnpj = %s and               \
#                        nu_nfce = %s and            \
#                        serie = %s and              \
#                        cd_modelo = %s'
#                        
#        cursor.execute(sql, (   dados_nfe['cd_uf'], 
#                                dados_nfe['cnpj'], 
#                                dados_nfe['nu_nfce'],
#                                dados_nfe['serie'],
#                                dados_nfe['cd_modelo'], ))
#        cursor.fetchall()
#                                    
#        if cursor.rowcount == 0:
#           
#            
#            sql = self.montar_insert(dados_nfe, 'nota_fiscal')
#            
#            cursor.execute(sql[0], sql[1])
            
        dd_complementares = self.nota_fiscal.obter_informacoes_complementares()
        dados_nfe['ds_informacoes_complementares'] = dd_complementares
        self.insert_invoice_data_in_db(dados_nfe, self.session)
            
#            if dd_complementares:
#                
#                sql =   'update nota_fiscal                     \
#                        set ds_informacoes_complementares = %s  \
#                        where   cd_uf = %s and                  \
#                                cnpj = %s and                   \
#                                nu_nfce = %s and                \
#                                serie = %s and                  \
#                                cd_modelo = %s'
#            
#                cursor.execute(sql, (dd_complementares,   
#                            dados_nfe['cd_uf'], 
#                            dados_nfe['cnpj'], 
#                            dados_nfe['nu_nfce'],
#                            dados_nfe['serie'],
#                            dados_nfe['cd_modelo'], ))
#            
#        else:
#            
#            print('Nota Fiscal {} serie {} modelo {} Cnpj {} já se encontra na base'.format(
#                                                                                        dados_nfe['nu_nfce'], 
#                                                                                        dados_nfe['serie'], 
#                                                                                        dados_nfe['cd_modelo'], 
#                                                                                        dados_nfe['cnpj']))
#            
#        cursor.close()
        
    
    def incluir_chaves(self, dict_valores):
        for chave,  valor in self.nota_fiscal.chaves_nota_fiscal.items():
            if chave not in dict_valores.keys():
                dict_valores[chave] = valor
                
                
    def __include_keys(self, dict_values, invoice_parser):
        for key,  value in invoice_parser.chaves_nota_fiscal.items():
            if key not in dict_values.keys():
                dict_values[key] = value
                
    def inserir_produtos_servicos_ean(self, produtos_servicos):
        cursor = self.conexao.cursor()
                
        for produto_servico in produtos_servicos:           #preenche o dicionario produtos_servicos_ncm a partir do dicionario produtos_servicos
            produtos_servicos_ncm = {   'cd_ncm_prod_serv':'',
                                        'ds_prod_serv':'', 
                                        'cd_prod_serv':'', 
                                        'cd_ex_tipi_prod_serv':'', 
                                        'cfop_prod_serv':'', 
                                        'cd_ean_prod_serv':''}
            
            for chave in produtos_servicos_ncm.keys():
                if chave in produto_servico.keys():
                    produtos_servicos_ncm[chave] = produto_servico[chave]
        
            sql =   'select cd_ncm_prod_serv                     \
                    from produtos_servicos_ean                    \
                    where   cd_ean_prod_serv = %s'
                            
            cursor.execute(sql, (produto_servico['cd_ean_prod_serv'],))
            cursor.fetchall()
                                        
            if cursor.rowcount == 0:
            
                sql = self.montar_insert(produtos_servicos_ncm, 'produtos_servicos_ean')
                
                cursor.execute(sql[0], sql[1])
                
                print('Inserido {}-{} com sucesso em produto_servico_ean'.format(produtos_servicos_ncm['cd_ean_prod_serv'], produtos_servicos_ncm['ds_prod_serv']))
                
            else:

                
                print('produto_servico_ean {}-{}  já se encontra na base'.format(produtos_servicos_ncm['cd_ean_prod_serv'], produtos_servicos_ncm['ds_prod_serv']))
                
        cursor.close()  


    def inserir_produtos_servicos_sem_gtim(self, produtos_servicos):
        cursor = self.conexao.cursor()
                
        for produto_servico in produtos_servicos:           #preenche o dicionario produtos_servicos_ncm a partir do dicionario produtos_servicos
            if produto_servico['cd_ean_prod_serv'].strip() == 'SEM GTIN':
                produtos_servicos_sem_gtim = {'cnpj':'','ds_prod_serv':'', 'cd_prod_serv':''}
                self.incluir_chaves(produto_servico)
                
                for chave in produtos_servicos_sem_gtim.keys():
                    if chave in produto_servico.keys():
                        produtos_servicos_sem_gtim[chave] = produto_servico[chave]
            
                sql =   'select cd_prod_serv                        \
                        from produtos_servicos_sem_gtim             \
                        where   cd_prod_serv = %s and               \
                                cnpj = %s'

                                
                cursor.execute(sql, (produtos_servicos_sem_gtim['cd_prod_serv'], \
                                     produtos_servicos_sem_gtim['cnpj']))
                cursor.fetchall()
                                            
                if cursor.rowcount == 0:
                    
                    max_manual_code_ean = self.get_max_manual_ean(cursor)
                    
                    produtos_servicos_sem_gtim['cd_gtim_prod_serv'] = max_manual_code_ean
                    
                    sql = self.montar_insert(produtos_servicos_sem_gtim, 'produtos_servicos_sem_gtim')
                    
                    cursor.execute(sql[0], sql[1])
                    
                    print('Inserido {}-{}-{} com sucesso em produto_servico_sem_gtim'.format(   produtos_servicos_sem_gtim['cnpj'], \
                                                                                                produtos_servicos_sem_gtim['cd_prod_serv'], 
                                                                                                produtos_servicos_sem_gtim['ds_prod_serv']))
                    
                else:                    
                    print('produto_servico sem GTIM {}-{}-{}  já se encontra na base'.format(   produtos_servicos_sem_gtim['cnpj'], \
                                                                                                produtos_servicos_sem_gtim['cd_prod_serv'], 
                                                                                                produtos_servicos_sem_gtim['ds_prod_serv']))
                    
                
        cursor.close()  
    
    
    def inserir_emitente(self):
        
#        cursor = self.conexao.cursor()
        
        dados_emitente = self.nota_fiscal.obter_dados_emitente_2()
        self.insert_supplier_data_in_db(dados_emitente, self.session)
        
#        sql =   'select cnpj                     \
#                from emitente                    \
#                where   cnpj = %s'
#                        
#        cursor.execute(sql, (   dados_emitente['cnpj'],))
#        cursor.fetchall()
#                                    
#        if cursor.rowcount == 0:
#        
#            sql = self.montar_insert(dados_emitente, 'emitente')
#            
#            cursor.execute(sql[0], sql[1])
#            
#            #self.conexao.commit()
#        else:
#            
#            print('Emitente {} - {} já se encontra na base'.format(  dados_emitente['cnpj'], 
#                                                                dados_emitente['razao_social']))
#            
#        cursor.close()
    
    def inserir_formas_pagamento(self):  
#        cursor = self.conexao.cursor()
        
        dados_formas_pagamento = self.nota_fiscal.obter_dados_cobranca()
        self.put_bill_data_in_db(dados_formas_pagamento, self.session)
#        if dados_formas_pagamento['ds_forma_pagamento']:
#            
#            self.incluir_chaves(dados_formas_pagamento)
#            
#            sql =   'select nu_nfce                     \
#                    from nota_fiscal_formas_pagamento   \
#                    where   cd_uf = %s and              \
#                            cnpj = %s and               \
#                            nu_nfce = %s and            \
#                            serie = %s and              \
#                            cd_modelo = %s'
#                        
#            cursor.execute(sql, (
#                                dados_formas_pagamento['cd_uf'], 
#                                dados_formas_pagamento['cnpj'], 
#                                dados_formas_pagamento['nu_nfce'],
#                                dados_formas_pagamento['serie'],
#                                dados_formas_pagamento['cd_modelo'], ))
#                        
#            
#            cursor.fetchall()
#                                    
#            if cursor.rowcount == 0:
#                
#                sql = self.montar_insert(dados_formas_pagamento, 'nota_fiscal_formas_pagamento')
#                cursor.execute(sql[0], sql[1])
#            
#                #self.conexao.commit()
#        else:
#            print('Nota Fiscal sem dados sobre formas de pagamento')
#        cursor.close()
        
    def inserir_totais(self):
        
#        cursor = self.conexao.cursor()
        
        totais = self.nota_fiscal.obter_dados_valores_totais()
        self.insert_total_data_in_db(totais, self.session)
            
#        self.incluir_chaves(totais)
#        
#        sql =   'select nu_nfce                     \
#                from nota_fiscal_totais             \
#                where   cd_uf = %s and              \
#                        cnpj = %s and               \
#                        nu_nfce = %s and            \
#                        serie = %s and              \
#                        cd_modelo = %s'
#                    
#        cursor.execute(sql, (
#                            totais['cd_uf'], 
#                            totais['cnpj'], 
#                            totais['nu_nfce'],
#                            totais['serie'],
#                            totais['cd_modelo'], ))
#                    
#        
#        cursor.fetchall()
#                                
#        if cursor.rowcount == 0:
#            
#            sql = self.montar_insert(totais, 'nota_fiscal_totais')
#            cursor.execute(sql[0], sql[1])
#        
#            #self.conexao.commit()
#        else:
#            print('Nota Fiscal {} serie {} modelo {} Cnpj {} já se encontra em nota_fiscal_totais'.format(
#                                                                                    totais['nu_nfce'], 
#                                                                                    totais['serie'], 
#                                                                                    totais['cd_modelo'], 
#                                                                                    totais['cnpj']))
#        cursor.close()
    
    def inserir_transporte(self):    
#        cursor = self.conexao.cursor()
        transporte = self.nota_fiscal.obter_dados_transporte()
        self.incluir_chaves(transporte)
        self.insert_delivery_data_in_db(transporte, self.session)
#        sql =   'select nu_nfce                     \
#                    from nota_fiscal_transporte   \
#                    where   cd_uf = %s and              \
#                            cnpj = %s and               \
#                            nu_nfce = %s and            \
#                            serie = %s and              \
#                            cd_modelo = %s'
#                        
#        cursor.execute(sql, (
#                            transporte['cd_uf'], 
#                            transporte['cnpj'], 
#                            transporte['nu_nfce'],
#                            transporte['serie'],
#                            transporte['cd_modelo'], ))
#                    
#        
#        cursor.fetchall()
#                                
#        if cursor.rowcount == 0:
#            
#            sql = self.montar_insert(transporte, 'nota_fiscal_transporte    ')
#            cursor.execute(sql[0], sql[1])
#        
#            #self.conexao.commit()
#        else:
#            print('Dados de Transporte já inseridos na Nota Fiscal {}'.format(transporte['nu_nfce']))
#        
#        cursor.close()
        
    
    def inserir_produtos_servicos(self):
        '''
            Inseri os produtos e serviços adquiridos na nota fiscal, 
            além de preencher a tabela de produtos_servicos_ean, e caso a produto não 
            tenha GTIM, inserie-o em produtos_servicos_sem_gtim
            
        '''

        produtos_servicos = self.nota_fiscal.obter_dados_produtos_e_servicos()

        self.insert_products_data_in_db(produtos_servicos)


    def adjust_prod_serv(self, product_data, session):
        query = session.query(ProdutoServicoAjuste)
        query = query.filter( ProdutoServicoAjuste.cnpj == product_data['cnpj'], 
                                          ProdutoServicoAjuste.cd_prod_serv_ajuste == product_data['cd_prod_serv'])

        if query.count() == 0:   #ProdutoServico não encontrado?(inseri!)
            prod_serv_ajuste = ProdutoServicoAjuste()   #inseri na tabela de ajuste
            prod_serv_ajuste.cnpj =  product_data['cnpj']
            prod_serv_ajuste.cd_prod_serv_ajuste = product_data['cd_prod_serv'] 
            if  product_data['cd_ean_prod_serv'] != 'SEM GTIN':
                prod_serv_ajuste.cd_ean_ajuste = product_data['cd_ean_prod_serv']
            prod_serv_ajuste.manual = 0
            session.add(prod_serv_ajuste)
            product_data['cd_ean_prod_serv_original'] = product_data['cd_ean_prod_serv']
            return product_data            
        else:
            result = query.first()
            if result.cd_ean_ajuste != None: 
                product_data['cd_ean_prod_serv_original'] = product_data['cd_ean_prod_serv']
                product_data['cd_ean_prod_serv'] = result.cd_ean_ajuste
            else:
                product_data['cd_ean_prod_serv_original'] = product_data['cd_ean_prod_serv']
            return product_data

    def criar_conexao(self):
        pass


    def gravar_dados_nfce(self):
        pass


    def get_max_manual_ean(self, cursor):
        
        sql = 'select max(cd_gtim_prod_serv) from nota_fiscal.produtos_servicos_sem_gtim where substring(cd_gtim_prod_serv,1,1)=\'X\';'
        
        cursor.execute(sql)
        
        row_proxy = cursor.fetchall()
    
        if row_proxy[0][0]:
            max_code = row_proxy[0][0][1:]      #retira o X do codigo
            max_code = 'X' + '{:014d}'.format(int(max_code) + 1)
            
        else:
            max_code = 'X{:014d}'.format(1)
        
        return max_code    
        
    def montar_insert(self, dict_campos, tabela):
        sql_insert = 'insert into ' + tabela + ' ( '
        sql_values = ''
        valores = []
        for campo,  valor in dict_campos.items():           
                
            if valor:
                if not sql_values:
                    sql_values = ' values( '
                else:
                    sql_values += ', '
                    sql_insert += ', '
                sql_insert += campo 
                sql_values += ' %s'
                valores.append(valor)
        sql_insert += ')'        
        sql_values += ')'
        return (sql_insert + sql_values, valores, )
            
def ajustar_texto(texto):
    tx = texto.replace('\xa0', '')          #retira caracter incluído no html
    tx = tx.replace('\n', '')                   #retira quebrar de linha
    brancos = re.compile(r'\s\s+')
    tx = brancos.sub('',  tx)                   #retira brancos em sequencia, deixando um só
    return tx.strip()     
                            #retira brancos do início e fim

def converter_data(data_string):    
    if data_string:
        data = datetime.datetime.strptime(data_string[:19],'%d/%m/%Y %H:%M:%S')
        return data.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return None
        

def obter_texto_labels(dict_labels, tag, aj_texto = False, aj_data = False,  aj_valor = False):
    '''
        Coleta todas as informações dos campos (labels) que estão dentro de uma determinada tag de html
        Argumentos:
        dict_labels (dicionario) Dicionario contendo {'texto_da_label':'Nome do Campo'},
        tag (obj:BeautifulSoup) - Tag BeautifulSoup onde vai ser procuradas as labels
        
        Retorna:
        dict_dados (dicionario): Dicionario contendo {'Nome do Campo' : 'Texto da Tag'}
        
        Cada 'texto label' 'do dicionario é procurado dentro da tag, caso ache, pega o texto da subsequente tag 'spam', e monta
            um novo dicionario {'Nome do Campo' : 'texto da tag Sam'
    '''
    if tag:
        dados = {}
        for texto_label in dict_labels.keys():
            label = tag.find('label', text = texto_label)
            if label:
                if aj_texto:
                    dados[dict_labels[texto_label]] = ajustar_texto(label.next_sibling.get_text())
                else:
                    dados[dict_labels[texto_label]] = label.next_sibling.get_text()
                if dict_labels[texto_label][:3] == 'cd_' and not dados[dict_labels[texto_label]]:
                    dados[dict_labels[texto_label]]  = 0
                if aj_data:
                    if dict_labels[texto_label][:3] == 'dt_':         #compara os 3 primeiros caracters do campo para saber se é um campo de data.
                        dados[dict_labels[texto_label]] = converter_data(dados[dict_labels[texto_label]])
                if aj_valor:
                    if dict_labels[texto_label][:3] == 'vl_' or dict_labels[texto_label][:3] == 'qt_':         #compara os 3 primeiros caracters do campo para saber se é um campo de data.
                        dados[dict_labels[texto_label]] = util.converte_monetario_float(dados[dict_labels[texto_label]])
            else:
                dados[dict_labels[texto_label]]  = None
        return dados
    else:
        return None
        
def make_logs_path():
    '''
        Verifica a existencia das pastas onde vão ser guardados os logs da aplicação
    '''
    log_path = 'data/logs'
    if os.path.exists('data'):        
        if not os.path.exists(log_path):            
            os.mkdir('log_path')
    else:        
        os.mkdir('data')
        os.mkdir(log_path) 
    return log_path

def teste_NfceParseGovBr():
#    nfce = NfceParseGovBr('', 
#                          verbose_log = True)
    nfce = NfceParseGovBr('/home/lcreina/Documents/cgu/campo.alegre.de.lourdes/vania.dionisio/ct.33.2018/pagamentos/pp.124.nota.fiscal.html', 
                          verbose_log = True)
    #
    print('**** Emitente ****')
    print('\n'.join([f'{chave}: {valor}' for chave, valor in nfce.obter_dados_emitente().items()]))
    print()
    print('**** Dados da Nota Fiscal ****')
    print('\n'.join([f'{chave}: {valor}' for chave, valor in nfce.obter_dados_nota().items()]))
    for i, dado_prod_serv in enumerate(nfce.obter_dados_produtos_e_servicos(), start=1):
        print(f'**** Produto e Serviços {i} ****')
        print('\n'.join([f'{chave}: {valor}' for chave,  valor in dado_prod_serv.items()]))

def nf_gov_para_csv(caminho):
    '''
        Gera um arquivo csv com os dados de notas fiscais constante na pasta
         (parâmetros): caminho (string) caminho para a pasta onde se encontram os arquivos.
         
    '''
    gerar_arquivo = False
    if os.path.exists(caminho):                                #a pasta existe?      
        print(f'Processando pasta {caminho} ...')
        for arq in os.listdir(caminho):                        #para cada arquivo na pasta
            if os.path.splitext(arq)[-1].lower() != '.html':   #verifica se é um arquivo html
                continue                                       #se não for pula pro próximo
            arq_nota_fiscal = os.path.join(caminho, arq)
            try:
                nota_fiscal = NfceParseGovBr(arq_nota_fiscal, 
                                        verbose_log = True)   #lê o arquivo de nota fiscal
            except Exception as e:
                print(f'Erro - {e}')                                #se der erro, mostra o erro
            else:                                                   #se não der erro na leitura, processa
                emitente =  nota_fiscal.obter_dados_emitente()
                dados_nota = nota_fiscal.obter_dados_nota()
                dados_prod_serv = nota_fiscal.obter_dados_produtos_e_servicos()
                if not gerar_arquivo:
                    csv_file_name = os.path.join(caminho, 'nfs_gov.csv')
                    print(csv_file_name)
                    csv_file = open(csv_file_name, 'w')
                    writer = csv.writer(csv_file, delimiter = ';',  quotechar = '"', quoting = csv.QUOTE_ALL)
                    writer.writerow([ 'nu_nfce', 
                                                'dt_emissao', 
                                                'vl_total', 
                                                'cnpj', 
                                                'razao_social', 
                                                'ds_prod_serv', 
                                                'qt_prod_serv', 
                                                'vl_prod_serv', 
                                                'un_comercial_prod_serv', 
                                                'vl_desconto_prod_serv', 
                                                'cd_ean_prod_serv', 
                                                'nu_prod_serv', 
                                                'endereco', 
                                                'bairro', 
                                                'cd_municipio'])
                    gerar_arquivo = True
                                                
                for prod_serv in dados_prod_serv:
                    writer.writerow([   dados_nota['nu_nfce'], \
                            dados_nota['dt_emissao'],  \
                            dados_nota['vl_total'],    \
                            emitente['cnpj'],     \
                            emitente['razao_social'],    \
                            prod_serv['ds_prod_serv'],   \
                            prod_serv['qt_prod_serv'], \
                            prod_serv['vl_prod_serv'],\
                            prod_serv['un_comercial_prod_serv'], \
                            prod_serv['vl_desconto_prod_serv'], \
                            prod_serv['cd_ean_prod_serv'], \
                           prod_serv['nu_prod_serv'], \
                            emitente['endereco'],\
                            emitente['bairro'], 
                            emitente['cd_municipio']]) 
        print('Processamento Finalizado.')
        if gerar_arquivo: #se o csv foi gerado...
            csv_file.close()
    else:
        print(f'Pasta inexistente: {caminho}')
        
        
def main_2(nt_fiscal):  
       
    print('*' * 10, 'Dados da Nota Fiscal', '*' * 10)
    chave_acesso = nt_fiscal.obter_chave_acesso()    
    print(nt_fiscal.obter_dados_nfe_codigo_acesso(chave_acesso))
    
    print('*' * 10, 'Emitente 2', '*' * 10)
    print(nt_fiscal.obter_dados_emitente_2())
    
    print('*' * 10, 'Produtos e Serviço', '*' * 10)
    print(nt_fiscal.obter_dados_produtos_e_servicos())
    
    print('*' * 10, 'Transporte', '*' * 10)
    print(nt_fiscal.obter_dados_transporte())
    
    print('*' * 10, 'Cobranca', '*' * 10)
    print(nt_fiscal.obter_dados_cobranca())
    
    print('*' * 10, 'Valores Totais', '*' * 10)
    print(nt_fiscal.obter_dados_valores_totais())
    
    print('*' * 10, 'Dados Complementares', '*' * 10)
    dd_complementares = nt_fiscal.obter_informacoes_complementares()
    if dd_complementares:
        print(len(dd_complementares))
    else:
        print('Nulo')


def ajustar_dados_emitente(emitente):
    dados_emitente = emitente
    if dados_emitente:
       for chave, valor in dados_emitente.items():
            if chave in ('cd_municipio', 'cd_pais'):         #para dados do tipo '1-descricao' pega somente o dado antes do '-'
                if isinstance(valor, str):
                    dado = valor.split('-')
                    if  len(dado) > 1:   #verifica se o dado veio no formato 'codigo-nome'
                        dados_emitente[chave] = dado[0]  #pega o codigo
                        if not dados_emitente[chave].strip():  #verfica se o código esta vazio
                            dados_emitente[chave] = '0'
                    else:  #caso o dado não venho no formato correto 
                        dados_emitente[chave] = '0'
            if chave in  ('cnpj', 'cep', 'telefone') :
                dados_emitente[chave] = util.retirar_pontuacao(valor)
    return dados_emitente


def renomear_arquivos_nfce(caminho):
    '''
    Parametros:
        (caminho:string) - Caminho da pasta onde estão os arquivos a serem renomeados
    '''
    if os.path.exists(caminho):                                #a pasta existe?
        log_file = os.path.join(caminho, 'arquivo.log')  
        for arq in os.listdir(caminho):                        #para cada arquivo na pasta
            if arq[0:3].lower() == 'nf_':                      #verifica se o arquivo já foi renomeado
                continue                                       #se já foi renomeado pula pro próximo
            if os.path.splitext(arq)[-1].lower() != '.html':   #verifica se é um arquivo html
                continue                                       #se não for pula pro próximo
            arq_nota_fiscal = os.path.join(caminho, arq)
            try:
                try:
                    nota_fiscal = NfceParse(arquivo_nfce =arq_nota_fiscal, 
                                            aj_valor = True, 
                                            log_file_name = log_file)   #lê o arquivo de nota fiscal
                except NfceArquivoInvalido:
                    nota_fiscal = NfceParseGovBr(arquivo_nfce =arq_nota_fiscal, 
                                            aj_valor = True, 
                                            log_file_name = log_file)   #lê o arquivo de nota fiscal gov.br
            except Exception as e:
                print(f'Erro - {e}')                                #se der erro, mostra o erro
            else:                                                   #se não der erro na leitura, processa
                acess_key = nota_fiscal.obter_chave_acesso()        #pega a chave de acesso da nota fiscal
                invoice_data = nota_fiscal.obter_dados_nfe_codigo_acesso(acess_key) #pega os dados da nota
                if type(invoice_data['dt_emissao']) is datetime.datetime:
                    dt = invoice_data['dt_emissao']
                else:
                    dt = dateutil.parser.parse(invoice_data['dt_emissao'], \
                                           dayfirst=True)           #converte o formata iso para datetime
                dados_emitente = nota_fiscal.obter_dados_emitente()     #pega os dados do emitente
                #o novo arquivo será, o nome de emitente(10 primeiros caracteres),
                #data/hora da compra e valor da nota
                razao_social = dados_emitente['razao_social']
                razao_social = re.sub(r'[\s\-_]', '',razao_social) #retira espaços e traços
                file_name = 'nf_' + razao_social[:10] +\
                            '_' + \
                            dt.strftime('%Y_%m_%d_%H_%M') +\
                            '_' + \
                            str(invoice_data['vl_total']) + \
                            '.html'
                shutil.move(os.path.join(caminho, arq),\
                            os.path.join(caminho,file_name))
                nota_fiscal.log.info(f'-;Arquivo {arq} renomeado para {file_name}')

        
if __name__ == '__main__':
    #arquivo = './nota_fiscal_arquivos/backup/29200513408943000108650010000444531023501903.yang.ping.html'
#    arquivo = 'page_source.html'
#    nt_fiscal = NfceParse(arquivo_nfce = arquivo, aj_texto = True, aj_data = True,  aj_valor = True  )
#    main_2(nt_fiscal)
#    renomear_arquivos_nfce('data/html_invoices')
    teste_NfceParseGovBr()
    pass
    


    
