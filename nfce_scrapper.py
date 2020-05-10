from selenium import webdriver
def open_browser(logger):    
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
    drive = webdriver.PhantomJS()    
    #drive = webdriver.Firefox()    
    logger.info('Ok')  
    
    return drive
