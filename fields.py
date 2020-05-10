from collections import OrderedDict
from tkinter import Entry, Button


class Field:
    OP_LIKE, \
    OP_GREATER, \
    OP_LESS, \
    OP_GREATER_EQUAL, \
    OP_LESS_EQUAL, \
    OP_EQUAL = ('LIKE', '>', '<', '>=', '<=', '=')
    
    ASC_ORDER,\
    DESC_ORDER,\
    NO_ORDER = range(3)

    WIDGET_TYPE,\
    LABEL, WIDTH,\
    VISIBLE,\
    KEY,\
    ROW,\
    COMPARISON_OPERATOR = range(7)

    def __init__(self, name_index, 
                 name_field,
                 widget_type,
                 label,
                 width,
                 visible,
                 key,
                 row,
                 comparison_operator,
                 order_by = NO_ORDER,  
                 callback=None):

        self._name_index = name_index
        self._name_field = name_field
        self._widget_type = widget_type
        self._label = label
        self._width = width
        self._visible = visible
        self._key = key
        self._row = row
        self._comparison_operator = comparison_operator
        self._order_by = order_by
        self.callback = callback

    @property
    def name_index(self):
        return self._name_index
        
    @property
    def name_field(self):
        return self._name_field

    @property
    def widget_type(self):
        return self._widget_type

    @property
    def label(self):
        return self._label

    @property
    def width(self):
        return self._width

    @property
    def visible(self):
        return self._visible

    @property
    def key(self):
        return self._key

    @property
    def row(self):
        return self._row

    @property
    def comparison_operator(self):
        return self._comparison_operator
    
    @property
    def order_by(self):
        return self._order_by


class Fields():

    def __init__(self, fields = None):
        self.__ord_dict__ = OrderedDict()
        if fields:
            for field in fields:
                self.add(field)

    def add(self, field):

        if isinstance(field, Field):
            self.__ord_dict__[field.name_index] = field

    def __setitem__(self, chave, valor):
        self.__ord_dict__[chave] = valor

    def __getitem__(self, chave):
        return self.__ord_dict__[chave]

    def __repr__(self):
        return '{}'.format(self.__ord_dict__)

    def keys(self):
        return self.__ord_dict__.keys()

    def values(self):
        return self.__ord_dict__.values()

    def __iter__(self):
        return self.__ord_dict__.__iter__()

    def get_keys(self):
        keys = []
        for field in self.__ord_dict__.values():
            if field.key:
                keys.append(field.name_field)
        return keys
        
    def get_order(self):
        pass
#        order = []
#        for field in self.__ord_dict__.values()
#            if field.order_by

    def set_visible(self, visibles):
        '''

        :param visibles (dictionarie): contém os campos que serão visíveis ou não.{'nome_do_campo',bolean}
        :return: Um novo objeto do tipo Fields, ajustado conforme o dicionario visible
        '''

        new_fields = Fields()
        for field in self.values():

            if field.name_field in visibles.keys():
                new_fields.add(Field(field.name_index, 
                                    field.name_field,
                                     field.widget_type,
                                     field.label,
                                     field.width,
                                     visibles[field.name_field],
                                     field.key,
                                     field.row,
                                     field.comparison_operator))
            else:
                new_fields.add(Field(field.name_index, 
                                    field.name_field,
                                     field.widget_type,
                                     field.label,
                                     field.width,
                                     False,
                                     field.key,
                                     field.row,
                                     field.comparison_operator))

        return new_fields

fields_search_invoice = Fields(
    [Field('cnpj','cnpj', Entry, 'Cnpj', 15, True, True, 1, Field.OP_EQUAL),
     Field('estabelecimento','estabelecimento', Entry, 'Estabelecimento', 40, True, False, 1, Field.OP_LIKE), 
     Field('dt_emissao_menor', 'dt_emissao', Entry, 'Data de', 10, True, False, 2, Field.OP_GREATER_EQUAL),
     Field('dt_emissao_maior', 'dt_emissao', Entry, 'Data até', 10, True, False, 2, Field.OP_LESS_EQUAL),
     Field('vl_total_menor','vl_total', Entry, 'Valor de', 7, True, False, 3, Field.OP_GREATER_EQUAL),
     Field('vl_total_maior','vl_total', Entry, 'Valor até', 7, True, False, 3, Field.OP_LESS_EQUAL),
     Field('hora_emissao','hora_emissao', Entry, 'Hora', 5, False, False, 1, Field.OP_EQUAL),
     Field('sg_uf','sg_uf', Entry, 'Uf', 2, False, False, 1, Field.OP_EQUAL), 
     Field('nu_nfce','nu_nfce', Entry, 'Nota Fiscal', 10, False, True, 1, Field.OP_EQUAL), 
     Field('endereco','endereco', Entry, 'End.', 40, True, False, 3, Field.OP_LIKE), 
     Field('bairro','bairro', Entry, 'Bairro', 15, True, False, 3, Field.OP_LIKE), 
     Field('nm_municipio','nm_municipio', Entry, 'Municipio', 20, True, False, 1, Field.OP_LIKE), 
     Field('telefone','telefone', Entry, 'Tel.', 11, False, False, 3, Field.OP_LIKE), 
     Field('cd_uf','cd_uf', Entry, 'Cd. Uf', 5, False, True, 1, Field.OP_EQUAL), 
     Field('cd_modelo','cd_modelo', Entry, 'Modelo', 5, False, True, 1, Field.OP_EQUAL), 
     Field('serie','serie', Entry, 'Serie', 5, False, True, 1, Field.OP_EQUAL)])

