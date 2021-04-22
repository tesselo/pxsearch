-- psql -h tesselo-production.ce3mi8diupls.eu-west-1.rds.amazonaws.com -p 5432 -U tesselo -d eo_catalog -a -f export_tables.sql -W

\copy (SELECT * FROM imagery) to '/home/keren/projects/API_Images/imagery_db.csv' with csv
