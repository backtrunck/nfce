import os
from sqlalchemy import create_engine
from sqlalchemy.sql import text, bindparam

PRODUCT_NO_CLASSIFIED = 146
engine = None
def execute_sql(db_connection, sql, dict_values_fields, dict_types_fields={}):
    #params=[]
    stmt = text(sql)
    
    for key, value in dict_types_fields.items():
        
        #params.append(bindparam(key, type_=value))
        stmt.bindparams(bindparam(key, type_=value))
         
    return db_connection.execute(stmt,  dict_values_fields)
    
def get_engine_bd():
    ''' 
        Conecta com um banco de dados e obtem um engine do mesmo
    '''
    global engine
    if not engine:
        user = os.environ.get('USER_DB_NTFCE')
        host = 'localhost'
#        host = '192.168.15.8'
        password = os.environ.get('PASS_DB_NTFCE')
        banco = 'nota_fiscal'
        engine = create_engine('mysql+pymysql://{}:{}@{}/{}'.format(user,password,host, banco), 
                                                            echo = False,
                                                            isolation_level="READ COMMITTED")
    return engine
    

def get_ncm_01(db_connection):
    
    sql = '''   SELECT distinct cd_ncm, concat(cd_ncm,' - ', ds_ncm_alt)
                FROM nota_fiscal.ncm_01 n01, produtos_servicos ps 
                where n01.cd_ncm = substring(ps.cd_ncm_prod_serv,1,2)
                order by concat(cd_ncm,' - ', ds_ncm_alt)
          '''  
    return db_connection.execute(sql).fetchall()
    
        
def get_ncm_02(db_connection):
    
    sql = '''   SELECT DISTINCT cd_ncm, concat(cd_ncm,' - ', ds_ncm), ds_ncm 
                FROM nota_fiscal.ncm_02 n02, produtos_servicos ps 
                WHERE n02.cd_ncm = substring(ps.cd_ncm_prod_serv,1,4)
                ORDER BY concat(cd_ncm,' - ', ds_ncm);
          '''  
    return db_connection.execute(sql).fetchall()
    
    
def get_ncm_05(db_connection):
    sql = '''   SELECT DISTINCT cd_ncm, concat(cd_ncm,' - ', ds_ncm) 
                FROM nota_fiscal.ncm_05 n05, produtos_servicos ps 
                WHERE n05.cd_ncm = substring(ps.cd_ncm_prod_serv,1,8)
                ORDER BY concat(cd_ncm,' - ', ds_ncm);
          '''  
    return db_connection.execute(sql).fetchall()

def get_product(db_connection,  product_code):
    
    sql = "SELECT * FROM produtos_ean WHERE cd_ean_prod_serv = %s"
    
    return db_connection.execute(sql, (product_code, ))
   
def get_connection():
    return get_engine_bd().connect()
    
        
        
    
if __name__ == '__main__':
    engine = get_engine_bd()
    print(engine)
