<?xml version="1.0" ?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html" />

<xsl:template match="period">
  <xsl:param name="person" select="someone" />
  <tbody>
    <xsl:element name="tr">
      <xsl:attribute name="class">
	<xsl:value-of select="concat('period', ./@number)"/>
      </xsl:attribute>
      <th><xsl:value-of select="concat(./@number, ' ', ./@starttime)" /> </th>
      <td><xsl:apply-templates select="year/day[./@name='Ma/Mo']/module[contains(./@responsible, $person) or ./@responsible='/Almal/' or ./@responsible='Almal']" /></td>
      <td><xsl:apply-templates select="year/day[./@name='Di/Tu']/module[contains(./@responsible, $person) or ./@responsible='/Almal/']" /></td>
      <td><xsl:apply-templates select="year/day[./@name='Wo/We']/module[contains(./@responsible, $person) or ./@responsible='/Almal/']" /></td>
      <td><xsl:apply-templates select="year/day[./@name='Do/Th']/module[contains(./@responsible, $person) or ./@responsible='/Almal/']" /></td>
      <td><xsl:apply-templates select="year/day[./@name='Vr/Fr']/module[contains(./@responsible, $person) or ./@responsible='/Almal/']" /></td>
    </xsl:element>
  </tbody>
</xsl:template>

<xsl:template match="module">
  <div class="subject">
    <xsl:if test="./@type='P' or ./@type='T'">(</xsl:if>
    <xsl:value-of select="./@name" /> &#160; <xsl:value-of select="./@language"/>
    <xsl:if test="./@type='P' or ./@type='T'">)</xsl:if>
  </div>
  <div class="venue"><xsl:value-of select="./@venue"/></div>
</xsl:template>

<xsl:template match="semester">
  <xsl:param name="person" select="someone" />
  <h2>Semester <xsl:value-of select="./@number"/> of <xsl:value-of select="/timetable/@year"/> </h2>
  <table class="year">
    <colgroup /><colgroup />
    <colgroup class="day"/>
    <colgroup class="day"/>
    <colgroup class="day"/>
    <colgroup class="day"/>
    <colgroup class="day"/>
    <thead>
      <tr>
	<th>Per</th><th>Ma/Mo</th><th>Di/Tu</th><th>Wo/We</th><th>Do/Th</th><th>Vr/Fr</th>
      </tr>
    </thead>
    <xsl:apply-templates select="period">
      <xsl:with-param name="person" select="$person"/>
    </xsl:apply-templates>
  </table>
</xsl:template>

<xsl:template match="/timetable">
  <html>
    <head>
      <link href="perlect.css" rel="stylesheet" type="text/css" />
    </head>
    <body>
      <xsl:for-each select="personnel/person">
	<xsl:if test="./@name!='Almal'">
	  <h1>
	    <span>
	      <xsl:attribute name="id">
		<xsl:value-of select="./@name"/>
		</xsl:attribute>
		Timetables for <xsl:value-of select="./@name"/> 
	      </span>
	    </h1>
	  <xsl:apply-templates select="/timetable/semesters/semester" >
	    <xsl:with-param name="person" select="concat('/', ./@name, '/')"/>
	  </xsl:apply-templates>
	</xsl:if>
      </xsl:for-each>
    </body>
  </html>
</xsl:template>

</xsl:stylesheet>
