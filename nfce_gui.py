import nfce_db
from nfce_produtos import FrameProductAdjust,make_product_adjust_window,make_gtin_window,FormGtin
from nfce_estoque import FrameSearchStock

from sqlalchemy import *
from sqlalchemy.sql import text 
import tkinter as tk
from tkinter import messagebox
from collections import Counter
from interfaces_graficas.ScrolledWindow import ScrolledWindow
from interfaces_graficas.db import FrameGridSearch, DBField, FrameFormData#, ComboBoxDB
from interfaces_graficas import show_modal_win, EntryDate
from nfce_models import nota_fiscal_v,\
                        produtos_servicos_v,\
                        nota_fiscal_produtos_v
from PIL import Image
from PIL.ImageTk import PhotoImage
from fields import fields_search_invoice, fields_form_invoice, fields_items_invoice, Field

class FormInvoice(FrameFormData):
    def __init__(self, master, connection, data_keys=[], grid_keys=[], state=0):
        super().__init__(master, 
                         connection,
                         data_table=nota_fiscal_v,
                         grid_table=produtos_servicos_v, 
                         state=state, 
                         data_keys=data_keys, 
                         grid_keys=grid_keys, 
                         enabled_update=False, 
                         enabled_delete=False, 
                         enabled_new=False)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)
        f.grid_columnconfigure([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], weight=1)
        pady = 1
        tk.Label(f, text='Data.:', width=9,  anchor='e').grid(row=0, column=0, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=11, state='readonly')
        e.grid(row=0, column=1, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT, pady=2)
        cnpj = DBField(field_name='dt_emissao')
                         
        self.add_widget(cnpj, e)
        
#        f = tk.Frame(self.form)
#        f.pack(fill=tk.X)        
        tk.Label(f, text='Hora:', width=6,  anchor='e').grid(row=0, column=2, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=6, state='readonly')
        e.grid(row=0, column=3, sticky=tk.W+tk.E, pady=pady)#.pack(side=tk.LEFT, pady=2)        
        cd_produto = DBField(field_name='hora_emissao')
        self.add_widget(cd_produto, e)
        
#        f = tk.Frame(self.form)
#        f.pack(fill=tk.X)        
        tk.Label(f, text='Uf:', width=6,  anchor='e').grid(row=0, column=4, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=3, state='readonly')#.pack(side=tk.LEFT, pady=2)
        e.grid(row=0, column=5, sticky=tk.W, pady=pady)        
        cd_produto = DBField(field_name='sg_uf')
        self.add_widget(cd_produto, e)
        
