/*confere a integridade do banco de dados a partir da conferência a soma dos produtos comprados
soma dos totais das notas, soma dos valores dos produtos comprados em produtos_servicos e a soma
dos valores pagos da view produtos_v. 
Caso dê erro entre o somatório de nota_fiscal e produtos e servicos, pode ser que algum produto 
de uma determinada nota não foi inserido. A aplicação não tem relação com esse erro caso ele apareça.
já uma divergência entre o somatirio da nota_fiscal e produtos_serviços com produtos_v, tem haver com
a aplicação, pois a aplicação é responsável pelo preenchimento automático das tabelas produtos_x_produtos_gtin e 
produtos_x_prod_serv_sem_gtin que fazem parte da view produtos_v*/
select sum(vl_total),count(*)  from nota_fiscal;
select sum(vl_prod_serv - vl_desconto_prod_serv),count(*) from produtos_servicos;
select sum(vl_pago),count(*) from produtos_servicos_v ;

