#!/usr/bin/env python

import sys
import jinja2

filenames = sys.argv[1:]
N = len(filenames)

files = [sorted(open(filearg).readlines()) for filearg in filenames]

subjects = set()
lookup = [dict() for f in files]
for i, f in enumerate(files):
    for l in f:
        fields = l.strip().split(" ")
        subjects.add(fields[0])
        numbers = list(map(int, fields[1:]))
        numbers.append(sum(numbers))
        lookup[i][fields[0]] = numbers


lines = []

for subject in sorted(subjects):
    line = {'subject': subject}
    matchflag = "match"
    row = []
    for i in range(N):
        if subject in lookup[i]:
            vals = lookup[i][subject]
            matches = [lookup[j][subject] for j in range(N)
                       if i != j and subject in lookup[j]]
            matchentries = []
            row.append({'type': 'matches', 'matchentries': matchentries})
            for vi, entry in enumerate(vals):
                if False in [m[vi] == entry for m in matches]:
                    match = False
                    matchflag = "mismatch"
                else:
                    match = True
                matchentries.append([match, entry])
        else:
            row.append({'type': 'missing'})
            matchflag = "mismatch"
    line['row'] = row
    line['matchflag'] = matchflag
    lines.append(line)

# TODO: This should be read from an environment
template = jinja2.Template(open('templates/subdiff.html').read())

print(template.render(filen=range(1, N+1),
                      headings=["L", "P", "O", "t"],
                      lines=lines))
