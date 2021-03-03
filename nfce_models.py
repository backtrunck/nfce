from nfce.nfce_db import get_engine_bd
#from sqlalchemy import Column, Integer, String,  Unicode,  
from sqlalchemy import MetaData, Table
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import mapper

engine = get_engine_bd()
meta_data = MetaData(engine)
emitente = Table('emitente', meta_data, autoload=True, autoload_with=engine)
nota_fiscal_t = Table('nota_fiscal', meta_data, autoload=True, autoload_with=engine)

class Produtos(object):
    def __repr__(self):
        if self.classificado:
                return f'<Produto {self.id_produto} - {self.ds_produto} / Classificado>'.format(self.razao_social)
        else:
                return f'<Produto {self.id_produto} - {self.ds_produto} / Não Classificado>'.format(self.razao_social)

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
                        self.cd_prod_serv_ajuste,\
                        self.ds_prod_serv, \
                        self.vl_prod_serv)
                        
class ProdutoServicoAjuste(object):
    def __repr__(self):
        return ('<Prod. Serv. Ajuste:Cnpj {}, Prod. Serv: '+\
                '{} Produto: {} Gtin: {}>')\
                .format(self.cnpj,\
                        self.ds_prod_serv,\
                        self.cd_ean_ajuste)
    
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

nota_fiscal_t = Table('nota_fiscal', meta_data, autoload=True, autoload_with=engine)
products_t = Table('produtos', meta_data, autoload=True, autoload_with=engine)
produtos_servicos_t = Table('produtos_servicos', meta_data, autoload=True, autoload_with=engine)
products_gtin_t = Table('produtos_gtin', meta_data, autoload=True, autoload_with=engine)
products_sem_gtin_products_t = Table('produtos_x_prod_serv_sem_gtin', meta_data, autoload=True, autoload_with=engine)
products_gtin_products_t = Table('produtos_x_produtos_gtin', meta_data, autoload=True, autoload_with=engine)
classe_produto_t = Table('classe_produto', meta_data, autoload=True, autoload_with=engine)
agrupamento_produto_t = Table('agrupamento_produto', meta_data, autoload=True, autoload_with=engine)
ajuste_estoque_t = Table('ajuste_estoque', meta_data, autoload=True, autoload_with=engine)
adjust_prod_serv_t = Table('produtos_servicos_ajuste', meta_data, autoload=True, autoload_with=engine)

nota_fiscal_produtos_v = Table('nota_fiscal_produtos_v', meta_data, autoload=True, autoload_with=engine)
nota_fiscal_v = Table('nota_fiscal_v', meta_data, autoload=True, autoload_with=engine)
products_sem_gtin_products_v = Table('produtos_sem_gtin_x_produtos_v', meta_data, autoload=True, autoload_with=engine)
products_gtin_products_v = Table('produtos_gtin_produtos_v', meta_data, autoload=True, autoload_with=engine)
products_exit_t = Table('saida_produtos', meta_data, autoload=True, autoload_with=engine)
products_exit_v = Table('saida_produtos_v', meta_data, autoload=True, autoload_with=engine)
products_v = Table('produtos_v', meta_data, autoload=True, autoload_with=engine)
produtos_servicos_v = Table('produtos_servicos_v', meta_data, autoload=True, autoload_with=engine)
products_class_v = Table('classe_produto_v', meta_data, autoload=True, autoload_with=engine)
stock_v = Table('estoque_v', meta_data, autoload=True, autoload_with=engine)

mapper(Emitente, emitente)
mapper(NotaFiscal, nota_fiscal_t)
mapper(NotaFiscalFormaPagamento, Table('nota_fiscal_formas_pagamento', meta_data, autoload=True, autoload_with=engine))
mapper(NotaFiscalTotais, Table('nota_fiscal_totais', meta_data, autoload=True, autoload_with=engine))
mapper(NotaFiscalTransporte, Table('nota_fiscal_transporte', meta_data, autoload=True, autoload_with=engine))
mapper(ProdutoServico, Table('produtos_servicos', meta_data, autoload=True, autoload_with=engine))
mapper(ProdutoGtin, Table('produtos_gtin', meta_data, autoload=True, autoload_with=engine))
mapper(ProdutosProdServSemGtin, products_sem_gtin_products_t)
mapper(ProdutosNcm, Table('produtos_x_ncm_05', meta_data, autoload=True, autoload_with=engine))
mapper(ProdutoProdutoGtin, products_gtin_products_t)
mapper(Produtos, products_t)
mapper(ProdutoServicoAjuste, adjust_prod_serv_t )


Session = sessionmaker(bind=engine, autoflush=True)
engine.echo=False


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
    
    
