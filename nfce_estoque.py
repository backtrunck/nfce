import datetime
import tkinter as tk
from tkinter.messagebox import showwarning
from interfaces_graficas.ScrolledWindow import ScrolledWindow
from util import string_to_date, formatar_data, is_valid_date
from interfaces_graficas.db import FrameGridSearch, DBField, ComboBoxDB
from nfce_models import engine, \
                        products_exit_t,\
                        products_exit_v,\
                        products_gtin_t,\
                        products_gtin_products_t,\
                        stock_v,\
                        products_v,\
                        classe_produto_t,\
                        agrupamento_produto_t, \
                        nota_fiscal_produtos_v
from nfce_db import PRODUCT_NO_CLASSIFIED
from nfce_gui import dlg_itens_invoice
from interfaces_graficas import show_modal_win
from sqlalchemy.sql import select, and_
from fields import Field
#from collections import namedtuple






class FrameProductExit(tk.Frame):    
    
    def __init__(self, master, connection,  **args):
        
        super().__init__(master, **args)
        self.controls = []
        self.conn = connection
        self.last_clicked_row = -1
        self.last_inserted_row = -1
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Id:', width=11,  anchor='e').pack(side=tk.LEFT , anchor='w')
        self.id_saida_produtos = tk.Entry(f, width=11, state='readonly')
        self.id_saida_produtos.pack(side=tk.LEFT, pady=2)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Data Saída:', width=11,  anchor='e').pack(side=tk.LEFT , anchor='w')
        self.dt_saida = tk.Entry(f, width=10)
        self.dt_saida.focus_set()
        self.dt_saida.pack(side=tk.LEFT, pady=2)
        
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='Gtin:', width=11,  anchor='e').pack(side=tk.LEFT, anchor='w')
        self.cd_ean_saida = tk.Entry(f, width=13)
        self.cd_ean_saida.pack(side=tk.LEFT, pady=2)
        #self.ds_produto = tk.Entry(f, width=50, state='readonly')
        self.ds_produto = tk.Label(f, width=50, relief=tk.SUNKEN)
        self.ds_produto.pack(side=tk.LEFT, pady=2, padx=2) 
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='Quant:', width=11,  anchor='e').pack(side=tk.LEFT, anchor='w')
        self.qt_saida = tk.Entry(f, width=5)
        self.qt_saida.pack(side=tk.LEFT, pady=2)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Data Criação:', width=11,  anchor='e').pack(side=tk.LEFT , anchor='w')
        self.dt_criacao = tk.Label(f, width=11, relief=tk.SUNKEN)         
        self.dt_criacao.pack(side=tk.LEFT, pady=2)
        
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
        
        self.pack()
        
        self.make_header()
