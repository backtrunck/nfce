import util
import datetime, os, csv
from tkinter import *
from tkinter.filedialog import askopenfilename,  askdirectory
from tkinter import messagebox
from nfce import NfceBd,  NfceParse, NfceArquivoInvalido
def send_invoice_to_csv_file(invoice, csv_file = '', print_header = True):
        
    #obtem dados da nota fiscal    
    dados_emitente = invoice.obter_dados_emitente_2()
    chave_acesso = invoice.obter_chave_acesso() 
    dados_nfce = invoice.obter_dados_nfe_codigo_acesso(chave_acesso)
    produtos_servicos = invoice.obter_dados_produtos_e_servicos()
    #cria arquivo csv 
    
    writer = csv.writer(csv_file, delimiter = ';',  quotechar = '"', quoting = csv.QUOTE_ALL)
   
    if print_header:
        writer.writerow([       'núm nota fiscal elet.', 
                                'Data de Emissão', 
                                'código uf', 'cnpj', 
                                'serie da nota', 
                                'número nota fiscal', 
                                'razão social',
                                'número produto', 
                                'produto', 
                                'quantidade', 
                                'unidade', 
                                'valor', 
                                'vl_desconto_prod_serv', 
                                'Código ncm', 
                                'Código ean'])
                                
    for produto_servico in produtos_servicos:
        
        writer.writerow([   dados_nfce['nu_nfce'], \
                            dados_nfce['dt_emissao'],  \
                            dados_nfce['cd_uf'],    \
                            dados_nfce['cnpj'],     \
                            dados_nfce['serie'],    \
                            dados_nfce['numero'],   \
                            dados_emitente['razao_social'], \
                            produto_servico['nu_prod_serv'],\
                            produto_servico['ds_prod_serv'], \
                            produto_servico['qt_prod_serv'], \
                            produto_servico['un_comercial_prod_serv'], \
                            produto_servico['vl_prod_serv'], \
                            produto_servico['vl_desconto_prod_serv'],\
                            produto_servico['cd_ncm_prod_serv'],\
                            produto_servico['cd_ean_prod_serv']]) 
       
def send_invoice_to_database(nt_fiscal):
    
    ntB = NfceBd(nt_fiscal)
    try:
        ntB.inserir_emitente()
        ntB.inserir_nfce()  
        ntB.inserir_formas_pagamento()
        ntB.inserir_totais()
        ntB.inserir_transporte()
        ntB.inserir_produtos_servicos()
        ntB.conexao.commit()
    except Exception as e:
        ntB.conexao.rollback()
        raise e

def make_window():
    root = Tk()
    root.title('Importar Nota Fiscal Eletronica')
    root.geometry('350x120')
    frm = Frame(root)
    frm.pack(fill = X)
    
    lbl = LabelFrame(frm, text = "Enviar saída para:")    
    lbl.pack(fill=X)
    option = StringVar(root)
    option.set('Arquivo *.csv')
    
    optMenu = OptionMenu(lbl,  option,  'Banco de Dados',  'Arquivo *.csv')
    optMenu.pack(fill = X)
    
    Button(frm, text='Importar uma Nota Fiscal', command = (lambda output = option:send_invoice(output))).pack(fill = X)
    Button(frm, text='Importar Lote de Notas Fiscais', command = (lambda output = option:send_invoices(output))).pack(fill = X)
    Button(frm, text='Sair', command = root.quit).pack(fill = X)
    root.mainloop()
    
