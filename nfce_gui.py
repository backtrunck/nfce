import nfce_db
from sqlalchemy import *
from sqlalchemy.sql import text
#from tkinter import * 
import tkinter as tk
from tkinter.ttk import Combobox
from collections import Counter
from interfaces_graficas.ScrolledWindow import ScrolledWindow
from PIL import Image
from PIL.ImageTk import PhotoImage
from fields import fields_search_invoice, fields_form_invoice, fields_items_invoice
    
def make_widget(self, master, widget_type, index_name, field_name='', comparison_operator='=', **options):
        
        e = widget_type(master, **options)
        e.index_name = index_name
        e.comparison_operator=comparison_operator
        
        if field_name:
            
            e.field_name = field_name
        else:
            
            e.field_name = index_name        
        
        return e
        
        
def search_invoice(master):
    
    win = tk.Toplevel(master)
    win.conn = master.conn
    win.title('Consultar Nota Fiscal')
    
    fields_f_invoice = fields_form_invoice.set_visible({'data_emissao':True, 'hora_emissao':True,'nu_nfce':True,
                                       'cnpj':True, 'estabelecimento':True, 'vl_total':True, 'button_1':True})
    f = FormSimpleSearch(win, fields_search_invoice, fields_f_invoice)
    f.pack()
    
class LabeledEntry(tk.Frame):
    def __init__(self, master, text_label = "", posLabel = tk.LEFT, padx = 0, pady = 0,  width = 20):
        
        super().__init__(master)
        
        if text_label:
            
            self.label = tk.Label(self, text=text_label)            

            self.label.pack(side = posLabel, padx = padx, pady = pady)
            self.entry = tk.Entry(self , width = width)
            self.entry.pack(side=posLabel,padx = padx, pady = pady)

    
class FrameGrid(tk.Frame):
    '''
        Class que representa um grid para apresentar dados em formato tabular
    '''

    def __init__(self, master, largura, altura, fields):
        '''

        :param master: widget pai do grid.
        :param largura: Largura do Grid
        :param altura: Altura do Grid
        :param fields: Coleçõo de objetos Field que contém as informações dos campos, tipos de widgets que serão
                mostrados no grid.
        '''

        super().__init__(master)

        self.conn = master.conn         #guarda  conexao com o banco de dados
        self.fields = fields

        dif_largura = -20               #a  partir da largura do pai, utilizada a diferença para obter a largura do pai
        dif_altura = -50                #idem o anterior

        #cria um frame com barras de rolagem que irá conter o grid
        scroll = ScrolledWindow(self, canv_w = largura + dif_largura, canv_h = altura + dif_altura)
        scroll.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=10, pady=10)
        
        self.frmGrid = tk.Frame(scroll.scrollwindow)       #Frame que ficará dentro do ScrolledWindows
        self.frmGrid.grid(row = 0,  column = 0)

        self.make_grid_header()


    def make_grid_header(self):
        '''
        Cria o cabeçalho do Grid
        '''
        for col, field in enumerate(self.fields.values()):

            if field.visible:
                
                e = tk.Entry(self.frmGrid, width=field.width, relief=tk.FLAT, background='#d9d9d9')
                e.grid(row=1, column=col, sticky=tk.W)
                e.insert(0, field.label)


    def fill_grid(self, data_rows, fields_match, callback):
        '''
        :param data_rows: Resultset do banco de dados (resultado de uma consulta que irá preencher o grid
        :param fields_key: Coleção com as informações dos campos. Estes campos foram utilizados no select que
                        resultou no parametro data_row. Vai ser utilizado para gerar os controles (widgets) do grid.
        :param callback: Função que irá ser atrelada a um botão. A idéia é que cada linha  do grid tenha um botão
                            do lado direito para que o usuário click e vá para uma nova tela com o detalhamento daquela
                            linha
        :return: None
        '''
        #limpa o grid
        self.clear_grid()
        
        #cria um dicionário somente com as chaves, vai ser utilizada na função callback que irá selecionar dados deta-
        #   lhados daquela linha no banco de dados.
        keys = dict([(i,'') for i in fields_match.get_keys()])

        #para cada linha retornada em data_rows
        for r, row in enumerate(data_rows, 2):

            #para cada campo ....
            for c, field in enumerate(fields_match.values()):
                #pega o tipo de widget a ser criado
                widget_class = field.widget_type
                #se o campo é visivel, cria o widget
                if field.visible:
                    #se for um Button...
                    if widget_class == tk.Button and callback:
                        #pega a imagem a ser exibida no botão
                        image = Image.open('./static/check2.png')
                        image2 = image.resize((22, 18), Image.ANTIALIAS)
                        photo = PhotoImage(image2)
                        
                        #pega o valor das chaves no data_row atual
                        for ch in keys:
                           keys[ch] = row[ch]
                        
                        # como não foi possivel passar o dicionario pelo callback no button.command (ele sempre levava o ultimo valor do loop
                        # criei uma lista de tuplas, a qual retornei para um dicionario na função get_itens_invoice
                        invoc = [(i, j) for i, j in keys.items()]


                        #cria um botão com imagem atrelado a uma função qeu irá detalhar o dado da linha
                        widget = widget_class(self.frmGrid, image=photo,
                                              command=(lambda k=(invoc), conn=self.conn: callback(k, conn)))
                        
