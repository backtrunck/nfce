#sites para verificar o header http://www.rexswain.com
#testei este: 'https://www.whatismybrowser.com' pelo phantomjs
#o firefox está com o seguinte header/ User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0 
import os,  re, csv, io, logging, datetime
import tkinter as tk
import nfce_db
from nfce_models import products_gtin_products_t
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import  TimeoutException,\
                                        NoSuchElementException
from nfce_scrapper import   open_browser, \
                            open_site, \
                            make_image_file, \
                            verifica_path, \
                            initialize
from bs4 import BeautifulSoup
from tkinter.messagebox import showwarning
from util import check_gtin, retirar_pontuacao
from interfaces_graficas import ScrolledText,\
                                ScrolledTextHandler,\
                                get_image,\
                                show_modal_win
from PIL import Image, ImageTk

blank_image = 'data/products/blank.png'
csv_products_file = "data/products/products.csv"
bluesoft_site = 'https://cosmos.bluesoft.com.br'

def get_db_products_images():
    '''
        Pega os produtos da Base de dados e procura-os na net, baixando 
        as imagens e descrições(guardadas no csv
    '''
    engine = nfce_db.get_engine_bd()    
    db_connection = engine.connect()    
    logging.basicConfig(
                    format='%(asctime)s %(levelname)s %(message)s', 
                    level=logging.INFO, 
                    datefmt='%m/%d/%Y %H:%M:%S'
                    )

    logger = logging.getLogger('new_products')
    verifica_path()
    dt_hr= datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    fh = logging.FileHandler(
            'data/products/db_products.{}.log'.format(dt_hr), 
             mode='w')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s', 
                                    datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)    
    logger.addHandler(fh)   
    drive = open_browser(logger)
    open_site(drive, bluesoft_site, logger)
    #cd_ean_prod_serv = \'7891000094792\' and 
    #result = db_connection.execute('select * from produtos_servicos_ean where insercao_manual = 0')
    result = db_connection.execute('''select cd_ean_prod_serv,ds_prod_serv,cd_ean_produto from produtos_servicos ps
        left join produtos_gtim p 
        on ps.cd_ean_prod_serv = p.cd_ean_produto
        where cd_ean_prod_serv != 'SEM GTIN' 
        order by cd_ean_produto''')
    products = result.fetchall() 
    for product in products:
        logger.info('Procurando Produto {} - {}...'.format(product['cd_ean_prod_serv'], 
                                                           product['ds_prod_serv'])) 
        if check_gtin(product['cd_ean_prod_serv']):
            get_product_from_net(drive, product['cd_ean_prod_serv'], logger)
        else:
            logger.info('Código Ean Inválido')

    
def get_others_product_from_html(html):
    products = []
    html_soup = BeautifulSoup(html,'lxml')
    span = html_soup.find('span',{'class':'translation_missing'})
    if span:
        tbody = span.parent.parent.parent
        if tbody.name == 'tbody':            
            for tr in tbody.findAll('tr'):
                product = {}
                for i,td in enumerate(tr.findAll('td')):
                    if i == 0:
                        product['cd_ean_produto'] = td.get_text().strip()
                    elif i == 1:
                        product['embalagem'] = td.get_text().strip()
                    elif i == 2:
                        product['qt_item_embalagem'] = td.get_text().strip()
                    else:
                        break
                products.append(product)
    return products


def update_other_product_db(main_product, other_products, conn):
    if other_products:
        for other_product in other_products:
            if len(other_product['cd_ean_produto']) == 14: 
                other_product['cd_ean_produto'] = other_product['cd_ean_produto'][1:]
            if len(other_product['cd_ean_produto']) == 13: #somente GTIN-13
                if other_product['cd_ean_produto'] != main_product['cd_ean_produto']:
                    other_product['ds_produto'] = main_product['ds_produto']
                    other_product['cd_ncm_produto'] = main_product['cd_ncm_produto']
                    other_product['ds_ncm_produto'] = main_product['ds_ncm_produto']
                    other_product['cadastrado'] = main_product['cadastrado']
                    other_product['img_produto'] = main_product['img_produto']
                    other_product['img_barcode'] = main_product['img_barcode']
                    other_product['cd_ean_interno'] = main_product['cd_ean_produto']
                    if not get_product_from_db(conn, other_product['cd_ean_produto']): #se não achar o produto na base                    
                        insert_product_db(conn, other_product)
                    else:                    
                        update_product_db(conn, other_product)


