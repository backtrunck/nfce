#codigo para obter o captch obtido em 
#https://stackoverflow.com/questions/36636255/selenium-downloading-different-captcha-image-than-the-one-in-browser

import base64, re
import tkinter as tk
import nfce
from tkinter.messagebox import showwarning, askokcancel
from nfce_scrapper import   get_logger,\
                            initialize,\
                            wait_by_id, \
                            wait_presence_by_id
                            
from interfaces_graficas import ScrolledText,\
                                ScrolledTextHandler,\
                                get_image,\
                                show_modal_win
                                
from util import    check_key_nfce,\
                    converte_monetario_float,\
                    retirar_pontuacao
                    
from bs4 import BeautifulSoup
from nfce_models import Session


sefaz_ba_site = 'https://nfe.sefaz.ba.gov.br/servicos/nfce/Modulos/Geral/NFCEC_consulta_chave_acesso.aspx'

def main():
    make_window()
    return 
  

def wait_html_errors(drive, qt_seconds, id_tag):
    '''
        Aguarda para ver se o elemento do html (que informa erro) esta na tela
    '''
    if not wait_presence_by_id(drive, qt_seconds, id_tag):
        element = drive.find_element_by_id(id_tag)
        if element.text:
            showwarning('Download Nota Fiscal',element.text)  
            return 0
        else:
            return 1
    else:
        return 1
        
        
def wait_html_tab(drive, qt_second, id_tab, alert):
    '''
        Aguarda uma determinada aba ser aberta no site. 
        parâmetros:
            (drive objeto): Selenium WebDrive
            (qt_second int): Quantidade de tempo a esperar por uma aba ser aberta
            (id_tab: string): tag id do html que representa a aba a ser esperada
            (alert: string): caso o tempo de espera estoure, apresenta uma mensagem para esperar ou sair
        Retorno: 0 - site respondeu no tempo
                 1 - timeout
    '''
    result =  wait_by_id(drive, qt_second, id_tab)
    while result:
            if askokcancel('Download Nota Fiscal',alert):
                result = wait_by_id(drive, qt_second, id_tab)
            else:
                return 1        
    return result
    