#        f = tk.Frame(self.form)
#        f.pack(fill=tk.X)        
        tk.Label(f, text='Nfce:', width=6,  anchor='e').grid(row=0, column=6, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=10, state='readonly')
        e.grid(row=0, column=7, sticky=tk.W+tk.E, pady=pady)#.pack(side=tk.LEFT, pady=2)        
        cd_produto = DBField(field_name='nu_nfce')
        self.add_widget(cd_produto, e)
        
        tk.Label(f, text='Nota Fiscal:', width=12,  anchor='e').grid(row=0, column=8, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=10, state='readonly')
        e.grid(row=0, column=9, sticky=tk.W+tk.E, pady=pady)#.pack(side=tk.LEFT, pady=2)        
        cd_produto = DBField(field_name='num_nf')
        self.add_widget(cd_produto, e)        
        
        tk.Label(f, text='Cnpj:', width=9,  anchor='e').grid(row=1, column=0, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=14, state='readonly')
        e.grid(row=1, column=1, columnspan=3, sticky=tk.W+tk.E, pady=pady)#.pack(side=tk.LEFT, pady=2)        
        cd_produto = DBField(field_name='cnpj')
        self.add_widget(cd_produto, e)
        
        tk.Label(f, text='Estab:', width=6,  anchor='e').grid(row=1, column=4, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=50, state='readonly')
        e.grid(row=1, column=5, columnspan=5, sticky=tk.W+tk.E, pady=pady)#.pack(side=tk.LEFT, pady=2)        
        cd_produto = DBField(field_name='estabelecimento')
        self.add_widget(cd_produto, e)
        
        tk.Label(f, text='End:', width=9,  anchor='e').grid(row=2, column=0, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=50, state='readonly')
        e.grid(row=2, column=1, columnspan=3, sticky=tk.W+tk.E, pady=pady)#.pack(side=tk.LEFT, pady=2)        
        cd_produto = DBField(field_name='endereco')
        self.add_widget(cd_produto, e)
        
        tk.Label(f, text='Bairro:', width=6,  anchor='e').grid(row=2, column=4, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=20, state='readonly')
        e.grid(row=2, column=5, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT, pady=2)        
        cd_produto = DBField(field_name='bairro')
        self.add_widget(cd_produto, e)
        
        tk.Label(f, text='Mun.:', width=6,  anchor='e').grid(row=2, column=6, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=20, state='readonly')
        e.grid(row=2, column=7, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT, pady=2)        
        cd_produto = DBField(field_name='nm_municipio')
        self.add_widget(cd_produto, e)
        
        tk.Label(f, text='Tel.:', width=12,  anchor='e').grid(row=2, column=8, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=20, state='readonly')
        e.grid(row=2, column=9, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT, pady=2)        
        cd_produto = DBField(field_name='telefone')
        self.add_widget(cd_produto, e)
        
        tk.Label(f, text='Chave:', width=9,  anchor='e').grid(row=3, column=0, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=50, state='readonly')
        e.grid(row=3, column=1, columnspan=5, sticky=tk.W+tk.E, pady=pady)#.pack(side=tk.LEFT, pady=2)        
        cd_produto = DBField(field_name='chave_acesso_format')
        self.add_widget(cd_produto, e)
        
        tk.Label(f, text='Valor:', width=6,  anchor='e').grid(row=3, column=6, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=10, state='readonly')
        e.grid(row=3, column=7, sticky=tk.W+tk.E, pady=pady)#.pack(side=tk.LEFT, pady=2)        
        cd_produto = DBField(field_name='vl_total')
        self.add_widget(cd_produto, e)
        
        tk.Label(f, text='Inf.Comp.:', width=9,  anchor='e').grid(row=4, column=0, sticky=tk.W, pady=pady)#.pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=60, state='readonly')
        e.grid(row=4, column=1 , columnspan=9, sticky=tk.W+tk.E, pady=pady)#.pack(side=tk.LEFT, pady=2)        
        cd_produto = DBField(field_name='ds_informacoes_complementares')
        self.add_widget(cd_produto, e)       
        
        nu_prod_serv= DBField(field_name='nu_prod_serv',label='Item', width=5)
        ds_prod_serv= DBField(field_name='ds_prod_serv',label='Desc.', width=28)
        qt_prod_serv= DBField(field_name='qt_prod_serv',label='Qt.', width=6)
        vl_pago = DBField(field_name='vl_pago',label='Vl. Pago', width=9)
        vl_por_unidade= DBField(field_name='vl_por_unidade', label='Vl. Unit.',width=9)
        unid_comercial = DBField(field_name='un_comercial_prod_serv', label='Un.',width=3)
        ncm = DBField(field_name='cd_ncm_prod_serv', label='NCM',width=10)
        ean = DBField(field_name='cd_ean_prod_serv', label='Gtin',width=15)
        ds_produto =  DBField(field_name='ds_produto',label='Produto', width=28)
        ds_classe_produto =  DBField(field_name='ds_classe_produto',label='Classe Prod.', width=20)
        nu_nfce = DBField(field_name='nu_nfce',width=10, label='Nota', visible=False)
        cd_uf = DBField(field_name='cd_uf',label='Uf', width=2, visible=False)
        cnpj = DBField(field_name='cnpj',label='Cnpj', width=14, visible=False)        
        serie = DBField(field_name='serie',width=5, visible=False) 
        cd_modelo = DBField(field_name='cd_modelo', label='Modelo',width=6, visible=False)  
        cd_prod_serv = DBField(field_name='cd_prod_serv', label='Cd. Prod.',width=12, visible=True)
        
        self.columns = [nu_prod_serv, ds_prod_serv, qt_prod_serv,vl_por_unidade, 
                        vl_pago,unid_comercial, ncm, ean,ds_produto,  
                        ds_classe_produto, cd_prod_serv, nu_nfce, cd_uf,
                        cnpj,serie, cd_modelo]
        self.scroll.set_header(self.columns)
        
        self.add_widget_tool_bar(text='Ajustar', width = 10, command=self.adjust_product)
        self.add_widget_tool_bar(text='Produto', width=10, command=self.detalha_produto)
        self.add_widget_tool_bar(text='Estoque', width=10, command=self.conferir_estoque)
        
        if self.state == self.STATE_UPDATE:
            data = self.get_form_dbdata(self.data_keys) 
            self.set_form_dbdata(data)
            self.set_data_columns()
            self.set_filter_grid(grid_keys)
            self.get_grid_dbdata()
            
    def adjust_product(self):
        if self.last_clicked_row != -1:
            nu_nfce = self.get_grid_data_by_fieldname(self.last_clicked_row)
            make_product_adjust_window(master = self, 
                                       frame=FrameProductAdjust, 
                                       title='Ajuste Produto',
                                       keys={'cd_prod_serv_ajuste':nu_nfce['cd_prod_serv'], 
                                             'cnpj': nu_nfce['cnpj']}, 
                                       state=0)
    def detalha_produto(self):
        if self.last_clicked_row != -1:
            nu_nfce = self.get_grid_data_by_fieldname(self.last_clicked_row)
            if nu_nfce['cd_ean_prod_serv'] != 'SEM GTIN':
                make_gtin_window(master=self, Frame=FormGtin, title='Gtin', keys={'cd_ean_produto': nu_nfce['cd_ean_prod_serv']}, state=0)
            else:
                messagebox.showinfo('Nota Fiscal',
                                     'Somente para Produtos com Gtin',parent=self)
    def conferir_estoque(self):
        if self.last_clicked_row != -1:
            nu_nfce = self.get_grid_data_by_fieldname(self.last_clicked_row)
            if nu_nfce['cd_ean_prod_serv'] != 'SEM GTIN':
                make_window( master=self,
                             Frame=FrameSearchStock,
                             title='Pesquisa Estoque',
                             auto_filter = {'Prod. Gtin': nu_nfce['cd_ean_prod_serv']})
            else:
                messagebox.showinfo('Nota Fiscal',
                                     'Somente para Produtos com Gtin',parent=self)
