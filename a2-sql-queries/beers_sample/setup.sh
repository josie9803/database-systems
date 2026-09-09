#!/bin/bash

mypath=`realpath $0`
mybase=`dirname $mypath`
username=postgres
dbname=beers

if [[ -n `psql -lqt | cut -d \| -f 1 | grep -w "$dbname"` ]]; then
    dropdb $dbname
fi
createdb $dbname

cd $mybase
psql -U $username -af create.sql $dbname
psql -U $username -af load.sql $dbname
