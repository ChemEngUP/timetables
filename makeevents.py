#!/usr/bin/env python

import sqlite3
from datetime import datetime, timedelta
import pytz

tz = pytz.timezone('Africa/Johannesburg')

def parsedate(datestr):
    return datetime.strptime(datestr, "%Y-%m-%d")

def parsedatetime(datetimestr):
    return tz.localize(datetime.strptime(datetimestr, "%Y-%m-%dT%H:%M:%S"))

days = {'Ma/Mo': 0,
        'Di/Tu': 1,
        'Wo/We': 2,
        'Do/Th': 3,
        'Vr/Fr': 4}

c = sqlite3.connect('timetable.sqlite')

def timeformat(time):
    return {'dateTime': time.isoformat(),
            'timeZone': 'Africa/Johannesburg',}

def eventtime(timestring, daystring, startdate):
    hours, minutes = map(int, timestring.split(":"))
    return startdate + timedelta(days=days[daystring],
                                 hours=hours, minutes=minutes)

def readevents(subject, discipline):
    result = c.execute("select ModuleName, language, day, fromtime, totime, "
                       "venue, startdate, repeatcount "
                       "from timetable natural join dates "
                       "where modulename = ? and "
                       "discipline = ?",
                       [subject, discipline])

    events = []
    for subject, language, day, fromtime, totime, venue, startdate, repeatcount in result:
        startdate = parsedate(startdate)
        d = {'summary': '{} {}'.format(subject, language),
             'location': venue,
             'start': timeformat(eventtime(fromtime, day, startdate)),
             'end': timeformat(eventtime(totime, day, startdate)),
             # see http://tools.ietf.org/html/rfc5545#section-3.8.6.2
             'recurrence': ['RRULE:FREQ=WEEKLY;COUNT={}'.format(repeatcount)],
             'repeatcount': repeatcount,
             }
        events.append(d)
    return events

def events_to_json(events, outfile):
    import json
    json.dump(events, outfile)

def events_to_ical(events, outfile):
    import icalendar
    cal = icalendar.Calendar()
    for event in events:
        ievent = icalendar.Event()
        ievent.add('summary', event['summary'])
        ievent.add('location', event['location'])
        ievent.add('dtstart', parsedatetime(event['start']['dateTime']))
        ievent.add('dtend', parsedatetime(event['end']['dateTime']))
        ievent.add('rrule', {'freq': 'weekly', 'count': event['repeatcount']})
        cal.add_component(ievent)
    outfile.buffer.write(cal.to_ical())
    outfile.buffer.flush()


if __name__ == '__main__':
    import sys
    import argparse
    today = datetime.utcnow().date().isoformat()

    parser = argparse.ArgumentParser("Create events for a subject")
    parser.add_argument("subject")
    parser.add_argument('-s', '--startdate', help="Start date", default=today)
    parser.add_argument('-f', '--format', help="Output format", default='json',
                         choices=['json', 'ical'])
    parser.add_argument('-o', '--outfile', help='Output file',
                        type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('-c', '--discipline',
                        help="Department code to match")
    args = parser.parse_args()

    events = readevents(args.subject, args.discipline)

    if args.format == 'json':
        events_to_json(events, args.outfile)
    if args.format == 'ical':
        events_to_ical(events, args.outfile)