def search_button(win):
    drive = win.drive
    invoice_key = win.entry_key_nfce.get()
    if not invoice_key: #se não digitou a chave da nota retorna
        showwarning('Download Nota Fiscal','Informe a Chave de Acesso da Nota Fiscal')  
        return        
    if not check_key_nfce(invoice_key):
        showwarning('Download Nota Fiscal','Chave da Nota Fiscal Inválida')  
        return
    #if  not win.solved_captcha:
    element = win.drive.find_element_by_id('img_captcha')
    path='data/invoices/capcha.png' 
    
    img_captcha_base64 = drive.execute_async_script("""
        var ele = arguments[0], callback = arguments[1];
        ele.addEventListener('load', function fn(){
          ele.removeEventListener('load', fn, false);
          var cnv = document.createElement('canvas');
          cnv.width = this.width; cnv.height = this.height;
          cnv.getContext('2d').drawImage(this, 0, 0);
          callback(cnv.toDataURL('image/jpeg').substring(22));
        }, false);
        ele.dispatchEvent(new Event('load'));
        """, element)
    # save the captcha to a file            
    with open(path, 'wb') as f:
        f.write(base64.b64decode(img_captcha_base64))
    #abre a tela para solucionar o captcha
    captcha_solution = make_dialog_captcha(path)
    if not captcha_solution: #se não digitou o captcha (fechou janela), sai.
        return
    search_box = drive.find_element_by_id('txt_cod_antirobo') 
    search_box.clear()
    search_box.send_keys(captcha_solution)          #insere o texto do captch
    key_box = drive.find_element_by_id('txt_chave_acesso')
    key_box.send_keys(invoice_key)                  # insere chave da nota fiscal        
    button =  drive.find_element_by_id('btn_consulta_completa')         
    button.click()      #faz a pesquisa
    if not wait_html_errors(drive, 10, 'lbl_invalido'):
        return 
    win.text_logger.erase()
    button =  drive.find_element_by_id('btn_visualizar_abas')
    button.click()      #visualização da nota em abas
    
    if wait_html_tab(drive, 10, 'btn_aba_nfe', "Site Lento, Aguardar pela Visualização da Nfe?"):
        return #se optou por não aguardar sai
    invoice_data = get_invoice_data(drive, invoice_key)        #pega os dados da nota fiscal  
    win.logger.info(f'Nota: {invoice_data["numero"]} Emissão: {invoice_data["dt_emissao"]} Valor: {invoice_data["vl_total"]}')
    emitente_button = drive.find_element_by_id('btn_aba_emitente')
    emitente_button.click()         #abre a aba emitente da nota
    
    if wait_html_tab(drive, 10, 'btn_aba_emitente', "Site Lento, Aguardar pela Visualização dos Emmitente da Nota?"):
        return #se optou por não aguardar sai
    supplier_data = get_supplier_data(drive)
    win.logger.info(f'Emitente: {supplier_data["razao_social"]} Cnpj: {supplier_data["cnpj"]}')
    products_button = drive.find_element_by_id('btn_aba_produtos')
    products_button.click()         #abre a aba de produtos e serviços  
    
    if wait_html_tab(drive, 10, 'btn_aba_produtos', "Site Lento, Aguardar pela Visualização dos Produtos/Serviços da Nota?"):
        return #se optou por não aguardar sai    
    products_data = get_products_data(drive, invoice_data)
    for i, product_data in enumerate(products_data, start=1):
        win.logger.info(f'{i}-{product_data["ds_prod_serv"]} Quant: {product_data["qt_prod_serv"]} Valor: {product_data["vl_prod_serv"]}')
    products_totais = drive.find_element_by_id('btn_aba_totais')
    products_totais.click()         #abre a aba valores totais da nota fiscal
    
    if wait_html_tab(drive, 10, 'btn_aba_totais', "Site Lento, Aguardar pela Visualização dos Totais da Nota?"):
        return #se optou por não aguardar sai    
    total_data = get_total_data(drive)
    total_data.update(invoice_data)
    products_transporte = drive.find_element_by_id('btn_aba_transporte')
    products_transporte.click()     #abre a aba transporte
    
    if wait_html_tab(drive, 10, 'btn_aba_transporte', "Site Lento, Aguardar pela Visualização do Transporte da Nota?"):
        return #se optou por não aguardar sai    
    delivery_data  = get_delivery_data(drive)
    delivery_data.update(invoice_data)
    products_cobranca = drive.find_element_by_id('btn_aba_cobranca')
    products_cobranca.click()       #abre a aba cobranca
    
    if wait_html_tab(drive, 10, 'btn_aba_cobranca', "Site Lento, Aguardar pela Visualização da Cobrança da Nota?"):
        return #se optou por não aguardar sai    
    bill_data = get_payment_data(drive)
    bill_data.update(invoice_data)
    button_adict = drive.find_element_by_id('btn_aba_infadicionais')
    button_adict.click()            #abre a aba informações adicionais 
    
    if wait_html_tab(drive, 10, 'btn_aba_infadicionais', "Site Lento, Aguardar pela Visualização das Inf. Adicionais da Nota?"):
        return #se optou por não aguardar sai    
    invoice_data['ds_informacoes_complementares'] = get_extra_data(drive)
    
    session = Session()
    try:    
        nfcebd = nfce.NfceBd(win.logger)
        nfcebd.insert_supplier_data_in_db(supplier_data, session)
        nfcebd.insert_invoice_data_in_db(invoice_data, session)
        nfcebd.insert_payment_data_in_db(bill_data, session)
        nfcebd.insert_total_data_in_db(total_data, session)
        nfcebd.insert_delivery_data_in_db(delivery_data, session)    
        nfcebd.insert_products_data_in_db(products_data, session)
    except Exception as e:
        session.rollback()
        print(e)
    else:
        session.commit()
    
    button_adict = drive.find_element_by_id('btn_voltar')
    button_adict.click()            #abre a aba informações adicionais 
    