#        sql = 'select id_produto,ds_produto,classificado FROM produtos order by ds_produto'
        stm = select([products_exit_v.c.id_saida_produtos, 
                     products_exit_v.c.dt_saida, 
                     products_exit_v.c.qt_saida, 
                     products_exit_v.c.dt_criacao, 
                     products_exit_v.c.ds_produto, 
                     products_exit_v.c.cd_ean_saida])
        result_proxy = self.conn.execute(stm) 
        self.fill_grid(result_proxy.fetchall())   


    def close(self):
        self.master.destroy()
    
    
    def row_click(self, event):
        self.last_clicked_row = event.widget.grid_info()['row']
        self.get_grid_line(int(event.widget.grid_info()['row']))


    def new_product(self):
        
        self.last_clicked_row = -1
        self.id_saida_produtos.config(state=tk.NORMAL)
        self.id_saida_produtos.delete(0, tk.END)
        self.id_saida_produtos.config(state='readonly')
        
        self.dt_saida.delete(0, tk.END)
        self.dt_saida.focus_set()
        
        self.cd_ean_saida.delete(0, tk.END)
        
        self.ds_produto.config(text = '', anchor='w')
        
        self.qt_saida.delete(0, tk.END)
        
        self.dt_criacao.config(text='', anchor='w')  


    def get_ds_product(self, cd_ean):
        if not cd_ean or len(cd_ean) != 13:
            return ''        
        try:
            stm = select([products_gtin_t.c.ds_produto]).where(products_gtin_t.c.cd_ean_produto == cd_ean)
            result_proxy = self.conn.execute(stm) 
        except Exception as e:
            showwarning('Saídas','Erro "{}" ao Verificar Gtin {}'.format(e, cd_ean))
            return ''
        if result_proxy.rowcount == 1:
            row = result_proxy.fetchone()
            return row['ds_produto']
        return ''


    def update_product(self):
        try:
            insert = False
            if not self.id_saida_produtos.get():
                insert = True
            if not self.dt_saida.get() or not self.qt_saida.get() or not self.cd_ean_saida.get():
                showwarning('Saídas','A data de saída, a quantidade e o código do produto devem ser informados')
                return -1
            
            if not is_valid_date(self.dt_saida.get()):
                showwarning('Saídas','Data inválida')
                return -1
            dt_saida = string_to_date(self.dt_saida.get())
            
            ds_produto = self.get_ds_product(self.cd_ean_saida.get())
            self.ds_produto.config(text = ds_produto, anchor='w')
            if not ds_produto:
                showwarning('Saídas','Código Gtin não Encontrado')
                return -1           
            
            try: 
                qt_saida = int(self.qt_saida.get())
            except ValueError:
                showwarning('Saídas','Quantidade inválida')
                return -1
            
            if insert:
                ins = products_exit_t.insert().values(cd_ean_saida=self.cd_ean_saida.get(),\
                                                     dt_saida=dt_saida, 
                                                     qt_saida=qt_saida)
                result = self.conn.execute(ins)
                self.last_inserted_row +=1
                self.fill_row(self.last_inserted_row, 
                              {
                               'id_saida_produtos':result.inserted_primary_key[0],
                               'ds_produto':ds_produto,
                               'qt_saida':qt_saida,
                               'dt_saida':dt_saida,
                               'dt_criacao':datetime.datetime.now(), 
                               'cd_ean_saida':self.cd_ean_saida.get()})
                self.last_clicked_row = self.last_inserted_row
                self.id_saida_produtos.config(state=tk.NORMAL)
                self.id_saida_produtos.delete(0, tk.END)
                self.id_saida_produtos.insert(0, result.inserted_primary_key[0])
                self.id_saida_produtos.config(state='readonly')
                
                self.dt_criacao.config(text=formatar_data(datetime.datetime.now() ,'%d/%m/%Y'), anchor='w')  
                return 0
            else:
                upd = products_exit_t.update().where(\
                            products_exit_t.c.id_saida_produtos==self.id_saida_produtos.get()).\
                            values(cd_ean_saida=self.cd_ean_saida.get(),\
                                    dt_saida=dt_saida, 
                                    qt_saida=qt_saida)
                self.conn.execute(upd)
                return 0
        except Exception as e:
            showwarning('Inserir Produto',e)
            return -1


    def update_row(self):
        if not self.update_product():
            self.set_grid_line()


    def get_grid_line(self, row):
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) == row:
                if widget.name == 'id_saida_produtos':
                    self.id_saida_produtos.config(state=tk.NORMAL)
                    self.id_saida_produtos.delete(0, tk.END)
                    self.id_saida_produtos.insert(0, widget.get())
                    self.id_saida_produtos.config(state='readonly')
                elif widget.name == 'dt_saida':
                    self.dt_saida.delete(0, tk.END)
                    self.dt_saida.insert(0, widget.get())
                elif widget.name == 'dt_criacao':
                    self.dt_criacao.config(text=widget.get(), anchor='w') 
                elif widget.name == 'qt_saida':
                    self.qt_saida.delete(0, tk.END)
                    self.qt_saida.insert(0, widget.get())
                elif widget.name == 'ds_produto':
                    self.ds_produto.config(text = widget.get(), anchor='w')
                elif widget.name == 'cd_ean_saida':                    
                    self.cd_ean_saida.delete(0, tk.END)
                    self.cd_ean_saida.insert(0, widget.get())


    def set_grid_line(self):
        if self.last_clicked_row == -1:
            return 
        for widget in self.scrolled_frame.grid_slaves():            
            if int(widget.grid_info()['row']) == self.last_clicked_row:
                if widget.name == 'ds_produto':
                    widget.config(state=tk.NORMAL)
                    widget.delete(0, tk.END)
                    widget.insert(0, self.ds_produto['text'])
                    widget.config(state='readonly')
                elif widget.name == 'id_saida_produtos':
                    widget.config(state=tk.NORMAL)
                    widget.delete(0, tk.END)
                    widget.insert(0, self.id_saida_produtos.get())
                    widget.config(state='readonly')                    
                elif widget.name == 'qt_saida':
                    widget.config(state=tk.NORMAL)
                    widget.delete(0, tk.END)
                    widget.insert(0, self.qt_saida.get())
                    widget.config(state='readonly')
                elif widget.name == 'dt_saida':
                    widget.config(state=tk.NORMAL)
                    widget.delete(0, tk.END)
                    widget.insert(0, self.dt_saida.get())
                    widget.config(state='readonly')
                elif widget.name == 'dt_criacao':
                    widget.config(state=tk.NORMAL)
                    widget.delete(0, tk.END)
                    widget.insert(0, self.dt_criacao['text'])
                    widget.config(state='readonly')
                elif widget.name == 'cd_ean_saida':
                    widget.config(state=tk.NORMAL)
                    widget.delete(0, tk.END)
                    widget.insert(0, self.cd_ean_saida.get())
                    widget.config(state='readonly')
                    
                   


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

    def str_to_date(self, str_date):
        dt = string_to_date(str_date)        
        return formatar_data(dt) 
        
    def fill_row(self, row, data_row):
        e = tk.Entry(self.scrolled_frame,width=7, readonlybackground='white')
        e.grid(row = row,column=0)
        e.insert(0, data_row['id_saida_produtos'])
        e.name = 'id_saida_produtos'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        #Button-1
        e.config(state='readonly')
                                                
        e = tk.Entry(self.scrolled_frame, width=10, readonlybackground='white')
        e.grid(row=row, column=1)
        #e.insert(0, data_row['dt_saida'])
        e.insert(0,formatar_data(data_row['dt_saida'] ,'%d/%m/%Y'))
        e.name = 'dt_saida'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
        
        e = tk.Entry(self.scrolled_frame, width=14, readonlybackground='white')
        e.grid(row=row, column=2)
        e.insert(0, data_row['cd_ean_saida'])
        e.name = 'cd_ean_saida'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
        
        e = tk.Entry(self.scrolled_frame, width=30, readonlybackground='white')
        e.grid(row=row, column=3)
        e.insert(0, data_row['ds_produto'])
        e.name = 'ds_produto'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
        
        e = tk.Entry(self.scrolled_frame, width=5, readonlybackground='white')
        e.grid(row=row, column=4)
        e.insert(0, data_row['qt_saida'])
        e.name = 'qt_saida'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')
        
        e = tk.Entry(self.scrolled_frame, width=10, readonlybackground='white')
        e.grid(row=row, column=5)
        e.insert(0,formatar_data(data_row['dt_criacao'] ,'%d/%m/%Y'))
        e.name = 'dt_criacao'
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')


    def make_header(self):
        
        e = tk.Entry(self.scrolled_frame, width=7, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=0, sticky=tk.W)
        e.insert(0,'id')
        
        e = tk.Entry(self.scrolled_frame, width=11, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=1, sticky=tk.W)
        e.insert(0,'Data Saída')
        
        e = tk.Entry(self.scrolled_frame, width=14, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=2, sticky=tk.W)
        e.insert(0,'Gtin')
        
        e = tk.Entry(self.scrolled_frame, width=30, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=3, sticky=tk.W)
        e.insert(0,'Produto.')
        
        e = tk.Entry(self.scrolled_frame, width=5, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=4, sticky=tk.W)
        e.insert(0,'Quant.')
        
        e = tk.Entry(self.scrolled_frame, width=11, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=5, sticky=tk.W)
        e.insert(0,'Data Criação')
        
        
    def clear_grid(self): 
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) > 1:
                
                widget.grid_forget()

