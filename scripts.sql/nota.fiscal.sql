#como root execute 
create database nota_fiscal;
#dando direitos de administrador ao usuario lcreina
grant all privileges on nota_fiscal to lcreina@'%';

insert into classe_despesa_01(id_classe, nm_classe)
values(1,"Alimentação");
insert into classe_despesa_01(id_classe, nm_classe)
values(2,"Combustível");
insert into classe_despesa_01(id_classe, nm_classe)
values(3,"Limpeza");
insert into classe_despesa_01(id_classe, nm_classe)
values(4,"Higiene Pessoal");
insert into classe_despesa_01(id_classe, nm_classe)
values(5,"Fármacos");


/*classes de despesas */

select 
	substring(cd_ncm_prod_serv,1,4) as ncm, 
	ds_prod_serv, count(*) 
from 	produtos_servicos 
group by substring(cd_ncm_prod_serv,1,4),ds_prod_serv 
order by count(*) desc;


set @classe = 1
insert into ncm_classe_despesa(cd_ncm,id_class) 
(select cd_ncm_prod_serv, @classe from produtos_servicos where substring(cd_ncm_prod_serv,1,2) = 02)

create trigger tgr_insert_produtos_servicos after insert
on produtos_servicos
for each row
begin
	case new.cd_prod_serv
		when '02' 
		then insert into ncm_classe_despesa
	end;
end;