#!/usr/bin/env python

import sys
import string

for line in sys.stdin:
    theline = line.strip()
    fields = theline.split('\t')
    for group in fields[-1].split(' '):
        print string.join(fields[0:-2] + [group[0], group[1]], '\t')