class FrameProductGtin(tk.Frame):
    
    
    def __init__(self, master, connection,  **args):
        
        super().__init__(master, **args)
        self.controls = []
        self.conn = connection
        self.last_clicked_row = -1
        self.last_inserted_row = -1
        
        f = tk.Frame(self)
        f.pack(fill=tk.X) 
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='Gtin:', width=11,  anchor='e').pack(side=tk.LEFT, anchor='w')
        self.cd_ean_produto = tk.Entry(f, width=13, state='readonly')
        
        self.cd_ean_produto.pack(side=tk.LEFT, pady=2)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='Descrição:', width=11,  anchor='e').pack(side=tk.LEFT, anchor='w')
        self.ds_produto = tk.Entry(f, width=60)
        self.ds_produto.pack(side=tk.LEFT, pady=2, padx=2) 
        self.ds_produto.focus_set()
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='NCM:', width=11,  anchor='e').pack(side=tk.LEFT, anchor='w')
        self.cd_ncm_produto = tk.Entry(f, width=8)
        self.cd_ncm_produto.pack(side=tk.LEFT, pady=2, padx=2)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='Gtin Interno:', width=11,  anchor='e').pack(side=tk.LEFT, anchor='w')
        self.cd_ean_interno = tk.Entry(f, width=13)
        self.cd_ean_interno.pack(side=tk.LEFT, pady=2)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Label(f, text='Qt. Embalag.:', width=11,  anchor='e').pack(side=tk.LEFT, anchor='w')
        self.qt_item_embalagem = tk.Entry(f, width=5)
        self.qt_item_embalagem.pack(side=tk.LEFT, pady=2)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Data Criação:', width=11,  anchor='e').pack(side=tk.LEFT , anchor='w')
        self.dt_criacao = tk.Label(f, width=11, relief=tk.SUNKEN)
        self.dt_criacao.pack(side=tk.LEFT, pady=2)
        
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
        
        self.pack()
        
        self.make_header()
        
        stm = select([products_gtin_t.c.cd_ean_produto, 
                     products_gtin_t.c.ds_produto, 
                     products_gtin_t.c.cd_ncm_produto, 
                     products_gtin_t.c.dt_criacao, 
                     products_gtin_t.c.cd_ean_interno, 
                     products_gtin_t.c.qt_item_embalagem]).order_by(products_gtin_t.c.ds_produto) #.where(products_gtin_t.c.cd_ean_produto.like('560%'))
        result_proxy = self.conn.execute(stm) 
        self.fill_grid(result_proxy.fetchall())   


    def close(self):
        self.master.destroy()
    
    
    def row_click(self, event):
        self.last_clicked_row = event.widget.grid_info()['row']
        self.get_grid_line(int(event.widget.grid_info()['row']))


    def new_product(self):
        
        self.last_clicked_row = -1
        self.cd_ean_produto.config(state=tk.NORMAL)
        self.cd_ean_produto.delete(0, tk.END)
        
        self.ds_produto.delete(0, tk.END)
        self.ds_produto.focus_set()
        
        self.cd_ean_interno.delete(0, tk.END)
        self.cd_ncm_produto.delete(0, tk.END)
        self.qt_item_embalagem.delete(0, tk.END)
        
        self.dt_criacao.config(text = '', anchor='w')


    def get_ds_product(self, cd_ean):
        if not cd_ean or len(cd_ean) != 13:
            return ''        
        try:
            stm = select([products_gtin_t.c.ds_produto]).where(products_gtin_t.c.cd_ean_produto == cd_ean)
            result_proxy = self.conn.execute(stm) 
        except Exception as e:
            showwarning('Saídas','Erro "{}" ao Verificar Gtin {}'.format(e, cd_ean))
            return ''
        if result_proxy.rowcount == 1:
            row = result_proxy.fetchone()
            return row['ds_produto']
        return ''


    def update_product(self):
        try:
            insert = False
            if self.last_clicked_row == -1:
                insert = True                
            if not self.cd_ean_produto.get() or\
               not self.ds_produto.get() or\
               not self.cd_ean_interno.get() or \
               not self.cd_ncm_produto.get() or \
               not self.qt_item_embalagem.get():
                showwarning('Produto Gtin','O Gtin, descrição,Gtin Interno, NCM e Quantidade da embalagem devem ser informados')
                return -1
            
            try: 
                qt_saida = int(self.qt_item_embalagem.get())
            except ValueError:
                showwarning('Produto Gtin','Quantidade inválida')
                return -1
            
            if insert:
                try:
                    transaction = self.conn.begin()
                    ins = products_gtin_t.insert().values(cd_ean_produto=self.cd_ean_produto.get(),\
                                                          ds_produto=self.ds_produto.get(), 
                                                          cd_ean_interno=self.cd_ean_interno.get(), 
                                                          cd_ncm_produto=self.cd_ncm_produto.get(), 
                                                          qt_item_embalagem=qt_saida)
                    #result = self.conn.execute(ins)
                    self.conn.execute(ins)
                    self.last_inserted_row +=1
                    self.fill_row(self.last_inserted_row, 
                                  {
                                   'cd_ean_produto':self.cd_ean_produto.get(),
                                   'ds_produto':self.ds_produto.get(),
                                   'cd_ean_interno':self.cd_ean_interno.get(),
                                   'cd_ncm_produto':self.cd_ncm_produto.get(),
                                   'dt_criacao':datetime.datetime.now(), 
                                   'qt_item_embalagem':self.qt_item_embalagem.get()})
                    self.last_clicked_row = self.last_inserted_row
                    self.cd_ean_produto.config(state='readonly')                
                    self.dt_criacao.config(text=formatar_data(datetime.datetime.now() ,'%d/%m/%Y'), anchor='w')
                    ins = products_gtin_products_t.insert().values(cd_ean_produto=self.cd_ean_produto.get(), 
                                                                    id_produto = PRODUCT_NO_CLASSIFIED, 
                                                                    manual = 1)
                    self.conn.execute(ins)
                    transaction.commit()
                except Exception as e:
                    transaction.rollback()
                    showwarning('Inserir Produto',e)
                    return -1
                return 0
            else:
                upd = products_gtin_t.update().where(\
                            products_gtin_t.c.cd_ean_produto==self.cd_ean_produto.get()).\
                            values(cd_ean_interno=self.cd_ean_interno.get(),\
                                   ds_produto=self.ds_produto.get(), 
                                   cd_ncm_produto=self.cd_ncm_produto.get(), 
                                   qt_item_embalagem=qt_saida )
                self.conn.execute(upd)
                return 0
        except Exception as e:
            showwarning('Inserir Produto',e)
            return -1


    def update_row(self):
        if not self.update_product():
            self.set_grid_line()


    def get_grid_line(self, row):
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) == row:
                if widget.name == 'cd_ean_produto':
                    self.cd_ean_produto.config(state=tk.NORMAL)                    
                    self.cd_ean_produto.delete(0, tk.END)
                    self.cd_ean_produto.insert(0, widget.get())
                    self.cd_ean_produto.config(state='readonly')
                elif widget.name == 'ds_produto':
                    self.ds_produto.delete(0, tk.END)
                    self.ds_produto.insert(0, widget.get())
                elif widget.name == 'cd_ncm_produto':
                    self.cd_ncm_produto.delete(0, tk.END)
                    self.cd_ncm_produto.insert(0, widget.get())
                elif widget.name == 'cd_ean_interno':
                    self.cd_ean_interno.delete(0, tk.END)
                    self.cd_ean_interno.insert(0, widget.get())
                elif widget.name == 'dt_criacao':
                    self.dt_criacao.config(text=widget.get(), anchor='w')
                elif widget.name == 'qt_item_embalagem':
                    self.qt_item_embalagem.delete(0, tk.END)
                    self.qt_item_embalagem.insert(0, widget.get())

    def set_grid_widget(self, widget, value_widget): 
        try:
            widget.config(state=tk.NORMAL)
            widget.delete(0, tk.END)
            widget.insert(0, value_widget)
            widget.config(state='readonly')
        except Exception as e:
            raise e 


    def set_grid_line(self):
        try:
            if self.last_clicked_row == -1:
                return 
            for widget in self.scrolled_frame.grid_slaves():            
                if int(widget.grid_info()['row']) == self.last_clicked_row:
                    if widget.name == 'cd_ean_produto':
                        self.set_grid_widget(widget, self.cd_ean_produto.get())
                    elif widget.name == 'ds_produto':
                        self.set_grid_widget(widget, self.ds_produto.get())
                    elif widget.name == 'cd_ncm_produto':
                        self.set_grid_widget(widget, self.cd_ncm_produto.get())
                    elif widget.name == 'cd_ean_interno':
                        self.set_grid_widget(widget, self.cd_ean_interno.get())
                    elif widget.name == 'qt_item_embalagem':
                        self.set_grid_widget(widget, self.qt_item_embalagem.get())            
                    elif widget.name == 'dt_criacao':
                        self.set_grid_widget(widget, self.dt_criacao['text'])
        except Exception as e:
            raise e


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

    def str_to_date(self, str_date):
        dt = string_to_date(str_date)        
        return formatar_data(dt) 


    def create_row_widget(self, widget_class=None, widget_name='',value='', row=0, column=0, width=11, **kargs):
        e = widget_class(self.scrolled_frame,width=width, readonlybackground='white', **kargs)
        e.grid(row = row,column=column)
        if value is None:
            value = ''
        e.insert(0, value)
        e.name = widget_name
        e.bind("<Key>", lambda a: "break")
        e.bind('<ButtonRelease>', self.row_click)
        e.config(state='readonly')


    def fill_row(self, row, data_row):
        self.create_row_widget( widget_class=tk.Entry, widget_name='cd_ean_produto',value=data_row['cd_ean_produto'], 
                                row=row, column=0, width=13)
        self.create_row_widget( widget_class=tk.Entry, widget_name='ds_produto',value=data_row['ds_produto'], 
                                row=row, column=1, width=60)
        self.create_row_widget( widget_class=tk.Entry, widget_name='cd_ncm_produto',value=data_row['cd_ncm_produto'], 
                                row=row, column=2, width=8)
        self.create_row_widget( widget_class=tk.Entry, widget_name='cd_ean_interno',value=data_row['cd_ean_interno'], 
                                row=row, column=3, width=13)
        self.create_row_widget( widget_class=tk.Entry, widget_name='qt_item_embalagem',value=data_row['qt_item_embalagem'], 
                                row=row, column=4, width=5)
        self.create_row_widget( widget_class=tk.Entry, widget_name='dt_criacao',value=formatar_data(data_row['dt_criacao'] ,'%d/%m/%Y'), 
                                row=row, column=5, width=11)


    def make_header(self):
        
        e = tk.Entry(self.scrolled_frame, width=13, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=0, sticky=tk.W)
        e.insert(0,'Gtin')
        
        e = tk.Entry(self.scrolled_frame, width=30, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=1, sticky=tk.W)
        e.insert(0,'Descrição')
        
        e = tk.Entry(self.scrolled_frame, width=8, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=2, sticky=tk.W)
        e.insert(0,'NCM')
        
        e = tk.Entry(self.scrolled_frame, width=13, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=3, sticky=tk.W)
        e.insert(0,'Interno.')
        
        e = tk.Entry(self.scrolled_frame, width=5, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=4, sticky=tk.W)
        e.insert(0,'Quant.')
        
        e = tk.Entry(self.scrolled_frame, width=11, relief=tk.FLAT, background='#d9d9d9')
        e.grid(row=1, column=5, sticky=tk.W)
        e.insert(0,'Data Criação')
        
        
    def clear_grid(self): 
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) > 1:
                
                widget.grid_forget()