fields_form_invoice = Fields(
    [Field('data_emissao','data_emissao', Entry, 'Data', 10, True, False, 1, Field.OP_GREATER),
     Field('hora_emissao','hora_emissao', Entry, 'Hora', 5, True, False, 1, Field.OP_LESS),
     Field('sg_uf','sg_uf', Entry, 'Uf', 2, True, False, 1, Field.OP_EQUAL),
     Field('nu_nfce','nu_nfce', Entry, 'Nota Fiscal', 10, True, True, 1, Field.OP_EQUAL),
     Field('cnpj','cnpj', Entry, 'Cnpj', 15, True, True, 2, Field.OP_EQUAL),
     Field('estabelecimento','estabelecimento', Entry, 'Estabelecimento', 60, True, False, 2, Field.OP_LIKE),
     Field('vl_total','vl_total', Entry, 'Val. Total', 8, True, False, 3, Field.OP_GREATER_EQUAL),
     Field('endereco','endereco', Entry, 'End.', 40, True, False, 3, Field.OP_GREATER_EQUAL),
     Field('bairro','bairro', Entry, 'Bairro', 15, True, False, 3, Field.OP_LIKE),
     Field('nm_municipio','nm_municipio', Entry, 'Municipio', 20, True, False, 1, Field.OP_LIKE),
     Field('telefone','telefone', Entry, 'Tel.', 11, True, False, 3, Field.OP_LIKE),
     Field('cd_uf','cd_uf', Entry, 'Cd. Uf', 5, False, True, 1, Field.OP_GREATER_EQUAL),
     Field('cd_modelo','cd_modelo', Entry, 'Modelo', 5, False, True, 1, Field.OP_LESS_EQUAL),
     Field('button_1','button_1', Button, ' ', 5, False, False, 1, None),
     Field('serie','serie', Entry, 'Serie', 5, False, True, 1, Field.OP_LESS_EQUAL), 
     Field('chave_acesso_format','chave_acesso_format', Entry, 'Chave Acesso', 53, True, False, 4, Field.OP_LIKE)])

fields_items_invoice = Fields(
    [Field('ds_prod_serv', 'ds_prod_serv', Entry, 'Produto',  28, True, False, 1, Field.OP_EQUAL),
    Field('qt_prod_serv', 'qt_prod_serv', Entry, 'Quant.',  5, True, False, 1, Field.OP_EQUAL), 
    Field('vl_pago', 'vl_pago', Entry, 'Valor',  8, True, False, 1, Field.OP_EQUAL), 
    Field('vl_por_unidade', 'vl_por_unidade', Entry, 'Vl. Unit', 8, True, False, 1, Field.OP_EQUAL), 
    Field('un_comercial_prod_serv', 'un_comercial_prod_serv', Entry, 'Un.',  3, True, False, 1, Field.OP_EQUAL),
    Field('cd_ncm_prod_serv', 'cd_ncm_prod_serv', Entry, 'Ncm', 10, True, False, 1, Field.OP_EQUAL),
    Field('cd_ean_prod_serv', 'cd_ean_prod_serv', Entry, 'Gtim', 15, True, False, 1, Field.OP_EQUAL), 
    Field('cd_uf','cd_uf', Entry, 'Cd. Uf', 5, False, True, 1, Field.OP_GREATER_EQUAL),
    Field('cnpj','cnpj', Entry, 'Cnpj', 15, True, True, 2, Field.OP_EQUAL), 
    Field('nu_nfce','nu_nfce', Entry, 'Nota Fiscal', 10, True, True, 1, Field.OP_EQUAL),     
    Field('serie','serie', Entry, 'Serie', 5, False, True, 1, Field.OP_LESS_EQUAL), 
    Field('cd_modelo','cd_modelo', Entry, 'Modelo', 5, False, True, 1, Field.OP_LESS_EQUAL)])


if __name__ == '__main__':
    a = Fields([Field('data_emissao','data_emissao', Entry, 'Data', 10, True, False, 1, Field.OP_GREATER)])
    print(a)
    print(a['data_emissao'].name_index)