#drive.close()


def get_delivery_data(drive):
    page = BeautifulSoup(drive.page_source, 'lxml') 
    id = page.find('div', {'id': 'Transporte'})
    if id:
       dados_transporte = nfce.obter_texto_labels(nfce.NfceParse._dados_transporte, id,  True)
       return dados_transporte
    else:
        return None


def get_total_data(drive):
    page = BeautifulSoup(drive.page_source, 'lxml') 
    div = page.find('div', {'id': 'Totais'})
    if div:         
       dados_totais = nfce.obter_texto_labels(nfce.NfceParse._dados_totais, div, True, True, True)
       return dados_totais
    else:
        return None


def get_extra_data(drive):
    page = BeautifulSoup(drive.page_source, 'lxml') 
    td = page.find('td', {'class': 'table-titulo-aba-interna'},  text = 'Informações Complementares de Interesse do Contribuinte')
    if td:
        if td.parent.parent.name =='table': #caso a estrutura seja <table><tr><td>
            inf_complementar = td.parent.parent.next_sibling.next_sibling.get_text() 
            return inf_complementar
        elif td.parent.parent.parent.name == 'table': #caso a estrutura seja <table><tbody><tr><td>
            inf_complementar = td.parent.parent.parent.next_sibling.next_sibling.get_text()            
            return inf_complementar
        else:
            return None
    else:
        return None

        
def get_payment_data(drive):
    campos = (  'ds_forma_pagamento',
                'vl_pagamento',
                'cnpj_credenciadora',
                'bandeira_operacao',
                'numero_autorizacao')
    page = BeautifulSoup(drive.page_source, 'lxml')             
    id = page.find('div', {'id': 'Cobranca'})
    spans = id.findAll('span')
    
    if spans:
        str_log = ''
        cobranca = {}
        for indice,  span in enumerate(spans):  
            valor = span.get_text()
            cobranca[campos[indice]] = valor
            str_log += str(campos[indice]) + ' = ' + str(valor) + ' '
        return cobranca
    else:
        return None


def get_cofins_data(tag):
        td = tag.find('td', {'class': 'table-titulo-aba-interna'},  text = 'COFINS')
        if td:
           if td.parent.parent.name == 'tbody':
                tabela = td.parent.parent.parent
           else:
                tabela = td.parent.parent
           div = tabela.next_sibling
           dados_cofins = nfce.obter_texto_labels(nfce.NfceParse._dados_cofins, div,  True, True, True)
           return dados_cofins
        else:
            return None


def get_pis_data(tag):    
    td = tag.find('td', {'class': 'table-titulo-aba-interna'},  text = 'PIS')
    if td:
       #obtem a tag <table> que contém a <td> procurada, a estrutura do html esta assim <table> <tbory><tr><td> 
        if td.parent.parent.name == 'tbody':
            tabela = td.parent.parent.parent
        else:
            tabela = td.parent.parent
        #pega a proxima div irmã que contém os labels relativos ao ICMS normal
        div = tabela.next_sibling
        dados_pis = nfce.obter_texto_labels(nfce.NfceParse._dados_pis, div,  True, True, True)
       
        return dados_pis
    else:
        return None


def get_icms_data(tag):
    td = tag.find('td', {'class': 'table-titulo-aba-interna'},  text = 'ICMS Normal e ST')
    if td:            
       #obtem a tag <table> que contém a <td> procurada, a estrutura do html esta assim <table> <tbory><tr><td> 
        if td.parent.parent.name == 'tbody':
            
            tabela = td.parent.parent.parent                
        else:                
            tabela = td.parent.parent                
        #pega a proxima tabela irmã que contém os labels relativos ao ICMS normal
        tabela = tabela.next_sibling
        dados_icms_normal = nfce.obter_texto_labels(nfce.NfceParse._dados_icms_normal, tabela,  True, True,  True)
       
        return dados_icms_normal
    else:
        return None


