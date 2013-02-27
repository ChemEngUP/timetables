#!/usr/bin/env python

import sys
import datetime
# TODO: Use logging module for logging!
#import logging
import shutil
import os
import re
import itertools
import glob
import subprocess
from email.mime.text import MIMEText
import smtplib
# TODO: Use argparse for argument handling

import argparse
parser = argparse.ArgumentParser(description='Generate timetables')
parser.add_argument('--sendmail', help='Send a notification e-mail', action="store_true", default=False)
parser.add_argument('filename', nargs="?", help='XLS file to parse for timetable')

args = parser.parse_args()


logfile = file('log', 'w')

def log(string, echo=False):
    if echo:
        print string
    print >> logfile, string

def system(string):
    #print string
    os.system(string)

datestr = str(datetime.datetime.now())
log("Run on" + datestr)


# regenerate fulltable if filename specified
if args.filename:
    if os.path.exists('fulltable.csv'):
        shutil.move('fulltable.csv', 'fulltable_prev.csv')

    system('xls2csv ' + args.filename[0] + ' | sed -f shorten.sed | ./extractcolumns.py --headerfile headers.txt --sort -o fulltable.csv')
    log("Regenerated fulltable from " + args.filename[0], echo=True)
    open('datafilename', 'w').write(args.filename[0])
else:
    print "Assuming same data as last time or other source of data"

if args.sendmail:
    shutil.copy('mailhead.txt', 'mailbody.txt')
    system('diff fulltable.csv fulltable_prev.csv | tee -a mailbody.txt')
    msg = MIMEText(open('mailbody.txt').read())
    msg['Subject'] = "Timetable regenerated"
    msg['From'] = "carl.sandrock@up.ac.za"
    msg['To'] = "carl.sandrock@up.ac.za,philip.devaal@up.ac.za"

    s = smtplib.SMTP('localhost')
    s.sendmail(msg['From'], msg['To'].split(','), msg.as_string())
    s.quit()


datafilename = open('datafilename').read().strip()

outputdir="output"
subdiff="./subdiff"

# assuming the filename looks like timetable_2010_20090201.xls, parse out the pieces
datayear, datadate = re.match(r'.*_(\d{4})_(\d+).*', datafilename).groups()

print "Timetable for %s given on %s" % (datayear, datadate)

# backup old output
if os.path.exists(outputdir + '.old'):
    shutil.rmtree(outputdir + ".old")
if os.path.exists(outputdir):
    shutil.move(outputdir, outputdir + '.old')

# Generate 4 year and 5 year plan entries
departmentlist = {}
depts = []
for line in file('departmentlist'):
    code, afr, eng = line.strip().split("\t")
    departmentlist[code] = [afr + ' (4 jr)', eng + ' (4 yr)']
    departmentlist[code.lower()] = [afr + ' (5 jr)', eng + ' (5 yr)']
    depts += [code, code.lower()]

os.mkdir(outputdir)
indexfilename = os.path.join(outputdir, 'index.html')
indexfile = open(indexfilename, 'w')

def index(string):
    print >> indexfile, string


def checkdifferences(countfile, dirname, lang1, lang2):
    result = os.path.join(dirname, "diff_" + lang1 + lang2 + ".html")
    print "    checking difference between",  lang1, "and", lang2
    system(subdiff + " " + countfile + "." + lang1 + " " + countfile + "." + lang2 + " > " + result)
    index('<li>Differences between <a href="' + result + '">1=' + lang1 + ', 2=' + lang2+ '</a></li>')


index("<html>")
for line in open('indexscript'):
    indexfile.write(line)

index("<body onload=hideall()>")
index("<h1>Timetables</h1>")
index("<p>These timetables were automatically generated on " + datestr + ".  Click on the headings to expand the options.</p>")


# Make target directory
for dept in depts:
    name = departmentlist[dept][1]
    # TODO: clean up this replace chain
    safename = name.replace(" ", '_').replace('(', '').replace(')', '')
    index("<h2 onclick=showhide(\"" + safename + "\")>" + name + "</h2>" )
    index('<div id="' + safename + '">')

    print 'Doing', name, '...'
    dirname = os.path.join(outputdir, safename)
    os.mkdir(dirname)
    for f in glob.glob(os.path.join('stylesheets', '*')):
        shutil.copy(f, dirname)

    xmlfile = os.path.join(dirname, 'timetable.xml')
    system('./ttable.py -o ' + xmlfile  +
              ' --group ' + dept +
              ' --deptident "' + name + '"'
              ' --year ' + datayear +
              ' < fulltable.csv')

    print "  Running checks"

    # Generate subjects list
    countfile = xmlfile + ".count"
    system('cut -d" " -f 1 ' + countfile + '> ' + dirname + '/subjectlist')

    # Generate language based counts
    for lang in ['A', 'E']:
        system('sed -n "/ ' + lang + ' /s/ ' + lang + '//p " ' + countfile + ' > ' + countfile + '.' + lang)

    # pull subject counts for this group
    system('grep -f yearbook/subjects_' + dept + '*.txt yearbook/counts.txt > ' + countfile + '.yearbook')

    # compare
    index("<h3>Differences</h3>")
    index("<p>The timetable is compared for consistency between the Afrikaans and English classes as well as with the yearbook.  Click a link.</p>")
    index("<ol>")

    for f1, f2 in itertools.combinations(['A', 'E', 'yearbook'], 2):
        checkdifferences(countfile, dirname, f1, f2)

    index("</ol>")

    # Run transforms
    index("<h3>Tables</h3>")
    index("<ol>")
    for style in glob.glob('transforms/*.xsl'):
    	stylename = os.path.basename(style)[:-4]
    	index("<li>")
    	print "  creating", stylename
    	if 'tex' in stylename:
            system(' '.join(['sabcmd -x', xmlfile, style, os.path.join(dirname, stylename + '.tex')]))
    	    print "   - calling LaTeX"
            # TODO: Handle LaTeX errors
    	    system('cd ' + dirname + ';pdflatex -interaction=nonstopmode ' +  stylename + ' | grep "No pages"')
    	    index( '<a href="' + dirname + '/' + stylename + '.pdf">' + stylename[:-4] + ' (pdf)</a>')
    	else:
    	    system('sabcmd -x ' + xmlfile + ' ' + style + ' ' + dirname + '/' + stylename + '.html')
    	    index('<a href="' + dirname + '/' + stylename + '.html''">' + stylename + '</a>')
    	index("</li>")
    index("</ol>")
    index("</div>")


#TODO: combined PDF output
#print "Combining pdf output for ..."
#for filename in glob.glob(outputdir + "/*/*.pdf"):
#    print "  ", filename
#    system('pdftk ' + outputdir/*/$filename.pdf cat output $outputdir/all$filename.pdf

index("</body></html>")

system("sed -i 's," + outputdir + "/,,g' " + indexfilename)


