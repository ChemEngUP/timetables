#!/usr/bin/env python

import pandas
import sys

import argparse
parser = argparse.ArgumentParser(description="Prepare a CSV file in the 2013 format for processing by ttable")
parser.add_argument('infile', nargs="?", help='filename to read')
parser.add_argument('-o, --outfile', nargs="?", help='Filename to write to, default stdin')

args = parser.parse_args()

d = pandas.read_csv(args.infile)
if 'outfile' in args:
    d.to_csv(args.outfile)
else:
    d.to_csv(sys.stdout)