import tkinter as tk
from tkinter.messagebox import showwarning
#import nfce_db
import nfce_gui
from fields import Field
from interfaces_graficas.ScrolledWindow import ScrolledWindow
from interfaces_graficas.db import FrameGridManipulation, DBField, ComboBoxDB, FrameFormData, FrameGridSearch
from interfaces_graficas import show_modal_win, ChkButton
from sqlalchemy import text
from sqlalchemy.sql import select, and_
from nfce_models import engine, \
                        products_t,\
                        products_gtin_products_v, \
                        products_gtin_products_t, \
                        products_sem_gtin_products_v,\
                        products_sem_gtin_products_t, \
                        classe_produto_t, \
                        products_v, \
                        products_class_v, \
                        agrupamento_produto_t, \
                        products_gtin_t, \
                        adjust_prod_serv_t, \
                        produtos_servicos_t

#class FrameSearchProduct(tk.Frame):
#    
#    def __init__(self, master, db_connection, **options):
#        
#        super().__init__(master, **options)
#        
#        self.controls = {}
#        self.db_connection = db_connection
#        self.make_controls()
#        
#        self.get_ncm_01()
#        self.get_ncm_02()
#        self.get_ncm_05()
#        
#        self.controls['cd_ncm_01'].fill_list(self.ncm_01_list)
#        self.controls['cd_ncm_02'].fill_list(self.ncm_02_list)
#        self.controls['cd_ncm_05'].fill_list(self.ncm_05_list)
#       
#        
#    def __make_widget(self, widget_type, index_name, field_name='', comparison_operator='=', **options):
#        
#        e = widget_type(self, **options)
#        e.index_name = index_name
#        e.comparison_operator=comparison_operator
#        
#        if field_name:
#            
#            e.field_name = field_name
#        else:
#            
#            e.field_name = index_name        
#        
#        return e
#        
#    def make_controls(self, **options):
#        
#        if not options:
#            options['sticky'] = 'w'
#            options['padx'] = 2
#            options['pady'] = 2
#        
#        row = 0         
#        tk.Label(self, text='Ean:', anchor='e').grid(row=row, column=0)        
#        e = self.__make_widget(tk.Entry, 'cd_ean_prod_serv','','LIKE',  width=15)
#        self.controls[e.index_name] = e
#        e.grid(row=row, column=1, sticky=options['sticky'], padx=options['padx'], pady=options['pady'])
#        
#        #row += 1
#        tk.Label(self, text='Desc. Prod.: ', anchor='e').grid(row=row, column=2)        
#        e = self.__make_widget(tk.Entry, 'ds_prod_serv','','LIKE', width=35)
#        self.controls[e.index_name] = e
#        e.grid(row=row, column=3, sticky=options['sticky'], padx=options['padx'], pady=options['pady'])
#        
#        row += 1
#        tk.Label(self, text='Ncm 01:', anchor='e').grid(row=row, column=0)        
#        e = self.__make_widget(nfce_gui.ComboBoxDB, 'cd_ncm_01' , '', '=', state='readonly')
#        self.controls[e.index_name] = e
#        e.grid(row=row, column=1, sticky=options['sticky'], padx=options['padx'], pady=options['pady'])
#        
#        #row += 1
#        tk.Label(self, text='Ncm 02:', anchor='e').grid(row=row, column=2)        
#        e = self.__make_widget(nfce_gui.ComboBoxDB, 'cd_ncm_02', '', '=', width=35, state='readonly')
#        self.controls[e.index_name] = e
#        e.grid(row=row, column=3, sticky=options['sticky'], padx=options['padx'], pady=options['pady'])
#        
#        row += 1
#        tk.Label(self, text='Ncm 05:', anchor='e').grid(row=row,  column=0)        
#        e = self.__make_widget(nfce_gui.ComboBoxDB, 'cd_ncm_05' , '' ,'=', width=40, state='readonly')
#        self.controls[e.index_name] = e
#        e.grid(row=row, column=1, sticky=options['sticky'], padx=options['padx'], pady=options['pady'])
#        
#        row += 1
#        self.search_button = tk.Button(self, text = 'Procurar',  command=self.search)
#        self.search_button.grid(row=row, column=3, sticky='E', padx=options['padx'], pady=10)
#        self.columnconfigure(0, weight=1)
#        self.columnconfigure(1, weight=1)
#        
#        row += 1
#         #cria um frame com barras de rolagem que irá conter o grid
#        scroll = ScrolledWindow(self, canv_w=200, canv_h = 200, scroll_h = False)
#        scroll.columnconfigure(0, weight=1)
#        scroll.grid(row=row, column=0, columnspan=4, sticky='WE')
#        #scroll.pack(side=LEFT, fill=X, expand=YES, padx=10, pady=10)
#        
#        self.scrolled_frame = tk.Frame(scroll.scrollwindow)       #Frame que ficará dentro do ScrolledWindows
#        self.scrolled_frame.grid(row = 0, column = 0)
#
#
#    def make_header(self):
#        
#        e = tk.Entry(self.scrolled_frame, width=15, relief=tk.FLAT, background='#d9d9d9')
#        e.grid(row=1, column=0, sticky=tk.W)
#        e.insert(0,'EAN')
#        
#        e = tk.Entry(self.scrolled_frame, width=25, relief=tk.FLAT, background='#d9d9d9')
#        e.grid(row=1, column=1, sticky=tk.W)
#        e.insert(0,'Desc. Produto')
#        
#        e = tk.Entry(self.scrolled_frame, width=9, relief=tk.FLAT, background='#d9d9d9')
#        e.grid(row=1, column=0, sticky=tk.W)
#        e.insert(0,'NCM')
#        
#        e = tk.Entry(self.scrolled_frame, width=45, relief=tk.FLAT, background='#d9d9d9')
#        e.grid(row=1, column=0, sticky=tk.W)
#        e.insert(0,'Desc. NCM')
#        
#        
#    def search(self):
#        
#        '''
#            Pesquisa os dados a partir dos campos preenchidos
#        '''
#        
#        values = self.get_values_controls()             #pega os valor preenchidos nos controles
#        
#        select = "SELECT cd_ean_prod_serv,ds_prod_serv,cd_ncm_prod_serv,ds_ncm_05 "
#        
#        if values:                                      #se algum campo foi preenchido
#        
#            where = self.make_sql_where(values)
#            
#            sql = select + ' FROM produtos_servicos_ean ps, ncm_v WHERE ps.cd_ncm_prod_serv = cd_ncm_05 and ' + where     #atenção a tabela do BD esta fixa, deve-se mudar a estratégia
#
#            result_proxy = self.db_connection.execute(text(sql), **values)               #executa a consulta    
#            
#        else:
#            
#            sql = select + ' FROM produtos_servicos_ean ps, ncm_v where ps.cd_ncm_prod_serv = cd_ncm_05'
#            result_proxy = self.db_connection.execute(text(sql))               #executa a consulta
#        
#       
#        
#        self.fill_grid(result_proxy.fetchall())    #preenche o grid
#
#
#    def make_sql_where(self, values_in_controls):
#        '''
#            Gera um lista de clausulas ligadas por "and" para compor um sql where
#        '''
#        sql_where = []
#
#        for key in values_in_controls:
#            field_name = self.controls[key].field_name     #pega o name_field correspondente ao controle
#            comparison_operator = self.controls[key].comparison_operator #peda o operador de comparação do campo
#            sql_where.append(field_name + ' ' + comparison_operator + ' :'+ key  )
#
#        sql = " and ".join(sql_where)
#
#        return sql
#
#
#    def get_values_controls(self):    
#        '''
#            Obtem os valor preenchidos nos controles, com isto não vai ser necessário saber em que
#            tipo de controle esta cada valor.
#        '''
#        values = {}
#        
#        for key in self.controls:
#            
#            value = None
#            
#            if type(self.controls[key]) == tk.Entry:
#                
#                value = self.controls[key].get()
#        
#            elif type(self.controls[key]) == nfce_gui.ComboBoxDB:
#                
#                value = self.controls[key].get_key()
#                
#            if value:
#                
#                    values[key] = value 
#                
#        return values           #retorna um dicionário com a chave(nome do campo no BD) e o valor preenchido no widget    
#        
#    def get_ncm_01(self):
#        sql = '''   SELECT distinct cd_ncm, concat(cd_ncm,' - ', ds_ncm_alt)
#                    FROM nota_fiscal.ncm_01 n01, produtos_servicos ps 
#                    where n01.cd_ncm = substring(ps.cd_ncm_prod_serv,1,2)
#                    order by concat(cd_ncm,' - ', ds_ncm_alt)
#              '''  
#        self.ncm_01_list = self.db_connection.execute(sql).fetchall()
#        
#        
#    def get_ncm_02(self):
#        sql = '''   SELECT DISTINCT cd_ncm, concat(cd_ncm,' - ', ds_ncm), ds_ncm 
#                    FROM nota_fiscal.ncm_02 n02, produtos_servicos ps 
#                    WHERE n02.cd_ncm = substring(ps.cd_ncm_prod_serv,1,4)
#                    ORDER BY concat(cd_ncm,' - ', ds_ncm);
#              '''  
#        self.ncm_02_list = self.db_connection.execute(sql).fetchall()
#        
#        
#    def get_ncm_05(self):
#        sql = '''   SELECT DISTINCT cd_ncm, concat(cd_ncm,' - ', ds_ncm) 
#                    FROM nota_fiscal.ncm_05 n05, produtos_servicos ps 
#                    WHERE n05.cd_ncm = substring(ps.cd_ncm_prod_serv,1,8)
#                    ORDER BY concat(cd_ncm,' - ', ds_ncm);
#              '''  
#        self.ncm_05_list = self.db_connection.execute(sql).fetchall()
#        
#        
#    def fill_grid(self, data_rows):
#        '''
#            Preenche um grid a partir de um data_rows passado
#        '''
#        #limpa o grid
#        self.clear_grid()
#        
#        self.data_rows = data_rows
#        frm = self.scrolled_frame
#        #para cada linha retornada em data_rows
#        for r, row in enumerate(data_rows, 2):
#            
#            e = tk.Entry(frm,width=14)
#            e.grid(row = r,column=0)
#            e.insert(0, row['cd_ean_prod_serv'])
#            product_code = row['cd_ean_prod_serv']
#            e.bind("<Key>", lambda a: "break")
#                                                    
#            e = tk.Entry(frm, width=30)
#            e.grid(row=r, column=1)
#            e.insert(0, row['ds_prod_serv'])
#            e.bind("<Key>", lambda a: "break")
#                
#            e = tk.Entry(frm, width=9)
#            e.grid(row=r, column=2)
#            e.insert(0, row['cd_ncm_prod_serv'])
#            e.bind("<Key>", lambda a: "break")
#                                   
#            e = tk.Entry(frm, width=40)
#            e.grid(row=r, column=3)
#            e.insert(0, row['ds_ncm_05'])
#            e.bind("<Key>", lambda a: "break")
#                                   
#            image = PIL.Image.open('./static/check2.png')
#            image2 = image.resize((22, 18), PIL.Image.ANTIALIAS)
#            photo = PilImageTk.PhotoImage(image2)
#            bt = tk.Button(frm, image=photo)
#            bt.grid(row=r, column=4)   
#            bt.image = photo            
#            bt.config(command=(lambda product=product_code:open_product(self.master, self.db_connection, product)))
#
#
#    def clear_grid(self): 
#        
#        for widget in self.scrolled_frame.grid_slaves():
#            
#            if int(widget.grid_info()['row']) > 1:
#                
#                widget.grid_forget()
#
#
class FrameSearchProducts(FrameGridSearch):
    
    def __init__(self, master, connection, **kwargs):
        super().__init__(master, connection, grid_table=products_gtin_t, **kwargs)
        
        fr = tk.Frame(self.form)
        fr.pack(fill=tk.X)   
        
        f = tk.Frame(fr)
        f.pack(fill=tk.X)
        tk.Label(f, text='Gtin:', width=11,  anchor='e').pack(side=tk.LEFT, anchor='w')
        e = tk.Entry(f, width=14)
        
        cd_ean_produto = DBField(field_name='cd_ean_produto',
                        comparison_operator = Field.OP_EQUAL,
                        label='Gtin',
                        width=14,
                        type_widget=tk.Entry)
        self.add_widget(cd_ean_produto, e)
        
        e.pack(side=tk.LEFT, pady=2)
        
        f = tk.Frame(fr)
        f.pack(fill=tk.X)
        tk.Label(f, text='Descrição:', width=11,  anchor='e').pack(side=tk.LEFT, anchor='w')
        e = tk.Entry(f, width=60)
        e.pack(side=tk.LEFT, pady=2, padx=2) 
        e.focus_set()
        
        ds_produto = DBField(field_name='ds_produto',
                        comparison_operator = Field.OP_LIKE,
                        label='Desc.',
                        width=60,
                        type_widget=tk.Entry)
        self.add_widget(ds_produto, e)
        
        f = tk.Frame(fr)
        f.pack(fill=tk.X)
        tk.Label(f, text='NCM:', width=11,  anchor='e').pack(side=tk.LEFT, anchor='w')
        e = tk.Entry(f, width=8)
        e.pack(side=tk.LEFT, pady=2, padx=2)
        
        cd_ncm_produto = DBField(field_name='cd_ncm_produto',
                        comparison_operator = Field.OP_EQUAL,
                        label='NCM',
                        width=8,
                        type_widget=tk.Entry)
        self.add_widget(cd_ncm_produto, e)
        
        f = tk.Frame(fr)
        f.pack(fill=tk.X)
        tk.Label(f, text='Gtin Interno:', width=11,  anchor='e').pack(side=tk.LEFT, anchor='w')
        e = tk.Entry(f, width=13)
        e.pack(side=tk.LEFT, pady=2)
        
        cd_ean_interno = DBField(field_name='cd_ean_interno',
                        comparison_operator = Field.OP_EQUAL,
                        label='Gtin Int.',
                        width=13,
                        type_widget=tk.Entry)
        self.add_widget(cd_ean_interno, e)
        
        f = tk.Frame(fr)
        f.pack(fill=tk.X)
        tk.Label(f, text='Qt. Embalag.:', width=11,  anchor='e').pack(side=tk.LEFT, anchor='w')
        e = tk.Entry(f, width=5)
        e.pack(side=tk.LEFT, pady=2)
        
        qt_item_embalagem = DBField(field_name='qt_item_embalagem',
                        comparison_operator = Field.OP_EQUAL,
                        label='Qt Embalag.',
                        width=5,
                        type_widget=tk.Entry)
        self.add_widget(qt_item_embalagem, e)
        
