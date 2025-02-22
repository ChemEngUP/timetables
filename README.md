# Timetable generation tooling

The files in this repository gather the tooling for generating timetables currently hosted at http://chemeng.up.ac.za/timetables

## Prerequisites/installation

Python requirements are captured in `environment.yml` which can be used to spin up a conda environment for the project:

```
conda env create -f environment.yml
```

Additional tools required:

* GNU Make
* rsync
* sed
* awk
* xsltproc

## Processing

Normal processing steps involve running `make`. The default entry point will download the timetable data, process it and upload it to chemeng. Check the `Makefile` for details on running these processes separately.


## Legacy documentation - old process


To use this tool, the following things have to be in place:

1. Timetable data

An Excel file containing data under the following headings (in any order)
Heading	      Sample 
ModuleName    ABV 320	
YearPhase     S2	
Group	      G01	
Language      A	
Activity      L1	
Day	      Wo/We	
Time	      13:30-14:20	
Venue	      EMB 4-151	
ENGcode	      B4	

This file is converted to "fulltable" using xls2csv


2. Lecturer data

A text file called 'subjects.txt', containing subject name, Afrikaans
lecturer and English lecturer in three tab delimited columns with no
headings.  If the Afrikaans and English lecturers are the same, use
"=" in the third column.  Use "/" to separate multiple lecturers.

Sample:
CBI310	BP	=
CLB321	HR/BP/PV/ET/CS/WF/WN	=


3. Department data

The file "departmentlist" contains the department code and an Afrikaans and English full department name

Sample departmentlist:
C	Chemiese Ingenieurswese	Chemical Engineering
Z	Elektroniese Ingenieurswese	Electronic Engineering

This file will be expanded to versions for 4 year and 5 year programs
by the "expand" script.

The file "genlist" contains the department codes for the departments the run will be run for, one per line.  

Sample genlist:
c 
C

3. Yearbook data

The number of lectures required for each subject is stored in
yearbook_counts.txt.  This file can be generated using the script
"count_yearbook", which reads a text version of the yearbook, which
can be generated using pdftotext.

A typical workflow would be 

$ pdftotext -layout yearbook.pdf # this generates a file called yearbook.txt
$ ./count_yearbook yearbook.txt | sort > yearbook_counts.txt

Sample output:

ABV320 3 0 0
BCC410 2 1 2
BER310 4 0 0
BES220 2 1 0
BFB310 2 1 0
BGC410 3 1 0
BID320 3 1 2
BIE310 2 1 0
BIE320 2 1 0
BLK320 4 2 0

For each timetable that will be generated a file called
yearbook_subjects_X*.txt must be supplied.  This file contains a
sorted list (ideally generated from the yearbook) of the subjects that
should appear on the timetable.  X in the filename must correspond to
the department code, and can be followed by any discriminating text.


4. XSL transforms and html stylesheets

The "work" of generating output is handled using XSL.  Transforms are
stored in the transforms directory.  The transform will be run on a
timetable.xml file and generate either html or latex output.  If the
transform generates latex output, its filename should end in
"_tex.xsl".  If there are stylesheets required to view the html, store
them in the "stylesheets" directory.


5. Generating the timetable

When all the above has been set up, generating the timetables is as
easy as running "./generate spreadsheet.xls".


6. Checking the timetable

The following things have to be checked on a new timetable:

- Are all the subjects indicated in the yearbook scheduled on the timetable?


- Are the correct number of periods of each type scheduled for each language?


- Are there clashes?
  The "dupreport.html" file should contain a list of possible clashes.
  Some of them will be false positives, but there shouldn't be clashes
  that aren't caught.