def make_class_search_invoice_window(master=None):
    make_window(master=master, Frame=FrameSearchInvoices, title='Pesquisa Nota Fiscal', resizable=False)

    
def make_invoice_window(master=None, 
                        Frame=FormInvoice,
                        title='Nota Fiscal',
                        keys={'cd_ean_produto':'7894321218526'}, 
                        state=1):
#retirar após teste de FormInvoice
#    root = tk.Tk()
#    root.conn = engine.connect()
#    root.title(title)
#    if Frame:
#        f = Frame(root, root.conn, keys, state)
#        f.pack(fill = tk.X)
#        root.resizable(False, False)
#        root.mainloop()
    pass


def make_window(master=None, Frame=None, title=None, resizable=True, **kwargs):
    if master:
        root = tk.Toplevel(master)
        root.conn = master.conn
    else:
        root = tk.Tk()
        root.conn = nfce_db.get_engine_bd().connect()
    if title:
        root.title(title)
    #if Frame:
    if kwargs:
        f = Frame(root, root.conn, **kwargs)
    else:
        f = Frame(root, root.conn)
    f.pack(fill = tk.X)
    if not resizable:
        root.resizable(False, False)
    if master:
        show_modal_win(root)
    else:
        root.mainloop()

    return
def make_widget(master, widget_type, index_name, field_name='', comparison_operator='=', **options):
        
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
    show_modal_win(win)
    
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


