#!/usr/bin/env python3
import nfce_gui
import nfce_db
import nfce_estoque
import nfce_produtos
import import_invoice
import product_scraper
import invoice_scraper
import tkinter as tk

def main():
    
    root = tk.Tk()
    root.title('Controle de Compras')
    root.geometry("900x700")
#    root.iconbitmap('./static/icons8-carrinho-de-compras-carregado-48.xbm')
    img = tk.PhotoImage(file='./static/icons8-carrinho-de-compras-carregado-48.png')
    root.tk.call('wm', 'iconphoto', root._w, img)
    engine = nfce_db.get_engine_bd()
    
    root.conn = engine.connect()
  
    top = tk.Menu(root)
    root.config(menu=top)
    
    view=tk.Menu(top)
#    view.add_command(label='Consultar Nota Fiscal',  command=(lambda master = root: nfce_gui.search_invoice(master)), underline=0)
    view.add_command(label='Consultar Nota Fiscal',  command=(lambda master = root: nfce_gui.make_class_search_invoice_window(master)), underline=0)
    
    view.add_command(label='Consultar Produto',  command=(lambda master = root: nfce_produtos.search_product(master)), underline=0)
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
    estoque_nfce.add_command(label='Saída Produtos',  command=(lambda master = root: nfce_estoque.make_product_exit_window(master)), underline=0)
    
    
    top.add_cascade(label='Consultar', menu=view,  underline=0) 
    top.add_cascade(label='Importar', menu=import_nfce,  underline=0) 
    top.add_cascade(label='Sistema', menu=sistema_nfce,  underline=0)
    top.add_cascade(label='Estoque', menu=estoque_nfce,  underline=0) 
    
   
    root.eval('tk::PlaceWindow %s center' % root.winfo_pathname(root.winfo_id()))
    root = tk.mainloop()

if __name__ == '__main__':
    main()

