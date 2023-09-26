#!/bin/bash

# Set the directory where your files are located
directory="/var/lib/mysql-files/"

# Set the MySQL database name
database="option_chains"

# Loop through files and load them into MySQL
for file in ${directory}spx_eod_2020*.txt; do
    mysql -u root --password=1 -D $database -e "LOAD DATA INFILE '$file' INTO TABLE options_data FIELDS TERMINATED BY ', ' LINES TERMINATED BY '\n' IGNORE 1 LINES;"
done