class FrameSearchInvoices(FrameGridSearch):
    def __init__(self, master, connection, **kwargs):
        super().__init__(master, connection, grid_table=nota_fiscal_produtos_v, order_by=[('data_emissao',1)], **kwargs)
        
        width_label = 12
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)   
        
        l = tk.Label(f, text='Ch. de Acesso:', width=width_label,  anchor='e')
#        l.pack(side=tk.LEFT , anchor='w')
        l.grid(row=0,column=0,stick=tk.E + tk.W)
        e = tk.Entry(f, width=44)
#        e.pack(side=tk.LEFT, pady=2)
        e.grid(row=0,column=1,columnspan=3,stick=tk.E + tk.W)
        field = DBField(field_name='chave_acesso',
                        comparison_operator = Field.OP_EQUAL,
                        label='chave_acesso',
                        width=44,
                        type_widget=None)
        self.add_widget(field, e)
           
#        f = tk.Frame(self.form)
#        f.pack(fill=tk.X)
        
        l = tk.Label(f, text='Cnpj:', width=width_label,  anchor='e')
#        l.pack(side=tk.LEFT , anchor='w')
        l.grid(row=1,column=0,stick=tk.E + tk.W)
        e = tk.Entry(f, width=14)
#        e.pack(side=tk.LEFT, pady=2)
        e.grid(row=1,column=1,columnspan=1,stick=tk.E + tk.W)
        cnpj_field = DBField(field_name='cnpj', 
                                 comparison_operator = Field.OP_EQUAL,
                                 label='cnpj',
                                 width=14, 
                                 type_widget=tk.Entry)
        self.add_widget(cnpj_field, e)
        
#        f = tk.Frame(self.form)
#        f.pack(fill=tk.X)   
    
        l = tk.Label(f, text='Estabelec.:', width=width_label,  anchor='e')
#        l.pack(side=tk.LEFT , anchor='w')
        l.grid(row=1,column=2,stick=tk.E + tk.W)    
        e = tk.Entry(f, width=40)
#        e.pack(side=tk.LEFT, pady=2)
        e.grid(row=1,column=3,columnspan=1,stick=tk.E + tk.W)
        supplier_field = DBField(field_name='estabelecimento', 
                                     comparison_operator = Field.OP_LIKE,
                                    label='estabelecimento',
                                    width=40, 
                                    type_widget=tk.Entry)        
        self.add_widget(supplier_field, e)

        #        f = tk.Frame(self.form)
        #        f.pack(fill=tk.X)

        l = tk.Label(f, text='Gtin:', width=width_label, anchor='e')
        #        l.pack(side=tk.LEFT , anchor='w')
        l.grid(row=2, column=0, stick=tk.E + tk.W)
        e = tk.Entry(f, width=14)
        #        e.pack(side=tk.LEFT, pady=2)
        e.grid(row=2, column=1, columnspan=1, stick=tk.E + tk.W)
        filter = DBField(field_name='cd_ean_prod_serv',
                         comparison_operator=Field.OP_EQUAL,
                         label='cd_ean_prod_serv',
                         width=14,
                         type_widget=None)
        self.add_widget(filter, e)

        #        f = tk.Frame(self.form)
        #        f.pack(fill=tk.X)
        l = tk.Label(f, text='Produto:', width=width_label, anchor='e')
        #        l.pack(side=tk.LEFT , anchor='w')
        l.grid(row=2, column=2, stick=tk.E + tk.W)
        e = tk.Entry(f, width=35)
        #        e.pack(side=tk.LEFT, pady=2)
        e.grid(row=2, column=3, columnspan=1, stick=tk.E + tk.W)
        filter = DBField(field_name='ds_prod_serv',
                         comparison_operator=Field.OP_LIKE,
                         label='ds_prod_serv',
                         width=35,
                         type_widget=None)
        self.add_widget(filter, e)

