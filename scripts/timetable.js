var downarrow = "&#x25bc;";
var rightarrow = "&#x25b6;";

function showhide(blockid) {
    var el=document.getElementById(blockid);
    var h=el.previousElementSibling;

    if (el.style.display == 'block') {
        el.style.display = 'none';
        h.innerHTML = rightarrow + h.innerHTML.substring(1);
    } else {
        el.style.display = 'block';
        h.innerHTML = downarrow + h.innerHTML.substring(1);
    }
}

function hideall() {
    var divs=document.getElementsByTagName('div');
    for (var i = 0; i<divs.length; i++) {
        divs[i].style.display = 'none';
    }
    var headings=document.getElementsByTagName('h2');
    for (var i = 0; i<headings.length; i++) {
        headings[i].innerHTML = rightarrow + " " + headings[i].innerHTML;
    }
}

function strhash(str) {
    var hash=0;
    for (var i = 0; i<str.length; i++) {
	hash += str.charCodeAt(i);
    }
    return hash % 10;
}

function armhighlights() {
    var divs=document.getElementsByTagName('div');
    for (var i = 0; i<divs.length; i++) {
	if (divs[i].className=='subject') {
	    subject = divs[i].innerHTML.replace(/[()]/g,'');
	    divs[i].onclick=Function("highlight('" + subject + "')");
	}
    }
}

function highlight(subject) {
    var subs=document.getElementsByTagName('div');
    for (var i = 0; i<subs.length; i++) {
	if (subs[i].className=='subject' & subs[i].innerHTML.replace(/[()]/g,'')==subject) {
	    var p = subs[i].parentNode;
	    p.className = /high.$/.test(p.className)?p.className.substr(0,3):(p.className + 'high' + strhash(subject));
	}
    }
}

function yearvis(year) {
    var rows=document.getElementsByTagName('tr');
    for (var i=0; i<rows.length; i++) {
	if (rows[i].className==('year'+year)) {
	    rows[i].style.display = rows[i].style.display=='none'?'':'none';
	}
    }
}