#        f = tk.Frame(fr)
#        f.pack(fill=tk.X)        
#        tk.Label(f, text='Data Criação:', width=11,  anchor='e').pack(side=tk.LEFT , anchor='w')
#        e = tk.Label(f, width=11, relief=tk.SUNKEN)
#        e.pack(side=tk.LEFT, pady=2)
        dt_criacao = DBField(field_name='dt_criacao',
                        comparison_operator = Field.OP_EQUAL,
                        label='Data Criação.',
                        width=10,
                        type_widget=tk.Entry)
#        self.add_widget(dt_criacao, e)
        
        self.add_widget_tool_bar(text='Detalhar', width = 10, command=(lambda param=0:(self.row_detail(param))))
        self.add_widget_tool_bar(text='Novo', width = 10, command=(lambda param=1:(self.row_detail(param))))
        
        self.columns = [cd_ean_produto, ds_produto, cd_ncm_produto, cd_ean_interno, dt_criacao]
        self.scroll.set_header(self.columns)
        #self.order_by(self.grid_table.c.ds_produto) #fiquei de alterar o self.get_grid_dbdata
    
    
    def row_detail(self, state):
        if state: #state == 1;chama form de inclusão 
           make_gtin_window(Frame=FormGtin, title='Gtin',keys=None, state=state) 
        else:#state == 1;chama form de update
            
            product = self.get_grid_data_by_fieldname(self.last_clicked_row)
            
            make_gtin_window(Frame=FormGtin, title='Gtin',keys={'cd_ean_produto':product['cd_ean_produto']}, state=state)