#        f = tk.Frame(self.form)
#        f.pack(fill=tk.X)  
        
        l = tk.Label(f, text='Data De:', width=width_label,  anchor='e')
#        l.pack(side=tk.LEFT , anchor='w')
        l.grid(row=3,column=0,stick=tk.E + tk.W)  
        #e = tk.Entry(f, width=10)
        e = EntryDate(f, width=10)
#        e.pack(side=tk.LEFT, pady=2)
        e.grid(row=3,column=1,columnspan=1,stick=tk.E + tk.W)
        dt_emission_field = DBField(field_name='data_emissao',
                                        comparison_operator = Field.OP_GREATER_EQUAL,
                                        label='Emissão',
                                        width=10, 
                                        type_widget=tk.Entry)        
        self.add_widget(dt_emission_field, e)
        
#        f = tk.Frame(self.form)
#        f.pack(fill=tk.X)                
        l= tk.Label(f, text='Data Até:', width=width_label,  anchor='e')
#        l.pack(side=tk.LEFT , anchor='w')
        l.grid(row=3,column=2,stick=tk.E + tk.W)  
        #e = tk.Entry(f, width=10)
        e = EntryDate(f, width=10)
#        e.pack(side=tk.LEFT, pady=2)
        e.grid(row=3,column=3,columnspan=1,stick=tk.E + tk.W)
        field = DBField(field_name='data_emissao',
                            comparison_operator = Field.OP_LESS_EQUAL,
                            label='dt_emissao_2',
                            width=10, 
                            type_widget=None)        
        self.add_widget(field, e)

        
        
        nfce_field = DBField(field_name='nu_nfce', 
                             comparison_operator = '=', 
                             label='Número', 
                             width=8, 
                             type_widget=tk.Entry)
        uf_field = DBField(field_name='cd_uf',
                           comparison_operator = '=', 
                           label='Uf', 
                           width=8, 
                           type_widget=tk.Entry)
        serie_field = DBField(field_name='serie', 
                              comparison_operator = '=', 
                              label='Série', 
                              width=5, 
                              type_widget=tk.Entry)
        modelo_field = DBField(field_name='cd_modelo', 
                               comparison_operator = '=', 
                               label='Modelo', 
                               width=6, 
                               type_widget=tk.Entry)
        vl_total_field = DBField(field_name='vl_total', 
                               comparison_operator = '=', 
                               label='Vl. Total', 
                               width=8, 
                               type_widget=tk.Entry)
                               
        self.columns = [dt_emission_field, cnpj_field, supplier_field,vl_total_field, nfce_field, 
                        serie_field, modelo_field, uf_field ]
        self.scroll.set_header(self.columns)
        self.add_widget_tool_bar(text='Detalhar', width = 10, command=self.row_detail)
               
    def row_detail(self):
        if self.last_clicked_row != -1:
            nu_nfce = self.get_grid_data_by_fieldname(self.last_clicked_row)
            data_keys = {key:value for key, value in nu_nfce.items() if key in ['cd_uf',
                                                                        'cd_modelo',
                                                                        'serie', 
                                                                        'nu_nfce',
                                                                        'cnpj' ]}
            make_window(master=self, 
                        Frame=FormInvoice, 
                        title='Nota Fiscal', 
                        resizable=True, 
                        data_keys= data_keys, 
                        grid_keys=data_keys)


    

class FrameSearchInvoices2(FrameGridSearch):
    def __init__(self, master, connection, **kwargs):
        super().__init__(master, connection, grid_table=nota_fiscal_produtos_v, **kwargs)
        
        width_label = 12
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)   
        
        l = tk.Label(f, text='Ch. de Acesso:', width=width_label,  anchor='e')
        l.pack(side=tk.LEFT , anchor='w')
