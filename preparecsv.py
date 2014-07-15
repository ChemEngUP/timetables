#!/usr/bin/env python

import pandas
import sys

import argparse
parser = argparse.ArgumentParser(description="Prepare a CSV file in the 2013 format for processing by ttable")
parser.add_argument('infile', nargs="?", help='filename to read')
parser.add_argument('--outfile', help='Filename to write to, default stdout', 
                    nargs="?", 
                    type=argparse.FileType, 
                    default=sys.stdout, 
                    )

args = parser.parse_args()

d = pandas.read_csv(args.infile, encoding='utf-8-sig').dropna(how='all')

# Source file:
# ModDesc1  NADescr  ActGrp1  ActLang1  ActNr1  DBDayName  FromTime  ToTime  LocDesc       SSet  SSetLang
# ABV 320   S2       G01      A         L1      Wednesday  13:30     14:30   EB/EMB 4-151  A
# ABV 320   S2       G01      A         L1      Wednesday  13:30     14:30   EB/EMB 4-151  (B4)  A
# Target  file:
# ModuleName  Group  Language  Activity  YearPhase  Day    Time         Venue        ENGcode
# ABV 320     G01    A         L1        S2         Wo/We  13:30-14:20  EMB 4-151    B4
# ABV 320     G01    A         L2        S2         Do/Th  14:30-15:20  EMB 4-151    B4

# First, just rename columns
renamecols = {'ModDesc1': 'ModuleName',
              'NADescr': 'YearPhase',
              'ActGrp1': 'Group',
              'ActNr1': 'Activity',
              'DBDayName': 'Day',
              'LocDesc': 'Venue',
              'SSet': 'ENGcode',
              'SSetLang': 'Language',
             }

d.rename(columns=renamecols, inplace=True)
    
# Then merge FromTime and ToTime
d['Time'] = d.FromTime + '-' + d.ToTime

# and remove the brackets from the ENGcode
d.ENGcode = d.ENGcode.str.strip('()').str.replace(' 5jr', '')

d.to_csv(args.outfile, index=False)