class FrameProductGrouping(FrameGridManipulation):


    def __init__(self,  master, connection,  **args):
        
        super().__init__(master, connection, data_table=agrupamento_produto_t , **args)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Id:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=6, state='readonly')
        e.pack(side=tk.LEFT, pady=2)
        
        id_agrupamento = DBField(field_name='id_agrupamento', comparison_operator = '=', label='id', width=10, type_widget=tk.Entry)
        self.add_widget(id_agrupamento, e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Descrição:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=50)
        e.pack(side=tk.LEFT, pady=2)
        
        ds_agrupamento = DBField(field_name='ds_agrupamento', comparison_operator = '=', label='Agrupamento', width=40, type_widget=tk.Entry)
        self.add_widget(ds_agrupamento, e)
        
       
        
        self.columns = [id_agrupamento, ds_agrupamento]

        self.scroll.set_header(self.columns)
        
        self.order_by(self.grid_table.c.ds_agrupamento)
        self.get_grid_dbdata()

class FrameClassProduct(FrameGridManipulation):


    def __init__(self,  master, connection,  **args):
        
        super().__init__(master, connection, data_table=classe_produto_t,grid_table=products_class_v , **args)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Id:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=6, state='readonly')
        e.pack(side=tk.LEFT, pady=2)
        
        id_classe_produto = DBField(field_name='id_classe_produto', comparison_operator = '=', label='id', width=10, type_widget=tk.Entry)
        self.add_widget(id_classe_produto, e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Classe:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=50)
        e.pack(side=tk.LEFT, pady=2)
        
        ds_classe_produto = DBField(field_name='ds_classe_produto', comparison_operator = '=', label='Produto', width=40, type_widget=tk.Entry)
        self.add_widget(ds_classe_produto, e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Agrup.:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = ComboBoxDB(f, width=40, state='readonly')
        e.ds_key = 'ds_agrupamento'
        e.pack(side=tk.LEFT, pady=2)

        id_agrupamento = DBField(field_name='id_agrupamento', comparison_operator = '=', label='Id. Agr.', width=6, type_widget=tk.Entry)
        self.add_widget(id_agrupamento, e)
        s = select([agrupamento_produto_t.c.id_agrupamento,
                    agrupamento_produto_t.c.ds_agrupamento]).\
                    order_by(agrupamento_produto_t.c.ds_agrupamento)
        result = self.conn.execute(s)
        e.fill_list(result.fetchall())
        
        ds_agrupamento = DBField(field_name='ds_agrupamento', comparison_operator = '=', label='Agrup.', width=30, type_widget=tk.Entry)
        self.columns = [id_classe_produto, ds_classe_produto, id_agrupamento, ds_agrupamento]

        self.scroll.set_header(self.columns)
        
        self.order_by(self.grid_table.c.ds_classe_produto)
        self.get_grid_dbdata()

class FormGtin(FrameFormData):


    def __init__(self, master, connection, keys, state=0, ):
        super().__init__(master, connection, data_table=products_gtin_t, state=state, data_keys=keys)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Gtin:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=14)
        e.pack(side=tk.LEFT, pady=2)
        
        cd_ean_produto = DBField(field_name='cd_ean_produto', comparison_operator = '=', label='cd_ean_produto', width=14, type_widget=tk.Entry)
        self.add_widget(cd_ean_produto, e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Produto:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=80)
        e.pack(side=tk.LEFT, pady=2)
        
        ds_produto = DBField(field_name='ds_produto', comparison_operator = '=', label='Produto', width=40, type_widget=tk.Entry)
        self.add_widget(ds_produto, e)

        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='NCM.:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=10)
        e.pack(side=tk.LEFT, pady=2)
        
        cd_ncm_produto = DBField(field_name='cd_ncm_produto', comparison_operator = '=', label='Classif.', width=5, type_widget=ChkButton)
        self.add_widget(cd_ncm_produto, e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Manual.:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = ChkButton(f, width=1, anchor="w")
        e.pack(side=tk.LEFT, pady=2)
        
        manual = DBField(field_name='manual', comparison_operator = '=', label='Manual.', width=5, type_widget=ChkButton)
        self.add_widget(manual, e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Gtin Interno:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=14)
        e.pack(side=tk.LEFT, pady=2)
        
        cd_ean_interno = DBField(field_name='cd_ean_interno', comparison_operator = '=', label='cd_ean_interno', width=14, type_widget=tk.Entry)
        self.add_widget(cd_ean_interno, e)

        
        if self.state == self.STATE_UPDATE:
            data = self.get_form_dbdata(self.data_keys) 
            self.set_form_dbdata(data)

        

class FrameProduct(FrameGridManipulation):


    def __init__(self,  master, connection,  **args):


        super().__init__(master, connection, data_table=products_t,grid_table=products_v , **args)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Id:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=10, state='readonly')
        e.pack(side=tk.LEFT, pady=2)
        
        id_produto = DBField(field_name='id_produto', comparison_operator = '=', label='id', width=10, type_widget=tk.Entry)
        self.add_widget(id_produto, e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Produto:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=50)
        e.pack(side=tk.LEFT, pady=2)
        
        ds_produto = DBField(field_name='ds_produto', comparison_operator = '=', label='Produto', width=40, type_widget=tk.Entry)
        self.add_widget(ds_produto, e)

        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Classif.:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = ChkButton(f, width=1, anchor="w")
        e.pack(side=tk.LEFT, pady=2)
        
        classificado = DBField(field_name='classificado', comparison_operator = '=', label='Classif.', width=5, type_widget=ChkButton)
        self.add_widget(classificado, e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Classe:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = ComboBoxDB(f, width=40, state='readonly')
        e.ds_key = 'ds_classe_produto'
        e.pack(side=tk.LEFT, pady=2)
        
        id_classe_produto = DBField(field_name='id_classe_produto', comparison_operator = '=', label='Cd.Classe', width=8, type_widget=tk.Entry)
        self.add_widget(id_classe_produto, e)
        
        s = select([classe_produto_t.c.id_classe_produto,
                    classe_produto_t.c.ds_classe_produto]).\
                    order_by(classe_produto_t.c.ds_classe_produto)
        result = self.conn.execute(s)
        e.fill_list(result.fetchall())        

        ds_classe_modelo = DBField(field_name='ds_classe_produto', comparison_operator = '=', label='Classe', width=30, type_widget=tk.Entry)
        
        self.columns = [id_produto, ds_produto, ds_classe_modelo,id_classe_produto, classificado]

        self.scroll.set_header(self.columns)
        
        self.order_by(self.grid_table.c.ds_produto)
        self.get_grid_dbdata()


class FrameProduct_old(tk.Frame):
    def __init__(self, master, connection,  **args):
        super().__init__(master, **args)
        self.controls = []
        self.conn = connection
        self.last_clicked_row = -1
        self.last_inserted_row = -1
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Código:', width=11,  anchor='e').pack(side=tk.LEFT , anchor='w')
        self.id_product = tk.Entry(f, width=10, state='readonly')
        self.id_product.pack(side=tk.LEFT, pady=2)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='Descrição:', width=11,  anchor='e').pack(side=tk.LEFT, anchor='w')
        self.ds_product = tk.Entry(f, width=50)
        self.ds_product.pack(side=tk.LEFT, pady=2)
        self.ds_product.focus_set()
        self.pack()
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='Classificado:', width=11, anchor='e').pack(side=tk.LEFT, anchor='w')
        self.labeled = tk.Checkbutton(f, width=1, anchor='w')
        self.labeled.var = tk.IntVar()
        self.labeled.config(variable=self.labeled.var)
        self.labeled.pack(side=tk.LEFT, pady=2)
        self.pack()
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        scroll = ScrolledWindow(f, canv_w=450, canv_h = 200, scroll_h = False)
        scroll.pack(pady=2)
        self.scrolled_frame = tk.Frame(scroll.scrollwindow)       #Frame que ficará dentro do ScrolledWindows
        self.scrolled_frame.grid(row = 0, column = 0)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Button(f, text='Fechar', width = 10, command=self.close).pack(side=tk.RIGHT, padx=2, pady=5)
        tk.Button(f, text='Salvar', width = 10, command=self.update_row).pack(side=tk.RIGHT, padx=2, pady=5)
        tk.Button(f, text='Novo', width = 10, command=self.new_product).pack(side=tk.RIGHT, padx=2, pady=5)
        #self.bind('<Button-1>', self.mouse_click)
        
        self.make_header()
        sql = 'select id_produto,ds_produto,classificado FROM produtos order by ds_produto'
        result_proxy = self.conn.execute(text(sql)) 
        self.fill_grid(result_proxy.fetchall())   


    def close(self):
        self.master.destroy()
    
    
    def row_click(self, event):
        self.last_clicked_row = event.widget.grid_info()['row']
        self.get_grid_line(int(event.widget.grid_info()['row']))


    def new_product(self):
        self.last_clicked_row = -1
        self.id_product.config(state=tk.NORMAL)
        self.id_product.delete(0, tk.END)
        self.id_product.config(state='readonly')
        self.ds_product.delete(0, tk.END)
        self.ds_product.focus_set()


    def update_product(self):
        try:
            insert = False
            if not self.id_product.get():
                insert = True
            if not self.ds_product.get():
                showwarning('Inserir Produto','Informe a descrição do produto')
                return -1
            if insert:
                ins = products_t.insert().values(ds_produto=self.ds_product.get(),\
                                                     classificado=self.labeled.var.get())
                result = self.conn.execute(ins)
                self.last_inserted_row +=1
                self.fill_row(self.last_inserted_row, 
                              {'id_produto':result.inserted_primary_key[0],
                               'ds_produto':self.ds_product.get(), 
                               'classificado':self.labeled.var.get()})
                self.id_product.config(state=tk.NORMAL)
                self.id_product.delete(0, tk.END)
                self.id_product.insert(0, result.inserted_primary_key[0])
                self.id_product.config(state='readonly')
                return 0
            else:
                upd = products_t.update().where(\
                            products_t.c.id_produto==self.id_product.get()).\
                            values(ds_produto=self.ds_product.get(), \
                                   classificado=self.labeled.var.get())
                self.conn.execute(upd)
                return 0
        except Exception as e:
            showwarning('Inserir Produto',e)
            return -1


    def update_row(self):
        if self.update_product():
            self.set_grid_line()
        
    def get_grid_line(self, row):
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) == row:
                if widget.name == 'id_produto':
                    self.id_product.config(state=tk.NORMAL)
                    self.id_product.delete(0, tk.END)
                    self.id_product.insert(0, widget.get())
                    self.id_product.config(state='readonly')
                elif widget.name == 'ds_produto':
                    self.ds_product.delete(0, tk.END)
                    self.ds_product.insert(0, widget.get())
                elif widget.name == 'classificado':
                    if widget.var.get():
                        self.labeled.select()
                    else:
                        self.labeled.deselect()


    def set_grid_line(self):
        if self.last_clicked_row == -1:
            return 
        for widget in self.scrolled_frame.grid_slaves():            
            if int(widget.grid_info()['row']) == self.last_clicked_row:
                if widget.name == 'ds_produto':
                    widget.config(state=tk.NORMAL)
                    widget.delete(0, tk.END)
                    widget.insert(0, self.ds_product.get())
                    widget.config(state='readonly')
                elif widget.name == 'id_produto':
                    widget.config(state=tk.NORMAL)
                    widget.delete(0, tk.END)
                    widget.insert(0, self.id_product.get())
                    widget.config(state='readonly')                    
                elif widget.name == 'classificado':
                    if self.labeled.var.get():
                        widget.select()
                    else:
                        widget.deselect()


    def fill_grid(self, data_rows):
        '''
            Preenche um grid a partir de um data_rows passado
        '''
        #limpa o grid
        self.clear_grid()
        
        self.data_rows = data_rows
        #para cada linha retornada em data_rows
        for row, data_row in enumerate(data_rows, 2):
            self.fill_row(row, data_row)
        self.last_inserted_row = row


    def fill_row(self, row, data_row):
        e = tk.Entry(self.scrolled_frame,width=10, readonlybackground='white')
        e.grid(row=row,column=0)
        e.insert(0, data_row['id_produto'])
        e.name = 'id_produto'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        #Button-1
        e.config(state='readonly')
                                                
        e = tk.Entry(self.scrolled_frame, width=50, readonlybackground='white')
        e.grid(row=row, column=1)
        e.insert(0, data_row['ds_produto'])
        e.name = 'ds_produto'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
        
        c = tk.Checkbutton(self.scrolled_frame)
        c.name = 'classificado'
        c.var = tk.IntVar()
        c.config(variable=c.var)
        if data_row['classificado']:
            c.select()
        else:
            c.deselect()
        c.grid(row=row, column=2)


    def make_header(self):
        
        e = tk.Entry(self.scrolled_frame, width=10, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=0, sticky=tk.W)
        e.insert(0,'Código')
        
        e = tk.Entry(self.scrolled_frame, width=25, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=1, sticky=tk.W)
        e.insert(0,'Descrição')
        
        e = tk.Entry(self.scrolled_frame, width=5, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=2, sticky=tk.W)
        e.insert(0,'Class.')
        
    def clear_grid(self): 
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) > 1:
                
                widget.grid_forget()


