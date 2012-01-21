#!/usr/bin/env python

import BeautifulSoup
import mechanize
import csv
import sys
import logging
logging.basicConfig(level=logging.INFO)

headers = ["ModuleName", "Group", "Language", "Activity", "ING", "YearPhase", 
           "Day", "Time", "Venue", "oldENGCode", "ENGcode"]

url = "http://uptt.up.ac.za:90/eng_timetable.html"

daylookup = {'Monday': 'Ma/Mo', 
             'Tuesday': 'Di/Tu',
             'Wednesday': 'Wo/We', 
             'Thursday': 'Do/Th',
             'Friday': 'Vr/Fr'}

def engcodesplit(codestr):
    return (codestr[i:i+2] for i in range(0, len(codestr), 2)) 

def parse(rowvals):
    logging.debug(rowvals)
    try:
        code, YearPhase, longDay, From, To, Venue, ENGcodes = rowvals
        _, ModuleName, Group, Language, Activity = code.split('/')
        Day = daylookup[longDay]
        Time = From[0:-3] + "-" + To[0:-5] + '20'
        if ENGcodes:
            for ENGcode in engcodesplit(ENGcodes.replace(' ', '')):
                yield([ModuleName, Group, Language, Activity, "ING",  YearPhase,
                       Day, Time, Venue, ENGcode, ENGcode])
    except:
        logging.error("Problem with this record: " + str(rowvals))
        yield []
        
def readinto(outfilename):
    br = mechanize.urlopen(url)
    r = BeautifulSoup.BeautifulSoup(br.read())
    
    table = r.find(id='myTable')
    
    out = csv.writer(open(outfilename, 'w'))
    out.writerow(headers)
    
    for row in table.findAll('tr'):
        rowvals = [i.string for i in row.findAll('td')]
        if rowvals:
            parsedvals = parse(rowvals)
            if parsedvals:
                out.writerows(parsedvals)
            
if __name__ == "__main__":
    outfilename = sys.argv[1]
    readinto(outfilename)
