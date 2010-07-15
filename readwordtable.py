#!/usr/bin/env python

import csv, sys

def listify(v):
    if type(v) is list:
        return(v)
    else:
        return([v])

infile = csv.reader(file(sys.argv[1]))
venues = csv.reader(file(sys.argv[2]))
outfile = csv.writer(sys.stdout)

headers = infile.next()

for rec in infile:
    for lang, day, time in zip(*[listify(rec[i].strip().split())
                                 for i in [4, 5, 6]]):
        outfile.writerow(rec[0:3] + [lang, day, time] + rec[7:])
    
