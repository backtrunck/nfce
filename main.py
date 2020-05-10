import nfce_gui
import nfce_db
import nfce_produtos
import import_invoice
import product_scraper
import tkinter as tk

def main():
    
    root = tk.Tk()
    root.title('Controle de Compras')
    root.geometry("900x700")
    engine = nfce_db.get_engine_bd()
    
    root.conn = engine.connect()
  
    top = tk.Menu(root)
    root.config(menu=top)
    
    file=tk.Menu(top)
    file.add_command(label='Consultar Nota Fiscal',  command=(lambda master = root: nfce_gui.search_invoice(master)), underline=0)
    file.add_command(label='Consultar Produto',  command=(lambda master = root: nfce_produtos.search_product(master)), underline=0)
    file.add_command(label='Importar Nota Fiscal',  command=(lambda master = root, conn=None: import_invoice.make_window(master, conn)), underline=0)
    file.add_command(label='Importar Imagens Produtos',  command=(lambda master = root, conn=None: product_scraper.make_window(master)), underline=0)
    file.add_command(label='Sair', command=root.quit)
    top.add_cascade(label='Arquivo', menu=file,  underline=0) 
   
    root.eval('tk::PlaceWindow %s center' % root.winfo_pathname(root.winfo_id()))
    root = tk.mainloop()

if __name__ == '__main__':
    main()