def get_products_data(drive, invoice_data):
    data_produts = []
    page = BeautifulSoup(drive.page_source, 'lxml')    
    tables = page.findAll('table', {'id': re.compile('table-\d+')})
    for indice_tabela,  tabela in enumerate(tables):
        data_product={}
        tr = tabela.previous_sibling
        data_product['nu_prod_serv'] = tr.find('label', text = 'Número').next_sibling.get_text()
        data_product['ds_prod_serv'] = tr.find('label', text = 'Descrição').next_sibling.get_text()
        data_product['qt_prod_serv'] = tr.find('label', text = 'Qtd.').next_sibling.get_text()
        data_product['un_comercial_prod_serv'] = tr.find('label', text = 'Unidade Comercial').next_sibling.get_text()
        data_product['vl_prod_serv'] = tr.find('label', text = 'Valor (R$)').next_sibling.get_text()
        
        data_product['cd_prod_serv'] = tabela.find('label', text = 'Código do Produto').next_sibling.get_text()
        data_product['cd_ncm_prod_serv'] = tabela.find('label', text = 'Código NCM').next_sibling.get_text()
        data_product['cd_ex_tipi_prod_serv'] = tabela.find('label', text = 'Código EX da TIPI').next_sibling.get_text()
        data_product['cfop_prod_serv'] = tabela.find('label', text = 'CFOP').next_sibling.get_text()
        data_product['vl_out_desp_acess'] = tabela.find('label', text = 'Outras Despesas Acessórias').next_sibling.get_text()
        data_product['vl_desconto_prod_serv'] = tabela.find('label', text = 'Valor do Desconto').next_sibling.get_text()
        data_product['vl_frete_prod_serv'] = tabela.find('label', text = 'Valor Total do Frete').next_sibling.get_text()
        data_product['vl_seguro_prod_serv'] = tabela.find('label', text = 'Valor do Seguro').next_sibling.get_text()
        data_product['ind_composicao_prod_serv'] = tabela.find('label', text = '\n                              Indicador de Composição do Valor Total da NF-e\n                            ').next_sibling.get_text()
        data_product['cd_ean_prod_serv'] = tabela.find('label', text = 'Código EAN Comercial').next_sibling.get_text()
        data_product['qt_comercial_prod_serv'] = tabela.find('label', text = 'Quantidade Comercial').next_sibling.get_text()
        data_product['cd_ean_tributavel_prod_serv'] = tabela.find('label', text = 'Código EAN Tributável').next_sibling.get_text()
        data_product['un_tributavel_prod_serv'] = tabela.find('label', text = 'Unidade Tributável').next_sibling.get_text()
        data_product['qt_tributavel_prod_serv'] = tabela.find('label', text = 'Quantidade Tributável').next_sibling.get_text()
        data_product['vl_unit_comerc_prod_serv'] = tabela.find('label', text = 'Valor unitário de comercialização').next_sibling.get_text()
        data_product['vl_unit_tribut_prod_serv'] = tabela.find('label', text = 'Valor unitário de tributação').next_sibling.get_text()
        data_product['nu_pedido_compra_prod_serv'] = tabela.find('label', text = 'Número do pedido de compra').next_sibling.get_text()
        data_product['item_pedido_prod_serv'] = tabela.find('label', text = 'Item do pedido de compra').next_sibling.get_text()
        data_product['vl_aprox_tributos_prod_serv'] = tabela.find('label', text = 'Valor Aproximado dos Tributos').next_sibling.get_text()
        data_product['nu_fci_prod_serv'] = tabela.find('label', text = 'Número da FCI').next_sibling.get_text()
        data_product['cest_prod_serv'] = tabela.find('label', text = 'CEST').next_sibling.get_text()
        for key in data_product:
            data_product[key] = nfce.ajustar_texto(data_product[key])
            if key[:3] == 'dt_':
                data_product[key] = nfce.converter_data(data_product[key])
            if key[:3] in ('vl_', 'qt_', ):
                data_product[key] = converte_monetario_float(data_product[key])
        data_product.update(invoice_data)
        data_produts.append(data_product)
    return data_produts 
    
        
