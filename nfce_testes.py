from nfce_models import products_gtin_t,  engine, classe_produto_t
from sqlalchemy.sql import select, and_
def main():
    print_select()
    
def print_select():
    #conn = engine.connect()
#    stm = classe_produto_t.update().values(**{'ds_classe_produto':'teste', 'id_classe_produto':'1'})
#    print(sql.compile(engine))
    sql = select([products_gtin_t.c.cd_ean_produto, products_gtin_t.c.ds_produto]).where(and_(\
                            products_gtin_t.c.cd_ncm_produto=='08013200', 
                            products_gtin_t.c.manual==0))
    sql = sql.where(products_gtin_t.c.cadastrado==0)
                            
    print(sql.compile(engine))
    #conn.execute(sql)

if __name__ == '__main__':
    main()
