#/usr/bin/env python

import sys
import re
import collections

import argparse
parser = argparse.ArgumentParser(
    description='Count the contact time in the yearbook')
parser.add_argument('filename', default=sys.stdin, type=argparse.FileType('r'),
                    help='The file to be processed')
parser.add_argument('--debug', help='Print debugging output', 
                    default=False, action='store_true')
args = parser.parse_args()

import logging
loglevel = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(level=loglevel)

reading = False

subre = re.compile('^([A-Z][A-Z][A-Z]).([0-9][0-9][0-9])')
contactre = re.compile('Contact time: (.*)')
contactitem = re.compile('([0-9])+ (.)pw')

columns = ['L', 'P', 'O']
equivalence = {'d': 'O',
               'l': 'L',
               'p': 'P',
               's': 'O',
               't': 'P',
               'o': 'O'}

for line in args.filename:
    if line.startswith('ALPHABETICAL LIST OF MODULES IN THE'):
        reading = True
        continue

    if not reading: continue
    
    m = subre.match(line)
    if m:
        logging.debug('Matched subject: {}'.format(line.strip()))
        subject = ''.join(m.groups(0))
        continue

    m = contactre.match(line)
    if m:
        logging.debug('Matched contact time: {}'.format(line.strip()))
        contact = collections.defaultdict(lambda: '0')
        periods = contactitem.findall(m.groups(1)[0])
        for (lnum, ltype) in periods:
            if ltype in equivalence:
                contact[equivalence[ltype]] = lnum
        print subject, ' '.join(contact[c] for c in columns)
