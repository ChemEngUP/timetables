<?xml version="1.0" ?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html" />

<xsl:template match="module">
  <tr>
  <td><xsl:value-of select="../../../@number" /></td>
  <td><xsl:value-of select="../@name" /></td>
  <td><xsl:value-of select="../../@number" /></td>
  <td><xsl:value-of select="./@name"/> <xsl:value-of select="./@language" /></td>
  <td><xsl:value-of select="./@venue" /></td>
  </tr>
</xsl:template>

<xsl:template match="/timetable">
  <html>
    <body>
      <h1>Duplicate entries - <xsl:value-of select="/timetable/geninfo/@dept"/></h1>
      <xsl:for-each select="/timetable/semesters/semester" >
	<h2>Semester <xsl:value-of select="./@number"/></h2>
	<table>
	  <tr><th>Period</th><th>Day</th><th>Year</th><th>Subject</th><th>Venue</th></tr>
	  <xsl:apply-templates select=".//module[(./@language='A' and (count(..//module[./@language='B'])+count(..//module[./@language='A']))>1) or (./@language='E' and (count(..//module[./@language='B'])+count(..//module[./@language='E']))>1) or (./@language='B' and (count(..//module[./@language='B'])+count(..//module[./@language='A'])+count(..//module[./@language='E']))>1)]" />
 	</table>
	</xsl:for-each>
    </body>
  </html>
</xsl:template>

</xsl:stylesheet>
