import os, logging
from urllib.parse import urlparse
from urllib.request import Request,  urlopen, urlretrieve
from mimetypes import guess_extension
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def wait_presence_by_id(drive, qt_seconds, id):
    try:
        WebDriverWait(drive, qt_seconds).until(
            EC.presence_of_element_located((By.ID, id)))
        return 0 #ok, achou o elemento
    except TimeoutException:        
        return 1
        
        
def wait_by_id(drive, qt_seconds, id):
    try:
        WebDriverWait(drive, qt_seconds).until(
            EC.visibility_of_element_located((By.ID, id)))
        return 0 #ok, achou o elemento
    except TimeoutException:        
        return 1
        
        
def initialize(win):    
    '''
        Após a janela ser aberta, faz a inicilização do webdrive, vai para o site 
        para o site, após habilita o botão submit da janela
    '''
    win.drive = open_browser(win.logger, win.browser_type)        #abre o browser
    open_site(win.drive, win.site, win.logger)  #vai para a página
    win.btSubmit.config(state='active')         #ativa o botão

def get_logger( name_logger, 
                level=logging.INFO, 
                format='%(asctime)s %(levelname)s %(message)s', 
                datefmt='%m/%d/%Y %I:%M:%S %p'):
    
    logging.basicConfig(
                    format=format, 
                    level=level, 
                    datefmt=datefmt
                    )
    logger = logging.getLogger(name_logger)
    return logger
    
def open_browser(logger, browser_type='phanton'):    
    '''
        Open o webDrive
        parâmetros:
        text_log:ScrolledText: Text onde as mensagens de log vão ser impressas
        
        return: o objeto webDrive aberto
    '''    
    caps = DesiredCapabilities.PHANTOMJS    
    fake_browser = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0'    
    caps["phantomjs.page.settings.userAgent"] = fake_browser
    logger.info('abrindo browser... ')    
    if browser_type == 'phanton':
        logger.info('phanton')
        drive = webdriver.PhantomJS(desired_capabilities= caps)
        #drive = webdriver.PhantomJS()    
    elif browser_type == 'firefox':
        logger.info('firefox')
        drive = webdriver.Firefox()    
    else:
        raise Exception("Browser Inválido")
    logger.info('Ok')  
    
    return drive


def open_site(drive, site, logger):    
    '''
        Abre o site de pesquisa
        parâmetros:
        (drive:webDrive) Objeto WebDrive - para controlar o browser
        (site:string) site que vai ser aberto para pesquisa
        (logger:logging.Logger) logger para realizar o log.
        
        return: sem retorno
    '''    
    logger.info('Abrindo site {}...'.format(site))
    drive.get(site)    
    logger.info('Ok')
    
def make_image_file(uri, filename, main_url=''):
    '''
        Obtem da URI o arquivo de imagem e salva-o
        parâmetros:
        (uri:string) URI do arquivo
        (filename:string) nome do arquivo a ser salvo
        
        return: nome do arquivo salvo
    '''
    if not uri:
        return ''
    verifica_path()
    filename = 'data/products/' + filename    
    if uri.split(':', 1)[0] == 'data':        
        filename, m = urlretrieve(uri, filename)        
        extension = guess_extension(m.get_content_type())        
        os.rename(filename, filename + extension)        
        return (filename + extension)        
    else:
        parsed_uri = urlparse(uri)
        if parsed_uri.scheme:
            resource = get_resource(uri)
        else:
            url = urlparse(main_url)._replace(path=parsed_uri.path)
            resource = get_resource(url.geturl())
            
        if resource:
            with open(filename, 'wb') as file:
                file.write(resource.read())
                return filename
        else:
            return ''


def verifica_path():
    '''
        Verifica a existencia das pastas onde vão ser guardadas as imagens e logs da aplicação
    '''
    if os.path.exists('data'):        
        if not os.path.exists('data/products'):            
            os.mkdir('data/products')
    else:        
        os.mkdir('data')
        os.mkdir('data/products') 
        
def get_resource(uri):
    '''
        Obtem o arquivo apontado pela URI passada
        parâmetros:
        (uri:string) URI do recurso a ser baixado
        
        return: retorna o arquivo
    '''
    fake_browser = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0'    
    
    request = Request(uri, headers={'User-Agent':fake_browser})    
    resource = urlopen(request)
    
    return resource    

def main():
    open_browser()


    
    