class FrameProductGtimProduct(tk.Frame):
    def __init__(self, master, connection,  **args):
        super().__init__(master, **args)
        self.controls = []
        self.conn = connection
        self.last_clicked_row = -1
        self.last_inserted_row = -1
        
        label_width = 11
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Gtim:', width=label_width,  anchor='e').pack(side=tk.LEFT , anchor='w')
        self.cd_gtin = tk.Entry(f, width=14, state='readonly')
        self.cd_gtin.pack(side=tk.LEFT, pady=2)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='Desc. Gtin:', width=label_width,  anchor='e').pack(side=tk.LEFT, anchor='w')
        self.ds_gtin = tk.Entry(f, width=60, state='readonly')
        self.ds_gtin.pack(side=tk.LEFT, pady=2)
        self.ds_gtin.focus_set()
                
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='Produto:', width=label_width, anchor='e').pack(side=tk.LEFT, anchor='w')
        self.product = ComboBoxDB(f, width=40, state='readonly')
        self.id_product = tk.Entry(f)
        self.fill_products()
        self.product.pack(side=tk.LEFT, pady=2)
        self.product.focus_set()
        self.pack()
        #Grid - Scrolled Window
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        scroll = ScrolledWindow(f, canv_w=650, canv_h = 200, scroll_h = False)
        scroll.pack(pady=2)
        self.scrolled_frame = tk.Frame(scroll.scrollwindow)       #Frame que ficará dentro do ScrolledWindows
        self.scrolled_frame.grid(row = 0, column = 0)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Button(f, text='Fechar', width = 10, command=self.close).pack(side=tk.RIGHT, padx=2, pady=5)
        tk.Button(f, text='Salvar', width = 10, command=self.update_row).pack(side=tk.RIGHT, padx=2, pady=5)
                
        self.make_header()
        self.fill_grid()   

    def fill_products(self):
        s = select([products_t.c.id_produto,
                    products_t.c.ds_produto]).\
                    order_by(products_t.c.ds_produto)
        result = self.conn.execute(s)
        self.product.fill_list(result.fetchall())
        
    def close(self):
        self.master.destroy()
    
    
    def row_click(self, event):
        self.last_clicked_row = event.widget.grid_info()['row']
        self.get_grid_line(int(self.last_clicked_row))


    def update_product(self):
        try:
            if not self.cd_gtin.get() or self.product.get_key() == -1:
                showwarning('Produto Gtin x Produto','Dados não fornecidos')
                return -1
            if self.product.get_key() != -1:
                upd = products_gtin_products_t.update().where(and_(\
                            products_gtin_products_t.c.id_produto==int(self.id_product.get()), 
                            products_gtin_products_t.c.cd_ean_produto==self.cd_gtin.get())).\
                            values(id_produto=int(self.product.get_key()))
                self.conn.execute(upd)
                return 0 
            return -1
        except Exception as e:
            showwarning('Produto Gtin x Produto',e)
            return -1


    def update_row(self):
        if not self.update_product():
            self.set_grid_line()
            self.get_grid_line(int(self.last_clicked_row))
        
    def get_grid_line(self, row):
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) == row:
                if widget.name == 'id_produto':
                    self.product.set_key(int(widget.get()))
                    self.id_product.delete(0, tk.END) 
                    self.id_product.insert(0, widget.get())
                elif widget.name == 'ds_gtin':
                    self.ds_gtin.config(state=tk.NORMAL)
                    self.ds_gtin.delete(0, tk.END)
                    self.ds_gtin.delete(0, tk.END)
                    self.ds_gtin.insert(0, widget.get())
                    self.ds_gtin.config(state='readonly')
                elif widget.name == 'cd_gtin':
                    self.cd_gtin.config(state=tk.NORMAL)
                    self.cd_gtin.delete(0, tk.END)
                    self.cd_gtin.delete(0, tk.END)
                    self.cd_gtin.insert(0, widget.get())
                    self.cd_gtin.config(state='readonly')    


    def set_grid_line(self):
        if self.last_clicked_row == -1:
            return 
        for widget in self.scrolled_frame.grid_slaves():            
            if int(widget.grid_info()['row']) == self.last_clicked_row:
                if widget.name == 'ds_product':
                    widget.config(state=tk.NORMAL)
                    widget.delete(0, tk.END)
                    widget.insert(0, self.product.get())
                    widget.config(state='readonly')
                if widget.name == 'id_produto':
                    widget.config(state=tk.NORMAL)
                    widget.delete(0, tk.END)
                    widget.insert(0, self.product.get_key())
                    widget.config(state='readonly')


    def fill_grid(self):
        '''
            Preenche um grid a partir de um data_rows passado
        '''
        #limpa o grid
        self.clear_grid()
        s = select([products_gtin_products_v]).order_by(products_gtin_products_v.c.ds_produto,
                                                        products_gtin_products_v.c.ds_gtin)
        result = self.conn.execute(s)
        self.data_rows = result.fetchall()
        #para cada linha retornada em data_rows
        for row, data_row in enumerate(self.data_rows, 2):
            self.fill_row(row, data_row)
        self.last_inserted_row = row


    def fill_row(self, row, data_row):
        e = tk.Entry(self.scrolled_frame,width=14, readonlybackground='white')
        e.grid(row = row,column=0)
        e.insert(0, data_row['cd_gtin'])
        e.name = 'cd_gtin'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
                                                
        e = tk.Entry(self.scrolled_frame, width=70, readonlybackground='white')
        e.grid(row=row, column=1)
        e.insert(0, data_row['ds_gtin'])
        e.name = 'ds_gtin'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
        
        e = tk.Entry(self.scrolled_frame, width=7, readonlybackground='white')
        e.grid(row=row, column=2)
        e.insert(0, data_row['id_produto'])
        e.name = 'id_produto'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
        
        e = tk.Entry(self.scrolled_frame, width=20, readonlybackground='white')
        e.grid(row=row, column=3)
        e.insert(0, data_row['ds_produto'])
        e.name = 'ds_product'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
        
        c = tk.Checkbutton(self.scrolled_frame)
        c.name = 'classificado'
        c.var = tk.IntVar()
        c.config(variable=c.var)
        c.config(state='disabled')
        if data_row['classificado']:
            c.select()
        else:
            c.deselect()
        c.grid(row=row, column=4)


    def make_header(self):
        
        e = tk.Entry(self.scrolled_frame, width=14, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=0, sticky=tk.W)
        e.insert(0,'Gtin')
        
        e = tk.Entry(self.scrolled_frame, width=60, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=1, sticky=tk.W)
        e.insert(0,'Desc. Gtin')
        
        e = tk.Entry(self.scrolled_frame, width=7, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=2, sticky=tk.W)
        e.insert(0,'id')
        
        e = tk.Entry(self.scrolled_frame, width=20, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=3, sticky=tk.W)
        e.insert(0,'Produto')
        
        e = tk.Entry(self.scrolled_frame, width=6, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=4, sticky=tk.W)
        e.insert(0,'Class.')

    def clear_grid(self): 
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) > 1:
                
                widget.grid_forget()


