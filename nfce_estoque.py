import datetime
import tkinter as tk
from tkinter.messagebox import showwarning, askokcancel
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
        
        self.frame_header = tk.Frame(self)
        self.frame_header.pack(fill=tk.X)
        
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        scroll = ScrolledWindow(f, canv_w=450, canv_h = 200, scroll_h = False)
        scroll.pack(pady=2)
        self.scrolled_frame = tk.Frame(scroll.scrollwindow)       #Frame que ficará dentro do ScrolledWindows
        self.scrolled_frame.grid(row = 0, column = 0)
        
        f = tk.Frame(self)
        f.pack(fill=tk.X)
        tk.Button(f, text='Fechar', width = 10, command=self.close).pack(side=tk.RIGHT, padx=2, pady=5)
        tk.Button(f, text='Salvar', width = 10, command=self.update).pack(side=tk.RIGHT, padx=2, pady=5)
        tk.Button(f, text='Apagar', width = 10, command=self.delete).pack(side=tk.RIGHT, padx=2, pady=5)
        tk.Button(f, text='Novo', width = 10, command=self.new).pack(side=tk.RIGHT, padx=2, pady=5)


    def add_widget(self, name_widget, widget):
        self.controls[name_widget] = widget

    
    def check_form_for_update(self, insert=False):
        '''
            Verifica se os dados do formulário estão aptos a serem salvos, conforme a configurção dos campos do banco de dados
        '''
        
        for key in self.controls.keys():
            col = self.data_table.c.get(key)
            data = self.get_widget_data(self.controls[key])
            
            if (not col.nullable and not data and not insert) or (insert and not col.nullable and not data and not col.autoincrement):
                return (key, 'null')
            elif col.type._type_affinity in [sqltypes.Date, sqltypes.DateTime]:
                if data:                    
                    if not is_valid_date(data):
                        return(key, 'invalid_data')
            elif col.type._type_affinity in [sqltypes.Integer]:
                if data:                    
                    try: 
                        int(data)
                    except ValueError:
                        return(key, 'invalid_data')
            elif col.type._type_affinity in [sqltypes.Float, sqltypes.Numeric]:
                if data:
                    pass
                print(key, 'numérico(float)')
            elif col.type._type_affinity in [sqltypes.String]:
                if not data:
                    pass
                print(key, 'string')
            else:
                raise(Exception(f'Tipo do campo tratado: {col.type._type_affinity}'))
        return('', '')


    def clear_form(self):
        for key in self.controls.keys():
            form_widget = self.controls[key]
            self.set_widget_data(form_widget, '')


    def clear_grid(self): 
        ''' Limpa o grid'''
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) > 1:
                
                widget.grid_forget()


    def clear_grid_line(self, row):
        qt_cols = len(self.controls.keys())
        for i, key in enumerate(reversed(self.controls.keys())):
            index = (self.last_inserted_row - (row))*len(self.controls.keys())-len(self.controls.keys())
            widget = self.scrolled_frame.grid_slaves()[index + (qt_cols + i)]
            self.set_widget_data(widget, '')


    def close(self):
        '''Fecha a janela'''
        self.master.destroy()
    

    def convert_data_to_bd(self, data):
        datum={}
        for key in data.keys():
            col = self.data_table.c.get(key)
            if col.type._type_affinity in [sqltypes.Date, sqltypes.DateTime]:
                if is_valid_date(data[key]):
                    datum[key] = string_to_date(data[key])
                else:
                    datum[key] = None
            elif col.type._type_affinity in [sqltypes.Integer]:
                try: 
                    datum[key] = int(data[key])
                except ValueError:
                    datum[key] = None
            elif col.type._type_affinity in [sqltypes.Float, sqltypes.Numeric]:
                try:
                    datum[key] = float(data[key])
                except ValueError:
                    datum[key] = None
            elif col.type._type_affinity in [sqltypes.String]:
                datum[key] = data[key]
            else:
                raise(Exception(f'Tipo do campo tratado: {col.type._type_affinity}'))
        return datum

    
    def create_row_header(self, header=[], **kargs):
        
        for col, key in enumerate(self.controls.keys()):
            try:
                value = header[col]
            except IndexError:
                value = key        
            e = tk.Label(self.frame_header,text=value, width=self.controls[key]['width'])
            e.grid(row = 0,column=col, sticky=tk.W)


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

    
    def delete(self):
        '''
            Apaga a linha atual do grid e a correspondente do banco de dados 
        '''
        if self.last_clicked_row != -1:                     #se tiver um linha atual
            if not askokcancel('Delete', 'Confirme a Operação'):
                return
            grid_keys = self.get_grid_keys(self.last_clicked_row)
            dlt = self.data_table.delete()
            for key in grid_keys:
                dlt = dlt.where(self.data_table.c[key] == grid_keys[key])
            self.conn.execute(dlt)
            self.forget_grid_line(self.last_clicked_row)            #apaga a linha do grid
            self.last_clicked_row = self.get_grid_next_line(self.last_clicked_row) #pega a próxima linha
            self.last_inserted_row -= 1                                #diminui quantidade de linhas
            datum = self.get_grid_data_3(self.last_clicked_row)     #pega os dados da linha atual do grid
            self.set_form_data(datum)                               #põe os dados atuais no formulário


    def forget_grid_line(self, row):
        '''
            Apaga a linha (row) do grid
        '''
        #pega os widgets da linha (row)
        widgets = [widget for widget in self.scrolled_frame.grid_slaves() if widget.grid_info()['row'] == row]
        for widget in widgets:
            widget.grid_forget()        #apaga o widget


    
    def insert(self):
        '''
            Insere os dados do formulário no banco de dados
        '''
        try:
            transaction = self.conn.begin()
            form_data = self.convert_data_to_bd(self.get_form_data())
            form_data = self.get_auto_increment_values(form_data)
            ins = classe_produto_t.insert().values(**form_data)
            self.conn.execute(ins)
            transaction.commit()
            self.last_inserted_row +=1           
            result = self.get_form_dbdata(form_data)
            self.fill_row(self.last_inserted_row, result)
            self.last_clicked_row = self.last_inserted_row
            self.set_form_data(self.get_grid_data(self.last_clicked_row))
        except Exception as e:
            print(f'Error: {e}')
            return -1
            
        return 0


    def fill_grid(self, data_rows):
        '''
            Preenche um grid a partir de um data_rows passado
        '''
        #limpa o grid
        self.clear_grid()
        
        #para cada linha retornada em data_rows
        for row, data_row in enumerate(data_rows, 1):
            self.fill_row(row, data_row)
        self.last_inserted_row = row


    def fill_row(self, row, data_row):
        '''
            Criar os widgets do grid a partir dos controles do form(self.controls) e já preeche os dados nele
        '''
        for col, key in enumerate(self.controls.keys()):
            self.create_row_widget(widget_class=tk.Entry, widget_name=key, value=data_row[key], 
                                    row=row, column=col, width=self.controls[key]['width'])


    def get_auto_increment_values(self, data):
        '''
            Obtem os dados dos campos autoincrement do formulário
        '''
        datum = {}
        for key in data.keys():
            if self.data_table.c.get(key).autoincrement == True:
                result = self.conn.execute(f'select auto_increment from information_schema.tables where table_name = "{self.data_table.name}" LOCK IN SHARE MODE ')
                datum[key] = result.fetchone()[0]
            else:
                datum[key] = data[key]
        return datum


    def get_form_data(self):
        '''
            Pega os dados dos widget do formulário
        '''
        datum = {}
        for key in self.controls.keys():
            form_widget = self.controls[key]
            datum[key] = self.get_widget_data(form_widget)
        return(datum)


    def get_form_keys(self):
        '''
            Obtém os dados dos campos do formulaŕio que são chaves primárias da tabela
        '''
        datum = {}
        for key in self.controls.keys():
            column = self.data_table.c[key]
            widget = self.controls[key]
            if column.primary_key:
                datum[key]  = self.get_widget_data(widget)
        return datum


    def get_form_dbdata(self, form_data):
        '''
            Obtem dados do banco de dados a partir dos dados das chaves primárias do formulário
            Parâmetros
                (form_data:dictionary) Dados de onde se vai retirar as chaves que vão filtrar os dados do banco de dados
            return
                (row_proxy) com os dados obtidos do banco de dados
        '''
        sel = select(self.data_table.c)            
        for key in form_data.keys():
            column = self.data_table.c[key]            
            if column.primary_key:
                sel = sel.where(self.data_table.c.get(key) == form_data[key])
        result = self.conn.execute(sel)
        return result.fetchone()


    def get_grid_data(self, row):
        '''
            Pega os dados da linha (row) passada como parâmetro e coloca num dicionário
            parametros
                (row:int) Linha do grid que se vai obter os dados
            retorno
                (datum:dictionary) Dados obtidos da linha na forma 'campo:valor'            
        '''
        datum = {}
        for widget in self.scrolled_frame.grid_slaves(): #loop nos widget do grid            
            if int(widget.grid_info()['row']) == row:       #se o widget pertencer a linha pega os dados
                datum[widget.name] = self.get_widget_data(widget)
        return datum
    
    def get_grid_data_3(self, row):
        '''
            Pega os dados da linha (row) passada como parâmetro e coloca num dicionário
            parametros
                (row:int) Linha do grid que se vai obter os dados
            retorno
                (widgets:dictionary) Dados obtidos da linha na forma 'campo:valor'            
        '''
        widgets = {widget.name:self.get_widget_data(widget) for widget in self.scrolled_frame.grid_slaves() if widget.grid_info()['row'] == row}
        return widgets


    def get_grid_data_2(self, row):
        datum = {}
        qt_cols = len(self.controls.keys())
        for i, key in enumerate(reversed(self.controls.keys())):            
            index = (self.last_inserted_row - (row))*len(self.controls.keys())-len(self.controls.keys())
            datum[key] = self.scrolled_frame.grid_slaves()[index + (qt_cols + i)].get()
        return datum


    def get_grid_dbdata(self):
        '''
            Obtem os dados do Banco de Dados e preenche o grid
        '''
        result_proxy = self.conn.execute(self.grid_select_stm) 
        self.fill_grid(result_proxy.fetchall())
    
    def get_grid_keys(self, row):
        '''
            Obtém os dados do grid que são chaves primárias da tabela
        '''
        data = self.get_grid_data_3(row)
        datum = {}
        for key in self.data_table.c.keys():
            column = self.data_table.c[key]
            if column.primary_key:
                datum[key]  = data[key]
        return datum

    def get_grid_next_line(self, row):
        '''
            Pega a proxima linha do grid após row, se não tiver, pega uma das primeiras linahs, caso não tenha 
            retorna uma lista vazia
        '''
        widgets = reversed(self.scrolled_frame.grid_slaves()) 
        if widgets:
            rows = [widget.grid_info()['row'] for widget in widgets if widget.grid_info()['row'] > row]
            if rows:
                return rows[0]
            rows = [widget.grid_info()['row'] for widget in self.scrolled_frame.grid_slaves() if widget.grid_info()['row'] < row]
            if rows:
                return rows[0]
        return -1


    def get_widget_data(self, widget):
        '''
            Pega o dado do widget
        '''
        if type(widget) == tk.Entry:
            return widget.get().strip()
        elif type(widget) == tk.Label:
           return widget['text'].strip()


    def new(self):
        '''
            Limpa o form e ajusta a última linha clicada para -1
        '''
        self.last_clicked_row = -1
        self.clear_form()


    def order_by(self, list_order):
        self.grid_select_stm = self.grid_select_stm.order_by(list_order)


    def row_click(self, event):
        '''
            Disparado ao clicar no grid
            Pega os dados do grid e põe no form
        '''
        self.last_clicked_row = event.widget.grid_info()['row']     #pega o numero da linha clicada
        self.set_form_data(self.get_grid_data_3(int(event.widget.grid_info()['row'])))

    
    def set_form_data(self, datum):
        for key in self.controls.keys():
            data = datum[key]
            form_widget = self.controls[key]
            self.set_widget_data(form_widget, data)


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


    def set_grid_line(self):
        '''
            Pega os dados do formulaŕio e atualiza a linha atual do grid
        '''
        data = self.get_form_data()                             #pega os dados do formuario
        self.set_grid_line_data(data, self.last_clicked_row)    #atualiza a linha atual


    def set_grid_line_data(self, data, row):
        '''
            Pega os dados de um dicionario passado e atualiza a linha do grid (row) passada como parâmetro
        '''
        for widget in self.scrolled_frame.grid_slaves():        #loop em todos os widget do grid
            if int(widget.grid_info()['row']) == row:           #se o widget pertence a linha (row)
                self.set_widget_data(widget, data[widget.name]) #atualiza o widget


    def set_grid_line_data_2(self, data, row):
        qt_cols = len(self.controls.keys())
        for i, key in enumerate(reversed(self.controls.keys())):
            index = (self.last_inserted_row - (row))*len(self.controls.keys())-len(self.controls.keys())
            widget = self.scrolled_frame.grid_slaves()[index + (qt_cols + i)]
            self.set_widget_data(widget, data[key])

    def set_grid_widget(self, widget, value_widget): 
        try:
            widget.config(state=tk.NORMAL)
            widget.delete(0, tk.END)
            widget.insert(0, value_widget)
            widget.config(state='readonly')
        except Exception as e:
            raise e


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


    def str_to_date(self, str_date):
        dt = string_to_date(str_date)        
        return formatar_data(dt) 


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
                    return self.insert()
                form_data = self.convert_data_to_bd(self.get_form_data())                
                #form_keys = self.convert_data_to_bd(self.get_form_keys())
                grid_keys = self.get_grid_keys(self.last_clicked_row)
                updt = self.data_table.update()
                for key in grid_keys:
                    updt = updt.where(self.data_table.c[key] == grid_keys[key])
                updt = updt.values(**form_data)
                self.conn.execute(updt)
                self.set_grid_line()                
                return 0
            return -1
        except Exception as e:
            print(e)
            return -1


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
        
        self.create_row_header(['id', 'Classe'])
        self.order_by(self.grid_table.c.ds_classe_produto)
        self.get_grid_dbdata()


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