def get_product_from_net(drive, product_code, logger):
    
    html_result = search_product(drive, product_code, logger)   #executa o pesquisar da página        
    if html_result:
        product_data = get_data_from_html(drive, product_code) #pega os dados no html de retorno        
        if product_data: #trouxe resultado?     
            logger.info('Grava Produto {} no csv'.format(product_code))
            with open(csv_products_file, 'a') as file:
                csvWriter = csv.writer(file, quoting = csv.QUOTE_ALL, delimiter = ';')
                csvWriter.writerow([product_data['cd_ean_produto'], 
                                    product_data['ds_produto'],
                                    product_data['cd_ncm_produto'],
                                    product_data['ds_ncm_produto'],
                                    product_data['cadastrado']])
            #grava imagem do produto
            try:
                make_image_file(product_data['product_img_uri'],
                    product_data['cd_ean_produto'] + '.image', main_url=bluesoft_site) 
                logger.info('Gravou Imagem Produto "{}"'.format(product_data['product_img_uri']))
            except Exception as e:
                logger.error('"{}" gravando imagem do prod. {} - de "{}"'.format(
                         e, product_data['cd_ean_produto'], product_data['product_img_uri']))
            #grava código de barras
            try:
                make_image_file(product_data['barcode_uri'],
                    product_data['cd_ean_produto'] + '.barcode', main_url=bluesoft_site)
                logger.info('Gravou código barras Produto "{}"'.format(product_data['cd_ean_produto']))
            except Exception as e:
                logger.error('Erro "{}" ao gravar cd de barras do produto {}'.format(
                         e, product_data['cd_ean_produto']))
        else:
            logger.info('Produto Não Encontrado')
    else:
        logger.info('Produto Não Encontrado')


def change_image(widget, path):
    '''
        Troca ou mesmo atribui uma imagem de um arquivo a um widget
        parâmetros. Caso seja passado um path vazio, atribui uma imagem em branco
        (widget:object): Objeto tkinter que vai receber a imagem
        (path:string): Caminho do arquivo de imagem
        
        return: no return
    '''
    if path:
        widget.image = get_image(path)
    else:
        widget.image = get_image(blank_image)    
        
    widget.configure(image= widget.image )
    
def search_button(win):
    try:
        product_code = win.entCodeProduct.get()
        
        title = 'Importação de Produto'
        
        if product_code:
            if check_gtin(product_code):                
                #limpa os controles
                win.text_logger.erase()
                win.bt1.image = get_image(blank_image)
                win.bt1.configure(image= win.bt1.image )
                win.bt2.image = get_image(blank_image)
                win.bt2.configure(image= win.bt2.image )
                win.entry_produto.delete(0, 'end')                
                product_included = get_product_from_csv(product_code) #produto no csv?                
                html_source = search_product(win.drive, product_code, win.logger)   #executa o pesquisar da página 
                if not is_found_product(html_source):
                    showwarning(title,'Produto {} não encontrado'.format(product_code))
                    return
                try:
                    win.logger.info('Aguardando o download completo da página')
                    WebDriverWait(win.drive, 120).until(
                        EC.visibility_of_element_located((By.ID, 'barcode'))) #verifica se a imagem do barcode foi baixada
                except TimeoutException:        
                    win.logger.warning('tempo excessivo para o download completo da página')
                    return
                win.logger.info('Download finalizado!')
                product_data = get_data_from_html(win.drive, product_code) #pega os dados no html de retorno                    
                if product_data: #trouxe resultado?                        
                    win.entry_produto.insert(0, product_data['ds_produto'])  #coloca a descrição do produto na tela
                    if not product_included:    #se não estiver no csv, inclui
                        win.logger.info('Incluindo no CSV... ')                        
                        with open(csv_products_file, 'a') as file:            
                            csvWriter = csv.writer(file, quoting = csv.QUOTE_ALL, delimiter = ';')
                            csvWriter.writerow([product_data['cd_ean_produto'], 
                                                product_data['ds_produto'],
                                                product_data['cd_ncm_produto'],
                                                product_data['ds_ncm_produto'],
                                                product_data['cadastrado']])                        
                        win.logger.info('ok')   
                    
                    try:
                        file_image = make_image_file(product_data['product_img_uri'],
                                    product_data['cd_ean_produto'] + '.image', main_url=bluesoft_site)
                        change_image(win.bt1, file_image)  
                        product_img = get_image_file(filename = file_image)
                        product_data['img_produto'] = product_img
                        win.logger.info('Gravou Imagem Produto "{}" em "{}"'.format(product_data['product_img_uri'], file_image))
                    except Exception as e:
                        win.logger.error('"{}" gravando imagem do prod. {} - de "{}"'.format(
                                e, product_data['cd_ean_produto'], product_data['product_img_uri']))  
                    try:
                        barcode_image = make_image_file(product_data['barcode_uri'],
                                        product_data['cd_ean_produto'] + '.barcode', main_url=bluesoft_site)                        
                        change_image(win.bt2, barcode_image)
                        product_barcode_img = get_image_file(filename = barcode_image)
                        product_data['img_barcode'] = product_barcode_img        
                        win.logger.info('Gravou código barras Produto "{}" em "{}"'.format(product_data['cd_ean_produto'], barcode_image))
                    except Exception as e:
                            win.logger.error('Erro "{}" ao gravar cd de barras do produto {}'.format(
                                     e, product_data['cd_ean_produto']))
                    db_connection = nfce_db.get_engine_bd().connect()    
                    if not get_product_from_db(db_connection, product_data['cd_ean_produto']): #se não achar o produto na base
                        insert_product_db(db_connection, product_data)
                    else:
                        update_product_db(db_connection, product_data)
                    other_products_data = get_others_product_from_html(win.drive.page_source)
                    update_other_product_db(product_data, other_products_data, db_connection)
                    win.logger.info('Finalizado')   
                else:
                    showwarning(title,'Produto {} não encontrado'.format(product_code))
            else:                
                showwarning(title,'Código GTIM inválido: {}'.format(product_code))    
        else:
            showwarning(title,'Informe o Código EAN do Produto')
        
    except Exception as e:
        win.logger.info('Erro -> {}'.format(e))
    finally:
        win.entCodeProduct.focus_set()


