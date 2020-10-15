insert into produtos(ds_produto,classificado) values('Tábua da Passar',1) ; 
select * from produtos;
/* produto com gtin a classificar */

select p.id_produto,p.ds_produto,ppg.cd_ean_produto,pg.ds_produto
from produtos p 
inner join produtos_x_produtos_gtin ppg
on p.id_produto = ppg.id_produto
inner join produtos_gtin pg
on ppg.cd_ean_produto = pg.cd_ean_produto
where p.id_produto = 146

select concat(" update produtos_x_produtos_gtin set id_produto = x where id_produto = ",p.id_produto," and cd_ean_produto = '",ppg.cd_ean_produto,"';")
from produtos p 
inner join produtos_x_produtos_gtin ppg
on p.id_produto = ppg.id_produto
inner join produtos_gtin pg
on ppg.cd_ean_produto = pg.cd_ean_produto
where p.id_produto = 146

/*produto com gtim com classificação genérica */
select pg.cd_ean_produto,pg.ds_produto,p.id_produto,p.ds_produto
from produtos_x_produtos_gtin ppg 
inner join produtos p 
on ppg.id_produto = p.id_produto 
inner join produtos_gtin pg
on pg.cd_ean_produto = ppg.cd_ean_produto
where classificado = 0 ;

select concat("update produtos_x_produtos_gtin set id_produto = x where id_produto = ",p.id_produto," and cd_ean_produto = '", pg.cd_ean_produto,"';"),p.ds_produto,pg.ds_produto
from produtos_x_produtos_gtin ppg 
inner join produtos p 
on ppg.id_produto = p.id_produto 
inner join produtos_gtin pg
on pg.cd_ean_produto = ppg.cd_ean_produto
where classificado = 0 ;


/* produto sem gtin x NCM */

select p.ds_produto,pn.cd_ncm,n.ds_ncm_01,n.ds_ncm_02,n.ds_ncm_03,n.ds_ncm_04,n.ds_ncm_05
from produtos p 
inner join produtos_x_ncm_05 pn
on p.id_produto = pn.id_produto
inner join ncm_v n
on pn.cd_ncm = n.cd_ncm_05
where p.id_produto = 146


select concat(" update produtos_x_ncm_05 set id_produto = x where id_produto = ",p.id_produto," and cd_ncm = '",pn.cd_ncm,"';")
from produtos p 
inner join produtos_x_ncm_05 pn
on p.id_produto = pn.id_produto
where p.id_produto = 146

/* produto sem gtin a classificar */

select distinct p.id_produto,p.ds_produto,psg.cnpj,psg.cd_prod_serv,ps.ds_prod_serv
from produtos p 
inner join produtos_x_prod_serv_sem_gtin psg
on p.id_produto = psg.id_produto
inner join produtos_servicos ps
on psg.cnpj = ps.cnpj and
   psg.cd_prod_serv = ps.cd_prod_serv
where p.id_produto = 146

select distinct concat(" update produtos_x_prod_serv_sem_gtin set id_produto = x where id_produto = ",p.id_produto," and cnpj = '",psg.cnpj,"' and cd_prod_serv = '",psg.cd_prod_serv , "'")
from produtos p 
inner join produtos_x_prod_serv_sem_gtin psg
on p.id_produto = psg.id_produto
inner join produtos_servicos ps
on psg.cnpj = ps.cnpj and
   psg.cd_prod_serv = ps.cd_prod_serv
where p.id_produto = 146;

/*produto sem gtin com classificação genérica */
select distinct p.id_produto,p.ds_produto,psg.cnpj,psg.cd_prod_serv,ps.ds_prod_serv
from produtos p 
inner join produtos_x_prod_serv_sem_gtin psg
on p.id_produto = psg.id_produto
inner join produtos_servicos ps
on psg.cnpj = ps.cnpj and
   psg.cd_prod_serv = ps.cd_prod_serv
where p.classificado = 0;

select distinct concat(" update produtos_x_prod_serv_sem_gtin set id_produto = x where id_produto = ",p.id_produto," and cnpj = '",psg.cnpj,"' and cd_prod_serv = '",psg.cd_prod_serv , "';"),
p.ds_produto,ps.ds_prod_serv
from produtos p 
inner join produtos_x_prod_serv_sem_gtin psg
on p.id_produto = psg.id_produto
inner join produtos_servicos ps
on psg.cnpj = ps.cnpj and
   psg.cd_prod_serv = ps.cd_prod_serv
where p.classificado = 0;



select cnpj,nu_nfce,ds_prod_serv from produtos_servicos where cd_ncm_prod_serv = '11081900'