def get_supplier_data(drive):    
    data_supplier = {}
    page = BeautifulSoup(drive.page_source, 'lxml')    
    data_supplier['cnpj'] = page.find('label',text='CNPJ').next_sibling.get_text()
    data_supplier['razao_social'] = page.find('label',text='Nome / Razão Social').next_sibling.get_text()
    data_supplier['nm_fantasia'] = page.find('label',text='Nome Fantasia').next_sibling.get_text()
    data_supplier['endereco'] = page.find('label',text='Endereço').next_sibling.get_text()
    data_supplier['bairro'] = page.find('label',text='Bairro / Distrito').next_sibling.get_text()
    data_supplier['cep'] = page.find('label',text='CEP').next_sibling.get_text()
    data_supplier['cd_municipio'] = page.find('label',text='Município').next_sibling.get_text()
    data_supplier['cd_municipio_ocorrencia'] = page.find('label',text='Município da Ocorrência do Fato Gerador do ICMS').next_sibling.get_text()
    data_supplier['telefone'] = page.find('label',text='Telefone').next_sibling.get_text()
    data_supplier['sg_uf'] = page.find('label',text='UF').next_sibling.get_text()
    data_supplier['cd_pais'] = page.find('label',text='País').next_sibling.get_text()
    data_supplier['insc_estadual'] = page.find('label',text='Inscrição Estadual').next_sibling.get_text()
    data_supplier['cnae_fiscal'] = page.find('label',text='CNAE Fiscal').next_sibling.get_text()
    data_supplier['ds_regime_tributario'] = page.find('label',text='Código de Regime Tributário').next_sibling.get_text()
    data_supplier['insc_municipal'] = page.find('label',text='Inscrição Municipal').next_sibling.get_text()
    data_supplier['insc_estadual_substituto'] = page.find('label',text='Inscrição Estadual do Substituto Tributário').next_sibling.get_text()
    
    
    for key in data_supplier:
        data_supplier[key] = nfce.ajustar_texto(data_supplier[key])
        if key[:3] == 'dt_':
            data_supplier[key] = nfce.converter_data(data_supplier[key])
        if key[:3] in ('vl_', 'qt_', ):
            data_supplier[key] = converte_monetario_float(data_supplier[key])
        elif key  in ('cnpj', 'cep', 'telefone') :
            data_supplier[key] = retirar_pontuacao(data_supplier[key])        
        elif key  in ('cd_municipio', 'cd_pais') :     #este campos tem a seguinte formatacao 'cogigo-descricao'
            data_supplier[key] = data_supplier[key].split('-')[0].strip()
            if not data_supplier[key]:
                data_supplier[key] = '0'
       
    
    return data_supplier