def make_window(master=None):
    '''
        Cria a janela principal, onde se vai importar os produtos.
    '''    
    padx = 3
    pady = 3    
    if master: 
       win = tk.Toplevel(master)
    else:
        win = tk.Tk()
    
    win.title('Importar Dados do Produto')
    frm = tk.Frame(win)
    frm.pack(fill=tk.X)
    #primeira linha do Form - Label e Entry
    frm2 = tk.Frame(frm)
    frm2.grid(row=0, column=0, sticky='w')
    tk.Label(frm2,text='Código EAN:').pack(side=tk.LEFT,fill=tk.X)
    win.entCodeProduct = tk.Entry(frm2)
    win.entCodeProduct.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=padx,  pady=pady)    
    #botão submit
    win.btSubmit = tk.Button(frm, text='Buscar')    
    win.btSubmit.grid(row=0, column=1, sticky='e', padx=padx, pady=pady)
    win.btSubmit.config(state='disabled')    
    #Text para mostrar o log do sistema
    win.text_logger = ScrolledText(frm, width=50, height=10)
    win.text_logger.grid(row=1, column=0, columnspan=2, padx=padx, pady=pady)    
    win.entry_produto = tk.Entry(frm)
    win.entry_produto.grid(row=2, column=0, columnspan=2, sticky='ew', padx=padx, pady=pady)    
    frmImg = tk.Frame(frm)
    frmImg.grid(row=3, column=0, columnspan=2, sticky='ew')
    frmImg.columnconfigure(0, weight=1)
    frmImg.columnconfigure(1, weight=1)
    photo = get_image('data/products/blank.png')    
    width = 200
    height = 200    
    win.bt1 = tk.Button(frmImg, image=photo, width = width,  height = height)
    win.bt1.image = photo
    win.bt1.grid(row=0, column=0, sticky='ew', padx=padx, pady=pady)    
    win.bt2 = tk.Button(frmImg, image=photo)
    win.bt2.image = photo
    win.bt2.grid(row=0, column=1, sticky='ew', padx=padx, pady=pady)    
    win.btSubmit.config(command=(lambda:search_button(win)))    
    win.entCodeProduct.focus_set()
    if not master:
        win.eval('tk::PlaceWindow %s center' % win.winfo_pathname(win.winfo_id()))    
    win.logger = make_logger( win.text_logger)    
    win.site = bluesoft_site
    win.drive = None
    win.browser_type = 'phanton'
    win.browser_type = 'firefox'
    win.after(20, (lambda w=win :initialize(w)))
    if master: 
       show_modal_win(win)
    else:
        win.mainloop()
    win.drive.close()


