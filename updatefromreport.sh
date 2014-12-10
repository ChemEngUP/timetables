#!/bin/bash

target=fulltable.csv
backup=fulltable_prev.csv
filename=engallmodules.csv
year=`cat targetyear`

[ -e $target ] && mv $target $backup

wget -q http://uptt.up.ac.za:90/csvfiles/engallmodules$year.csv -O - |\
 dos2unix |\
 sed -e 's/,[[:blank:]]*/,/g'\
     -e 's/[[:blank:]]*,/,/g'\
     -e 's/[[:blank:]]*$//g' \
 > $filename

./preparecsv.py "$filename" |  sed -f shorten.sed | ./extractcolumns.py --headerfile headers.txt --sort -o $target
cat extras.csv >> $target
date +"report_"$year"_%Y%m%d" > datafilename

diff $target $backup
