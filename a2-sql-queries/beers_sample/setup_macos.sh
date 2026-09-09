#!/bin/bash

mypath=`realpath $0`
mybase=`dirname $mypath`
username=postgres
dbname=beers

if [[ -n `psql -U $username -lqt | cut -d \| -f 1 | grep -w "$dbname"` ]]; then
    dropdb -U $username $dbname
fi
createdb -U $username $dbname

cd $mybase
psql -U $username -af create.sql $dbname
psql -U $username -af load.sql $dbname
