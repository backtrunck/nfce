#entrar com usuario root (sudo mysql)
#criar banco de dados (create database nota_fiscal;)
#criar usuario
create user 'nota_fiscal_app'@'%' identified by ''
grant select,update,delete,insert,show view on nota_fiscal.* to 'nota_fiscal_app'@'%'; #usuario 
FLUSH PRIVILEGES

#carrega ultima base da dados (mysql -u usuario_adm -p nota_fiscal < backup.sql)
'
