#!/usr/bin/env python

import pandas
import sqlite3

db = sqlite3.connect('timetable.sqlite')

df = pandas.read_csv('fulltable.csv')

times = pandas.DataFrame(df.Time.str.split('-').tolist(),
                         columns=['fromtime', 'totime'])

df = df.join(times)

df['Discipline'] = df.ENGcode.str[0]
df['Year'] = df.ENGcode.str[1].apply(int)

df.to_sql('timetable', db, if_exists='replace', index=False)

venues = set(v.strip() for v in sum((v.replace(" and ", "; ").split(';')
                                     for v in df.Venue.unique()), []) if len(v) > 3)

pandas.Series(list(venues), name="name").to_sql('venues', db, if_exists='replace', index=False)

# TODO: should I close the db?
