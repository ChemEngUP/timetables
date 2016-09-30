#!/usr/bin/env python3

import sys
import datetime
import shutil
import os
import re
import itertools
import glob

import email
import smtplib
import difflib
import logging

import argparse
parser = argparse.ArgumentParser(description='Generate timetables')
parser.add_argument('--sendmail', help='Send a notification e-mail',
                    action="store_true", default=False)
parser.add_argument('--debug', help='Print commands as they are written',
                    action="store_true", default=False)
parser.add_argument('--quiet', help='Print less',
                    action="store_true", default=False)
parser.add_argument('filename', nargs="?", help='XLS file to parse for timetable')
parser.add_argument('--nodiff', help="Don't do a diff on the files",
                    action="store_true", default=False)
parser.add_argument('--ignore', help='Ignore errors on system call',
                    action='store_true', default=False)
parser.add_argument('--calendar', action="store_true",
                    default=False,
                    help='Generate calendar entries')
parser.add_argument('--parallel', action="store_true",
                    default=False,
                    help='Try to parallelise')
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.debug
                          else (logging.INFO if not args.quiet
                                else logging.ERROR))

queue1 = []
queue2 = []
queues = [queue1, queue2]

def system(string, queue=False):
    logging.debug(string)
    if args.parallel and queue is not False:
        queue.append(string + '\n')
        return 0
    else:
        result = os.system(string)
        if not args.ignore and result != 0:
            raise Exception("Command processing error")
    return result

datestr = str(datetime.datetime.now())
logging.info("Run on " + datestr)

inputfilename = 'fulltable.csv'
backupfilename = 'fulltable_prev.csv'
lastrunfilename = 'fulltable_lastrun.csv'

# regenerate fulltable if filename specified
if args.filename:
    filterchain = " | dos2unix | sed -f shorten.sed | ./extractcolumns.py --headerfile headers.txt --sort -o {}".format(inputfilename)

    if os.path.exists(inputfilename):
        shutil.move(inputfilename, backupfilename)

    system('in2csv ' + args.filename + filterchain)
    system('cat extras.csv >> {}'.format(inputfilename))
    logging.info("Regenerated fulltable from " + args.filename)
    with open('datafilename', 'w') as datafilenamef:
        datafilenamef.write(args.filename)
else:
    logging.info("Assuming same data as last time or other source of data")

# logging.info("Building database") 
# import builddb
# builddb.build('fulltable.csv', 'timetable.sqlite')

import makeevents

if not args.nodiff:
    differ = difflib.HtmlDiff()
    diffs = differ.make_file(open(lastrunfilename), open(inputfilename),
                              "Previous version", "Current version",
                              context=True, numlines=0)
    with open('diffs.html', 'w') as f:
        f.write(diffs)

if args.sendmail:
    shutil.copy('mailhead.txt', 'mailbody.txt')

    msg = email.mime.multipart.MIMEMultipart()
    msg['Subject'] = "Timetable regenerated"
    msg['From'] = "carl.sandrock@up.ac.za"
    msg['To'] = ','.join(i.strip() for i in open('maillist') if not i.startswith('#'))
    msg.attach(email.mime.text.MIMEText(open('mailbody.txt').read()))
    if not args.nodiff:
        attachmentpart = email.mime.text.MIMEText(diffs, 'html')
        attachmentpart.add_header('Content-Disposition', 'attachment; filename="diffs.html')
        msg.attach(attachmentpart)

    s = smtplib.SMTP('localhost')
    s.sendmail(msg['From'], msg['To'].split(','), msg.as_string())
    s.quit()


datafilename = open('datafilename').read().strip()
# assuming the filename looks like timetable_2010_20090201.xls, parse out the pieces
datayear, datadate = re.match(r'.*_(\d{4})_(\d+).*', datafilename).groups()

outputdir = os.path.join("output", datayear)
subdiff = "./subdiff.py"

logging.info("Timetable for {} given on {}".format(datayear, datadate))

# backup old output
if os.path.exists(outputdir + '.old'):
    shutil.rmtree(outputdir + ".old")
if os.path.exists(outputdir):
    shutil.move(outputdir, outputdir + '.old')

# Generate 4 year and 5 year plan entries
departmentlist = {}
depts = []
for line in open('departmentlist'):
    code, afr, eng = line.strip().split("\t")
    departmentlist[code] = [afr + ' (4 jr)', eng + ' (4 yr)']
    departmentlist[code.lower()] = [afr + ' (5 jr)', eng + ' (5 yr)']
    depts += [code, code.lower()]

