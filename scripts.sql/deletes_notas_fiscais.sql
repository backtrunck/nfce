/*delete from produtos_x_ncm_05 where manual = 0;*/


insert into produtos_x_prod_serv_sem_gtin_temp 
(id_produto, cnpj, cd_prod_serv, manual, dt_criacao)
select id_produto, cnpj, cd_prod_serv, manual, dt_criacao
from produtos_x_prod_serv_sem_gtin where manual = 1;
delete from produtos_x_prod_serv_sem_gtin;

insert into produtos_x_produtos_gtin_temp
(id_produto, cd_ean_produto, manual, dt_criacao)
select id_produto, cd_ean_produto, manual, dt_criacao
from produtos_x_produtos_gtin where manual = 1;
delete from produtos_x_produtos_gtin;

insert into produtos_servicos_ajuste_temp
(cnpj, cd_prod_serv_ajuste, cd_ean_ajuste)
select cnpj, cd_prod_serv_ajuste, cd_ean_ajuste
from produtos_servicos_ajuste;
delete from produtos_servicos_ajuste;



/*delete from produtos_servicos_sem_gtim;*/
/*delete from produtos_servicos_ean where insercao_manual = 0;*/
delete from produtos_servicos_ajuste;
delete from produtos_servicos;
delete from nota_fiscal_transporte;
delete from nota_fiscal_totais;
delete from nota_fiscal_formas_pagamento;
delete from nota_fiscal;
delete from emitente;

/*
insert into produtos_x_prod_serv_sem_gtin 
(id_produto, cnpj, cd_prod_serv, manual, dt_criacao)
select id_produto, cnpj, cd_prod_serv, manual, dt_criacao
from produtos_x_prod_serv_sem_gtin_temp;
delete from produtos_x_prod_serv_sem_gtin_temp;

insert into produtos_x_produtos_gtin
(id_produto, cd_ean_produto, manual, dt_criacao)
select id_produto, cd_ean_produto, manual, dt_criacao
from produtos_x_produtos_gtin_temp;
delete from produtos_x_produtos_gtin_temp;

insert into produtos_servicos_ajuste
(cnpj, cd_prod_serv_ajuste, cd_ean_ajuste)
select cnpj, cd_prod_serv_ajuste, cd_ean_ajuste
from produtos_servicos_ajuste_temp;
delete from produtos_servicos_ajuste_temp;
*/

