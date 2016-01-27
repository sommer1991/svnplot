Readme for GSoC2010 contributions to SVNPlot

# Introduction #

This project contributed code to SVNPlot (http://code.google.com/p/svnplot/). I (Oscar) was given commiter rights to SVNPlot's SVN repository hosted on Google Code. A new branch (ocastaneda\_gsoc2010) was created based on the work and research conducted during GSoC2010.

The Python scripts svnsqlite2ora.py and svnsqlite2gexf.py convert SVN logs stored in sqlite databases, collected through svnlog2sqlite.py, into formats consumable by **CMU's ORA tool** ([1](.md)) and **Gephi** ([2](.md)). Both scripts take parameters as specified below:

> Usage: svnsqlite2ora.py < sqlitedbpath > < outputfile >

> Usage: svnsqlite2gexf.py < sqlitedbpath > < outputfile >

Once the SVN logs have been converted the output files can be used in **CMU's ORA** and **Gephi**.

Note: The sociomatrix conversion algorithm in svnsqlite2ora.py and svsqlite2gexf.py has been heavily revised and thoroughly tested. While the idea remains similar to that of GSoC'09, the algorithm has been improved and corrected. In addition the code has been tested under the collection of data from **all** projects of The Apache Software Foundation from the years of 2004-2009. Apache's SVN repository is being hosted on a test server at Delft University of Technology to prevent generating excessive traffic on Apache's servers and to allow for extensive experimentation.

# Quick Start #

1. First generate the sqlite database for your project.

> Usage: svnlog2sqlite.py [options ](.md) <svnrepo root url> 

&lt;sqlitedbpath&gt;

 <startdate (yearmonthday)> <enddate (yearmonthday)>

> <svnrepo root url> can be any repository format supported by Subversion. If you are using the local repositories on windows use the [file:///d:/](file:///d:/)... format. < sqlitedbpath > is sqlite database file path. Its a path on your local machine

> <startdate (yearmonthday)> is the start collection date specified as a single number with 4 digits for year, 2 digits for month and 2 digits for day.

> <enddate (yearmonthday)> similar to startdate above, but meant to indicate the end date of a collection period.

> You can run this step multiple times. The new revisions added in the repository will get added to database

> Options :
  * -l : Update the changed line count data also. By default line count data is NOT updated.
  * -v : Verbose output
  * -g : enable logging of intermediate data and errors. Enable this option if you face any problems like line count not getting generated, no data in the generated sqlite database etc.

2. Now create the output files.

  * svnsqlite2ora.py < sqlitedbpath > < outputfile >

  * svnsqlite2gexf.py < sqlitedbpath > < outputfile >

3. Use the output files in **CMU's ORA** or **Gephi**.

# Source code #

All the source for these additions can be found in the "ocastaneda\_gsoc2010" branch.

http://svnplot.googlecode.com/svn/branches/ocastaneda_gsoc2010/src/svnplot/

# Additions to svnlog2sqlite.py for collecting SVN logs from varying time periods #

SVNPlot collects SVN logs through svnlog2sqlite.py. This script in turn uses another Python script, svnlogiter.py. Changes have been made to svnlogiter.py and to svnlog2sqlite.py to allow collection of SVN logs from different time periods specified through the command-line options of svnlog2sqlite.py. These additions are useful when analyzing the evolution of an open source codebase.

# Future Research #

**Collect cumulative data and employ pattern recognition and machine learning techniques.**

**Collect cumulative data and test whether open source communities grow according to preferential attachment.**

As far as I know, these techniques have not been applied on source code, but instead have been applied on other data such as collections of email messages. But what distinguishes open source developers is that they write code, not that they send emails. And even though interesting communications patterns may be uncovered, it is by concentrating on work practice that we can discover interesting patterns and improve our understanding of innovation in open source.

# Acknowledgements #

I thank Google and the Google Open Source Programs Office for the support of this work and my research. I would also like to express my gratitute to Nitin Bhide for his mentorship and shared interest in social network analysis of open source communities. Nitin's help and suggestions during my Google Summer of Code (2010) project have greatly enriched my learning experience. I would also like to thank my MSc thesis supervisors, Prof.dr. Michel van Eeten and Dr. Victor Scholten, for their extensive mentoring, their patience and friendship.


_Oscar Castañeda_

_Delft, 2010_


# License #

SVNPlot is released under New BSD License http://www.opensource.org/licenses/bsd-license.php

# References #

[1](.md) http://www.casos.cs.cmu.edu/projects/ora/

[2](.md) http://gephi.org/

[3](.md) http://code.google.com/p/svnplot/