class FrameProductSemGtimProduct(tk.Frame):
    def __init__(self, master, connection,  **args):
        super().__init__(master, **args)
        self.controls = []
        self.conn = connection
        self.last_clicked_row = -1
        self.last_inserted_row = -1
        
        label_width = 11
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='Cnpj:', width=label_width,  anchor='e').pack(side=tk.LEFT, anchor='w')
        self.cnpj = tk.Entry(f, width=14, state='readonly')
        self.cnpj.pack(side=tk.LEFT, pady=2)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X) 
        tk.Label(f, text='Estabelec.:', width=label_width,  anchor='e').pack(side=tk.LEFT, anchor='w')
        self.ds_supplier = tk.Entry(f, width=50, state='readonly')
        self.ds_supplier.pack(side=tk.LEFT, pady=2)
        self.ds_supplier.focus_set()
            
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='Item Compra:', width=label_width,  anchor='e').pack(side=tk.LEFT, anchor='w')
        self.cd_product = tk.Entry(f, width=15, state='readonly')
        self.cd_product.pack(side=tk.LEFT, pady=2)
        self.ds_product = tk.Entry(f, width=50, state='readonly')
        self.ds_product.pack(side=tk.LEFT, pady=2)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='Produto:', width=label_width, anchor='e').pack(side=tk.LEFT, anchor='w')
        self.product = ComboBoxDB(f, width=40, state='readonly')
        self.fill_products()
        self.id_product = tk.Entry(f) #sem pack(invisivel), usado para guardar a chave pro update
        self.product.pack(side=tk.LEFT, pady=2)
        self.product.focus_set()
        
        self.pack()
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        scroll = ScrolledWindow(f, canv_w=650, canv_h = 200, scroll_h = False)
        scroll.pack(pady=2)
        self.scrolled_frame = tk.Frame(scroll.scrollwindow)       #Frame que ficará dentro do ScrolledWindows
        self.scrolled_frame.grid(row = 0, column = 0)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Button(f, text='Fechar', width = 10, command=self.close).pack(side=tk.RIGHT, padx=2, pady=5)
        tk.Button(f, text='Salvar', width = 10, command=self.update_row).pack(side=tk.RIGHT, padx=2, pady=5)
                
        self.make_header()
        self.fill_grid()   

    def fill_products(self):
        s = select([products_t.c.id_produto,
                    products_t.c.ds_produto]).\
                    order_by(products_t.c.ds_produto)
        result = self.conn.execute(s)
        self.product.fill_list(result.fetchall())
        
    def close(self):
        self.master.destroy()
    
    
    def row_click(self, event):
        self.last_clicked_row = event.widget.grid_info()['row']
        self.get_grid_line(int(self.last_clicked_row))


    def update_product(self):
        try:
            if not self.cnpj.get() or\
               not self.cd_product or\
               self.product.get_key() == -1:
                   
                showwarning('Inserir Produto Sem Gtin x Produto','Dados não fornecidos')
                return -1
            if self.product.get_key() != -1:
                upd = products_sem_gtin_products_t.update().where(and_(\
                            products_sem_gtin_products_t.c.id_produto==int(self.id_product.get()), 
                            products_sem_gtin_products_t.c.cnpj==self.cnpj.get(), 
                            products_sem_gtin_products_t.c.cd_prod_serv==self.cd_product.get())).\
                            values(id_produto=int(self.product.get_key()))
                self.conn.execute(upd)
                return 0 
            return -1
        except Exception as e:
            showwarning('Inserir Produto Sem Gtin x Produto',e)
            return -1


    def update_row(self):
        if not self.update_product():
            self.set_grid_line()
            self.get_grid_line(int(self.last_clicked_row))
        
    def get_grid_line(self, row):
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) == row:
                if widget.name == 'id_product':                   
                    self.product.set_key(int(widget.get()))
                    self.id_product.delete(0, tk.END)
                    self.id_product.insert(0, widget.get())

                elif widget.name == 'cnpj':
                    self.cnpj.config(state=tk.NORMAL)
                    self.cnpj.delete(0, tk.END)
                    self.cnpj.delete(0, tk.END)
                    self.cnpj.insert(0, widget.get())
                    self.cnpj.config(state='readonly')    
                elif widget.name == 'ds_supplier':
                    self.ds_supplier.config(state=tk.NORMAL)
                    self.ds_supplier.delete(0, tk.END)
                    self.ds_supplier.delete(0, tk.END)
                    self.ds_supplier.insert(0, widget.get())
                    self.ds_supplier.config(state='readonly')
                elif widget.name == 'ds_product':
                    self.ds_product.config(state=tk.NORMAL)
                    self.ds_product.delete(0, tk.END)
                    self.ds_product.delete(0, tk.END)
                    self.ds_product.insert(0, widget.get())
                    self.ds_product.config(state='readonly') 
                elif widget.name == 'cd_product':
                    self.cd_product.config(state=tk.NORMAL)
                    self.cd_product.delete(0, tk.END)
                    self.cd_product.delete(0, tk.END)
                    self.cd_product.insert(0, widget.get())
                    self.cd_product.config(state='readonly')   
                    

    def set_grid_line(self):
        if self.last_clicked_row == -1:
            return 
        for widget in self.scrolled_frame.grid_slaves():            
            if int(widget.grid_info()['row']) == self.last_clicked_row:
                if widget.name == 'product':
                    widget.config(state=tk.NORMAL)
                    widget.delete(0, tk.END)
                    widget.insert(0, self.product.get())
                    widget.config(state='readonly')
                if widget.name == 'id_product':
                    widget.config(state=tk.NORMAL)
                    widget.delete(0, tk.END)
                    widget.insert(0, self.product.get_key())
                    widget.config(state='readonly')


    def fill_grid(self):
        '''
            Preenche um grid a partir de um data_rows passado
        '''
        #limpa o grid
        self.clear_grid()
        s = select([products_sem_gtin_products_v]).order_by(products_sem_gtin_products_v.c.ds_produto)
        result = self.conn.execute(s)
        self.data_rows = result.fetchall()
        #para cada linha retornada em data_rows
        for row, data_row in enumerate(self.data_rows, 2):
            self.fill_row(row, data_row)
        self.last_inserted_row = row


    def fill_row(self, row, data_row):
        
        e = tk.Entry(self.scrolled_frame,width=14, readonlybackground='white')
        e.grid(row = row,column=0)
        e.insert(0, data_row['cnpj'])
        e.name = 'cnpj'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
        
        e = tk.Entry(self.scrolled_frame,width=36, readonlybackground='white')
        e.grid(row = row,column=1)
        e.insert(0, data_row['razao_social'])
        e.name = 'ds_supplier'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
                                                
        e = tk.Entry(self.scrolled_frame, width=15, readonlybackground='white')
        e.grid(row=row, column=2)
        e.insert(0, data_row['cd_prod_serv'])
        e.name = 'cd_product'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
        
        e = tk.Entry(self.scrolled_frame, width=25, readonlybackground='white')
        e.grid(row=row, column=3)
        e.insert(0, data_row['ds_prod_serv'])
        e.name = 'ds_product'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
        
        e = tk.Entry(self.scrolled_frame, width=7, readonlybackground='white')
        e.grid(row=row, column=4)
        e.insert(0, data_row['id_produto'])
        e.name = 'id_product'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
        
        e = tk.Entry(self.scrolled_frame, width=20, readonlybackground='white')
        e.grid(row=row, column=5)
        e.insert(0, data_row['ds_produto'])
        e.name = 'product'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
        
        c = tk.Checkbutton(self.scrolled_frame)
        c.name = 'classificado'
        c.var = tk.IntVar()
        c.config(variable=c.var)
        if data_row['classificado']:
            c.select()
        else:
            c.deselect()
        c.grid(row=row, column=6)


    def make_header(self):
        
        e = tk.Entry(self.scrolled_frame, width=14, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=0, sticky=tk.W)
        e.insert(0,'Cnpj')
        
        e = tk.Entry(self.scrolled_frame, width=36, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=1, sticky=tk.W)
        e.insert(0,'Estabelecimento')
        
        e = tk.Entry(self.scrolled_frame, width=15, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=2, sticky=tk.W)
        e.insert(0,'Cod. Item')
        
        e = tk.Entry(self.scrolled_frame, width=25, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=3, sticky=tk.W)
        e.insert(0,'Item Compra')
        
        e = tk.Entry(self.scrolled_frame, width=7, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=4, sticky=tk.W)
        e.insert(0,'Id')
        
        e = tk.Entry(self.scrolled_frame, width=7, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=5, sticky=tk.W)
        e.insert(0,'Produto')
        
        e = tk.Entry(self.scrolled_frame, width=6, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=6, sticky=tk.W)
        e.insert(0,'Class.')

    def clear_grid(self): 
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) > 1:
                
                widget.grid_forget()

