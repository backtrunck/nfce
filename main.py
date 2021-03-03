#!/usr/bin/env python3
import tkinter as tk
from nfce import nfce_db
import sys
sys.path.append("..")

def main():
    
    try:
        conn = nfce_db.get_connection()
    except Exception as e:
        msg = e.args
        msg_error = 'Não foi possível conectar com o servidor de banco de  dados'
        
        root = tk.Tk()
        root.title('Erro')
        f = tk.Frame(root)
        f.pack()
        tk.Label(f, text = msg_error).pack()
        tk.Label(f, text=msg).pack()
        tk.Button(f, text="Sair", command=root.quit).pack()
        root.mainloop()
        return
        
    root = tk.Tk()
    root.title('Controle de Compras v0.5')
    root.geometry("900x700")
    img = tk.PhotoImage(file='./nfce/static/icons8-carrinho-de-compras-carregado-48.png')
    root.tk.call('wm', 'iconphoto', root._w, img)
    root.conn = conn
#    engine = nfce_db.get_engine_bd()
    from nfce import nfce_gui
    from nfce import nfce_estoque
    from nfce import nfce_produtos
    from nfce import import_invoice
    from nfce import product_scraper
    from nfce import invoice_scraper
   
#    root.conn = engine.connect()
    
    top = tk.Menu(root)
    root.config(menu=top)
    
    view=tk.Menu(top)

    view.add_command(label='Consultar Nota Fiscal',  command=(lambda master = root: nfce_gui.make_class_search_invoice_window(master)), underline=0)    
    view.add_command(label='Consultar Produto',  command=(lambda master = root: nfce_produtos.make_search_products_window(master)), underline=0)    
    view.add_command(label='Ver Imagens de Produtos',  command=(lambda master = root, conn=None: product_scraper.products_images_search(master)), underline=0)    
    view.add_command(label='Sair', command=root.quit)
    
    import_nfce = tk.Menu(top)
    import_nfce.add_command(label='Importar Nota Fiscal da SEFAZ',  command=(lambda master = root: invoice_scraper.make_window(master)), underline=0)
    import_nfce.add_command(label='Importar Nota Fiscal de Arquivos',  command=(lambda master = root, conn=None: import_invoice.make_window(master, conn)), underline=0)
    import_nfce.add_command(label='Importar Imagens Produtos da Web',  command=(lambda master = root, conn=None: product_scraper.make_window(master)), underline=0)
    
    sistema_nfce = tk.Menu(top)
    sistema_nfce.add_command(label='Produtos',  command=(lambda master = root: nfce_produtos.make_product_window(master)), underline=0)
    sistema_nfce.add_command(label='Classe Produto',  command=(lambda master = root: nfce_produtos.make_class_product_window(master)), underline=0)
    sistema_nfce.add_command(label='Agrupamento Produto',  command=(lambda master = root: nfce_produtos.make_product_grouping_window(master)), underline=0)
    sistema_nfce.add_command(label='Produtos Gtin',  command=(lambda master = root: nfce_estoque.make_product_gtin_window(master)), underline=0)
    sistema_nfce.add_command(label='Produtos Gtin x Produtos',  command=(lambda master = root: nfce_produtos.make_product_gtin_product_window(master)), underline=0)
    sistema_nfce.add_command(label='Produtos Sem Gtin x Produtos',  command=(lambda master = root: nfce_produtos.make_product_sem_gtin_product_window(master)), underline=0)
    
    estoque_nfce = tk.Menu(top)
    estoque_nfce.add_command(label='Consulta Estoque',  command=(lambda master = root: nfce_estoque.make_class_search_stock_window(master)), underline=0)
    estoque_nfce.add_command(label='Consulta Consumo Produtos',  command=(lambda master = root: nfce_estoque.make_search_exit_window(master)), underline=0)
    estoque_nfce.add_command(label='Saída Produtos',  command=(lambda master = root: nfce_estoque.make_product_exit_window(master)), underline=0)
    
    
    top.add_cascade(label='Consultar', menu=view,  underline=0) 
    top.add_cascade(label='Importar', menu=import_nfce,  underline=0) 
    top.add_cascade(label='Sistema', menu=sistema_nfce,  underline=0)
    top.add_cascade(label='Estoque', menu=estoque_nfce,  underline=0) 
    
   
    root.eval('tk::PlaceWindow %s center' % root.winfo_pathname(root.winfo_id()))
    root = tk.mainloop()

if __name__ == '__main__':
    main()

