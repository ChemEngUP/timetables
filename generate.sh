#!/bin/bash

# Todo: Use rubber or similar tool for latex builds
echo Run on `date` >> log

if test `uname` = Darwin; then
	echo "Running on Mac"
	SED=gsed
else
	echo "Running on Linux"
	SED=sed
fi

# regenerate fulltable if a first argument is given
if [ ! -z $1 ] ; then
    [ -e fulltable.csv ] && mv fulltable.csv fulltable_prev.csv
    xls2csv "$1" | $SED -f shorten.sed | ./extractcolumns.py --headerfile headers.txt --sort -o fulltable.csv && echo Regenerated fulltable.csv from $1 | tee -a log
    cp mailhead.txt mailbody.txt
    diff fulltable.csv fulltable_prev.csv | tee -a mailbody.txt
    dos2unix mailbody.txt
    # send mail about regeneration if a second argument is given
    [ ! -z $2 ] && nail -s "Timetable regenerated" -r "carl.sandrock@up.ac.za" -c "carl.sandrock@up.ac.za" "philip.devaal@up.ac.za" < mailbody.txt 
    echo $1 > datafilename
else
    echo Assuming same data as last time.
fi

# assuming the filename looks like timetable_2010_20090201.xls, parse out the pieces
IFS="_." read n datayear datadate rest < datafilename
echo Timetable for $datayear given on $datadate

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
index "<h1>Timetables for $datayear</h1>"
index "<p>These timetables were automatically generated on " `date` ".</p>"
index "<p>The original datafile was sent on $datadate. Note that these timetables are only trustworthy near the date of the original datafile for departments other than Chemical Engineering.</p>"
index "<p>Click on the headings to expand the options.</p>"

awk '{print $1; print tolower($1)}' departmentlist > genlist

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
    ./ttable.py -o $xmlfile --group $dept --deptident "$name" --year $datayear < fulltable.csv || exit

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
    index "<p>The timetable is compared for consistency between the Afrikaans and English classes as well as with the yearbook.  Click a link.</p>"
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
        printname=${stylename//_/ } # replace underscores with spaces
        index "<li>"
        echo "  " creating $printname
        if echo $stylename | grep -q tex; then
            sabcmd -x $xmlfile $style $dirname/$stylename.tex
            echo "   "- calling LaTeX
            pushd $dirname > /dev/null
            ans=`pdflatex -interaction=nonstopmode $stylename | grep "No pages"` && echo $ans for $stylename in $name
            popd > /dev/null
            printname=${printname% tex} # strip tex
            index '<a href="'$dirname/$stylename.pdf'">' $printname ' (pdf)</a>'
        else
            sabcmd -x $xmlfile $style $dirname/$stylename.html
            index '<a href="'$dirname/$stylename.html'">' $printname '</a>'
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
$SED -i 's,output/,,g' $indexfile

echo "Deleting temporary files"
rm genlist departmentlist_expanded