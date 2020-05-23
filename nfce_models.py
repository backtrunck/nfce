from nfce_db import get_engine_bd
#from sqlalchemy import Column, Integer, String,  Unicode,  
from sqlalchemy import MetaData, Table
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import mapper

engine = get_engine_bd()
meta_data = MetaData(engine)
emitente = Table('emitente', meta_data, autoload=True, autoload_with=engine)
nota_fiscal = Table('nota_fiscal', meta_data, autoload=True, autoload_with=engine)

    
class Emitente(object):
    def __repr__(self):
        return '<Razão Social {}>'.format(self.razao_social)

class NotaFiscalTransporte(object):
     def __repr__(self):
        return ('<Nota Fiscal: {}, Transporte: {}'\
                .format(self.nu_nfce,
                        self.ds_modalidade_frete))
                        
                        
class NotaFiscalFormaPagamento(object):
     def __repr__(self):
        return ('<Forma Pagamento: {}, Nota Fiscal: '+\
                '{} emitente: {} Valor Pagamento: {}>')\
                .format(self.ds_forma_pagamento,\
                        self.nu_nfce,\
                        self.cnpj,
                        self.vl_pagamento)

class NotaFiscalTotais(object):
    def __repr__(self):
        return ('<Nota Fiscal Totais: {} Emitente: {} Valor: {}>'\
                .format(self.nu_nfce,\
                        self.cnpj,
                        self.vl_pagamento))
                        
class ProdutoServico(object):
    def __repr__(self):
        return ('<Nota Fiscal {}, Emitida em: '+\
                '{:%d/%m/%Y %H:%M} Produto: {} Valor: {}>')\
                .format(self.numero,\
                        self.dt_emissao,\
                        self.ds_prod_serv, \
                        self.vl_prod_serv)
                        
class ProdutoGtin(object):
    def __repr__(self):
        return ('<Produto Gtim {} - {}> '\
                .format(self.numero,\
                        self.cd_ean_produto))

class ProdutosProdServSemGtin(object):
    def __repr__(self):
        return (('<Prod. Serv. sem Gtim, id produto: {}'+\
                ' cnpj: {} cod. produto:{}> ')\
                .format(self.id_produto,\
                        self.cnpj, self.cd_prod_serv))

class ProdutosNcm(object):
    def __repr__(self):
        return ('<Produto x Ncm, NCM: {}, EAN: {}> '\
                .format(self.cd_ncm,\
                        self.id_produto))

class ProdutoProdutoGtin(object):
    def __repr__(self):
        return ('<Produto x Gtim, Id Produto: {}, EAN: {}> '\
                .format(self.id_produto,\
                        self.cd_ean_produto))
     
        
class NotaFiscal(object):
    def __repr__(self):
        return ('<Nota Fiscal {}, Emitida em: '+\
                '{:%d/%m/%Y %H:%M} Emitente: {} Valor: {}>')\
                .format(self.numero,\
                        self.dt_emissao,\
                        self.cnpj,
                        self.vl_total)
        
mapper(Emitente, emitente)
mapper(NotaFiscal, nota_fiscal)
mapper(NotaFiscalFormaPagamento, Table('nota_fiscal_formas_pagamento', meta_data, autoload=True, autoload_with=engine))
mapper(NotaFiscalTotais, Table('nota_fiscal_totais', meta_data, autoload=True, autoload_with=engine))
mapper(NotaFiscalTransporte, Table('nota_fiscal_transporte', meta_data, autoload=True, autoload_with=engine))
mapper(ProdutoServico, Table('produtos_servicos', meta_data, autoload=True, autoload_with=engine))
mapper(ProdutoGtin, Table('produtos_gtin', meta_data, autoload=True, autoload_with=engine))
mapper(ProdutosProdServSemGtin, Table('produtos_x_prod_serv_sem_gtin', meta_data, autoload=True, autoload_with=engine))
mapper(ProdutosNcm, Table('produtos_x_ncm_05', meta_data, autoload=True, autoload_with=engine))
mapper(ProdutoProdutoGtin, Table('produtos_x_produtos_gtin', meta_data, autoload=True, autoload_with=engine))


Session = sessionmaker(bind=engine)
engine.echo=True


if __name__ == '__main__':
    session = Session()
#    print(session)
#    query = session.query(Emitente)
#    print(query)
#    query.filter(Emitente.cnpj=='00063960004864')
    query = session.query(NotaFiscal)
#    for obj in query:
#        print(obj)
    nota= query.filter(NotaFiscal.nu_nfce == 26034 and
                              NotaFiscal.cd_uf == 29  and
                              NotaFiscal.serie == 8  and
                              NotaFiscal.cnpj == '06626253099506' and
                              NotaFiscal.cd_modelo == 65)
#    query = session.query(NotaFiscalFormaPagamento)
#    nota= query.filter(NotaFiscal.nu_nfce == 26034 and
#                              NotaFiscal.cd_uf == 29  and
#                              NotaFiscal.serie == 8  and
#                              NotaFiscal.cnpj == '06626253099506' and
#                              NotaFiscal.cd_modelo == 65)
    print(nota)
    
    
