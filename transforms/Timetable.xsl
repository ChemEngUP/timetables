<?xml version="1.0" ?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html" />

<xsl:template match="period">
  <tbody>
    <xsl:element name="tr">
      <xsl:attribute name="class">
	<xsl:value-of select="concat('period', ./@number)"/>
      </xsl:attribute>
      <th rowspan="5"><xsl:value-of select="concat(./@number, ' ', ./@starttime)" /> </th>
      <xsl:apply-templates select="year" />
    </xsl:element>
  </tbody>
</xsl:template>

<xsl:template match="year">
  <xsl:element name="tr">
    <xsl:attribute name="class"> 
      <xsl:value-of select="concat('year', ./@number)"/> 
    </xsl:attribute>
    <td><xsl:value-of select="./@number" /></td>
    <xsl:apply-templates select="day"/>
  </xsl:element>
</xsl:template>

<xsl:template match="day">
  <xsl:choose>
    <xsl:when test="./module/@language='B'">
      <td class="both" colspan="2">
      <xsl:apply-templates select="module[./@language='B']"/></td>
    </xsl:when>
    <xsl:otherwise>
      <td class="afr">
	<xsl:apply-templates select="module[./@language='A']" />
      </td>
      <td class="eng">
	<xsl:apply-templates select="module[./@language='E']" />
      </td>
    </xsl:otherwise>
    </xsl:choose>
</xsl:template>

<xsl:template match="module">
    <div class="subject">
      <xsl:if test="./@type='P' or ./@type='T'">(</xsl:if>
      <xsl:value-of select="./@name" />
      <xsl:if test="./@type='P' or ./@type='T'">)</xsl:if>
    </div>
    <div class="venue"><xsl:value-of select="./@venue"/></div>
</xsl:template>

<xsl:template match="semester">
  <xsl:param name="startperiod" select="1" />
  <xsl:param name="endperiod" select="10" />
  <h2><xsl:value-of select="/timetable/geninfo/@dept"/> - Semester <xsl:value-of select="./@number"/> of <xsl:value-of select="/timetable/@year"/> (generated on <xsl:value-of select="/timetable/geninfo/@date"/> )</h2>
    <p>Click here to show or hide years:<button onclick="yearvis(1)">1</button> <button onclick="yearvis(2)">2</button> <button onclick="yearvis(3)">3</button> <button onclick="yearvis(4)">4</button> </p>
  <table class="year">
    <colgroup /><colgroup />
    <colgroup span="2" class="day"/>
    <colgroup span="2" class="day"/>
    <colgroup span="2" class="day"/>
    <colgroup span="2" class="day"/>
    <colgroup span="2" class="day"/>
    <thead>
      <tr>
	<th rowspan="2">Per</th>
	<th rowspan="2">Yr</th>
	<th colspan="2">Ma/Mo</th>
	<th colspan="2">Di/Tu</th>
	<th colspan="2">Wo/We</th>
	<th colspan="2">Do/Th</th>
	<th colspan="2">Vr/Fr</th>
      </tr>
      <tr align="center">
	<td>Afr</td><td>Eng</td>
	<td>Afr</td><td>Eng</td>
	<td>Afr</td><td>Eng</td>
	<td>Afr</td><td>Eng</td>
	<td>Afr</td><td>Eng</td>
      </tr>
    </thead>
    <xsl:apply-templates select="period[(./@number >= $startperiod) and ($endperiod >= ./@number) ]" />
  </table>
</xsl:template>

<xsl:template match="/timetable">
  <html>
    <head>
      <link href="timetable.css" rel="stylesheet" type="text/css" />
  <script type="text/javascript">
//<![CDATA[
<!--//
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
              p.className = /high$/.test(p.className)?p.className.substr(0,3):(p.className + 'high');
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
//-->
//]]>
  </script>
    </head>
    <body onload='armhighlights()'>
      <xsl:for-each select="semesters/semester">
	<xsl:apply-templates select="." >
	  <xsl:with-param name="startperiod" select="1" />
	  <xsl:with-param name="endperiod" select="10" />
	</xsl:apply-templates>
      </xsl:for-each>
    </body>
  </html>
</xsl:template>

</xsl:stylesheet>
