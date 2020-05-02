import re, os, datetime, util
import logging
import mysql.connector
from bs4 import BeautifulSoup


class NfceArquivoInvalido(Exception):
    pass
   
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
    #    NFC-e.tintas.html
    #nota.fiscal.impressa.NFC-e.html    
    def __init__(self, arquivo_nfce ='NFC-e.tintas.html', aj_texto = False,  aj_data = False,  aj_valor = False, log_file_name = '',  logNivel = logging.INFO):
        
        self.file_nfce = arquivo_nfce
        
        if not log_file_name:
            
            nome_base = os.path.basename(arquivo_nfce)
            
            logging.basicConfig(level       = logNivel, \
                                filename    = nome_base + '.log', \
                                filemode    = 'w', \
                                format      = '%(levelname)s;%(asctime)s;%(name)s;%(funcName)s;%(message)s')
        else:
            logging.basicConfig(level       = logNivel, \
                                filename    = log_file_name, \
                                format      = '%(levelname)s;%(asctime)s;%(name)s;%(funcName)s;%(message)s')
            
        self.log = logging.getLogger(__name__)                    
        try:
            self.log.info('Abrindo arquivo {}'.format(arquivo_nfce))
            arq = open(arquivo_nfce,'r', encoding='utf-8')
            self.log.info('Arquivo aberto com sucesso')
            
        except Exception as e:
            self.log.info('Erro ao abrir {}'.format(arquivo_nfce))
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
            self.log.info('Nota Fiscal {nu_nfce} Serie {serie} Modelo {cd_modelo} Uf {cd_uf} cnpj {cnpj}'.format(**nfce))
        else:
            self.log.info('Arquivo de Nota Fiscal Inválido: {}'.format(arquivo_nfce))
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
        self.log.info('Obtendo dados sobre Nota Fiscal')
        
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
        if dados_completos:
            dados_nota['chave_acesso'] = codigo_acesso
            #inclui outros dados da nota
            ntfce = self.obter_dados_nfc_e()
            if ntfce:
                for chave, valor in ntfce.items():
                    if chave not in dados_nota.keys():
                        dados_nota[chave]= valor
                        str_log += str(chave)+ ' = ' + str(valor) + ' '
            
        self.log.info(str_log) 
        self.log.info('Dados sobre Nota Fiscal obtidos com sucesso')
        return dados_nota
        
    def obter_dados_nfc_e(self):
        '''
            Obtém os dados da nota fiscal a partir dos dados contindos em <div id="NFe">
        '''
        div = self._obter_informacao_por_id('NFe', 'Núḿero da Nota')
        
        if div:
            dados_nfc = obter_texto_labels(NfceParse._dados_nfc_e, div,  self.aj_texto,  self.aj_data, self.aj_valor)
            return dados_nfc
            
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
        
        self.log.info('Obtendo dados sobre produtos e serviços')
        
        dados_produtos_servicos = []
        str_log = ''
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
                        str_log += str(chave) + ' = ' + str(campo) + ' '                    
                        
                    if dado_produtos_servicos_2:
                        for chave,  campo  in dado_produtos_servicos_2.items():
                            dado_produtos_servicos[chave] = campo
                            str_log += str(chave) + ' = ' + str(campo) + ' '
                            
                    dados_produtos_servicos.append(dado_produtos_servicos)
                    
                if dados_produtos_icms:
                    for chave,  valor in dados_produtos_icms.items():
                        dado_produtos_servicos[chave] = valor
                        str_log += str(chave) + ' = ' + str(campo) + ' '
                        
                if dados_produtos_cofins:   
                    for chave,  valor in dados_produtos_cofins.items():
                        dado_produtos_servicos[chave] = valor
                        str_log += str(chave) + ' = ' + str(campo) + ' '
                    
                if dados_produtos_pis:   
                    for chave,  valor in dados_produtos_pis.items():
                        dado_produtos_servicos[chave] = valor
                        str_log += str(chave) + ' = ' + str(campo) + ' '
                self.log.info(str_log)        
                str_log = ''
        else:
                self.log.info('Não foi possivel encontrar produtos e serviços na nota, não foram encontradas tag <table> com id do tipo: table-1,table-2,table-3 ...')
                return None
                
        self.log.info('Dados sobre produtos e serviços obtidos com sucesso')
        return dados_produtos_servicos
                
    def obter_numero_nota(self):
        numero_nota = self._obter_informacao_por_id('lbl_numero_nfe', 'Núḿero da Nota')
        if numero_nota:
            return numero_nota.get_text()
        else:
            return None
    
    
    def obter_dados_transporte(self):
        self.log.info('Obtendo dados sobre transporte')
        id = self.dados_nota_fiscal.find('div', {'id': 'Transporte'})
        str_log = ''       
        if id:
          
           dados_transporte = obter_texto_labels(NfceParse._dados_transporte, id,  self.aj_texto)
           for chave, valor in dados_transporte.items():
               str_log += chave + ' = ' + valor + ' '
               
           self.log.info(str_log)
           self.log.info('Dados sobre produtos e serviços obtidos com sucesso')
           return dados_transporte
        else:
            self.log.info('Não foi possivel encontrar dados do transporte na nota, , não foi encontrada a tag <table> com id do tipo: "Transporte"')
            return None
            
    def obter_informacoes_complementares(self):
        ''' Obtem Dados complementares da Nota'''
        
        self.log.info('Obtendo dados sobre informações complementares')
        #procura uma tag <td> no html da nota fiscal que contenha class='table-titulo-aba-interna' e text='Informações Complementares de Interesse do Contribuinte'
        td = self.dados_nota_fiscal.find('td', {'class': 'table-titulo-aba-interna'},  text = 'Informações Complementares de Interesse do Contribuinte')
        if td:
            
            if td.parent.parent.name =='table': #caso a estrutura seja <table><tr><td>
                inf_complementar = td.parent.parent.next_sibling.next_sibling.get_text() 
                self.log.info('Dados Complementares = ' + inf_complementar)
                self.log.info('Dados Complementares obtidos com sucesso')
                return inf_complementar
            elif td.parent.parent.parent.name == 'table': #caso a estrutura seja <table><tbody><tr><td>
                inf_complementar = td.parent.parent.parent.next_sibling.next_sibling.get_text()
                self.log.info('Dados Complementares = ' + inf_complementar)
                self.log.info('Dados Complementares obtidos com sucesso')
                return inf_complementar
            else:
                self.log.info('Não foi possivel encontrar as inforamções complementares da Nota, não encontrada a tab table que engloba a tag <td> das inf. complementares')
                return None
        else:
            self.log.info('Não foi possivel as informações complementares da Nota, não foi encontrada tag <td> com class="table-titulo-aba-interna" e text ="Informações Complementares de Interesse do Contribuinte"')
    
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
        
        self.log.info('Obtendo dados sobre valores totais da Nota')
        div = self.dados_nota_fiscal.find('div', {'id': 'Totais'})
        if div:         
           str_log = '' 
           dados_totais = obter_texto_labels(NfceParse._dados_totais, div, self.aj_texto, self.aj_data, self.aj_valor)
           for chave, valor in dados_totais.items():
               str_log += str(chave) + ' = ' + str(valor) + '  '
               
           self.log.info(str_log)
           self.log.info('Dados sobre valores totais da Nota obtidos com sucesso')
           return dados_totais
        else:
            self.log.info('Não foi possivel encontrar os totais da nota, não foi encontrada a <div> com id igual a "Totais"')
            return None
        
    
    def obter_dados_cobranca(self):
        ''' Obtem os dados da cobrança do arquivo html relativo a Notas Fiscais'''
        
        self.log.info('Obtendo dados sobre Cobrança')
        
        campos = (  'ds_forma_pagamento',  'vl_pagamento',  'cnpj_credenciadora',  'bandeira_operacao',  \
                            'numero_autorizacao')
                            
        #não foi possivel utilizar a função obter_texto_labels, pois os <span> não ficam ao lodo do <label>
        id = self.dados_nota_fiscal.find('div', {'id': 'Cobranca'})
        spans = id.findAll('span')
        
        if spans:
            str_log = ''
            cobranca = {}
            for indice,  span in enumerate(spans):  
                valor = span.get_text()
                cobranca[campos[indice]] = valor
                str_log += str(campos[indice]) + ' = ' + str(valor) + ' '
                
            self.log.info('Dados de Cobrança-> ' + str_log)
            self.log.info('Dados de Cobrança obtidos com sucesso')
            return cobranca
        else:
            self.log.info('Não foi possivel encontrar dados da cobrança na nota, não foi encontrada a <div> com id igual a "Cobranca"')
            return None
        
    def obter_dados_emitente_2(self):
        
        self.log.info('Obtendo dados sobre Emitentes')
        
        div = self.dados_nota_fiscal.find('div', {'id': 'Emitente'})
        
        if div:
            str_log = ''
            dados_emitente = obter_texto_labels(NfceParse._dados_emitente, div,  self.aj_texto, self.aj_data, self.aj_valor)
           
            if dados_emitente:
               for chave, valor in dados_emitente.items():
                    if chave in ('cd_municipio', 'cd_pais'):         #para dados do tipo '1-descricao' pega somente o dado antes do '-'
                       dados_emitente[chave] = valor.split('-')[0]  
                    if chave in  ('cnpj', 'cep', 'telefone') :
                        dados_emitente[chave] = util.retirar_pontuacao(valor)
                        
                    str_log += str(chave) + ' = ' + str(dados_emitente[chave]) + ' '
                    
            self.log.info(str_log)
            self.log.info('Dados sobre Emitentes obtidos com sucesso')            
            return dados_emitente
        else:
            return None
            
    def obter_dados_emitente(self, id = 'Emitente'):
        ''' Obtem dados relativos ao Emitente da Nota Fiscal'''
        
        self.log.info('Obtendo dados do Emitente da Nota Fiscal')   
        
        #obtem a div com id 'Emitente'
        div_emitente = self._obter_informacao_por_id(id, 'Emitente')
        
        
        if div_emitente:            #se acho a div 'Emitente'
            str_log = ''
            #informações disponiveis do emitente na nota
            campos = (  'razao_social', 'nm_fantasia',  'cnpj',  'endereco',  'bairro_distrito',  'cep',  \
                                'cd_municipio',  'telefone',  'uf',  'cd_pais',  'insc_estadual',  \
                                'insc_estadual_substituto',  'insc_municipal',  \
                                'cd_municipio_ocorrencia',  'cnae_fiscal',  'ds_regime_tributario')
            #obtem as tags filhas de div 'Emitente' e transforma numa lista
            lst_emitente = list(div_emitente.children)            
            #cria um novo objeto BeautifuSoup a partir dos filhos da div 'Emitente', usei a função str, sem ela dá erro
            table_emitente = BeautifulSoup(str(lst_emitente[1]), 'lxml')
        
            emitente={}             #cria um dicionario para guardar as informações do emitente
            
            for chave, span in enumerate(table_emitente.findAll('span')):     
                if campos[chave]  in ('cnpj', 'cep', 'telefone') :
                     valor = util.retirar_pontuacao(ajustar_texto(span.get_text()))
                     emitente[campos[chave]] = valor
                     str_log += str(campos[chave]) + '=' + str(valor) + ' '
                elif campos[chave]  in ('cd_municipio', 'cd_pais') :     #este campos tem a seguinte formatacao 'cogigo-descricao'
                    dados = ajustar_texto(span.get_text()).split('-')                                        #quebra o campo em '-'
                    valor = dados[0].strip() 
                    emitente[campos[chave]] = valor                                              #guarda o codigo
                    str_log += str(campos[chave]) + '=' + str(valor) + ' '
                else:
                    valor = ajustar_texto(span.get_text())
                    emitente[campos[chave]] = valor 
                    str_log += str(campos[chave]) + '=' + str(valor) + ' '
                    
            self.log.info('retornou->' +  str_log)   
            return emitente
        else:
            self.log.info('Emitente não encontrado, nenhuma tag com id="Emitente"' + str_log) 
            return None
            
        
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
    def __init__(self,  nota_fiscal_e, 
                        user        =   'nota_fiscal_app', 
                        password    =   'wolverine', 
                        host        =   '127.0.0.1', 
                        database    =   'nota_fiscal'):
                            
        self.conexao = mysql.connector.connect(user = user,  password = password,  host = host,  database = database)
        
        self.nota_fiscal = nota_fiscal_e
    
    
        
    def inserir_nfce(self):
        
        
        cursor = self.conexao.cursor()
        
        chave_acesso = self.nota_fiscal.obter_chave_acesso()  
        dados_nfe = self.nota_fiscal.obter_dados_nfe_codigo_acesso(chave_acesso)
        
        sql =   'select nu_nfce                     \
                from nota_fiscal                    \
                where   cd_uf = %s and              \
                        cnpj = %s and               \
                        nu_nfce = %s and            \
                        serie = %s and              \
                        cd_modelo = %s'
                        
        cursor.execute(sql, (   dados_nfe['cd_uf'], 
                                dados_nfe['cnpj'], 
                                dados_nfe['nu_nfce'],
                                dados_nfe['serie'],
                                dados_nfe['cd_modelo'], ))
        cursor.fetchall()
                                    
        if cursor.rowcount == 0:
           
            
            sql = self.montar_insert(dados_nfe, 'nota_fiscal')
            
            cursor.execute(sql[0], sql[1])
            
            dd_complementares = self.nota_fiscal.obter_informacoes_complementares()
            
            if dd_complementares:
                
                sql =   'update nota_fiscal                     \
                        set ds_informacoes_complementares = %s  \
                        where   cd_uf = %s and                  \
                                cnpj = %s and                   \
                                nu_nfce = %s and                \
                                serie = %s and                  \
                                cd_modelo = %s'
            
                cursor.execute(sql, (dd_complementares,   
                            dados_nfe['cd_uf'], 
                            dados_nfe['cnpj'], 
                            dados_nfe['nu_nfce'],
                            dados_nfe['serie'],
                            dados_nfe['cd_modelo'], ))
            
        else:
            
            print('Nota Fiscal {} serie {} modelo {} Cnpj {} já se encontra na base'.format(
                                                                                        dados_nfe['nu_nfce'], 
                                                                                        dados_nfe['serie'], 
                                                                                        dados_nfe['cd_modelo'], 
                                                                                        dados_nfe['cnpj']))
            
        cursor.close()
        
    
    def incluir_chaves(self, dict_valores):
        for chave,  valor in self.nota_fiscal.chaves_nota_fiscal.items():
            if chave not in dict_valores.keys():
                dict_valores[chave] = valor
                
                
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
        cursor = self.conexao.cursor()
        
        dados_emitente = self.nota_fiscal.obter_dados_emitente_2()
        
        sql =   'select cnpj                     \
                from emitente                    \
                where   cnpj = %s'
                        
        cursor.execute(sql, (   dados_emitente['cnpj'],))
        cursor.fetchall()
                                    
        if cursor.rowcount == 0:
        
            sql = self.montar_insert(dados_emitente, 'emitente')
            
            cursor.execute(sql[0], sql[1])
            
            #self.conexao.commit()
        else:
            
            print('Emitente {} - {} já se encontra na base'.format(  dados_emitente['cnpj'], 
                                                                dados_emitente['razao_social']))
            
        cursor.close()
    
    def inserir_formas_pagamento(self):  
        cursor = self.conexao.cursor()
        
        dados_formas_pagamento = self.nota_fiscal.obter_dados_cobranca()
        if dados_formas_pagamento['ds_forma_pagamento']:
            
            self.incluir_chaves(dados_formas_pagamento)
            
            sql =   'select nu_nfce                     \
                    from nota_fiscal_formas_pagamento   \
                    where   cd_uf = %s and              \
                            cnpj = %s and               \
                            nu_nfce = %s and            \
                            serie = %s and              \
                            cd_modelo = %s'
                        
            cursor.execute(sql, (
                                dados_formas_pagamento['cd_uf'], 
                                dados_formas_pagamento['cnpj'], 
                                dados_formas_pagamento['nu_nfce'],
                                dados_formas_pagamento['serie'],
                                dados_formas_pagamento['cd_modelo'], ))
                        
            
            cursor.fetchall()
                                    
            if cursor.rowcount == 0:
                
                sql = self.montar_insert(dados_formas_pagamento, 'nota_fiscal_formas_pagamento')
                cursor.execute(sql[0], sql[1])
            
                #self.conexao.commit()
        else:
            print('Nota Fiscal sem dados sobre formas de pagamento')
        cursor.close()
        
    def inserir_totais(self):
        
        cursor = self.conexao.cursor()
        
        totais = self.nota_fiscal.obter_dados_valores_totais()
        
            
        self.incluir_chaves(totais)
        
        sql =   'select nu_nfce                     \
                from nota_fiscal_totais             \
                where   cd_uf = %s and              \
                        cnpj = %s and               \
                        nu_nfce = %s and            \
                        serie = %s and              \
                        cd_modelo = %s'
                    
        cursor.execute(sql, (
                            totais['cd_uf'], 
                            totais['cnpj'], 
                            totais['nu_nfce'],
                            totais['serie'],
                            totais['cd_modelo'], ))
                    
        
        cursor.fetchall()
                                
        if cursor.rowcount == 0:
            
            sql = self.montar_insert(totais, 'nota_fiscal_totais')
            cursor.execute(sql[0], sql[1])
        
            #self.conexao.commit()
        else:
            print('Nota Fiscal {} serie {} modelo {} Cnpj {} já se encontra em nota_fiscal_totais'.format(
                                                                                    totais['nu_nfce'], 
                                                                                    totais['serie'], 
                                                                                    totais['cd_modelo'], 
                                                                                    totais['cnpj']))
        cursor.close()
    
    def inserir_transporte(self):    
        cursor = self.conexao.cursor()
        transporte = self.nota_fiscal.obter_dados_transporte()
        self.incluir_chaves(transporte)
        sql =   'select nu_nfce                     \
                    from nota_fiscal_transporte   \
                    where   cd_uf = %s and              \
                            cnpj = %s and               \
                            nu_nfce = %s and            \
                            serie = %s and              \
                            cd_modelo = %s'
                        
        cursor.execute(sql, (
                            transporte['cd_uf'], 
                            transporte['cnpj'], 
                            transporte['nu_nfce'],
                            transporte['serie'],
                            transporte['cd_modelo'], ))
                    
        
        cursor.fetchall()
                                
        if cursor.rowcount == 0:
            
            sql = self.montar_insert(transporte, 'nota_fiscal_transporte    ')
            cursor.execute(sql[0], sql[1])
        
            #self.conexao.commit()
        else:
            print('Dados de Transporte já inseridos na Nota Fiscal {}'.format(transporte['nu_nfce']))
        
        cursor.close()
        
    
    def inserir_produtos_servicos(self):
        '''
            Inseri os produtos e serviços adquiridos na nota fiscal, 
            além de preencher a tabela de produtos_servicos_ean, e caso a produto não 
            tenha GTIM, inserie-o em produtos_servicos_sem_gtim
            
        '''
        
        cursor = self.conexao.cursor()
        
        #obtem os dados dos produtos na nota fiscal
        produtos_servicos = self.nota_fiscal.obter_dados_produtos_e_servicos()
        
        self.inserir_produtos_servicos_ean(produtos_servicos) #inseri em produtos_servicos_ean
        self.inserir_produtos_servicos_sem_gtim(produtos_servicos) #inseri em produtos_servicos_gtim
        
        for prod_serv in produtos_servicos:            
            
            self.incluir_chaves(prod_serv)
            #verifica se já tem o produto na tabela
            sql =   'select nu_nfce                     \
                    from produtos_servicos              \
                    where   cd_uf = %s and              \
                            cnpj = %s and               \
                            nu_nfce = %s and            \
                            serie = %s and              \
                            cd_modelo = %s and          \
                            nu_prod_serv = %s'
                        
            cursor.execute(sql, (
                                prod_serv['cd_uf'], 
                                prod_serv['cnpj'], 
                                prod_serv['nu_nfce'],
                                prod_serv['serie'],
                                prod_serv['cd_modelo'], 
                                prod_serv['nu_prod_serv'], ))
                        
            
            cursor.fetchall()
                                    
            if cursor.rowcount == 0:                                            #não tem o produto?
                
                sql = self.montar_insert(prod_serv, 'produtos_servicos    ')    
                cursor.execute(sql[0], sql[1])                                  #inseri o produto
            
            else:
                print('Produto {} já incluido na Nota Fiscal {}'.format(prod_serv['ds_prod_serv'],  prod_serv['nu_nfce']))

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
        Coleta todas as informações dos campos (labels) que estão dentro de uma obter_texto_labels determinada tag de html
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

    
if __name__ == '__main__':
    #arquivo = './nota_fiscal_arquivos/backup/29200513408943000108650010000444531023501903.yang.ping.html'
    #nt_fiscal = NfceParse(arquivo_nfce = arquivo, aj_texto = True, aj_data = True,  aj_valor = True  )
    #main_2(nt_fiscal)
    pass
    


    
