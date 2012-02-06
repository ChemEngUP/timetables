#/usr/bin/env python

import sys
import re
import collections

reading = False

subre = re.compile('^([A-Z][A-Z][A-Z]).([0-9][0-9][0-9])')
contactre = re.compile('Contact time: (.*)')
contactitem = re.compile('([0-9])+ (.)pw')

columns = ['L', 'P', 'O']
equivalence = {'d': 'O',
               'l': 'L',
               'p': 'P',
               's': 'O',
               't': 'P'}

for line in file(sys.argv[1]):
    if line.startswith('ALPHABETICAL LIST OF MODULES IN THE'):
        reading = True
        continue

    if not reading: continue
    
    m = subre.match(line)
    if m:
        subject = ''.join(m.groups(0))
        continue

    m = contactre.match(line)
    if m:
        contact = collections.defaultdict(lambda: '0')
        periods = contactitem.findall(m.groups(1)[0])
        for (lnum, ltype) in periods:
            if ltype in equivalence:
                contact[equivalence[ltype]] = lnum
        print subject, ' '.join(contact[c] for c in columns)
