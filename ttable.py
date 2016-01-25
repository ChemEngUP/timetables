#!/usr/bin/env python3

# FIXME: this does three passes at the moment -- should be only one!

import xml.dom.minidom
import sys
import time
import getopt
import os
import os.path
import csv

ver = "1.2"
longdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
day_afr = ['Ma', 'Di', 'Wo', 'Do', 'Vr']
day_eng = ['Mo', 'Tu', 'We', 'Th', 'Fr']
day_both = ["/".join(i) for i in zip(day_afr, day_eng)]

def version():
    print("ttable version", ver)
    print("""Copyright (C) 2016 Carl Sandrock

ttable comes with NO WARRANTY, to the extent permitted by law
""")

def usage():
    """Print some descriptive text about the usage of this script"""
    print("""
Usage: ttable -[hqv] csvfile [-o outputfile] [-i ignorefile] [-s subjectsfile] [-c countfile] [-y year]
Options
   -h, --help       Prints this message
   -q, --quiet      Supresses most of the output
   -v, --verbose    Prints more information
   -d, --debug      Prints even more info than verbose mode, useful
                    for debugging
   -c, --countfile  specify a target for a 'count file', which contains counts
                    of different types of lectures.  Defaults to outfile
   -g, --group      specify a group to match against when generating the
                    table
   -i, --ignorefile what subjects should be ignored?
   -I, --deptident  specify a string use as the departmental identifier
   -o, --outfile    specify output file, defaults to standard output
   -y, --year       specify year to be printed on the timetables
                    defaults to this year
   -l, --languagemerge Merge identical classes for A and E at same time to B
""")
    return None

def fixup_arg(optarg, optshort, optlong):
    """Normalise options, getting rid of leading -- and keeping only
    full option name -- rudely stripped from chemgen"""
    opt = optarg[0]
    arg = optarg[1]

    # Get rid of trailing = and :
    optshort = [o[0] for o in optshort];
    for (i, o) in enumerate(optlong):
        if o.endswith('='):
            optlong[i] = o[:-1]

    # we don't have to check if the option is in the list or not, as
    # the parsing library takes care of that for us, raising an
    # exception which is handled in the processoptions function

    if opt.startswith('--'): # indicating long option
        opt = opt.lstrip('-')
    else:
        opt = optlong[optshort.index(opt.lstrip('-'))]

    return [opt, arg]

def processoptions(argv):
    """Process commandline options and respond to the request for help and
    version information."""

    # keep options seperate, but reconstitute when calling getopt
    optshort = ["h", "q", "v", "d", "V", "o:", "g:", "I", "c:", "y", "l"]
    optlong = ["help", "quiet", "verbose", "debug", "version", "outfile=", "group=", "deptident=", "countfile=", "year=", "languagemerge"]

    try:
        opts, args = getopt.getopt(argv, \
                                   ".".join(optshort), \
                                   optlong)

    except getopt.GetoptError:
        print("ttable: unrecognised input argument")
        print()
        usage()
        sys.exit(2)

    options = dict([fixup_arg(elem, optshort, optlong) for elem in opts])

    options.setdefault("subjectsfile", os.path.join('.', 'subjects.txt'))
    options.setdefault("ignorefile", os.path.join('.', 'ignore.txt'))
    options.setdefault("deptident", "Chemical Engineering")
    options.setdefault("group", "C")
    options.setdefault("year", time.strftime("%Y"))

    if "outfile" in options:
        options.setdefault("countfile", options["outfile"] + '.count')

    if "version" in options:
        version()
        sys.exit(0)

    if "help" in options:
        usage()
        sys.exit(0)

    if "verbose" in options:
        print("Options:")
        for key, value in options.items():
            print(key, end=' ')
            if value: print('=', value)
            else: print('on')

    return options

def checkoptions(options):
    """Check the validity of the options sent.  Currently only checks
    for the existance of the input and output directories."""

    for opt in ['ignorefile', 'subjectsfile']:
        if not os.path.exists(options[opt]):
            print(options[opt], "does not exist")
            sys.exit(2)

def listify(thing):
    if type(thing) is list:
        return thing
    else:
        return [thing]

def wantmatch(entry, wanted):
    retval = True
    for field in list(wanted.keys()):
        for want in listify(wanted[field]):
            entrymatches = False
            for ent in listify(entry[field]):
                entrymatches |= ent == want
            retval &= entrymatches
    return retval

def ignorematch(entry, ignore):
    retval = True
    for item in ignore:
        retval |= wantmatch(entry, item)

def periodnumber(timestring):
    return int(timestring[0:2]) - 6

def spanstring(entry):
    startperiod = periodnumber(entry["starttime"])
    endperiod = periodnumber(entry["endtime"]) - 1

    if endperiod == startperiod: # only one period
        return '%i' % startperiod
    else:
        return '%i - %i' % (startperiod, endperiod)