def get_invoice_data(drive, invoice_key):    
    invoice_data = {}
    page = BeautifulSoup(drive.page_source, 'lxml')
    invoice_data['chave_acesso'] = invoice_key    #inclue nos dados da nota a chave de acesso digitada
    invoice_data['cd_uf'] = invoice_data['chave_acesso'][:2]
    invoice_data['cnpj'] = invoice_key[6:20]
    invoice_data['nu_nfce'] = invoice_key[35:43]
    invoice_data['cd_forma_emissao'] = invoice_data['chave_acesso'][34:35]
    invoice_data['cd_modelo'] = invoice_data['chave_acesso'][20:22]
    #invoice_data['cd_modelo'] = page.find('label',text='Modelo').next_sibling.get_text()
    invoice_data['serie'] = invoice_data['chave_acesso'][22:25]
    #invoice_data['serie'] = page.find('label',text='Série').next_sibling.get_text()
    invoice_data['numero'] = invoice_data['chave_acesso'][25:34]
    #invoice_data['numero'] = page.find('label',text='Número').next_sibling.get_text()
    invoice_data['dt_emissao'] = page.find('label',text='Data de Emissão').next_sibling.get_text()
    invoice_data['vl_total'] = page.find('label',text='Valor Total da Nota Fiscal  ').next_sibling.get_text()
    for key in invoice_data:
        invoice_data[key] = nfce.ajustar_texto(invoice_data[key])
        if key[:3] == 'dt_':
            invoice_data[key] = nfce.converter_data(invoice_data[key])
        if key[:3] in ('vl_', 'qt_', ):
            invoice_data[key] = converte_monetario_float(invoice_data[key])
    return invoice_data

def make_dialog_captcha(path):    
    def close_dialog():
        if entry_capcha.get():
            dialog.captcha_solution = entry_capcha.get()
            dialog.destroy()
        else:
            showwarning('Captcha','Você deve informar o captcha')  
        
    dialog = tk.Toplevel()
    dialog.captcha_solution = ''
    frm1 = tk.Frame(dialog)
    frm1.pack(fill=tk.BOTH, expand=tk.YES)
    tk.Label(frm1,text='Digite o Captcha:').pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
    entry_capcha = tk.Entry(frm1)
    entry_capcha.pack(side=tk.LEFT, fill=tk.X,  expand=tk.YES)
    image = get_image(path)
    tk.Button(dialog, image=image, command=close_dialog).pack(fill=tk.BOTH, expand=tk.YES)
    dialog.image = image
    show_modal_win(dialog)
    return dialog.captcha_solution
    

def make_window(master=None):    
    padx = 3
    pady = 3    
    if master: 
       win = tk.Toplevel(master)
    else:
        win = tk.Tk()
    
    win.title('Download Notas Fiscais')
    frm = tk.Frame(win)
    frm.pack(fill=tk.X)
    #primeira linha do Form - Label e Entry
    frm2 = tk.Frame(frm)
    frm2.grid(row=0, column=0, sticky='w')
    tk.Label(frm2,text='Chave:').pack(side=tk.LEFT,
                                      fill=tk.X)
    win.entry_key_nfce = tk.Entry(frm2, 
                                  width=45)
    win.entry_key_nfce.pack(side=tk.LEFT,
                            fill=tk.X,
                            expand=tk.YES,
                            padx=padx,
                            pady=pady)    
    #botão submit
    win.btSubmit = tk.Button(frm, text='Buscar')    
    win.btSubmit.grid(  row=0,
                        column=1,
                        sticky='e',
                        padx=padx,
                        pady=pady) 
    win.btSubmit.config(command=(lambda:search_button(win)), 
                        state='disabled') 
    #Text para mostrar o log do sistema
    win.text_logger = ScrolledText( frm, 
                                    width=50,
                                    height=30)
    win.text_logger.grid(   row=1,
                            column=0,
                            columnspan=2,
                            padx=padx,
                            pady=pady,
                            sticky='ew')   
    frm.columnconfigure(0, weight=1) 
    #preparando para iniciar o selenium
    win.logger = get_logger('invoice_scrapper')
    win.logger.addHandler(ScrolledTextHandler(win.text_logger))
    win.drive = None
    win.site = sefaz_ba_site
    #win.browser_type = 'phanton'
    win.browser_type = 'firefox'
    win.solved_captcha = False
    #após a janela abrir, dispara o initialize
    win.after(20, (lambda w=win :initialize(w)))    
    
    if not master:
        win.eval('tk::PlaceWindow %s center' % win.winfo_pathname(win.winfo_id()))    
    
    if master: 
        show_modal_win(win)
    else:
        win.mainloop()
    
    win.drive.close()

if __name__ == '__main__':
    main()
