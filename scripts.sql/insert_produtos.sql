delete from produtos_x_ncm_05 where manual = 0;
delete from produtos_x_prod_serv_sem_gtin  where manual = 0;
delete  from produtos_x_produtos_gtin where manual = 0 ;
delete from produtos;
ALTER TABLE produtos AUTO_INCREMENT = 1;


load data local infile "produtos_locais.csv" into table produtos fields terminated by ';' (id_produto,ds_produto,classificado);
load data local infile "produtos_x_ncm_05.csv" into table produtos_x_ncm_05 fields terminated by ';' ENCLOSED BY  '"' (cd_ncm,id_produto,manual);
load data local infile "produtos_sem_gtin.csv" into table produtos_x_prod_serv_sem_gtin fields terminated by ';' ENCLOSED BY  '"' (id_produto,cnpj,cd_prod_serv,manual);
load data local infile "produtos_x_produtos_gtin.csv" into table produtos_x_produtos_gtin fields terminated by ';' ENCLOSED BY  '"' (id_produto,cd_ean_produto,manual);



