#!/bin/bash

target=fulltable.csv
backup=fulltable_prev.csv
lastrun=fulltable_lastrun.csv
filename=engallmodules.csv
year=`cat targetyear`
#url="http://uptt.up.ac.za:90/csvfiles/engallmodules$year.csv"
#url="http://upnet.up.ac.za/timetables/csvfiles/engallmodules$year.csv"

# Since 2016
url="http://www1.up.ac.za/tt/csvfiles/engallmodules$year.csv"

[ -e $target ] && mv $target $backup

wget -q "$url" -O - |\
 dos2unix |\
 sed -e 's/,[[:blank:]]*/,/g'\
     -e 's/[[:blank:]]*,/,/g'\
     -e 's/[[:blank:]]*$//g' \
 > $filename

./preparecsv.py "$filename" |  sed -f shorten.sed | ./extractcolumns.py --headerfile headers.txt --sort -o $target
cat extras.csv >> $target
date +"report_"$year"_%Y%m%d" > datafilename

dos2unix $target

diff $target $lastrun
