set @cd_barras 	= 'X00000000000003';
set @cnpj 	= '00063960004864';
set @prod_serv 	= '00000799603';
insert into produtos_servicos_ean(
	cd_ncm_prod_serv, ds_prod_serv,cd_prod_serv,cd_ean_prod_serv,insercao_manual)
(select distinct cd_ncm_prod_serv,psg.ds_prod_serv,psg.cd_prod_serv, @cd_barras,1
from produtos_servicos as ps, produtos_servicos_sem_gtim psg
where ps.cnpj = psg.cnpj and
	ps.cd_prod_serv = psg.cd_prod_serv and
	psg.cnpj = @cnpj and
	psg.cd_prod_serv = @prod_serv);




update 	produtos_servicos_sem_gtin as psg 
set 	cd_gtim_prod_serv = @cd_barras
where 	psg.cnpj = @cnpj and
	psg.cd_prod_serv = @prod_serv;

set @cd_barras = 'X00000000000003';
set @desc_produto = 'Abacaxi';
update 	produtos_servicos_ean as psa 
set 	ds_prod_serv = @desc_produto
where 	psa.cd_ean_prod_serv = @cd_barras;
select * 
from produtos_servicos_ean as psa
where psa.cd_ean_prod_serv = @cd_barras;

select * from produtos_servicos_sem_gtin;

set @cnpj = '00063960004864';
set @prod_serv = '00980004008';
select distinct psg.cnpj,psg.cd_prod_serv,cd_ncm_prod_serv, cd_ean_prod_serv,psg.ds_prod_serv 
from produtos_servicos as ps, produtos_servicos_sem_gtin psg
where ps.cnpj = psg.cnpj and
	ps.cd_prod_serv = psg.cd_prod_serv and
	psg.cnpj = @cnpj and
	psg.cd_prod_serv = @prod_serv