class FrameSearchStock(FrameGridSearch):
    def __init__(self, master, connection, **kwargs):
        super().__init__(master, connection, grid_table=stock_v, **kwargs)
        
        width_label = 12
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Agrupamento:', width=width_label,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = ComboBoxDB(f, width=40)
        e.pack(side=tk.LEFT, pady=2)
        product_group = DBField(field_name='id_agrupamento',
                        comparison_operator = Field.OP_EQUAL,
                        label='Agrupamento',
                        width=40,
                        type_widget=tk.Entry)
        self.add_widget(product_group, e)
        
        e.ds_key = 'ds_agrupamento'
        s = select([agrupamento_produto_t.c.id_agrupamento,
                    agrupamento_produto_t.c.ds_agrupamento]).\
                    order_by(agrupamento_produto_t.c.ds_agrupamento)
        result = self.conn.execute(s)
        e.fill_list(result.fetchall())
           
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Classe:', width=width_label,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = ComboBoxDB(f, width=40)
        e.pack(side=tk.LEFT, pady=2)
        product_class = DBField(field_name='id_classe_produto', 
                                 comparison_operator = Field.OP_EQUAL,
                                 label='Classe',
                                 width=40, 
                                 type_widget=tk.Entry)
        self.add_widget(product_class, e)
        
        e.ds_key = 'ds_classe_produto'
        s = select([classe_produto_t.c.id_classe_produto,
                    classe_produto_t.c.ds_classe_produto]).\
                    order_by(classe_produto_t.c.ds_classe_produto)
        result = self.conn.execute(s)
        e.fill_list(result.fetchall())
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Produto:', width=width_label,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = ComboBoxDB(f, width=40)
        e.pack(side=tk.LEFT, pady=2)
        product = DBField(field_name='id_produto', 
                                     comparison_operator = Field.OP_EQUAL,
                                    label='Produto',
                                    width=40, 
                                    type_widget=tk.Entry)        
        self.add_widget(product, e)
        
        e.ds_key = 'ds_produto'
        
        s = select([products_v.c.id_produto,
                    products_v.c.ds_produto]).\
                    order_by(products_v.c.ds_produto)
        result = self.conn.execute(s)
        e.fill_list(result.fetchall())
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Produto Gtin:', width=width_label,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=14)
        e.pack(side=tk.LEFT, pady=2)
        product_gtin = DBField(field_name='cd_gtin',
                                        comparison_operator = Field.OP_LIKE,
                                        label='Prod. Gtin',
                                        width=14, 
                                        type_widget=tk.Entry)        
        self.add_widget(product_gtin, e)
        
        
        self.add_widget_tool_bar(text='Detalhar', width = 10, command=self.row_detail)
        
        ds_gtin = DBField(field_name='ds_gtin',
                             comparison_operator = Field.OP_EQUAL, 
                             label='Produto Gtin',
                             width=50,
                             type_widget=tk.Entry)
        input = DBField(field_name='entrada',
                             comparison_operator = Field.OP_EQUAL, 
                             label='Entrada',
                             width=8,
                             type_widget=tk.Entry)
        output = DBField(field_name='saida',
                             comparison_operator = Field.OP_EQUAL, 
                             label='Saída',
                             width=8,
                             type_widget=tk.Entry)
        balance = DBField(field_name='saldo',
                             comparison_operator = Field.OP_EQUAL, 
                             label='Saldo',
                             width=8,
                             type_widget=tk.Entry)
        adjustment = DBField(field_name='ajuste',
                             comparison_operator = Field.OP_EQUAL, 
                             label='Ajuste',
                             width=8,
                             type_widget=tk.Entry)
        self.columns = [product_gtin, ds_gtin, input, output, adjustment, balance]
        self.scroll.set_header(self.columns)
               
    def row_detail(self):
        nu_nfce = self.get_grid_data(self.last_clicked_row)
        stm = select(nota_fiscal_produtos_v.c).where(and_(nota_fiscal_produtos_v.c['cd_uf'] == nu_nfce['cd_uf'], 
                                                     nota_fiscal_produtos_v.c['cd_modelo'] == nu_nfce['cd_modelo'], 
                                                     nota_fiscal_produtos_v.c['serie'] == nu_nfce['serie'], 
                                                     nota_fiscal_produtos_v.c['nu_nfce'] == nu_nfce['nu_nfce'], 
                                                     nota_fiscal_produtos_v.c['cnpj'] == nu_nfce['cnpj']))
        
        #dlg_itens_invoice
        result = self.conn.execute(stm).fetchall()
        #print(result)
        dlg_itens_invoice(result, self.conn)


def make_product_exit_window(master=None):
    make_window(master=master, Frame=FrameProductExit, title='Saída Produtos')

def make_product_gtin_window(master=None):
    make_window(master=master, Frame=FrameProductGtin, title='Produtos Gtin')

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

def make_class_search_stock_window(master=None):
    make_window(master=master, Frame=FrameSearchStock, title='Pesquisa Estoque', resizable=False)

def main():
    make_class_search_stock_window()
#    make_product_window()
#    make_class_search_invoice_window()
#    make_class_product_window()
#    make_product_exit_window()
#    make_product_gtin_window()

if __name__ == '__main__':
    main()
