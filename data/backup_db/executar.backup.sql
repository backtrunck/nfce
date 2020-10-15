#backup
mysqldump --add-drop-table -u lcreina -h x.x.x.x -p -x -e -B nota_fiscal > nota.fiscal.20200726.sql
#restaurar
mysql -u root -p < nota_fiscal.sql
