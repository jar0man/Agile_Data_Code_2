#!/usr/bin/env bash
#
# Script to download data for book
#
mkdir data

#
# Get airplane data
#

# Get on-time records for all flights in 2015 - 273MB
curl -Lko $DATASCIENCE_HOME/data/On_Time_On_Time_Performance_2015.csv.bz2 \
    http://s3.amazonaws.com/agile_data_science/On_Time_On_Time_Performance_2015.csv.bz2

# Get openflights data
curl -Lko /tmp/airports.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat
mv /tmp/airports.dat $DATASCIENCE_HOME/data/airports.csv

curl -Lko /tmp/airlines.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat
mv /tmp/airlines.dat $DATASCIENCE_HOME/data/airlines.csv

curl -Lko /tmp/routes.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat
mv /tmp/routes.dat $DATASCIENCE_HOME/data/routes.csv

curl -Lko /tmp/countries.dat https://raw.githubusercontent.com/jpatokal/openflights/master/data/countries.dat
mv /tmp/countries.dat $DATASCIENCE_HOME/data/countries.csv

# Get FAA data
curl -Lko $DATASCIENCE_HOME/data/aircraft.txt http://av-info.faa.gov/data/ACRef/tab/aircraft.txt
curl -Lko $DATASCIENCE_HOME/data/ata.txt http://av-info.faa.gov/data/ACRef/tab/ata.txt
curl -Lko $DATASCIENCE_HOME/data/compt.txt http://av-info.faa.gov/data/ACRef/tab/compt.txt
curl -Lko $DATASCIENCE_HOME/data/engine.txt http://av-info.faa.gov/data/ACRef/tab/engine.txt
curl -Lko $DATASCIENCE_HOME/data/prop.txt http://av-info.faa.gov/data/ACRef/tab/prop.txt
