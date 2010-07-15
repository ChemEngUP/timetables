#!/usr/env/python

import sys,os,os.path,datetime

logfile = file('log', 'w')

log("Run on" + datetime.datetime.now())

def log(string, echo=False):
    if echo:
        print string
    print >> logfile, string

# regenerate fulltable if a first argument is given
if len(sys.argv) > 1:
    os.system('xls2csv $1 -q0 -c\| | less | tr \| "\t" | ./shorten.sed > fulltable')
    log("Regenerated fulltable from " + sys.argv[1], echo=True)

outputdir="output"
subdiff="./subdiff"

# backup old output
[ -e $outputdir.old ] && rm -fr $outputdir.old
[ -e $outputdir ] && mv $outputdir $outputdir.old

# Generate 4 year and 5 year plan entries
./expand departmentlist > departmentlist_expanded

indexfile=$outputdir/index.html

mkdir $outputdir

function index() { 
    echo $* >> $indexfile 
}

function checkdifferences {
    countfile=$1
    dirname=$2
    lang1=$3
    lang2=$4
    result=$dirname/diff_$lang1$lang2.html
    echo "    " checking difference between $lang1 and $lang2
    $subdiff $countfile.{$lang1,$lang2} > $result
    index '<li>Differences between <a href="'$result'">1='$lang1', 2='$lang2'</a></li>'
}

index "<html>"
cat indexscript >> $indexfile
index "<body onload=hideall()>"
index "<h1>Timetables</h1>"
index "<p>These timetables were automatically generated on " `date` ".  Click on the headings to expand the options.</p>"

# Make target directory
for dept in `cat genlist`; do 
    name=`grep "^$dept" departmentlist_expanded | cut -f 3`
    safename=`echo $name | tr " " _ | tr -d "()"`
    index "<h2 onclick=showhide(\""$safename\"")>"$name"</h2>" 
    index '<div id="'$safename'">'

    echo Doing $name ...
    dirname=$outputdir/$safename
    mkdir -p $dirname
    cp stylesheets/* $dirname
    xmlfile=$dirname/timetable.xml
    ./ttable.py -o $xmlfile --group $dept --deptident "$name" < fulltable

    echo "  " Running checks
    # Generate subjects list
    countfile=$xmlfile.count
    cut -d" " -f 1 $countfile > $dirname/subjectlist

    # Generate language based counts
    for lang in A E; do
	sed -n "/ $lang /s/ $lang//p" $countfile > $countfile.$lang
    done

    # pull subject counts for this group
    grep -f yearbook/subjects_$dept*.txt yearbook/counts.txt > $countfile.yearbook

    # compare
    index "<h3>Differences</h3>"
    index "<ol>"

    checkdifferences $countfile $dirname A E
    checkdifferences $countfile $dirname A yearbook
    checkdifferences $countfile $dirname E yearbook

    index "</ol>"


    # Run transforms
    index "<h3>Tables</h3>"
    index "<ol>"
    for style in transforms/*.xsl; do
	stylename=`basename $style .xsl`
	index "<li>"
	echo "  " creating $stylename
	if echo $stylename | grep -q tex; then
	    sabcmd -x $xmlfile $style $dirname/$stylename.tex
	    echo "   "- calling LaTeX
	    pushd $dirname > /dev/null
	    ans=`pdflatex -interaction=nonstopmode $stylename | grep "No pages"` && echo $ans for $stylename in $name
	    popd > /dev/null
	    index '<a href="'$dirname/$stylename.pdf'">' ${stylename%_tex} ' (pdf)</a>'
	else
	    sabcmd -x $xmlfile $style $dirname/$stylename.html
	    index '<a href="'$dirname/$stylename.html'">' $stylename '</a>'
	fi
	index "</li>"
    done
    index "</ol>"
    index "</div>"
done

pdffiles=`echo $outputdir/*/*.pdf | tr " " "\n" | sed 's/.*\/\(.*\)\.pdf/\1/g' | sort | uniq`
echo Combining pdf output for ...
for filename in $pdffiles; do
    echo "  "$filename
    pdftk $outputdir/*/$filename.pdf cat output $outputdir/all$filename.pdf
done

index "</body></html>"
sed -i 's,output/,,g' $indexfile
