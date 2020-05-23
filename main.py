import nfce_gui
import nfce_db
import nfce_produtos
import import_invoice
import product_scraper
import invoice_scraper
import tkinter as tk

def main():
    
    root = tk.Tk()
    root.title('Controle de Compras')
    root.geometry("900x700")
    engine = nfce_db.get_engine_bd()
    
    root.conn = engine.connect()
  
    top = tk.Menu(root)
    root.config(menu=top)
    
    view=tk.Menu(top)
    view.add_command(label='Consultar Nota Fiscal',  command=(lambda master = root: nfce_gui.search_invoice(master)), underline=0)
    view.add_command(label='Consultar Produto',  command=(lambda master = root: nfce_produtos.search_product(master)), underline=0)
    view.add_command(label='Ver Imagens de Produtos',  command=(lambda master = root, conn=None: product_scraper.products_images_search(master)), underline=0)    
    view.add_command(label='Sair', command=root.quit)
    
    import_nfce = tk.Menu(top)
    import_nfce.add_command(label='Importar Nota Fiscal da SEFAZ',  command=(lambda master = root: invoice_scraper.make_window(master)), underline=0)
    import_nfce.add_command(label='Importar Nota Fiscal de Arquivos',  command=(lambda master = root, conn=None: import_invoice.make_window(master, conn)), underline=0)
    import_nfce.add_command(label='Importar Imagens Produtos da Web',  command=(lambda master = root, conn=None: product_scraper.make_window(master)), underline=0)
    
    
    top.add_cascade(label='Consultar', menu=view,  underline=0) 
    top.add_cascade(label='Importar', menu=import_nfce,  underline=0) 
    
   
    root.eval('tk::PlaceWindow %s center' % root.winfo_pathname(root.winfo_id()))
    root = tk.mainloop()

if __name__ == '__main__':
    main()

