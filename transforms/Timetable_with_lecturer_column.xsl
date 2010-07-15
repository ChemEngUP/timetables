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
      <th class="periodheading" rowspan="5"><xsl:value-of select="concat(./@number, ' ', ./@starttime)" /> </th>
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
    <td class="lect">
      <xsl:for-each select="module">
	<xsl:sort lang="C" select="./@language"/>
	<xsl:apply-templates select="." mode="lect"/>
      </xsl:for-each>
    </td>
</xsl:template>

<xsl:template match="module">
    <div class="subject">
      <xsl:if test="./@type='P' or ./@type='T'">(</xsl:if>
      <xsl:value-of select="./@name" />
      <xsl:if test="./@type='P' or ./@type='T'">)</xsl:if>
    </div>
    <div class="venue"><xsl:value-of select="./@venue"/></div>
</xsl:template>

<xsl:template match="module" mode="lect">
  <xsl:value-of select="translate(./@responsible, '/', ' ')" /><xsl:text> </xsl:text>
</xsl:template>

<xsl:template match="semester">
  <xsl:param name="startperiod" select="1" />
  <xsl:param name="endperiod" select="10" />
  <h2><xsl:value-of select="/timetable/geninfo/@dept"/> - Semester <xsl:value-of select="./@number"/> of <xsl:value-of select="/timetable/@year"/> (generated on <xsl:value-of select="/timetable/geninfo/@date"/>)</h2>
  <table class="year">
    <colgroup /><colgroup />
    <colgroup span="3" class="day"/>
    <colgroup span="3" class="day"/>
    <colgroup span="3" class="day"/>
    <colgroup span="3" class="day"/>
    <colgroup span="3" class="day"/>
    <thead>
      <tr>
	<th rowspan="3">Per</th>
	<th rowspan="3">Yr</th>
	<th colspan="3">Ma/Mo</th>
	<th colspan="3">Di/Tu</th>
	<th colspan="3">Wo/We</th>
	<th colspan="3">Do/Th</th>
	<th colspan="3">Vr/Fr</th>
      </tr>
      <tr align="center">
	<td>Afr</td><td>Eng</td><td>Lect</td>
	<td>Afr</td><td>Eng</td><td>Lect</td>
	<td>Afr</td><td>Eng</td><td>Lect</td>
	<td>Afr</td><td>Eng</td><td>Lect</td>
	<td>Afr</td><td>Eng</td><td>Lect</td>
      </tr>
    </thead>
    <xsl:apply-templates select="period[(./@number >= $startperiod) and ($endperiod >= ./@number) ]" />
  </table>
</xsl:template>

<xsl:template match="/timetable">
  <html>
    <head>
      <link href="timetable_lect.css" rel="stylesheet" type="text/css" />
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
	      subs[i].style.background = (subs[i].style.background.substring(4,0)=='pink')?'':'pink';
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
