#!/usr/bin/env python

import argparse
import sqlite3
import sys
import json

import pandas

today = pandas.datetime.utcnow().date().isoformat()

parser = argparse.ArgumentParser("Create events for a subject")
parser.add_argument("subject")
parser.add_argument('-s', '--startdate', help="Start date", default=today)
parser.add_argument('-f', '--format', help="Output format", default='json',
                     choices=['json', 'ical'])
parser.add_argument('-o', '--outfile', help='Output file',
                    type=argparse.FileType('w'), default=sys.stdout)
parser.add_argument('-r', '--repeatcount', help='Number of repeat lectures',
                    type=int, default=17)
parser.add_argument('-d', '--datefile', type=argparse.FileType('r'),
                    help='JSON file with dates for two semesters')
args = parser.parse_args()

if args.datefile:
    import json
    dates = json.load(args.datefile)
else:
    import collections
    dates = collections.defaultdict(lambda: args.startdate)

#TODO: Use dates for creating output

days = {'Ma/Mo': 0,
        'Di/Tu': 1,
        'Wo/We': 2,
        'Do/Th': 3,
        'Vr/Fr': 4}

startdate = pandas.to_datetime(args.startdate)

c = sqlite3.connect('timetable.sqlite')

result = c.execute("select ModuleName, language, day, fromtime, totime, venue from timetable where modulename like ?", [args.subject])

def timeformat(time):
    return {'dateTime': time.isoformat(),
            'timeZone': 'Africa/Johannesburg',}

def eventtime(timestring, daystring):
    hours, minutes = map(int, timestring.split(":"))
    return startdate + pandas.Timedelta(days=days[daystring],
                                        hours=hours, minutes=minutes)

events = []
for subject, language, day, fromtime, totime, venue in result:
    d = {'summary': '{} {}'.format(subject, language),
         'location': venue,
         'start': timeformat(eventtime(fromtime, day)),
         'end': timeformat(eventtime(totime, day)),
         # see http://tools.ietf.org/html/rfc5545#section-3.8.6.2
         'recurrence': ['RRULE:FREQ=WEEKLY;COUNT={}'.format(args.repeatcount)],
         }
    events.append(d)

if args.format == 'json':
    json.dump(events, args.outfile)
if args.format == 'ical':
    import icalendar
    cal = icalendar.Calendar()
    for event in events:
        ievent = icalendar.Event()
        ievent.add('summary', event['summary'])
        ievent.add('dtstart', pandas.to_datetime(event['start']['dateTime']))
        ievent.add('dtend', pandas.to_datetime(event['end']['dateTime']))
        ievent.add('rrule', {'freq': 'weekly', 'count': args.repeatcount})
        cal.add_component(ievent)
    args.outfile.buffer.write(cal.to_ical())
    args.outfile.buffer.flush()
