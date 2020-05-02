import os
from sqlalchemy import create_engine

def get_engine_bd():
    ''' 
        Conecta com um banco de dados e obtem um engine do mesmo
    '''
    user = os.environ.get('USER_DB_NTFCE')
    host = 'localhost'
    password = os.environ.get('PASS_DB_NTFCE')
    banco = 'nota_fiscal'
    engine = create_engine('mysql://{}:{}@{}/{}'.format(user,password,host, banco), echo = True)
    return engine
    
if __name__ == '__main__':
    engine = get_engine_bd()
    print(engine)