class FrameProductAdjust(FrameFormData):


    def __init__(self, 
                 master,
                 connection, 
                 keys, 
                 state=0, ):
                     
        super().__init__(master, 
                         connection, 
                         data_table=adjust_prod_serv_t,
                         state=state,
                         enabled_delete=False, 
                         enabled_new=False, 
                         data_keys=keys)
        
        self.produtos_servicos_t = produtos_servicos_t
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Estabel.:', width=10,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=14, state='readonly')
        e.pack(side=tk.LEFT, pady=2)
       
        cnpj = DBField(field_name='cnpj', 
                                 comparison_operator = '=', 
                                 label='cnpj', 
                                 width=14, 
                                 type_widget=tk.Entry)
        self.add_widget(cnpj, e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Produto:', width=10,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=80, state='readonly')
        e.pack(side=tk.LEFT, pady=2)
        
        cd_produto = DBField(field_name='cd_prod_serv_ajuste', 
                             comparison_operator = '=', 
                             label='cd_prod_serv_ajuste', 
                             width=40, 
                             type_widget=tk.Entry)
        self.add_widget(cd_produto, e)

        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Gtin:', width=10,  anchor='e').pack(side=tk.LEFT , anchor='w')

        e = ComboBoxDB(f, width=80, state='readonly')
        e.ds_key = 'cd_ean_produto'
        e.pack(side=tk.LEFT, pady=2)
       
        s = select([products_gtin_t.c.cd_ean_produto,
                    products_gtin_t.c.ds_produto]).\
                    order_by(products_gtin_t.c.ds_produto)
        result = self.conn.execute(s)
        e.fill_list(result.fetchall())
        
        gtin = DBField(field_name='cd_ean_ajuste', 
                                 comparison_operator = '=', 
                                 label='cd_ean_ajuste', 
                                 width=5, 
                                 type_widget=tk.Entry)
        self.add_widget(gtin, e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Manual.:', width=10,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = ChkButton(f, width=1, anchor="w")
        e.pack(side=tk.LEFT, pady=2)
        
        manual = DBField(field_name='manual', 
                         comparison_operator = '=', 
                         label='Manual.', 
                         width=5, 
                         type_widget=ChkButton)
        self.add_widget(manual, e)
        
        if self.state == self.STATE_UPDATE:
            data = self.get_form_dbdata(self.data_keys) 
            self.set_form_dbdata(data)


    def update(self):
        '''
            Atualiza o banco de dados com os dados do form
        '''   
        try:
            if self.state == self.STATE_INSERT:
                result = self.check_form_for_update(insert=True)
            else:
                result = self.check_form_for_update(insert=False)            
            if not result[0]:
                try:
                    transaction = self.conn.begin()
                    if self.state == self.STATE_INSERT:
                        return self.insert()
                    form_data = self.convert_data_to_bd(self.get_form_data())
                    form_keys = self.get_form_keys()
                    updt = self.data_table.update()
                    for key in self.data_keys:
                        updt = updt.where(self.data_table.c[key] == self.data_keys[key])
                    updt = updt.values(**form_data)                
                    self.conn.execute(updt)
                    updt =  self.produtos_servicos_t.update()
                    updt = updt.values(cd_ean_prod_serv = form_data['cd_ean_ajuste'] )
                    updt = updt.where(and_( self.produtos_servicos_t.c['cnpj'] == self.data_keys['cnpj'], 
                                            self.produtos_servicos_t.c['cd_prod_serv'] == self.data_keys['cd_prod_serv_ajuste']))
                    self.conn.execute(updt)
                    transaction.commit() 
                    for key in form_keys:
                        self.data_keys[key] = form_keys[key]
                except Exception as e:
                    transaction.rollback()
                    print(e)
                    return -1
                return 0
            return -1
        except Exception as e:
            print(e)
            return -1

class FrameProductEan(tk.Frame):
    
    def __init__(self, master, db_connection, product_code,  **options):
        
        super().__init__(master, **options)
        self.product_code = product_code
        self.controls = {}
        self.db_connection = db_connection
        self.make_controls()
 
#        self.controls['cd_ncm_01'].fill_list(nfce_db.get_ncm_01(self.db_connection))
#        self.controls['cd_ncm_02'].fill_list(nfce_db.get_ncm_02(self.db_connection))
#        self.controls['cd_ncm_05'].fill_list(nfce_db.get_ncm_05(self.db_connection))
        self.pack()
        

    def make_controls(self, **options):

        if not options:
            options['sticky'] = 'w'
            options['padx'] = 2
            options['pady'] = 2
        
        row = 0         
        tk.Label(self, text='Ean:', anchor='e').grid(row=row, column=0)        
        e = nfce_gui.make_widget(self, tk.Entry, 'cd_ean','','LIKE',  width=15)
        self.controls[e.index_name] = e
        e.grid(row=row, column=1, sticky=options['sticky'], padx=options['padx'], pady=options['pady'])
        
        #row += 1
        tk.Label(self, text='Desc. Prod.: ', anchor='e').grid(row=row, column=2)        
        e = nfce_gui.make_widget(self, tk.Entry, 'ds_produto','','LIKE', width=60)
        self.controls[e.index_name] = e
        e.grid(row=row, column=3, sticky=options['sticky'], padx=options['padx'], pady=options['pady'])
        
        row += 1
        tk.Label(self, text='Ncm 01:', anchor='e').grid(row=row, column=0)        
        #e = nfce_gui.make_widget(self, nfce_gui.ComboBoxDB, 'cd_ncm_01' , '', '=', state='readonly')
        e = nfce_gui.make_widget(self, tk.Label, 'ds_ncm_01' , '', '=', relief=tk.SUNKEN, wraplength=407, anchor="w", justify=tk.LEFT, width=50)
        self.controls[e.index_name] = e
        e.grid(row=row, column=1, sticky=options['sticky'], padx=options['padx'], pady=options['pady']) 
        
#        row += 1
#        tk.Label(self, text='Ncm 02:', anchor='e').grid(row=row, column=0)        
#        e = nfce_gui.make_widget(self, nfce_gui.ComboBoxDB, 'cd_ncm_02' , '', '=', state='readonly', width=70)
#        self.controls[e.index_name] = e
#        e.grid(row=row, column=1, columnspan=3, sticky=options['sticky'], padx=options['padx'], pady=options['pady']) 
        row += 1
        tk.Label(self, text='Ncm 02:', anchor='e').grid(row=row, column=0)        
        e = nfce_gui.make_widget(self, tk.Label, 'ds_ncm_02' , '', '=', relief=tk.SUNKEN, wraplength=570, anchor="w", justify=tk.LEFT, width=70)
        self.controls[e.index_name] = e
        e.grid(row=row, column=1, columnspan=3, sticky=options['sticky'], padx=options['padx'], pady=options['pady'])     
        
        row += 1
        tk.Label(self, text='Ncm 03:', anchor='e').grid(row=row, column=0)        
        #e = nfce_gui.make_widget(self, nfce_gui.ComboBoxDB, 'cd_ncm_03' , '', '=', state='readonly', width=70)
        e = nfce_gui.make_widget(self, tk.Label, 'ds_ncm_03' , '', '=', relief=tk.SUNKEN, wraplength=570, anchor="w", justify=tk.LEFT, width=70)
        self.controls[e.index_name] = e
        e.grid(row=row, column=1, columnspan=3,  sticky=options['sticky'], padx=options['padx'], pady=options['pady']) 
        
        row += 1
        tk.Label(self, text='Ncm 04:', anchor='e').grid(row=row, column=0)        
        #e = nfce_gui.make_widget(self, nfce_gui.ComboBoxDB, 'cd_ncm_04' , '', '=', state='readonly', width=70)
        e = nfce_gui.make_widget(self, tk.Label, 'ds_ncm_04' , '', '=', relief=tk.SUNKEN, wraplength=570, anchor="w", justify=tk.LEFT, width=70) 
        self.controls[e.index_name] = e
        e.grid(row=row, column=1, columnspan=3,  sticky=options['sticky'], padx=options['padx'], pady=options['pady']) 
        
        row += 1
        tk.Label(self, text='Ncm 05:', anchor='e').grid(row=row, column=0)        
        #e = nfce_gui.make_widget(self, nfce_gui.ComboBoxDB, 'cd_ncm_05' , '', '=', state='readonly', width=70)
        e = nfce_gui.make_widget(self, tk.Label, 'ds_ncm_05' , '', '=', relief=tk.SUNKEN, wraplength=570, anchor="w", justify=tk.LEFT, width=70)
        self.controls[e.index_name] = e
        e.grid(row=row, column=1, columnspan=3,  sticky=options['sticky'], padx=options['padx'], pady=options['pady']) 
        
    
    def fill_controls(self):
        sql = 'select * from produtos_v where cd_ean = %s'
        row_data = self.db_connection.execute(sql, self.product_code).fetchone()
        for key in self.controls:            
            if row_data[key]:                
                if type(self.controls[key]) == tk.Entry:                    
                    self.controls[key].delete(0, tk.END)
                    self.controls[key].insert(0, row_data[key])
                elif type(self.controls[key]) == nfce_gui.ComboBoxDB:
                    self.controls[key].set_key(row_data[key])
                elif type(self.controls[key]) == tk.Label:
                    self.controls[key].config(text=row_data[key])


def open_product(master, conn, product_code):
    tl = tk.Toplevel(master)
    tl.title('Produto')
    f = FrameProductEan(tl, conn, product_code)
    #f.fill_controls(conn, product_code)
    f.fill_controls()
    f.pack()
    nfce_gui.open_modal(tl)
    

#def search_product(master):
#    
#    win = tk.Toplevel(master)
#    win.title('Consultar Produto')
#    win.geometry('830x380')
#    
#    f = FrameSearchProduct(win,master.conn)
#
#    
#    f.pack(fill = tk.X)
#    show_modal_win(win)


#def testeFormSimpleDialog():
#    
#    root = tk.Tk()
#    root.title('Produtos')
#    #root.bind('<Configure>', configure) 
#    #root.geometry('830x380')
#    
#    engine = nfce_db.get_engine_bd()    
#    conn = engine.connect()
#    
#    f = FrameSearchProduct(root,conn)
#    f.pack(fill = tk.X)
#    root.mainloop()

def make_gtin_window(Frame=FormGtin, title='Gtin',keys={'cd_ean_produto':'7894321218526'}, state=1):
    root = tk.Tk()
    root.conn = engine.connect()
    root.title(title)
    if Frame:
        f = Frame(root, root.conn, keys, state)
        f.pack(fill = tk.X)
        root.resizable(False, False)
        root.mainloop()


def make_product_adjust_window( master = None,
                                frame=FrameProductAdjust,
                                title='Ajuste Produto',
                                keys={'cnpj':'00063960004864', 
                                      'cd_prod_serv_ajuste':'00000250781'},
                                state=0):
    if master:
        root = tk.Toplevel(master)
        root.conn = master.conn
    else:
        root = tk.Tk()
        root.conn = engine.connect()
    root.title(title)
    if frame:
        f = frame(root, root.conn,keys, state)
        f.pack(fill = tk.X)
        root.resizable(False, False)
        root.mainloop()


def make_product_grouping_window(master=None):
    make_window(master=master, Frame=FrameProductGrouping, title='Agrupamento')
    
def make_class_product_window(master=None):
    make_window(master=master, Frame=FrameClassProduct, title='Classe  Produto')
    
def make_window(master=None, Frame=None, title=None, resizable=True):
    if master:
        root = tk.Toplevel(master)
        root.conn = master.conn
    else:
        root = tk.Tk()
        root.conn = engine.connect()
    if title:
        root.title(title)
    if Frame:
        f = Frame(root, root.conn)
        f.pack(fill = tk.X)
        if not resizable:
            root.resizable(False, False)
        if master:
            show_modal_win(root)
        else:
            root.mainloop()
    return

def make_product_gtin_product_window(master=None, conn=None):
    make_window(master=master, Frame=FrameProductGtimProduct, title='Produtos x Produtos Gtin')

def make_product_sem_gtin_product_window(master=None, conn=None):
    make_window(master=master, Frame=FrameProductSemGtimProduct, title='Produtos x Produtos Sem Gtin')

def make_product_window(master=None):
    make_window(master=master, Frame=FrameProduct, title='Produtos')   
def make_search_products_window(master=None):
    make_window(master=master, Frame=FrameSearchProducts, title='Pesquisa Produtos')
    
def main():    
#    make_product_gtin_product_window()
#    make_product_grouping_window()
#    make_gtin_window()
    make_product_adjust_window()
#    make_product_window()
    

if __name__ == '__main__':
    
    #make_class_product_window()
    #make_product_gtin_product_window()
    #make_product_sem_gtin_product_window()
    main()
    