#                        widget = widget_class(self.frmGrid, image=photo,
#                                              command=(lambda :callback(self.conn, **field.chaves, )))
                        
                        widget.image = photo
                        widget.grid(row=r, column=c, padx=0, pady=0)

                    else:
                        #se o tipo de widget não for Button, cria e mostra na tela, não sem veficar se o valor é nulo
                        widget = widget_class(self.frmGrid, width = field.width)
                        widget.grid(row=r, column=c, padx=0, pady=0)

                        if row[field.name_field]:

                            widget.insert(0, row[field.name_field])

                        else:

                            widget.insert(0, ' ')
                            
    def clear_grid(self): 
        
        for widget in self.frmGrid.grid_slaves():
            if int(widget.grid_info()['row']) > 1:
                widget.grid_forget()
    

class FormSimpleDialog(tk.Frame):
    '''
        Um tkinter.Frame que conterá vaŕios campos (widgets) formando um formulários as informações sobre disposição e os tipos de widgets, largura
                    etc, estaram no parâmetro field_list passado no __init__ da classe. O atributo controls conterá todos os widgets indexados por nome
                    do campo de uma tabela no banco de dados.
    '''


    def __init__(self,master, fields_list):
        '''
            Cria os controles  e põe os mesmo no form de acordo com o atributo row de cada Field dentro de fields_list
            Parametros:
                master (tkinter widget container): Frame/Root/Toplevel (window) que ira ser o container do Frame
                fields_list (OrderedDict): Dicionário com os dados sobre os campos a serem gerados no form. O dicionário contém informações sobre 
                    o tipo do widget, a largura, qual linha do form será mostrado.
        '''

        super().__init__(master)
        self.controls = {}
        self.fields_list = fields_list
        
        self.make_controls()
        
                
    def make_controls(self):  
        '''
            Criar os controles do form a partir de fields_list
        '''
        
        linhas = set([field.row for field in list(self.fields_list.values())])      #Pega as linhas
        print(Counter([field.row for field in self.fields_list.values() if field.visible]))

        for linha in linhas:

            frm = tk.Frame(self)            
            show_frame = 0       #controla se o frm(row), irá ser mostrado. Se algun widget dentro dele for visivel

            for field in self.fields_list.values():

                if field.row == linha:   

                    if field.visible:   #se o campo for visivel, cria o widget correspondente no Frame

                        if field.widget_type == tk.Entry:   # se o tipo de widget for  Entry cria um LabeledEntry (um Entry com Label)

                            w = field.width

                            lb = LabeledEntry(frm, text_label = field.label + ': ', width=w, padx=5, pady=5)
                            lb.pack(side = tk.LEFT)

                            self.controls[field.name_index] = lb
                            
                            show_frame = 1

                        elif field.widget_type == tk.Button:

                            Button(frm, text = field.label).pack(side=RIGHT)

                            show_frame = 1
            if show_frame:
                frm.pack(fill = tk.X)    
        
    def fill_controls(self, result_set):
        '''
            Preenche os widget com dados oriundos do banco de dados. (result_set). De acordo com a chave do dicionario self.controls (que contém todos os widgets
                    do form é feita a correspondencia entre o campo do result_set (oriundo de um select do banco de dados) e o widget que mostrará o 
                    valor no form. Como os wildget foram criados no __init__ com fields_list, o select que gerou result_set deveria ser
                    baseado em fields_list. Contudo um dicionario com as mesmas chaves presente em self.controls, preencheria o form. Atenção a idéia e só mostrar
                    um registro do banco de dados ou de outra fonte qualquer
        '''
        for key in self.controls:     #varre todos os controles no form
            if type(self.controls[key]) == LabeledEntry:            #Se o tipo do controle for LabeledEntry
                self.controls[key].entry.delete(0, 'end')           #limpa o campo
                field = self.fields_list[key]
                if result_set[field.name_field]:                                 #Se o valor não for nulo,                
                    self.controls[key].entry.insert(0, result_set[field.name_field]) #preenche o campo com o valor