def make_logger(scrolled_text):    
        
        logging.basicConfig(
                    format='%(asctime)s %(levelname)s %(message)s', 
                    level=logging.INFO, 
                    datefmt='%m/%d/%Y %I:%M:%S %p'
                    )

        logger = logging.getLogger('logger')
        
        st = ScrolledTextHandler(scrolled_text)
        st.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        st.setFormatter(formatter)
        logger.addHandler(st)
        
        return logger    
    

def is_found_product(html_source):
    if html_source:
        html_soup = BeautifulSoup(html_source,'lxml') 
        if 'c_products' in html_soup.body['class']:
            return True
    return False


def get_data_from_html(driver, product_code):
    DESC_NAO_ENCONTRADA = 'descrição não encontrada'
    html = driver.page_source
    product_data = {}    
    html_soup = BeautifulSoup(html,'lxml') 
    if not html_soup.body['class'] == 'c_products': #caso seja encontrado.
        span = html_soup.find('span', {'id':'product_description'})
        if span:
            desc_product = span.get_text().strip()
        else:
           desc_product = DESC_NAO_ENCONTRADA
        
        span = html_soup.find('span', {'id':'product_gtin'})
        if span:
            if product_code.strip() != span.get_text().strip():
                product_code = span.get_text().strip()
        
        #product_img_tag = html_soup.find('img', {'title':re.compile('^' + product_code)})        
        #if product_img_tag:            
        #    data_text = product_img_tag.get('alt').split('-', 1)
        #    desc_product = data_text[1].strip()
        #else:
          
        ncm_tag = html_soup.find('span', {'class':'description ncm-name label-figura-fiscal'})        
        if ncm_tag.a:            
            data_text = ncm_tag.a.text.strip()
            code_ncm , desc_ncm = data_text.split('-', 1)            
        else:
            #codigos ncm não encontrados
            code_ncm = '00000000'
            desc_ncm = 'sem codigo ncm'
        #barcode_tag = html_soup.find('img',{'id':'barcode'})
        try:
            #usando BeutifulSoup o 'src' da tag 'img', ora aparecia ora não, usando Selenium
            barcode_tag = driver.find_element_by_id('barcode') 
        except NoSuchElementException:
            barcode_tag = None
            barcode_uri = None
        else:
            barcode_uri = barcode_tag.get_attribute('src')
               
        product_img_tag = html_soup.find('img', {'title':re.compile('^' + product_code)})        
        if product_img_tag:            
            product_img_uri = product_img_tag['src']        
        else:
            #não encontrou a imagem pelo código. Alguns produtos estão com códigos errados na imagem
            if desc_product != DESC_NAO_ENCONTRADA:
                product_img_tag = html_soup.find('img', {'title':re.compile(desc_product + '$')}) 
                if product_img_tag:            
                    product_img_uri = product_img_tag['src']
                
        if not product_img_tag:
            product_img_uri = None
            
        #preenche os dados capturados do produto na pagina html
        product_data['cd_ean_produto'] = product_code
        product_data['cd_ean_interno'] = product_code
        product_data['qt_item_embalagem'] = 1
        product_data['ds_produto'] = desc_product
        product_data['cd_ncm_produto'] = retirar_pontuacao(code_ncm.strip())
        product_data['ds_ncm_produto'] = desc_ncm.strip()
        product_data['barcode_uri'] = barcode_uri 
        product_data['product_img_uri'] = product_img_uri
        product_data['cadastrado'] = 1
    
    return product_data
    
    
def fill_product_csv_file(html_soup, product_code, file_name):
    '''
        inclui no arquivo csv os dados doproduto encontrado no site
        parâmetros:
        (html_soup:objeto) Objet BeautifulSoup com os dados da pagina html
        (product_code:string) Código do produto
        (file_name:string) Nome do arquivo csv, onde os dados vão ser gravados    '''
    
    product_img_tag = html_soup.find('img', {'title':re.compile('^' + product_code)})    
    if product_img_tag:        
        data_text = product_img_tag.get('alt').split('-')
        desc_product = data_text[1].strip()
    ncm_tag = html_soup.find('span', {'class':'description ncm-name label-figura-fiscal'})    
    if ncm_tag.a:        
        data_text = ncm_tag.a.text
        code_ncm , desc_ncm = data_text.split('-', 1)        
    else:
        #codigos ncm não encontrados
        code_ncm = '0000.00.00'
        desc_ncm = 'sem codigo ncm'    
    with open(file_name, 'a') as file:        
        csvWriter = csv.writer(file, quoting = csv.QUOTE_ALL, delimiter = ';')
        csvWriter.writerow([product_code, desc_product, code_ncm.strip(), desc_ncm.strip(), 1])
        
    return (1, desc_product, code_ncm.strip(), desc_ncm.strip(),code_ncm, desc_ncm)
    
    
