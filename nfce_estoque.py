import datetime
import tkinter as tk
from tkinter.messagebox import showwarning
from interfaces_graficas.ScrolledWindow import ScrolledWindow
from util import string_to_date, formatar_data, is_valid_date
from nfce_models import engine, products_exit_t, products_exit_v, products_gtin_t, classe_produto_t
from interfaces_graficas import show_modal_win
from sqlalchemy.sql import select, sqltypes
from collections import OrderedDict

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
        self.ds_produto = tk.Entry(f, width=50)
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
                                row=row, column=1, width=30)
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


class FrameGrid01(tk.Frame):
    
    
    def __init__(self, master, connection, data_table=None,grid_table=None, **args):
        
        super().__init__(master, **args)
        self.controls = OrderedDict()
        self.conn = connection
        self.last_clicked_row = -1
        self.last_inserted_row = -1
        self.data_table = data_table
        if grid_table:
            self.grid_table = grid_table
        else:
            self.grid_table = data_table
        self.grid_select_stm = select(self.grid_table.c)
        
        self.form = tk.Frame(self)
        self.form.pack(fill=tk.X)
        
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
        


    def add_widget(self, name_widget, widget):
        self.controls[name_widget] = widget


    def get_widget(self, name_widget):
        return name_widget
    

    def get_form_data(self):
        datum = {}
        for key in self.controls.keys():
            form_widget = self.controls[key]
            if type(form_widget) == tk.Entry:
                datum[key] = form_widget.get().strip()
            elif type(form_widget) == tk.Label:
                datum[key] = form_widget['text'].strip()
        return(datum)


    def get_form_keys(self):
        datum = {}
        for key in self.controls.keys():
            column = self.data_table.c[key]
            widget = self.controls[key]
            if column.primary_key:
                datum[key]  = self.get_widget_data(widget)
        return datum

    def order_by(self, list_order):
        self.grid_select_stm = self.grid_select_stm.order_by(list_order)


    def get_grid_dbdata(self):
        result_proxy = self.conn.execute(self.grid_select_stm) 
        self.fill_grid(result_proxy.fetchall())

   
    def close(self):
        '''Fecha a janela'''
        self.master.destroy()
    
    
    def row_click(self, event):
        '''
            Disparado ao clicar no grid
            Pega os dados do grid e põe no form
        '''
        self.last_clicked_row = event.widget.grid_info()['row']     #pega o numero da linha clicada
        self.set_form_data(self.get_grid_data(int(event.widget.grid_info()['row'])))


    def new_product(self):
        '''
            Limpa o form e ajusta a última linha clicada para -1
        '''
        self.last_clicked_row = -1
        self.clear_form()


    def clear_form(self):
        for key in self.controls.keys():
            form_widget = self.controls[key]
            self.set_widget_data(form_widget, '')


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


    def convert_data_to_bd(self, data):
        datum={}
        for key in data.keys():
            col = self.data_table.c.get(key)
            if col.type._type_affinity in [sqltypes.Date, sqltypes.DateTime]:
                if not is_valid_date(data[key]):
                    datum[key] = None
                datum[key] = string_to_date(data[key])
            elif col.type._type_affinity in [sqltypes.Integer]:
                try: 
                    datum[key] = int(data[key])
                except ValueError:
                    datum[key] = None
            elif col.type._type_affinity in [sqltypes.Float, sqltypes.Numeric]:
                datum[key] = data[key]
            elif col.type._type_affinity in [sqltypes.String]:
                datum[key] = data[key]
            else:
                raise(Exception(f'Tipo do campo tratado: {col.type._type_affinity}'))
        return datum


    def check_form_for_update(self, insert=False):
        
        for key in self.controls.keys():
            col = self.data_table.c.get(key)
            data = self.get_widget_data(self.controls[key])
            
            if (not col.nullable and not data and not insert) or (insert and not col.nullable and not data and not col.autoincrement):
                return (key, 'null')
            elif col.type._type_affinity in [sqltypes.Date, sqltypes.DateTime]:
                if not is_valid_date(data):
                    return(key, 'invalid_data')
            elif col.type._type_affinity in [sqltypes.Integer]:
                try: 
                    int(data)
                except ValueError:
                    return(key, 'invalid_data')
            elif col.type._type_affinity in [sqltypes.Float, sqltypes.Numeric]:
                print(key, 'numérico(float)')
            elif col.type._type_affinity in [sqltypes.String]:
                print(key, 'string')
            else:
                raise(Exception(f'Tipo do campo tratado: {col.type._type_affinity}'))
        return('', '')


    def insert(self):
        return False


    def update(self):
        '''
            Atualiza o banco de dados com os dados do form
        '''   
        try:
            if self.last_clicked_row == -1:
                result = self.check_form_for_update(insert=True)
            else:
                result = self.check_form_for_update(insert=False)
            
            if not result[0]:
                if self.last_clicked_row == -1:
                    return
                form_data = self.convert_data_to_bd(self.get_form_data())                
                form_keys = self.convert_data_to_bd(self.get_form_keys())
                updt = self.data_table.update()
                for key in form_keys:
                    updt = updt.where(self.data_table.c[key] == form_keys[key])
                updt = updt.values(**form_data)
                self.conn.execute(updt)
                
                return 0
        except Exception as e:
            print(e)
            return -1
            
            if self.last_clicked_row == -1:
                self.insert()
            else:
                pass
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
        '''
            Atualiza o banco de dados com os dados do form e atualiza o grid.
        '''
        if not self.update():   #atuliza o banco de dados com os dados do form
            #self.set_grid_line()        #atualiza o grid
            self.set_grid_line_data()


    def set_form_data(self, datum):
        for key in self.controls.keys():
            data = datum[key]
            form_widget = self.controls[key]
            self.set_widget_data(form_widget, data)


    def get_grid_data(self, row):
        '''
            Pega os dados da linha clicada e coloca num dicionário
            parametros
                (row:int) Linha do grid que se vai obter os dados
            retorno
                (datum:dicti0nary) Dados obtidos da linha na forma 'campo:valor'            
        '''
        datum = {}
        for widget in self.scrolled_frame.grid_slaves(): #loop nos widget do grid            
            if int(widget.grid_info()['row']) == row:       #se o widget pertencer a linha pega os dados
                #self.set_form_widget(widget)
                datum[widget.name] = self.get_widget_data(widget)
        return datum


    def get_widget_data(self, widget):
        if type(widget) == tk.Entry:
            return widget.get()


    def set_widget_data(self, widget, data):
        if type(widget) == tk.Entry:
            if widget['state'] == 'readonly':
                readonly = True
                widget.config(state=tk.NORMAL)
            else:
                readonly = False
            widget.delete(0, tk.END)
            widget.insert(0, data)
            if readonly:
                widget.config(state='readonly')
            return 0
        elif type(widget) == tk.Label:
                widget.config(text=data)
                return 0
        else:
            return -1
        
    def set_grid_widget(self, widget, value_widget): 
        try:
            widget.config(state=tk.NORMAL)
            widget.delete(0, tk.END)
            widget.insert(0, value_widget)
            widget.config(state='readonly')
        except Exception as e:
            raise e


    def set_form_widget(self, widget):
        form_widget = self.controls[widget.name]
        if type(form_widget) == tk.Entry:
            if form_widget['state'] == 'readonly':
                readonly = True
                form_widget.config(state=tk.NORMAL)
            else:
                readonly = False
            form_widget.delete(0, tk.END)
            form_widget.insert(0, widget.get())
            if readonly:
                form_widget.config(state='readonly')

    def set_grid_line_data(self):
        data = self.get_form_data()
        for widget in self.scrolled_frame.grid_slaves():
            if int(widget.grid_info()['row']) == self.last_clicked_row:
                self.set_widget_data(widget, data[widget.name])
            
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
        '''
            Criar os widgets do grid a partir dos controles do form(self.controls) e já preeche os dados nele
        '''
        for col, key in enumerate(self.controls.keys()):
            self.create_row_widget(widget_class=tk.Entry, widget_name=key, value=data_row[key], 
                                    row=row, column=col, width=self.controls[key]['width'])


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
        ''' Limpa o grid'''
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) > 1:
                
                widget.grid_forget()