class FormSimpleSearch(FormSimpleDialog):     
    '''   
        Classe com um formulário de busca , um botão de busca e um grid de resultado
    '''   
    def __init__(self, master, fields_search, fields_match, name_table='', order_by = ''):
        '''
            Parametros:
                master(tk.widget): widget pai onde será colocado o FormSimpleSearch
                fields_search(dictionarie): Dicionário com os dados para criar o form de pesquisa, bem como para
                            gerar o sql de busca
                fields_match(dictionarie): Dicionário com os dados para criar o grid de resultados da pesquisa, bem como para
                            gerar o sql de busca
        '''


        super().__init__(master, fields_search)     #cria o FrameSimpleDialog criando os controles a partir dos dados de fields_search
        
        self.fields_search = fields_search          #campos para o search
        self.fields_match = fields_match            #campos para o resultado
        self.conn = master.conn                     #conexão com o banco de dados
        self.order_by = order_by                    #o resultado da pesquisa será ordenado por
        self.name_table = name_table                #nome da tabela que vai ser pesquisa

        frm = tk.Frame(self)                           #form para acomodar o botão de pesquisa

        bt_search = tk.Button(frm, text = 'Search', command=self.search)
        frm.pack(fill = tk.X)
        bt_search.pack(side = tk.RIGHT)

        self.grid = FrameGrid(self, 0, 200, fields_match)  #Grid de pesquisa
        self.grid.pack()
        
        
    def search(self):
        '''
            Pesquisa os dados a partir dos campos preenchidos no FrameSimpleDialog criado no __init__
        '''
        
        values = self.get_values_controls()             #pega os valor preenchidos nos controles
        
        select = self.make_sql_select(self.fields_match)
        
        if values:                                      #se algum campo foi preenchido
        
            where = self.make_sql_where(values)
            
            sql = 'select ' + select + ' from nota_fiscal_v where ' + where     #atenção a tabela do BD esta fixa, deve-se mudar a estratégia
            sql += ' ORDER BY dt_emissao DESC'
            result_proxy = self.conn.execute(text(sql), **values)               #executa a consulta    
            
        else:
            
            sql = 'select ' + select + ' from nota_fiscal_v ORDER BY dt_emissao DESC'
            result_proxy = self.conn.execute(text(sql))               #executa a consulta
        
       
        
        self.grid.fill_grid(result_proxy.fetchall(),self.fields_match,get_itens_invoice)    #preenche o grid, passa o result_set,os campos e uma funçaõ
                                                                                                #de callback que irá chamar um tela de detalhamento de cada
                                                                                                #linha.
            
            
    def get_values_controls(self):    
        '''
            Obtem os valor preenchidos nos campos no FrameSimpleDialog
        '''
        values = {}
        controls = self.controls
        
        for key in controls:
            
            if type(controls[key]) == LabeledEntry:
                
                value = controls[key].entry.get()
                
                if value:
                    values[key] = value 
        
        return values           #retorna um dicionário com a chave(nome do campo no BD) e o valor preenchido no widget
        
    def make_sql_select(self, fields_list):
        '''
            Gera um lista de campos separados por virgula para compor um select sql
        '''
        
        select = []
        #pega o dados dos campos visíveis e  que não forem Botões
        for field in fields_list.values():
            
            #field.visible and
            if  field.widget_type != tk.Button:
                
                select.append(field.name_field)
                
        return ' , '.join(select)
        
        
    def make_sql_where(self, values_in_controls):
        '''
            Gera um lista de clausulas ligadas por "and" para compor um sql where
        '''
        sql_where = []

        for key in values_in_controls:

            field = self.fields_search[key]     #pega o Field correspondente ao campo 
            
            sql_where.append(field.name_field + ' ' + field.comparison_operator + ' :'+ field.name_index  )

        sql = " and ".join(sql_where)

        return sql


