#!/usr/bin/env python

import sqlite3
from itertools import product

with open('departmentlist') as f:
    disciplines = [line.split()[0] for line in f]

disciplines += [d.lower() for d in disciplines]

times = ["{:02d}:31".format(block) for block in range(7, 17+1)]

days = ["Ma/Mo",
        "Di/Tu",
        "Wo/We",
        "Do/Th",
        "Vr/Fr"]

semesters = ['S1']

years = range(1, 4+1)

languages = ['A', 'E']

db = sqlite3.connect('timetable.sqlite')

query = """
SELECT count(*) FROM timetable
WHERE (discipline=?)
       AND (? BETWEEN fromtime AND totime)
       AND Day=?
       AND YearPhase=?
       AND Year=?
       AND (Language=? OR Language='B')
"""

# Naively query which blocks are open
# Strategy: check whether %i:31 is in a session for this discipline
openblocks = []

for elements in product(disciplines, times, days, semesters, years, languages):
    [(number,)] = db.execute(query, elements)
    if number==0:
        openblocks.append(elements)

# Insert this into the database
db.execute("DELETE FROM openblocks")
db.executemany("INSERT INTO openblocks VALUES (?,?,?,?,?,?)", openblocks)
db.commit()
