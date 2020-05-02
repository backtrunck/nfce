from tkinter import Button, Entry, Frame, Label, Tk
from tkinter import X, FLAT
from nfce_db import get_engine_bd
from nfce_gui import ComboBoxDB
from interfaces_graficas.ScrolledWindow import ScrolledWindow
from sqlalchemy import text
from PIL import Image
from PIL.ImageTk import PhotoImage

class FrameSearchProduct(Frame):
    
    def __init__(self, master, db_connection, **options):
        
        super().__init__(master, **options)
        
        self.controls = {}
        self.db_connection = db_connection
        self.make_controls()
        
        self.get_ncm_01()
        self.get_ncm_02()
        self.get_ncm_05()
        
        self.controls['cd_ncm_01'].fill_list(self.ncm_01_list)
        self.controls['cd_ncm_02'].fill_list(self.ncm_02_list)
        self.controls['cd_ncm_05'].fill_list(self.ncm_05_list)
       
        
    def __make_widget(self, widget_type, index_name, field_name='', comparison_operator='=', **options):
        
        e = widget_type(self, **options)
        e.index_name = index_name
        e.comparison_operator=comparison_operator
        
        if field_name:
            
            e.field_name = field_name
        else:
            
            e.field_name = index_name        
        
        return e
        
    def make_controls(self, **options):
        
        if not options:
            options['sticky'] = 'w'
            options['padx'] = 2
            options['pady'] = 2
        
        row = 0         
        Label(self, text='Ean:', anchor='e').grid(row=row, column=0)        
        e = self.__make_widget(Entry, 'cd_ean_prod_serv','','LIKE',  width=15)
        self.controls[e.index_name] = e
        e.grid(row=row, column=1, sticky=options['sticky'], padx=options['padx'], pady=options['pady'])
        
        #row += 1
        Label(self, text='Desc. Prod.: ', anchor='e').grid(row=row, column=2)        
        e = self.__make_widget(Entry, 'ds_prod_serv','','LIKE', width=35)
        self.controls[e.index_name] = e
        e.grid(row=row, column=3, sticky=options['sticky'], padx=options['padx'], pady=options['pady'])
        
        row += 1
        Label(self, text='Ncm 01:', anchor='e').grid(row=row, column=0)        
        e = self.__make_widget(ComboBoxDB, 'cd_ncm_01' , '', '=', state='readonly')
        self.controls[e.index_name] = e
        e.grid(row=row, column=1, sticky=options['sticky'], padx=options['padx'], pady=options['pady'])
        
        #row += 1
        Label(self, text='Ncm 02:', anchor='e').grid(row=row, column=2)        
        e = self.__make_widget(ComboBoxDB, 'cd_ncm_02', '', '=', width=35, state='readonly')
        self.controls[e.index_name] = e
        e.grid(row=row, column=3, sticky=options['sticky'], padx=options['padx'], pady=options['pady'])
        
        row += 1
        Label(self, text='Ncm 05:', anchor='e').grid(row=row,  column=0)        
        e = self.__make_widget(ComboBoxDB, 'cd_ncm_05' , '' ,'=', width=40, state='readonly')
        self.controls[e.index_name] = e
        e.grid(row=row, column=1, sticky=options['sticky'], padx=options['padx'], pady=options['pady'])
        
        row += 1
        self.search_button = Button(self, text = 'Procurar',  command=self.search)
        self.search_button.grid(row=row, column=3, sticky='E', padx=options['padx'], pady=10)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        row += 1
         #cria um frame com barras de rolagem que irá conter o grid
        scroll = ScrolledWindow(self, canv_w=200, canv_h = 200, scroll_h = False)
        scroll.columnconfigure(0, weight=1)
        scroll.grid(row=row, column=0, columnspan=4, sticky='WE')
        #scroll.pack(side=LEFT, fill=X, expand=YES, padx=10, pady=10)
        
        self.scrolled_frame = Frame(scroll.scrollwindow)       #Frame que ficará dentro do ScrolledWindows
        self.scrolled_frame.grid(row = 0, column = 0)


    def make_header(self):
        
        e = Entry(self.scrolled_frame, width=15, relief=FLAT, background='#d9d9d9')
        e.grid(row=1, column=0, sticky=W)
        e.insert(0,'EAN')
        
        e = Entry(self.scrolled_frame, width=25, relief=FLAT, background='#d9d9d9')
        e.grid(row=1, column=1, sticky=W)
        e.insert(0,'Desc. Produto')
        
        e = Entry(self.scrolled_frame, width=9, relief=FLAT, background='#d9d9d9')
        e.grid(row=1, column=0, sticky=W)
        e.insert(0,'NCM')
        
        e = Entry(self.scrolled_frame, width=45, relief=FLAT, background='#d9d9d9')
        e.grid(row=1, column=0, sticky=W)
        e.insert(0,'Desc. NCM')
        
    def search(self):
        
        '''
            Pesquisa os dados a partir dos campos preenchidos
        '''
        
        values = self.get_values_controls()             #pega os valor preenchidos nos controles
        
        select = "SELECT cd_ean_prod_serv,ds_prod_serv,cd_ncm_prod_serv,ds_ncm_05 "
        
        if values:                                      #se algum campo foi preenchido
        
            where = self.make_sql_where(values)
            
            sql = select + ' FROM produtos_servicos_ean ps, ncm_v WHERE ps.cd_ncm_prod_serv = cd_ncm_05 and ' + where     #atenção a tabela do BD esta fixa, deve-se mudar a estratégia

            result_proxy = self.db_connection.execute(text(sql), **values)               #executa a consulta    
            
        else:
            
            sql = select + ' FROM produtos_servicos_ean ps, ncm_v where ps.cd_ncm_prod_serv = cd_ncm_05'
            result_proxy = self.db_connection.execute(text(sql))               #executa a consulta
        
       
        
        self.fill_grid(result_proxy.fetchall())    #preenche o grid


    def make_sql_where(self, values_in_controls):
        '''
            Gera um lista de clausulas ligadas por "and" para compor um sql where
        '''
        sql_where = []

        for key in values_in_controls:
            field_name = self.controls[key].field_name     #pega o name_field correspondente ao controle
            comparison_operator = self.controls[key].comparison_operator #peda o operador de comparação do campo
            sql_where.append(field_name + ' ' + comparison_operator + ' :'+ key  )

        sql = " and ".join(sql_where)

        return sql


    def get_values_controls(self):    
        '''
            Obtem os valor preenchidos nos controles, com isto não vai ser necessário saber em que
            tipo de controle esta cada valor.
        '''
        values = {}
        
        for key in self.controls:
            value = None
            #if isinstance(self.controls[key],  Entry):
            if type(self.controls[key]) == Entry:
                
                value = self.controls[key].get()
        
            elif type(self.controls[key]) == ComboBoxDB:
                
                value = self.controls[key].get_key()
                
            if value:
                
                    values[key] = value 
                
        return values           #retorna um dicionário com a chave(nome do campo no BD) e o valor preenchido no widget    
        
    def get_ncm_01(self):
        sql = '''   SELECT distinct cd_ncm, concat(cd_ncm,' - ', ds_ncm_alt)
                    FROM nota_fiscal.ncm_01 n01, produtos_servicos ps 
                    where n01.cd_ncm = substring(ps.cd_ncm_prod_serv,1,2)
                    order by concat(cd_ncm,' - ', ds_ncm_alt)
              '''  
        self.ncm_01_list = self.db_connection.execute(sql).fetchall()
        
        
    def get_ncm_02(self):
        sql = '''   SELECT DISTINCT cd_ncm, concat(cd_ncm,' - ', ds_ncm), ds_ncm 
                    FROM nota_fiscal.ncm_02 n02, produtos_servicos ps 
                    WHERE n02.cd_ncm = substring(ps.cd_ncm_prod_serv,1,4)
                    ORDER BY concat(cd_ncm,' - ', ds_ncm);
              '''  
        self.ncm_02_list = self.db_connection.execute(sql).fetchall()
        
        
    def get_ncm_05(self):
        sql = '''   SELECT DISTINCT cd_ncm, concat(cd_ncm,' - ', ds_ncm) 
                    FROM nota_fiscal.ncm_05 n05, produtos_servicos ps 
                    WHERE n05.cd_ncm = substring(ps.cd_ncm_prod_serv,1,8)
                    ORDER BY concat(cd_ncm,' - ', ds_ncm);
              '''  
        self.ncm_05_list = self.db_connection.execute(sql).fetchall()
        
        
    def fill_grid(self, data_rows):
        '''
            Preenche um grid a partir de um data_rows passado
        '''
        #limpa o grid
        self.clear_grid()
        
        self.data_rows = data_rows
        frm = self.scrolled_frame
        #para cada linha retornada em data_rows
        for r, row in enumerate(data_rows, 2):
            
            e = Entry(frm,width=14)
            e.grid(row = r,column=0)
            e.insert(0, row['cd_ean_prod_serv'])
            e.bind("<Key>", lambda a: "break")
                                                    
            e = Entry(frm, width=30)
            e.grid(row=r, column=1)
            e.insert(0, row['ds_prod_serv'])
            e.bind("<Key>", lambda a: "break")
                
            e = Entry(frm, width=9)
            e.grid(row=r, column=2)
            e.insert(0, row['cd_ncm_prod_serv'])
            e.bind("<Key>", lambda a: "break")
                                   
            e = Entry(frm, width=40)
            e.grid(row=r, column=3)
            e.insert(0, row['ds_ncm_05'])
            e.bind("<Key>", lambda a: "break")
                                   
            image = Image.open('./static/check2.png')
            image2 = image.resize((22, 18), Image.ANTIALIAS)
            photo = PhotoImage(image2)
            bt = Button(frm, image=photo)
            bt.grid(row=r, column=4)   
            bt.image = photo            
            #command=(lambda k=i:callback(k))


    def clear_grid(self): 
        
        for widget in self.scrolled_frame.grid_slaves():
            
            if int(widget.grid_info()['row']) > 1:
                
                widget.grid_forget()

def testeFormSimpleDialog():
    
    root = Tk()
    root.title('Consulta Produtos')
    #root.bind('<Configure>', configure) 
    root.geometry('830x380')
    
    engine = get_engine_bd()    
    conn = engine.connect()
    
    f = FrameSearchProduct(root,conn)
    f.pack(fill = X)
    root.mainloop()

def main():    
    testeFormSimpleDialog()
    return

if __name__ == '__main__':
    main()