def get_itens_invoice(keys, conn):
    
    dict_keys = dict(keys)
    
    sql = text('''select *
            from   nota_fiscal_produtos_v 
            where  cd_uf = :cd_uf and nu_nfce = :nu_nfce and cnpj = :cnpj and cd_modelo = :cd_modelo and serie = :serie ''')
    
    result = conn.execute(sql, **dict_keys).fetchall()
    
    dlg_itens_invoice(result, conn)
    
    
def dlg_itens_invoice(result, conn):
    
    win = tk.Toplevel() 
    win.conn = conn
    win.title("Nota Fiscal")
    form = FormSimpleDialog(win,fields_form_invoice)    
    form.pack()
    form.fill_controls(result[0])
    grid = FrameGrid(win, 680, 200, fields_items_invoice)
    grid.fill_grid(result, fields_items_invoice, None)
    grid.pack()
    
    tk.Button(win, text = 'OK', command = win.destroy).pack(side = tk.RIGHT)
    
    #torna a janela modal
    win.focus_set()
    win.grab_set()
    win.wait_window()
    

class ComboBoxDB(Combobox):
    
    def __init__(self, master = None, **options):
        super().__init__(master, **options)
        self.list_content = []
        self.bind('<Key>', self.__key)
    
    def __key(self, event):    
        print("pressed", repr(event.char))
        if event.char == '\x7f':
            self.set('')
        
    def fill_list(self, list_content, erase=False):
        '''
            Preenche o list box, list_content deve ser um lista na qual a descrição é a coluna 0,
            e a chave a coluna 1
        '''
        
        if erase:
            self['values'] = list_content
            self.list_content = [item[1] for item in list_content]
        else:
            if self.list_content:
                self['values'].extend([item[1] for item in list_content])
                self.list_content.extend(list_content)
            else:
                self['values'] = [item[1] for item in list_content]
                self.list_content = list_content
                
    def get_key(self):
        
        if self.current() != -1:
            
            return self.list_content[self.current()][0]
            
        return None    
    
    def set_key(self, key):
        
        try:
            
            index = self.list_content.index(key)
            self.set(self.list_content[index])
            
        except ValueError:
            
            self.set('')
            
            
        if key in [x[0] for x in self.list_content]:
            i
        
        
def configure(event):
    print(event.width, event.height)
    
def main():
    root = tk.Tk()
    root.title('Consulta Produtos')
    #root.geometry('830x380') 
    
    engine = nfce_db.get_engine_bd()    
    conn = engine.connect()
    root.conn = conn
    
    fields_f_invoice = fields_form_invoice.set_visible({'data_emissao':True, 
                                                        'hora_emissao':True,
                                                        'nu_nfce':True,
                                                        'cnpj':True, 
                                                        'estabelecimento':True, 
                                                        'vl_total':True, 
                                                        'button_1':True})
                                       
    f = FormSimpleSearch(root, fields_search_invoice, fields_f_invoice)
    f.pack()
    root.mainloop()

if __name__ == '__main__':
    main()