class FrameClassProduct(FrameGrid01):
    def __init__(self,  master, connection,  **args):
        
        FrameGrid01.__init__(self, master, connection,classe_produto_t, **args)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Id:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=6, state='readonly')
        e.pack(side=tk.LEFT, pady=2)
        self.add_widget('id_classe_produto', e)
        
        f = tk.Frame(self.form)
        f.pack(fill=tk.X)        
        tk.Label(f, text='Classe:', width=7,  anchor='e').pack(side=tk.LEFT , anchor='w')
        e = tk.Entry(f, width=50)
        e.pack(side=tk.LEFT, pady=2)
        self.add_widget('ds_classe_produto', e)
        
        self.order_by(self.grid_table.c.ds_classe_produto)
        self.get_grid_dbdata()
        
#    def get_data(self):
#        stm = select([classe_produto_t.c.id_classe_produto, 
#                     classe_produto_t.c.ds_classe_produto]).order_by(classe_produto_t.c.ds_classe_produto) #.where(products_gtin_t.c.cd_ean_produto.like('560%'))
#        result_proxy = self.conn.execute(stm) 
#        self.fill_grid(result_proxy.fetchall())
        
def make_class_product_window(master=None):
    make_window(master=master, Frame=FrameClassProduct, title='Classe  Produto')
    
def make_product_exit_window(master=None):
    make_window(master=master, Frame=FrameProductExit, title='Saída Produtos')

def make_product_gtin_window(master=None):
    make_window(master=master, Frame=FrameProductGtin, title='Produtos Gtin')

def make_window(master=None, Frame=None, title=None):
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
        if master:
            show_modal_win(root)
        else:
            root.mainloop()
    return



def main():
    make_class_product_window()
#    make_product_exit_window()
#    make_product_gtin_window()

if __name__ == '__main__':
    main()
