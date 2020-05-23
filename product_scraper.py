#sites para verificar o header http://www.rexswain.com
#testei este: 'https://www.whatismybrowser.com' pelo phantomjs
#o firefox está com o seguinte header/ User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0 
import os,  re, csv, io, logging, random, time, datetime
import tkinter as tk
import nfce_db
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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
                                get_image
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

    
def get_product_from_net(drive, product_code, logger):
    
    wait_time = random.uniform(1, 7) #pega um numero aleatório de segundos
    html_result = search_product(drive, product_code, logger, wait_time=wait_time)   #executa o pesquisar da página        
    if html_result:
        product_data = get_data_from_html(drive.page_source, product_code) #pega os dados no html de retorno        
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
                if not product_included:    #se não estiver
                    search_product(win.drive, product_code, win.logger)   #executa o pesquisar da página    
                    product_data = get_data_from_html(win.drive.page_source, product_code) #pega os dados no html de retorno                    
                    if product_data: #trouxe resultado?                        
                        win.entry_produto.insert(0, product_data['ds_produto'])  #coloca a descrição do produto na tela
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
                            filename = make_image_file(product_data['product_img_uri'],
                                        product_data['cd_ean_produto'] + '.image', main_url=bluesoft_site)
                            change_image(win.bt1, filename)   
                        
                            win.logger.info('Gravou Imagem Produto "{}"'.format(product_data['product_img_uri']))
                        except Exception as e:
                            win.logger.error('"{}" gravando imagem do prod. {} - de "{}"'.format(
                                    e, product_data['cd_ean_produto'], product_data['product_img_uri']))  
                        try:
                            filename = make_image_file(product_data['barcode_uri'],
                                            product_data['cd_ean_produto'] + '.barcode', main_url=bluesoft_site)                        
                            change_image(win.bt2, filename)                         
                            win.logger.info('Gravou código barras Produto "{}"'.format(product_data['cd_ean_produto']))
                        except Exception as e:
                                win.logger.error('Erro "{}" ao gravar cd de barras do produto {}'.format(
                                         e, product_data['cd_ean_produto']))
                        win.logger.info('Finalizado')   
                    else:
                        showwarning(title,'Produto {} não encontrado'.format(product_code))
                else:                    
                    showwarning(title,'{} - Produto {}, já foi importado'.format(product_included[0], product_included[1]))
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
    win.after(20, (lambda w=win :initialize(w)))    
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
        
    
    

def get_data_from_html(html, product_code):
    
    product_data = {}    
    html_soup = BeautifulSoup(html,'lxml')    
    #verifica se o codigo foi encontrado
    search_result_1 = html_soup.title.text.startswith(product_code) #titulo da pg começa com o codigo   
    serach_result_2 = product_code[:12] not in html_soup.title.text #titulo não contém o codigo sem digito
    if not (search_result_1 or serach_result_2): #caso seja encontrado.
        product_img_tag = html_soup.find('img', {'title':re.compile('^' + product_code)})        
        if product_img_tag:            
            data_text = product_img_tag.get('alt').split('-')
            desc_product = data_text[1].strip()
        ncm_tag = html_soup.find('span', {'class':'description ncm-name label-figura-fiscal'})        
        if ncm_tag.a:            
            data_text = ncm_tag.a.text.strip()
            code_ncm , desc_ncm = data_text.split('-', 1)            
        else:
            #codigos ncm não encontrados
            code_ncm = '0000.00.00'
            desc_ncm = 'sem codigo ncm'
        barcode_tag = html_soup.find('img',{'id':'barcode'})        
        if barcode_tag:            
            barcode_uri = barcode_tag['src']        
        product_img_tag = html_soup.find('img', {'title':re.compile('^' + product_code)})        
        if product_img_tag:            
            product_img_uri = product_img_tag['src']        
        #preenche os dados capturados do produto na pagina html
        product_data['cd_ean_produto'] = product_code
        product_data['ds_produto'] = desc_product
        product_data['cd_ncm_produto'] = code_ncm.strip()
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
        with  open(csv_products_file, 'r') as file:            
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
    file_path = 'data/products/' + filename
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        
        except Exception as e:
            print(e)
            
    return None
    
    
def search_product(drive, product_code, logger, wait_time=0):    
    search_box =  drive.find_element_by_id('search-input')
    search_box.clear()
    search_box.send_keys(product_code)
    if wait_time:#espera um tempo antes de submeter o form
        logger.info('Waiting {} seconds'.format(wait_time))
        time.sleep(wait_time)
    logger.info('baixando resultado da pesquisa')
    search_box.submit()
    try:
        WebDriverWait(drive, 10).until(
            EC.title_contains(product_code[:12])) #verifica codigo sem digito verificador no titulo
    except TimeoutException:        
        logger.warning('time-out na pesquisa do produto')
        return ''
    logger.info('pesquisa realizada')
    
    return  drive.page_source
    
def insert_product_db(db_connection, data_product, dict_types_field={}):
    
    sql =   '''insert into produtos_gtin(cd_ean_produto, 
                                    ds_produto,
                                    cd_ncm_produto,
                                    img_produto,
                                    img_barcode,
                                    cadastrado)
                        values( :cd_ean_produto,
                                :ds_produto,
                                :cd_ncm_produto,
                                :img_produto,
                                :img_barcode,
                                :cadastrado)
            '''
                                    
    nfce_db.execute_sql(db_connection, sql, data_product, dict_types_field)


def update_product_db(db_connection, data_product, dict_types_field={}):    
    sql =   '''update produtos_gtin 
                    set
                        ds_produto      = :ds_produto,
                        cd_ncm_produto  = :cd_ncm_produto,
                        img_produto     = :img_produto,
                        img_barcode     = :img_barcode,
                        cadastrado      = :cadastrado
                    where
                        cd_ean_produto  = :cd_ean_produto
            '''                        
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
    
#    img = Image.open(io.BytesIO(result['img_produto']))
#    img = img.resize((200, 200), Image.ANTIALIAS)
#    photo_product = ImageTk.PhotoImage(img)    
#    img = Image.open(io.BytesIO(result['img_barcode']))
#    img = img.resize((200, 200), Image.ANTIALIAS)
#    photo_barcode = ImageTk.PhotoImage(img)    
    
    #win.bt1 = tk.Button(frm, image=photo_product)
    
    win.bt1 = tk.Button(frm)
    win.bt1.image = None      
    change_image(win.bt1, '')
    
    win.bt1.grid(row=2, column=0, sticky='ew', padx=padx, pady=pady)    
    
    #win.bt2 = tk.Button(frm, image=photo_barcode)
    win.bt2 = tk.Button(frm)
    win.bt2.image = None
    change_image(win.bt2, '')
    #win.bt2.image = photo_barcode
    win.bt2.grid(row=2, column=1, sticky='ew', padx=padx, pady=pady)  
    
    win.eval('tk::PlaceWindow %s center' % win.winfo_pathname(win.winfo_id()))    
    win.mainloop()
   
    
def main():
#    get_db_products_images()
#    return
#    products_images_search()
#    return
#    result = data_base_update()
#    return
    make_window()
    

if __name__ == '__main__':
    main()
