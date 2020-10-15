ncm_05 (13819 linhas) codigo com 8 caracteres
ncm_05 (12862 linhas) para codigos com mais de 5 caracteres
ncm_02 (942 linhas) codigo com 4 caracteres
ncm_01 (99 linhas) codigo com 2 caracteres 


delete from ncm_01;
delete from ncm_02;
delete from ncm_03;
delete from ncm_04;
delete from ncm_05;



insert into ncm_01(cd_ncm,ds_ncm)
(select 	ncm_05.cd_ncm,ncm_05.ds_ncm
from 	ncm_05
where 
	(length(ncm_05.cd_ncm) = 2));


insert into ncm_02(cd_ncm,ds_ncm)(
select 	ncm_05.cd_ncm,ncm_05.ds_ncm
from 	ncm_05
where 
	length(ncm_05.cd_ncm) = 4;
	


insert into ncm_03(cd_ncm,ds_ncm)(
select ncm_05.cd_ncm,ncm_05.ds_ncm
from ncm_05
where 	length(ncm_05.cd_ncm) = 5 or 
	(length(ncm_05.cd_ncm) = 6 and substring(ncm_05.cd_ncm,6,1) = "0" ) or
	(length(ncm_05.cd_ncm) = 8 and substring(ncm_05.cd_ncm,6,3) = "000" ));
	

insert into ncm_04(cd_ncm,ds_ncm)(
select ncm_05.cd_ncm,ncm_05.ds_ncm
from ncm_05
where 	
	(length(ncm_05.cd_ncm) = 6) or
	(length(ncm_05.cd_ncm) = 8 and substring(ncm_05.cd_ncm,7,2) = "00"));
	
	

select distinct substring(cd_ncm,1,4) from ncm_05;

select cd_ncm from ncm_01 limit 50;

select 	n1.cd_ncm,n1.ds_ncm,n2.cd_ncm,n2.ds_ncm,n5.cd_ncm,n5.ds_ncm
from 	ncm_01 as n1, ncm_02 as n2, ncm_05 as n5
where
	n1.cd_ncm = substring(n5.cd_ncm,1,2) and
	n2.cd_ncm = substring(n5.cd_ncm,1,4);
	
select 	count(*) /*13819 linhas*/
from 	ncm_01 as n1, ncm_02 as n2, ncm_05 as n5
where
	n1.cd_ncm = substring(n5.cd_ncm,1,2) and
	n2.cd_ncm = substring(n5.cd_ncm,1,4);

select 	count(*) /*12862 linhas*/
from 	ncm_01 as n1, ncm_02 as n2, ncm_03 as n3, ncm_04 as n4, ncm_05 as n5
where
	n1.cd_ncm = substring(n5.cd_ncm,1,2) and
	n2.cd_ncm = substring(n5.cd_ncm,1,4) and
	n3.cd_ncm = substring(n5.cd_ncm,1,5) and 
	n4.cd_ncm = substring(n5.cd_ncm,1,6);

select 	n1.cd_ncm, n1.ds_ncm, n2.cd_ncm, n2.ds_ncm, n3.cd_ncm,n3.ds_ncm, n4.cd_ncm,n4.ds_ncm, n5.cd_ncm, n5.ds_ncm
from 	ncm_01 as n1, ncm_02 as n2, ncm_03 as n3, ncm_04 as n4, ncm_05 as n5
where
	n1.cd_ncm = substring(n5.cd_ncm,1,2) and
	n2.cd_ncm = substring(n5.cd_ncm,1,4) and
	n3.cd_ncm = substring(n5.cd_ncm,1,5) and 
	n4.cd_ncm = substring(n5.cd_ncm,1,6)
	limit 1;

	
/* todas as linha de n5 e as linhas de n2 q coincidir*/	
select 	n5.cd_ncm, n2.cd_ncm /*linhas 13819*/
from 	ncm_05 as n5
left join ncm_02 as n2 
on n2.cd_ncm = substring(n5.cd_ncm,1,4)
order by n2.cd_ncm asc limit 10

/*todas as linha de n5 que não coincidem com as linhas de n2*/	
select 	n5.cd_ncm, n2.cd_ncm
from 	ncm_05 as n5
left join ncm_02 as n2 
on n2.cd_ncm = substring(n5.cd_ncm,1,4)
where n2.cd_ncm is null


insert into ncm_02(ds_ncm,cd_ncm) /*item que já iniciam a partir do quarto nivel com xx.xx.00*/
select ds_ncm,substring(cd_ncm,1,4) from ncm_05 where length(cd_ncm) = 6 and substring(cd_ncm,5,2) = '00';

insert into ncm_02(ds_ncm,cd_ncm)/*item que já iniciam a partir do quinto nivel com xx.xx.00.00*/
select ds_ncm,substring(cd_ncm,1,4) from ncm_05 where length(cd_ncm) = 8 and substring(cd_ncm,5,4) = '0000';

select 	count(*) /* linhas*/
from 	ncm_03 as n3, ncm_05 as n5
where
	n3.cd_ncm = substring(n5.cd_ncm,1,2)

select cd_ncm from ncm_03 limit 10;

insert into ncm_03(ds_ncm,cd_ncm) /*todos códigos de terceiro nivel com xx.xx.x*/
select ds_ncm,substring(cd_ncm,1,5) from ncm_05 where length(cd_ncm) = 5;

insert into ncm_03(ds_ncm,cd_ncm) /*item que já iniciam a partir do terceiro e quarto nivel com xx.xx.x0*/
select ds_ncm,substring(cd_ncm,1,5) from ncm_05 where length(cd_ncm) = 6 and substring(cd_ncm,6,1) = '0';

insert into ncm_03(ds_ncm,cd_ncm)/*item que já iniciam a partir do quinto nivel com xx.xx.00.00*/
select ds_ncm,substring(cd_ncm,1,5) from ncm_05 where length(cd_ncm) = 8 and substring(cd_ncm,5,4) = '0000';

insert into ncm_03(ds_ncm,cd_ncm)/*item que já iniciam a partir do quinto nivel com xx.xx.00.00*/
select ds_ncm,substring(cd_ncm,1,5) from ncm_05 where length(cd_ncm) = 8 and substring(cd_ncm,6,3) = '000' and substring(cd_ncm,5,1) != '0';

/*todas as linha de n5 que não coincidem com as linhas de n3(deixei com alias n2)*/	
select 	n5.cd_ncm, n2.cd_ncm
from 	ncm_05 as n5
left join ncm_03 as n2 
on n2.cd_ncm = substring(n5.cd_ncm,1,5)
where n2.cd_ncm is null

select 	count(*) /* linhas*/
from 	ncm_03 as n3, ncm_05 as n5
where
	n3.cd_ncm = substring(n5.cd_ncm,1,5)
	
insert into ncm_04(ds_ncm,cd_ncm) /*todos códigos de terceiro nivel com xx.xx.x*/
select ds_ncm,substring(cd_ncm,1,6) from ncm_05 where length(cd_ncm) = 6;

insert into ncm_04(ds_ncm,cd_ncm)/*item que já iniciam a partir do quinto nivel com xx.xx.00.00*/
select ds_ncm,substring(cd_ncm,1,6) from ncm_05 where length(cd_ncm) = 8 and substring(cd_ncm,5,4) = '0000';

insert into ncm_04(ds_ncm,cd_ncm)/*item que já iniciam a partir do quinto nivel com xx.xx.00.00*/
select ds_ncm,substring(cd_ncm,1,6) from ncm_05 where length(cd_ncm) = 8 and substring(cd_ncm,6,3) = '000' and substring(cd_ncm,5,1) != '0';

insert into ncm_04(ds_ncm,cd_ncm)/*item que já iniciam a partir do quinto nivel com xx.xx.00.00*/
select ds_ncm,substring(cd_ncm,1,6) from ncm_05 where length(cd_ncm) = 8 and substring(cd_ncm,7,2) = '00' and substring(cd_ncm,6,1) != '0';

/*todas as linha de n5 que não coincidem com as linhas de n4(deixei com alias n2)*/	
select 	count(*) /* linhas*/
from 	ncm_04 as n3, ncm_05 as n5
where
	n3.cd_ncm = substring(n5.cd_ncm,1,6) and 
	length(n5.cd_ncm) > 5;

select 	count(*) /*12862 linhas*/
from 	ncm_05 as n5
where
	length(n5.cd_ncm) > 5;

/*todas as linha de n5 que não coincidem com as linhas de n4(deixei com alias n2)*/	
/*todas as linha de n5 que não coincidem com as linhas de n3(deixei com alias n2)*/	
select 	n5.cd_ncm, n2.cd_ncm
from 	ncm_05 as n5
left join ncm_04 as n2 
on n2.cd_ncm = substring(n5.cd_ncm,1,6)
where
   length(n5.cd_ncm) > 5 and
   n2.cd_ncm is null

/* Cruzamento entre produtos e a view ncm_v*/   
select 	ds_prod_serv as produto,
		concat(cd_ncm_01,' - ',ds_ncm_01) as ncm_01,
		concat(cd_ncm_02,' - ',ds_ncm_02) as ncm_02,
        	concat(cd_ncm_03,' - ',ds_ncm_03) as ncm_03,
        	concat(cd_ncm_04,' - ',ds_ncm_04) as ncm_04,
        	concat(cd_ncm_05,' - ',ds_ncm_05) as ncm_05
from produtos_servicos ps, ncm_v
where ps.cd_ncm_prod_serv = cd_ncm_05;

select count(*)
from produtos_servicos;

select count(*)
from produtos_servicos as ps, ncm_v
where ps.cd_ncm_prod_serv = cd_ncm_05;


	