def venuenames(venuestring):
    # Find English and Afrikaans names for venues
    # FIXME: This is a real pain to code, so I am going to defer
    if '/' in venuestring:
        return (venuestring, venuestring)
    else:
        return (venuestring, venuestring)

def parsesubjectsfile(filename):
    responsible = dict()
    personnel = set()
    names = dict()
    for line in open(filename):
        sub, names["A"], names["E"] = line.strip().split('\t')
        if names["E"] == "=":
            names["E"] = names["A"]
        for lang in ["A", "E"]: names[lang] = names[lang].split('/')
        names["B"] = list(filter(len, set(names["A"] + names["E"])))
        responsible[sub] = dict([lang,'/' + '/'.join(n) + '/']
                                 for lang,n in names.items())
        personnel.update(names["B"])
    return responsible, personnel

def parseignorefile(filename):
    ignore = []
    igfile = open(filename)
    igheadings = igfile.readline().strip().split(',')
    ignore = []
    for line in igfile:
        t = dict(list(zip(igheadings, line.strip().split(','))))
        ignore.append(t)
    igfile.close()
    return ignore

def conditiontime(t):
    """ Adjust times of the form 9:30 to 09:30 """
    if len(t) != 5:
        return "0" + t
    else:
        return t

def parseday(daystr):
    """ Attempt to parse the day string input to a shortened date string """
    if daystr in longdays:
        i = longdays.index(daystr)
    elif daystr in day_both:
        i = day_both.index(daystr)
    else:
        print('Error parsing day string', daystr)
        raise ValueError
    return day_both[i]

def readcsv(incsv, ignore, wanted, options):
    entries = [];
    neededfields = set(("ModuleName", "YearPhase", "ENGcode", "Language", "Activity", "Day", "Venue"))
    for t in incsv:
        if len(t) < 5 or all(len(i)==0 for i in t) or any(t[k] is None for k in neededfields):
            continue
        # Use heading names for a dict in the listings
        if 'debug' in options: print(t)
        sub = t["ModuleName"].replace(' ', '')
        ttime = list(map(conditiontime, t["Time"].split('-')))
        if len(ttime) != 2:
            continue
        starttime, endtime = ttime
        if endtime.endswith('30'):
            endtime = endtime[:-2] + '20'
        classtype = t["YearPhase"] # quarter/semester/year
        realname = sub
        if classtype.startswith('K'): # quarter
            q = int(classtype[1])
            semester = (q-1) / 2 + 1
            sub = "Q%i: %s" % (q, sub)
        elif classtype.startswith('S'):
            semester = int(classtype[1])
        elif classtype.startswith('J'):
            semester = [1, 2]

        for sem in listify(semester):
            #TODO: Make this cleanup more generic
            deltable = {c: None for c in "`' (),"}
            engcodes = t["ENGcode"].translate(deltable)
            groups = engcodes[0::2]
            years = list(map(int, engcodes[1::2]))
            assert len(groups)==len(years), "Problem parsing ENGcode " + engcodes
            for group, year in set(zip(groups, years)):
                entry = { 'module': sub,
                          'semester': "S%i" % sem,
                          'language': t["Language"],
                          'session': t["Activity"],
                          'day': parseday(t["Day"]),
                          'starttime': starttime,
                          'endtime': endtime,
                          'venue': t["Venue"],
                          'group': group,
                          'year': year,
                          'realname': realname }
                if "debug" in options: print(entry)
                if wantmatch(entry, wanted) and not ignorematch(entry, ignore):
                    entries.append(entry)
                if "debug" in options: print("matches", wanted, "but not", ignore)
    if "debug" in options: print(entries)

    return entries

def mergetimes(entries):
    # Merge times

    # FIXME: At the moment it is assumed that only adjacent items will
    # have overlapping times
    mergedentries = []
    if len(entries) > 0:
        current = entries[0];
        matchkeys = ['module', 'semester', 'language', 'day', \
                 'venue', 'group', 'year']

        for entry in entries:
            if all(entry[key] == current[key] for key in matchkeys) \
               and entry['starttime'] == current['endtime']:
                # contiguous period
                current['endtime'] = entry['endtime']

            else:
                mergedentries.append(current)
                current = entry

    return mergedentries

def mergevenues(entries):
    mergedentries = []
    for entry in entries:
        for matchentry in mergedentries: # find match
            if all(entry[key]==matchentry[key] for key in ["module", "language"]):
                matchentry["venue"] += ", " + entry["venue"]
                break
        else: # no match found, so add new entry
            mergedentries.append(entry.copy())
    return mergedentries