#        l.grid(row=0,column=0,stick=tk.E + tk.W)
#        e = tk.Entry(f, width=44)
        e.pack(side=tk.LEFT, pady=2)
        e.grid(row=0,column=1,columnspan=3,stick=tk.E + tk.W)
        field = DBField(field_name='chave_acesso',
                        comparison_operator = Field.OP_EQUAL,
                        label='chave_acesso',
                        width=44,
                        type_widget=None)
        self.add_widget(field, e)
           
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)
        
        l = tk.Label(f, text='Cnpj:', width=width_label,  anchor='e')
        l.pack(side=tk.LEFT , anchor='w')
#        l.grid(row=1,column=0,stick=tk.E + tk.W)
        e = tk.Entry(f, width=14)
        e.pack(side=tk.LEFT, pady=2)
#        e.grid(row=1,column=1,columnspan=1,stick=tk.E + tk.W)
        cnpj_field = DBField(field_name='cnpj', 
                                 comparison_operator = Field.OP_EQUAL,
                                 label='cnpj',
                                 width=14, 
                                 type_widget=tk.Entry)
        self.add_widget(cnpj_field, e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)   
    
        l = tk.Label(f, text='Estabelec.:', width=width_label,  anchor='e')
        l.pack(side=tk.LEFT , anchor='w')
#        l.grid(row=1,column=2,stick=tk.E + tk.W)    
        e = tk.Entry(f, width=40)
        e.pack(side=tk.LEFT, pady=2)
#        e.grid(row=1,column=3,columnspan=1,stick=tk.E + tk.W)
        supplier_field = DBField(field_name='estabelecimento', 
                                     comparison_operator = Field.OP_LIKE,
                                    label='estabelecimento',
                                    width=40, 
                                    type_widget=tk.Entry)        
        self.add_widget(supplier_field, e)
        
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)  
        
        l = tk.Label(f, text='Data De:', width=width_label,  anchor='e')
        l.pack(side=tk.LEFT , anchor='w')
#        l.grid(row=3,column=0,stick=tk.E + tk.W)  
        e = tk.Entry(f, width=10)
        e.pack(side=tk.LEFT, pady=2)
#        e.grid(row=3,column=1,columnspan=1,stick=tk.E + tk.W)
        dt_emission_field = DBField(field_name='data_emissao',
                                        comparison_operator = Field.OP_GREATER_EQUAL,
                                        label='Emissão',
                                        width=10, 
                                        type_widget=tk.Entry)        
        self.add_widget(dt_emission_field, e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)                
        l= tk.Label(f, text='Data Até:', width=width_label,  anchor='e')
        l.pack(side=tk.LEFT , anchor='w')
#        l.grid(row=3,column=2,stick=tk.E + tk.W)  
        e = tk.Entry(f, width=10)
        e.pack(side=tk.LEFT, pady=2)
