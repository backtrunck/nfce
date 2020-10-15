/*inserir uma saida do estoque na tabela saida_produtos*/
insert into saida_produtos(cd_ean_saida,qt_saida,dt_saida) values('',1,'2020--');
insert into saida_produtos(cd_ean_saida,qt_saida,dt_saida) values('7891141023910',1,'2020-05-03');
insert into saida_produtos(cd_ean_saida,qt_saida,dt_saida) values('7898939247039',1,'2020-05-17');
/*para ver as saidas*/
select dt_saida,cd_ean_saida,ds_produto,qt_saida 
from saida_produtos sp
inner join produtos p
on sp.cd_ean_saida = p.cd_ean_produto
order by dt_saida;

/*inserir manualmente um produto na tabela de produtos*/
insert into produtos	 (cd_ean_produto,ds_produto,cd_ncm_produto,manual,cadastrado)
values			 ('7898130777137','Néctar (polpa) de tangerina de baixa caloria 100g','20089900',1,0);