def send_invoice(output = '',  invoice_file = '',  log_file_name = '',  csv_file = None, print_header = True):    
    ''' Envia os dados da nota fiscal ou para o Banco de Dados ou para um Arquivo csv
        Parâmetros (output:string): Informa se a saída vai para o banco de dados ou para o arquivo csv
                    (invoice_file:string): Arquivo que contém os dados da nota fiscal, caso não seja passado 
                                            vai abrir um caixa de diálogo para escolher o arquivo de nota fiscal
                    (log_file_name:string): Arquivo onde serão guardadas as informções de log (quando rodando em lote),  caso não seja
                                            passado gerar-se um arquivo com nome de base identico ao da nota fiscal 
                                            com extensão log
                    (csv_file:arquivo): Arquivo que irá receber os dados da nota fiscal (quando rodando em lote), caso não seja passado gera-se
                                        um arquivo com nome de base idêntico ao da nota fiscal  com extensão csv
                    (print_header:boolean): Indica se vai se escrever um cabeçalho no arquivo csv'''
     
    if not invoice_file:
        #getting invoice file's path
        invoice_file = askopenfilename(  title='Selecione o arquivo da Nota Fiscal', 
                                    filetypes=(('html files', '*.html'), ('All files', '*')))
    
    if invoice_file:
        try:
            nt_fiscal = NfceParse(arquivo_nfce = invoice_file, aj_texto = True, aj_data = True,  aj_valor = True,  log_file_name = log_file_name)
            if output.get() == 'Arquivo *.csv':
                if not csv_file:                #verifica se esta importando uma nota
                    csv_file_name = os.path.basename(invoice_file) + '.csv'
                    dirname = os.path.dirname(invoice_file)
                    try:
                        csv_file = open(os.path.join(dirname, csv_file_name), 'w', encoding='utf-8')
                        send_invoice_to_csv_file(nt_fiscal, csv_file)
                        csv_file.close()
                    except Exception as e:
                        print('Erro ao Abrir Arquivo: {}\n Detalhes {}', csv_file_name, e)
                        raise e
                else:                            #se vir pro else, está processando um lote de notas, objeto csv_file passado por parâmetro    
                    send_invoice_to_csv_file(nt_fiscal, csv_file, print_header)
                
            elif output.get() == 'Banco de Dados':
                send_invoice_to_database(nt_fiscal)
            
        except NfceArquivoInvalido:
            messagebox.showerror('Erro',  'Arquivo Inválido, verifique se o arquivo trata-se de uma nota fiscal eletrônica')
            
        except Exception as e:
            messagebox.showerror('Error','{}'.format(e))
        
def show_invoice(nfce):      
    win = Toplevel()
    linha1 = Label(win)
    linha1.pack()
    lbl = LabelFrame(linha1, text = "Dados Nfce")
    lbl.pack(side = LEFT)
    
    caixas_texto = make_widget(lbl,  NfceParse._dados_nfc_e)     
    preencher_caixa_texto(caixas_texto,nfce.obter_dados_nfc_e() )
    
    lbl = LabelFrame(linha1, text = "Dados Emitente")
    lbl.pack(side = RIGHT)
    
    caixas_texto = make_widget(lbl,  nfce._dados_emitente)
    preencher_caixa_texto(caixas_texto,nfce.obter_dados_emitente_2())
    
    linha3 = Label(win)
    linha3.pack()
    
    lbl = LabelFrame(linha3, text = "Dados Mercadorias")
    lbl.pack()
    
    g = GridBox(lbl,tem_cabecalho = True)
    g.criar_cabecalho(nfce._dados_produtos_e_servicos_2.values())
    produtos_e_servicos = nfce.obter_dados_produtos_e_servicos()
    prod_serv = extrair_dados(produtos_e_servicos)
    g.preencher_cabecalho(prod_serv)
    g.pack()
    
    linha4 = Label(win)
    linha4.pack()
    Button(linha4, text='Sair', command = win.destroy).pack()
   
    
    win.focus_set()
    win.grab_set()
    win.wait_window()
    
    return   
    
    
def send_invoices(output):
    
    directory = askdirectory(title='Selecione a pasta que contém os arquivos de Nota Fiscal')
    
    if directory:
        
        files = util.obter_arquivos(directory, ('html', ))
        log_file_name = 'nfce.{}'.format(datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S'))
        csv_file_name = log_file_name + '.csv'
        log_file_name = log_file_name + '.log'
        try:
            csv_file = open( os.path.join(directory,csv_file_name), 'w', encoding='utf-8')
        except Exception as e:
            print('Erro ao Abrir Arquivo: {}\n Detalhes {}', csv_file_name, e)
            raise e
            
        print_header = True
        
        if files:
            for file in files:
                send_invoice(   output = output, 
                                invoice_file = file, 
                                log_file_name = os.path.join(directory,log_file_name), 
                                csv_file = csv_file, 
                                print_header = print_header)   
                print_header = False            #já imprimiu o header, não imprimi mais
                
        csv_file.close()
        
def make_widget(janela, dicionario_campos, width=20):
    
    caixas_de_texto = {}
    
    for chave, value in dicionario_campos.items():
        frame = Frame(janela)
        frame.pack()
        Label(frame, text = chave, width=width + 5).pack(side = LEFT)
        e = Entry(frame, width=width)
        caixas_de_texto[value] = e
        e.pack(side = LEFT)
    
    return caixas_de_texto
    
def preencher_caixa_texto(caixas_texto, dictValores):
    if dictValores:
        for id, cx_texto in caixas_texto.items():
            cx_texto.delete(0, END)
            if dictValores[id]:
                cx_texto.insert(0, dictValores[id])
    else:
        for id, cx_texto in caixas_texto:
            cx_texto.delete(0, END)
            cx_texto.insert(0, '')
            
if __name__ == '__main__':
    
    make_window()