#        e.grid(row=3,column=3,columnspan=1,stick=tk.E + tk.W)
        field = DBField(field_name='data_emissao',
                            comparison_operator = Field.OP_LESS_EQUAL,
                            label='dt_emissao_2',
                            width=10, 
                            type_widget=None)        
        self.add_widget(field, e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
       
        l = tk.Label(f, text='Gtin:', width=width_label,  anchor='e')
        l.pack(side=tk.LEFT , anchor='w')
#        l.grid(row=2,column=0,stick=tk.E + tk.W) 
        e = tk.Entry(f, width=14)
        e.pack(side=tk.LEFT, pady=2)
#        e.grid(row=2,column=1,columnspan=1,stick=tk.E + tk.W)
        filter = DBField(field_name='cd_ean_prod_serv',
                             comparison_operator = Field.OP_EQUAL,
                             label='cd_ean_prod_serv',
                             width=14, 
                             type_widget=None)        
        self.add_widget(filter, e)
        
#        f = tk.Frame(self.form)
#        f.pack(fill=tk.X)        
        l = tk.Label(f, text='Produto:', width=width_label,  anchor='e')
#        l.pack(side=tk.LEFT , anchor='w')
        l.grid(row=2,column=2,stick=tk.E + tk.W) 
        e = tk.Entry(f, width=35)
#        e.pack(side=tk.LEFT, pady=2)
        e.grid(row=2,column=3,columnspan=1,stick=tk.E + tk.W)
        filter = DBField(field_name='ds_prod_serv',
                             comparison_operator = Field.OP_LIKE,
                             label='ds_prod_serv',
                             width=35, 
                             type_widget=None)        
        self.add_widget(filter, e)
        
        
        
        nfce_field = DBField(field_name='nu_nfce', 
                             comparison_operator = '=', 
                             label='Número', 
                             width=8, 
                             type_widget=tk.Entry)
        uf_field = DBField(field_name='cd_uf',
                           comparison_operator = '=', 
                           label='Uf', 
                           width=8, 
                           type_widget=tk.Entry)
        serie_field = DBField(field_name='serie', 
                              comparison_operator = '=', 
                              label='Série', 
                              width=5, 
                              type_widget=tk.Entry)
        modelo_field = DBField(field_name='cd_modelo', 
                               comparison_operator = '=', 
                               label='Modelo', 
                               width=6, 
                               type_widget=tk.Entry)
        vl_total_field = DBField(field_name='vl_total', 
                               comparison_operator = '=', 
                               label='Vl. Total', 
                               width=8, 
                               type_widget=tk.Entry)
                               
        self.columns = [dt_emission_field, cnpj_field, supplier_field,vl_total_field, nfce_field, 
                        serie_field, modelo_field, uf_field ]
        self.scroll.set_header(self.columns)
        self.add_widget_tool_bar(text='Detalhar', width = 10, command=self.row_detail)
        self.add_widget_tool_bar(text='Ajustar', width = 10, command=self.adjust_product)
               
    def row_detail(self):
        if self.last_clicked_row != -1:
            nu_nfce = self.get_grid_data_by_fieldname(self.last_clicked_row)
            stm = select(nota_fiscal_produtos_v.c).where(and_(nota_fiscal_produtos_v.c['cd_uf'] == nu_nfce['cd_uf'], 
                                                         nota_fiscal_produtos_v.c['cd_modelo'] == nu_nfce['cd_modelo'], 
                                                         nota_fiscal_produtos_v.c['serie'] == nu_nfce['serie'], 
                                                         nota_fiscal_produtos_v.c['nu_nfce'] == nu_nfce['nu_nfce'], 
                                                         nota_fiscal_produtos_v.c['cnpj'] == nu_nfce['cnpj']))
            
            #dlg_itens_invoice
            result = self.conn.execute(stm).fetchall()
            #print(result)
            dlg_itens_invoice(result, self.conn)


    def adjust_product(self):
        if self.last_clicked_row != -1:
            nu_nfce = self.get_grid_data_by_fieldname(self.last_clicked_row)
            
            make_product_adjust_window(master = self, 
                                       frame=FrameProductAdjust, 
                                       title='Ajuste Produto',
                                       keys={'cnpj':nu_nfce['cnpj'], 'cd_prod_serv_ajuste':'00000250781'}, 
                                       state=0)

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
    
    open_modal(win)
   
   
def open_modal(win):
    '''
        abre a janela modal
    '''
    win.focus_set()
    win.grab_set()
    win.wait_window()


def configure(event):
    print(event.width, event.height)
    
def main():
    
            #make_invoice_window(keys, state=0)
            
#    make_class_search_invoice_window()
#    return
    root = tk.Tk()
    root.title('Teste')
    
    engine = nfce_db.get_engine_bd()    
    conn = engine.connect()
    root.conn = conn
    keys = {'cd_uf':29, 
            'cd_modelo':65, 
            'serie':2, 
            'nu_nfce':'54254509', 
            'cnpj':'00063960004864'}
    make_window(master=root, Frame=FormInvoice, title='Nota Fiscal', resizable=True, **keys)
    return 
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