def processentries(entries, mergedentries, responsible, personnel, options):
    # FIXME: This function is really, really ugly.  There must be a
    # better way to handle the hierarchy than the explicit for loops I
    # have at the moment.
    outputdoc = xml.dom.minidom.Document()
    rootElement = outputdoc.createElement("timetable")
    rootElement.setAttribute('year', options["year"])
    outputdoc.appendChild(rootElement)

    # Information about the run
    geninfo = outputdoc.createElement("geninfo")
    geninfo.setAttribute('generator', 'ttable')
    geninfo.setAttribute('version', ver)
    geninfo.setAttribute('date', time.strftime('%Y-%m-%d'))
    geninfo.setAttribute('time', time.strftime('%H:%M'))
    geninfo.setAttribute('dept', options["deptident"])
    rootElement.appendChild(geninfo)

    # Personnel info
    # FIXME: this should include all information
    personnelElement = outputdoc.createElement("personnel")
    for person in personnel:
        personElement = outputdoc.createElement("person")
        personElement.setAttribute("name", person)
        personnelElement.appendChild(personElement)
    rootElement.appendChild(personnelElement)

    semestersElement = outputdoc.createElement("semesters")
    rootElement.appendChild(semestersElement)
    yearsElement = outputdoc.createElement("years")
    rootElement.appendChild(yearsElement)

    for semester in range(1, 3):
        semesterElement = outputdoc.createElement("semester")
        semesterElement.setAttribute("number", '%i' % semester)
        semestersElement.appendChild(semesterElement)
        for period in range(1, 12):
            periodstring = '%02i:30' % (period+6)
            periodElement = outputdoc.createElement("period")
            periodElement.setAttribute("number", '%i' % period)
            periodElement.setAttribute("starttime", periodstring)
            semesterElement.appendChild(periodElement)
            for year in range(1, 5):
                yearElement = outputdoc.createElement("year")
                yearElement.setAttribute("number", '%i' % year)
                periodElement.appendChild(yearElement)
                for day in day_both:
                    dayElement = outputdoc.createElement("day")
                    dayElement.setAttribute("name", day)
                    yearElement.appendChild(dayElement)
                    matchingmodules = [entry for entry in entries \
                           if (entry["starttime"] <= periodstring \
                               and entry["endtime"] >= periodstring) \
                           and entry["semester"] == 'S%i' % semester \
                           and entry["year"] == year \
                           and entry["day"] == day]
                    if len(matchingmodules) > 0:
                        # merge same module for both languages
                        if "languagemerge" in options:
                            if len(matchingmodules) == 2:
                                if all(matchingmodules[0][key] \
                                       == matchingmodules[1][key] \
                                       for key in ["module", "venue"]):
                                   matchingmodules = [matchingmodules[0]]
                                   matchingmodules[0]["language"] = "B"

                        for entry in mergevenues(matchingmodules[:]):
                            moduleElement = outputdoc.createElement("module")
                            moduleElement.setAttribute("venue", entry["venue"])
                            moduleElement.setAttribute("name", entry["module"])
                            moduleElement.setAttribute("language", entry["language"])
                            if entry["module"] in responsible:
                                moduleElement.setAttribute("responsible", responsible[entry["module"]][entry["language"]])
                            moduleElement.setAttribute("type", entry["session"][0])
                            dayElement.appendChild(moduleElement)

    return outputdoc

def nperiods(start, end):
    return int(end.split(':')[0]) - int(start.split(':')[0])

def countentries(entries):
    counts = dict()
    for entry in entries:
        l = entry["language"]
        if l == "B":
            l = ["A", "E"]
        for lang in listify(l):
            ltype = entry["session"][0]
            if ltype == "T":
                ltype = "P"
            assert ltype in ["L", "P", "O"], "Unknown lecture type encountered"
            key = (entry["realname"], ltype, lang)
            n = nperiods(entry["starttime"], entry["endtime"])
            if key in counts:
                counts[key] += n
            else:
                counts[key] = n
    return counts

def main(argv):
    options = processoptions(argv)
    checkoptions(options)

    [responsible, personnel] = parsesubjectsfile(options["subjectsfile"])
    ignore = parseignorefile(options["ignorefile"])
    if "verbose" in options: print(ignore)

    wanted = {"group": options["group"]}

    infile = csv.DictReader(sys.stdin)

    entries = readcsv(infile, ignore, wanted, options)
    mergedentries = mergetimes(entries)
    counts = countentries(entries)
    outputdoc = processentries(entries, mergedentries, responsible, personnel, options)

    if "outfile" in options:
        outputdoc.writexml(open(options["outfile"], 'w'),
                           indent="  ", addindent="  ", newl="\n")
    else:
        print(outputdoc.toprettyxml("  "))

    if "countfile" in options:
        countfile = open(options["countfile"], 'w')
        subs = set([key[0] for key in counts])
        for sub in sorted(subs):
            for lang in ["A", "E"]:
                print(sub, lang, end=' ', file=countfile)
                for act in ["L", "P", "O"]:
                    key = (sub, act, lang)
                    if key in counts:
                        print(counts[key], end=' ', file=countfile)
                    else:
                        print("0", end=' ', file=countfile)
                print(file=countfile)
        countfile.close()

if __name__ == "__main__":
    main(sys.argv[1:])
