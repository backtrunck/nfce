select nu_nfce, nu_prod_serv, vl_prod_serv,ds_prod_serv,qt_prod_serv,un_comercial_prod_serv from produtos_servicos;
select nu_nfce, ds_modalidade_frete from nota_fiscal_transporte;
select nu_nfce, vl_total_produtos, vl_icms from nota_fiscal_totais;
select nu_nfce, ds_forma_pagamento from nota_fiscal_formas_pagamento;
select nu_nfce, serie, cnpj from nota_fiscal;
select cnpj, razao_social, nm_fantasia from emitente;


/* produtos_servicos_ean */
select cd_ean_prod_serv,ds_prod_serv,insercao_manual from produtos_servicos_ean
select cd_ean_prod_serv,ds_prod_serv,insercao_manual from produtos_servicos_ean where cd_ean_prod_serv = '7896006779674';


/*produtos sem GTIN*/
select cd_ean_prod_serv, ds_prod_serv, cd_ean_tributavel_prod_serv,cd_ncm_prod_serv from produtos_servicos where cd_ean_prod_serv = 'SEM GTIN';

/*Contagem de produtos GTIM */
select cd_ean_prod_serv, ds_prod_serv, count(cd_ean_prod_serv) from produtos_servicos group by cd_ean_prod_serv,ds_prod_serv;


select 	n01.cd_ncm,n01.ds_ncm_alt,n02.cd_ncm,n02.ds_ncm,ps.ds_prod_serv, sum(vl_prod_serv), count(vl_prod_serv)
from 	produtos_servicos as ps, ncm_02 as n02, ncm_010 as n01
where 	substring(ps.cd_ncm_prod_serv,1,2) = n01.cd_ncm and 
	substring(ps.cd_ncm_prod_serv,1,4) = n02.cd_ncm
order by sum(vl_prod_serv);

/*codigo ncm do produtos ean */
select n02.ds_ncm_alt,cd_ncm_prod_serv,ds_prod_serv,cd_ean_prod_serv
from produtos_servicos_ean ps, ncm_02 as n02
where substring(ps.cd_ncm_prod_serv,1,4) = n02.cd_ncm
order by ps.cd_ean_prod_serv;

/*filtro por gtim em produtos_ean*/
set @cd_barras = '7898257600059';
select ds_prod_serv,cd_ncm_prod_serv,ds_ncm,ds_ncm_alt 
from produtos_servicos_ean as psa, ncm_02 as n2 
where n2.cd_ncm = substring(psa.cd_ncm_prod_serv,1,4) and 
	cd_ean_prod_serv like @cd_barras;

/*filtro por ncm em produtos_ean*/
set @cd_ncm = '07%';
select ds_prod_serv,cd_ncm_prod_serv,ds_ncm,ds_ncm_alt 
from produtos_servicos_ean as psa, ncm_02 as n2 
where n2.cd_ncm = substring(psa.cd_ncm_prod_serv,1,4) and 
	psa.cd_ncm_prod_serv like @cd_ncm;

/*preços unitários produtos pela descrição*/
set 	@ds_prod_serv = '%Feij%';
select 	ds_prod_serv,cd_ean_prod_serv,vl_prod_serv / qt_prod_serv as vl_unit
from 	produtos_servicos ps, ncm_02 as n2 
where   n2.cd_ncm = substring(ps.cd_ncm_prod_serv,1,4) and 
	lcase(ps.ds_prod_serv) like lcase(@ds_prod_serv);

/*preços unitários codigo barras produtos pela descrição*/
set 	@cd_barras = '7891025101376';
select 	ds_prod_serv,cd_ean_prod_serv,vl_prod_serv / qt_prod_serv as vl_unit, vl_prod_serv,qt_prod_serv
from 	produtos_servicos ps, ncm_02 as n2 
where   n2.cd_ncm = substring(ps.cd_ncm_prod_serv,1,4) and 
	ps.cd_ean_prod_serv = @cd_barras;

/*preços unitários (totalização) produtos pela descrição*/
set 	@ds_prod_serv = '%';
select 	ds_prod_serv,cd_ean_prod_serv,format(avg(vl_prod_serv / qt_prod_serv),2) as vl_unit,count(cd_prod_serv) as quant,
	date_format(min(dt_emissao),'%d/%m/%Y') as de, date_format(max(dt_emissao),'%d/%m/%Y')  as a
from 	nota_fiscal as nf, produtos_servicos ps, ncm_02 as n2
where   
	nf.nu_nfce = ps.nu_nfce and
	nf.cd_uf = ps.cd_uf and 
	nf.serie = ps.serie and
	nf.cnpj = ps.cnpj and
	nf.cd_modelo = ps.cd_modelo and
	n2.cd_ncm = substring(ps.cd_ncm_prod_serv,1,4) and 
	lcase(ps.ds_prod_serv) like lcase(@ds_prod_serv)
group by ds_prod_serv,cd_ean_prod_serv
order by count(cd_prod_serv) desc,ds_prod_serv,cd_ean_prod_serv;

/*produtos sem gtim*.
/*preços unitários (totalização) produtos pela descrição*/
set 	@ds_prod_serv = '%';
select 	ds_prod_serv,cd_ncm_prod_serv,n2.ds_ncm_alt
from 	nota_fiscal as nf, produtos_servicos ps, ncm_02 as n2
where   
	nf.nu_nfce = ps.nu_nfce and
	nf.cd_uf = ps.cd_uf and 
	nf.serie = ps.serie and
	nf.cnpj = ps.cnpj and
	nf.cd_modelo = ps.cd_modelo and
	n2.cd_ncm = substring(ps.cd_ncm_prod_serv,1,4) and 
	cd_ean_prod_serv = 'SEM GTIN' and 
	lcase(ps.ds_prod_serv) like lcase(@ds_prod_serv)
order by cd_ncm_prod_serv;

/*produtos_servicos */
select 	n01.cd_ncm, n01.ds_ncm_alt, 
		n02.cd_ncm, n02.ds_ncm_alt,
        ps.ds_prod_serv,ps.cd_ean_prod_serv, sum(vl_prod_serv), count(vl_prod_serv)
from 	produtos_servicos as ps, 
		ncm_02 as n02, 
		ncm_01 as n01
where 	substring(ps.cd_ncm_prod_serv,1,2) = n01.cd_ncm and 
		substring(ps.cd_ncm_prod_serv,1,4) = n02.cd_ncm
group by 	n01.cd_ncm, n01.ds_ncm_alt, 
			n02.cd_ncm, n02.ds_ncm,
			ps.ds_prod_serv,ps.cd_ean_prod_serv
order by sum(vl_prod_serv) desc;




