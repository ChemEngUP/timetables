#!/usr/bin/env python

import BeautifulSoup
import argparse
import mechanize
import csv
import sys
import logging
logging.basicConfig(level=logging.INFO)

headers = ["Year", "ModuleName", "Group", "Language", "Activity", "YearPhase", 
           "Day", "Time", "Venue", "ENGcode"]

parser = argparse.ArgumentParser(description="Download timetable data from UP web")
parser.add_argument("url", default="http://uptt.up.ac.za:90/eng_timetable.html", 
                    nargs="?", type=str)
parser.add_argument('--outfile', '-o', default=sys.stdout, 
                    type=argparse.FileType('w'))

def engcodesplit(codestr):
    return (codestr[i:i+2] for i in range(0, len(codestr), 2)) 

def parse(row):
    logging.debug(row)
    try:
        code, YearPhase, Day, From, To, Venue, ENGcodes = row
        Year, ModuleName, Group, Language, Activity = code.split('/')
        Time = From[0:-3] + "-" + To[0:-5] + '20'
        return([Year, ModuleName, Group, Language, Activity, YearPhase,
               Day, Time, Venue, ENGcodes])
    except:
        logging.error("Problem with this record: " + str(row))
        
def downloadtable(url):
    br = mechanize.urlopen(url)
    soup = BeautifulSoup.BeautifulSoup(br.read())
    
    table = soup.find(id='myTable')
    for row in table('tr'):
        yield [i.string for i in row('td')]
            
if __name__ == "__main__":
    args = parser.parse_args()
    out = csv.writer(args.outfile)
    out.writerow(headers)
    out.writerows(parse(row) for row in downloadtable(args.url) if row)