os.mkdir(outputdir)
indexfilename = os.path.join(outputdir, 'index.html')
indexfile = open(indexfilename, 'w')

def index(string):
    indexfile.write(string + '\n')


def checkdifferences(countfile, dirname, lang1, lang2):
    result = os.path.join(dirname, "diff_" + lang1 + lang2 + ".html")
    logging.info("    checking difference between {} and {} ".format(lang1, lang2))
    system(subdiff
           + " " + countfile + "." + lang1
           + " " + countfile + "." + lang2
           + " > " + result, queue=queue2)
    index('<li>Differences between <a href="' + result + '">1=' + lang1 + ', 2=' + lang2+ '</a></li>')


index("""
<html>
<script src="scripts/timetable.js"></script>

<body onload=hideall()>
<h1>Timetables for {}</h1>
<p>These timetables were automatically generated on {}.
Click on the headings to expand the options.</p>
<p>The original datafile was sent on {}.
Note that these timetables are only trustworthy near the date of the original
datafile for departments other than Chemical Engineering.</p>
""".format(datayear, datestr, datadate))

BADCHARS = str.maketrans({' ': '_',
                          '(': None,
                          ')': None})
def sanitize(unsafe):
    return unsafe.translate(BADCHARS)


# Make target directory
for dept in depts:
    name = departmentlist[dept][1]
    safename = sanitize(name)

    index("<h2 onclick=showhide(\"" + safename + "\")>" + name + "</h2>" )
    index('<div id="' + safename + '">')

    logging.info('Doing ' + name + '...')
    dirname = os.path.join(outputdir, safename)
    os.mkdir(dirname)
    for f in glob.glob(os.path.join('stylesheets', '*')):
        shutil.copy(f, dirname)

    xmlfile = os.path.join(dirname, 'timetable.xml')
    system('./ttable.py -o ' + xmlfile +
              ' --group ' + dept +
              ' --deptident "' + name + '"'
              ' --year ' + datayear +
              (' --debug' if args.debug else '') +
              ' --englishonly englishonly.txt' +
              ' < {}'.format(inputfilename))

    logging.info("  Running checks")

    # Generate subjects list
    countfile = xmlfile + ".count"
    subjectlist = os.path.join(dirname, 'subjectlist')
    system('cut -d" " -f 1 ' + countfile + '> ' + subjectlist)

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
        logging.info("  creating " + stylename)
        if 'tex' in stylename:
            outfilename = os.path.join(dirname, stylename + '.tex')
            system(' '.join(['xsltproc', '-o', outfilename, style, xmlfile]),
                   queue=queue1)
            logging.info("   - calling LaTeX")
            # TODO: Handle LaTeX errors
            system('cd ' + dirname + ';pdflatex -interaction=nonstopmode ' +
                   stylename + ' | grep "No pages" && false || true',
                   queue=queue2)
            index( '<a href="' + dirname + '/' + stylename + '.pdf">' + stylename[:-4] + ' (pdf)</a>')
        else:
            outfilename = os.path.join(dirname, stylename + '.html')
            system(' '.join(['xsltproc',
                             '-o', outfilename, style, xmlfile]), queue=queue2)
            index('<a href="' + dirname + '/' + stylename + '.html''">' + stylename + '</a>')
        index("</li>")
    index("</ol>")

    if args.calendar:
        logging.info("Generating calendars")
        index("<h3>Subject calendars</h3>")
        repeatcount = 17
        for subject in sorted(set(open(subjectlist).read().splitlines())):
            logging.info("  " + subject)
            shortsub = subject.replace(' ', '')
            subject = shortsub[:3] + ' ' + shortsub[3:]
            subfile = os.path.join(dirname, shortsub + '.ics')
            events = makeevents.readevents(subject, dept)
            makeevents.events_to_ical(events, open(subfile, 'w'))
            index("<a href='{}' download>{}</a> ".format(subfile, shortsub))

    index("</div>")

for queue in queues:
    with open('queue', 'w') as f:
        f.writelines(queue)
    system('parallel --bar < queue')

#TODO: combined PDF output
#logging.info("Combining pdf output for ...")
#for filename in glob.glob(outputdir + "/*/*.pdf"):
#    logging.info("  " + filename)
#    system('pdftk ' + outputdir/*/$filename.pdf cat output $outputdir/all$filename.pdf

index("</body></html>")

indexfile.close()

system("sed -i.bak 's," + outputdir + "/,,g' " + indexfilename)

shutil.copytree('scripts', os.path.join(outputdir, 'scripts'))
shutil.copy(inputfilename, lastrunfilename)
