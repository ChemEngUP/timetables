#!/usr/bin/env python

# Author: Carl Sandrock
# Date: 20120206

import csv
import sys
import argparse
import logging
import os.path

parser = argparse.ArgumentParser(description="Extract certain named columns from a CSV file")
parser.add_argument('infile', default=[sys.stdin], nargs="*",
                    type=argparse.FileType('r'))
parser.add_argument('--outfile', '-o', default=sys.stdout,
                    type=argparse.FileType('w'))
parser.add_argument('--columns', '-c', nargs=1, type=str,
                    help="Column names to retain")
parser.add_argument('--headerfile', '-f', type=str,
                    help="Read column names from a file - one name per line")
parser.add_argument('--listheaders', '-l', action="store_true", default=False,
                    help="List the header lines in the input file")
parser.add_argument('--sort', '-s', action="store_true", default=False)

if __name__ == '__main__':
    args = parser.parse_args()

    outf = csv.writer(args.outfile)

    if args.columns:
        columns = args.columns[0].split(',')
    else:
        if args.headerfile:
            if os.path.exists(args.headerfile):
                columns = [w.strip() for w in open(args.headerfile)]
            else:
                logging.error("Bad header file")
                sys.exit(2)
        else:
            columns = None

    if not args.listheaders:
        outf.writerow(columns)
        data = []

    for infile in args.infile:
        inf = csv.DictReader(infile)
        incolumns = inf.fieldnames
        if args.listheaders:
            outf.writerows(enumerate(incolumns))
        else:
            data += [[row[column] for column in columns] for row in inf]

    if args.sort:
        data.sort()
    outf.writerows(data)