def get_product_from_csv(product_code):
    '''
        Obtem dados de um produto, gravados no arquivo csv
        parâmetros:
        (product_code:string) Código do produto
        
        return: uma lista com os dados do produto, caso encontre ou None    '''
    
    result = None    
    if os.path.exists(csv_products_file):        
        with  open(csv_products_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')            
            for row in reader:          
                if row and row[0] == product_code:                    
                    result = row
                    break

    return result
    
    
def get_product_from_db(db_connection, product_code, load_images=False):    
    if load_images:
        sql = 'select cd_ean_produto, ds_produto, cd_ncm_produto, img_produto, img_barcode from produtos_gtin where cd_ean_produto = %s'
    else:
        sql = 'select cd_ean_produto, ds_produto, cd_ncm_produto from produtos_gtin where cd_ean_produto = %s'
        
    return db_connection.execute(sql, product_code).fetchone()
    

def data_base_update():    
    '''
        Atualiza o banco de dados. Coleta os dados no arquivo csv e envia-os para o banco de dados 
        junto com as imagens dos produtos
    '''    
    engine = nfce_db.get_engine_bd()    
    db_connection = engine.connect()    
    if os.path.exists(csv_products_file):        
        dict_values_product = {}        
        with  open(csv_products_file, 'r') as file:     #abre o arquivo csv            
            reader = csv.reader(file, delimiter=';')    #cria o objeto csv            
            for row in reader:      #loop nas linhas do csv                
                if row:
                    #põe os dados do produto no dicionario dict_values_product
                    dict_values_product['cd_ean_produto'] = row[0]
                    dict_values_product['cd_ean_interno'] = row[0]
                    dict_values_product['qt_item_embalagem'] = 1
                    dict_values_product['ds_produto'] = row[1]
                    dict_values_product['cd_ncm_produto'] = retirar_pontuacao(row[2])                    
                    product_img = get_image_file(filename = row[0] + '.image')
                    product_barcode_img = get_image_file(filename = row[0] + '.barcode.png')                    
                    dict_values_product['img_produto'] = product_img
                    dict_values_product['img_barcode'] = product_barcode_img
                    dict_values_product['cadastrado'] = row[4]
                    if not get_product_from_db(db_connection, row[0]): #se não achar o produto na base
                        #insere no banco de dados
                        insert_product_db(db_connection, dict_values_product)
                    else:
                        update_product_db(db_connection, dict_values_product)

    
def get_image_file(filename) :  
    if filename:  
        file_base_name =  os.path.basename(filename)
        file_path = 'data/products/' + file_base_name
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    return f.read()
            
            except Exception as e:
                print(e)
            
    return None
    
    
def search_product(drive, product_code, logger):    
    search_box =  drive.find_element_by_id('search-input')
    search_box.clear()
    search_box.send_keys(product_code)
    logger.info('baixando resultado da pesquisa')
    search_box.submit()
    try:
        WebDriverWait(drive, 60).until(
            EC.presence_of_element_located((By.XPATH, "//*[@class='c_products a_show' or @class='c_search a_find']")))
            #EC.presence_of_element_located((By.CLASS_NAME, 'c_products'))) 
            #driver.find_elements_by_xpath("//*[@class='XELVh selectable-text invisible-space copyable-text']")
            
            #EC.title_contains(product_code[:12])) #verifica codigo sem digito verificador no titulo
    except TimeoutException:        
        logger.warning('time-out na pesquisa do produto')
        return ''
    logger.info('pesquisa realizada')
    
    return  drive.page_source
    
def insert_product_db(db_connection, data_product, dict_types_field={}):
    
    transaction = db_connection.begin()
    try:
        sql =   '''insert into produtos_gtin(cd_ean_produto, 
                                        ds_produto,
                                        cd_ncm_produto,
                                        img_produto,
                                        img_barcode,
                                        cadastrado,
                                        cd_ean_interno,
                                        qt_item_embalagem)
                            values( :cd_ean_produto,
                                    :ds_produto,
                                    :cd_ncm_produto,
                                    :img_produto,
                                    :img_barcode,
                                    :cadastrado,
                                    :cd_ean_interno,
                                    :qt_item_embalagem)
                '''
                                        
        nfce_db.execute_sql(db_connection, sql, data_product, dict_types_field)
        ins = products_gtin_products_t.insert().values(cd_ean_produto=data_product['cd_ean_produto'], 
                                                                        id_produto = nfce_db.PRODUCT_NO_CLASSIFIED, 
                                                                        manual = 1)
        db_connection.execute(ins)
        transaction.commit()
    except Exception as e:
        transaction.rollback()
        showwarning('Inserir Produto',\
            f'Produto {data_product["cd_ean_produto"]} - {data_product["ds_produto"]}, Erro - {e}')

def update_product_db(db_connection, data_product, dict_types_field={}):    
    sql =   '''update produtos_gtin 
                    set
                        cd_ncm_produto  = :cd_ncm_produto,
                        img_produto     = :img_produto,
                        img_barcode     = :img_barcode,
                        cadastrado      = :cadastrado,
                        cd_ean_interno  = :cd_ean_interno,
                        qt_item_embalagem = :qt_item_embalagem
                    where
                        cd_ean_produto  = :cd_ean_produto
            '''                        
    #ds_produto      = :ds_produto,
    nfce_db.execute_sql(db_connection, sql, data_product, dict_types_field)


def products_images_search(master=None):    
    '''
        Abre janela para procurar e mostrar as imagens salvas no bd
    '''
    def submit():
        ean_code = entry_ean.get()
        if ean_code:
            result = get_product_from_db(db_connection, ean_code, True)
            if result:
                if result['img_produto']:
                    img = Image.open(io.BytesIO(result['img_produto']))
                    img = img.resize((200, 200), Image.ANTIALIAS)
                    win.bt1.image = ImageTk.PhotoImage(img)    
                    win.bt1.config(image = win.bt1.image)    
                else:
                    change_image(win.bt1, '')
                
                if result['img_barcode']:
                    img = Image.open(io.BytesIO(result['img_barcode']))
                    img = img.resize((200, 200), Image.ANTIALIAS)
                    win.bt2.image = ImageTk.PhotoImage(img)    
                    win.bt2.config(image = win.bt2.image)
                    label_product.config(text=result['ds_produto'])
                else:
                    change_image(win.bt2, '')
                    
            else:
                showwarning('Teste Imagens','Cógigo não encontrado')
                change_image(win.bt1, '')
                change_image(win.bt2, '')
                label_product.config(text='')
        else:
            showwarning('Teste Imagens','Informe o Código')

    padx = 3
    pady = 3
    engine = nfce_db.get_engine_bd()    
    db_connection = engine.connect()    
    if master: 
       win = tk.Toplevel(master)       
    else:
        win = tk.Tk()
    
    win.title('Teste Imagens / Blob Mysql')    
    frm = tk.Frame(win)
    frm.pack(fill=tk.X, expand=tk.YES)
    
    tk.Label(frm, text="Digite Ean:").pack(side=tk.LEFT)
    entry_ean = tk.Entry(frm)
    entry_ean.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
    
    frm = tk.Frame(win)
    frm.pack(fill=tk.X)  
    label_product = tk.Label(frm, width=40, anchor="w", justify=tk.LEFT)
    label_product.pack(side=tk.LEFT)
    button_submit = tk.Button(frm, text='Search', command=submit)
    button_submit.pack(side=tk.RIGHT)
    
    frm = tk.Frame(win)
    frm.pack(fill=tk.X)    
    
    win.bt1 = tk.Button(frm)
    win.bt1.image = None      
    change_image(win.bt1, '')
    
    win.bt1.grid(row=2, column=0, sticky='ew', padx=padx, pady=pady)    

    win.bt2 = tk.Button(frm)
    win.bt2.image = None
    change_image(win.bt2, '')
    win.bt2.grid(row=2, column=1, sticky='ew', padx=padx, pady=pady)  
    
    if master:
        show_modal_win(win)
    else:
        win.eval('tk::PlaceWindow %s center' % win.winfo_pathname(win.winfo_id()))    
        win.mainloop()
   
    
def main():
#    get_db_products_images()
#    return
#    products_images_search()
#    return
#  result = data_base_update()
#    return
    make_window()
    

if __name__ == '__main__':
    main()
