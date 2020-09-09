#!/bin/sh

rsync -r --info=progress2 output/ root@chemeng.up.ac.za:/var/www/html/timetables/ && echo "Uploaded to chemeng.up.ac.za/timetables successfully"
