## This Project is moved to Bitbucket (https://bitbucket.org/nitinbhide/svnplot/wiki/Home) ##

Google code doesnot allow uploading of installers anymore. Hence I am moving the primary repository of this project to bitbucket. However, a clone of the bitbucket repository is available here. Also use google for reporting any issues as well.


### This project creates various types of statistics and graphs from subversion repository log data. ###

**Oscar Castaneda (SVNPlot Commiters) talks about his Summer of Code project on Google blog ([Life after Google Summer of Code](http://google-opensource.blogspot.com/2010/11/life-after-google-summer-of-code.html))**

<font color='red'><b>IMPORTANT</b></font> : Version 0.6.x users and 0.7.0 users, please upgrade to 0.7.10 and RECREATE the database.

#### News/Updates ####
<font color='blue'><b><sup>NEW</sup></b></font> Version 0.7.10 available (25 July 2013)*** Fixed issue where the details of commits (line count, changed etc) were not updated for local repositories.
  * Added the 'Wasted Effort Ratio Trend' graph. Its a graph of 'lines deleted'/'lines added'. Lines deleted are essentially efforts wasted.**

**Version 0.7.8 available (4 Aug 2012)**
  * Fixes [issue 83](https://code.google.com/p/svnplot/issues/detail?id=83) (Windows-specific conventions, does not run out-of-the-box on Unix)
  * Fixed a regression in svnplot-js.py introduced in 0.7.7

**Version 0.7.7 available (28 June 2012)**
  * This version is deprecated as it contains a regression bug in svnplot-js.py.
  * Fixes [issue 82](https://code.google.com/p/svnplot/issues/detail?id=82) : wrong line count in case of symlinks in the repository. (Patch contributed by EmTeedee DeLowbacca)
  * Added new options 'firstrev' and 'lastrev' to svnplot.py and svnplot-js.py for generating statistics from revisions
> > [firstrev:lastrev].  (Patch contributed by Georgios Koloventzos)

**version 0.7.6 available (14 Nov 2011)**
  * Fixes Fixes a bug where rare case svnlog2sqlite.py got an 'Inconsistent line ending style'
  * Fixes a bug in svnplot where svnplot crashed in end with error 'super object has no attribute del' message.

**version 0.7.5 available (28 May 2011)**
  * Fixes critical bugs about wrong line count, 'unknown node kind' messages, unicode errors ('expected character buffer' message).
  * There is a separate svnstatscsv.py which exports basic repository data in CSV (Comma Separated Values) format.
  * Please recreate the sqlite database after upgrade.

**Version 0.7.4 available (5 Feb 2011)**
  * Fixes critical bugs about wrong line count, 'unknown node kind' messages, unicode errors ('expected character buffer' message).
  * Please recreate the sqlite database after upgrade.
  * LocChurn graph added for matplot lib based svnplot (svnplot.py)
  * Command line parameters for specifying Username/password  for repository authentication.
  * Some basic support for exporting the stats in CSV format (svnstatscsv.py)
  * GSoC 2010/2009 changes merged into trunk. (Thanks Oscar)
  * Bug fixes for correct display of javascript charts in IE 7 and IE8.
  * Improvements in the computation of author activity index.
  * Many small bug fixes.

DO NOT USE 0.5.13. Version 0.5.13 has a bug in the linecount computations. If you are using 0.5.13, please discard the repository stats database and regenerate it again.

---


**Steps to generate these statistics :**
  1. _subversion log information is first converted into a sqlite database._
  1. _then using sql queries various stats are generated_
  1. _these stats are converted into graphs using the matplotlib package_

The various graphs generated are inspired by the graphs generated using StatSVN/StatCVS.

Currently following statistics and graphs are generated
  * **General Statistics**
    1. Revision count
    1. Author count
    1. File Count
    1. Head revision number
  * **Top 10 Hot List**
    1. Top 10 Active Authors
    1. Top 10 Active Files
  * **LoC graphs**
    1. total loc line graph (loc vs dates)
    1. average file size vs date line graph
    1. Contributed lines of code line graph (loc vs dates). Using different colour line for each developer
    1. Loc and Churn graph (loc vs date, churn vs date)- Churn is number of lines touched (i.e. lines added + lines deleted + lines modified)
  * **File Count graphs**
    1. file count vs dates line graph
    1. file type vs number of files horizontal bar chart
  * **Directory size graphs**
    1. directory size vs date line graph. Using different coloured lines for each directory
    1. directory size pie chart (latest status)
    1. Directory file count pie char(latest status)

  * **Commit Activity Graphs**
    1. Commit Activity Index
    1. Activity by hour of day bar graph (commits vs hour of day)
    1. Activity by day of week bar graph (commits vs day of week)
    1. Author Commit trend history (histogram of time between consecutive commits by same author)
    1. Author Activity horizontal bar graph (author vs adding+commiting percentage)
    1. Commit activity for each developer - scatter plot (hour of day vs date)
    1. Daily Commit count
    1. <font color='blue'><b><sup>NEW</sup></b></font> **Wasted Effort Trend graph (trend of ratio of lines deleted/lines added)**

  * **Others**
    1. Tag cloud of words from revision log messages.
    1. Tag cloud of author names.

These scripts depend on following python packages

  1. pysvn - Python interface to subversion
  1. sqlite3 - Included by default in python distribution
  1. matplotlib - python graph library

Currently I am experimenting with applying _social network analysis_ to repositories. Check the preliminary results at [Social Network Analysis of Rietveld Subversion Repository](http://thinkingcraftsman.in/projects/sna_subversion/sna_subversion.htm) and [Treemap of Commit count vs centrality for Rietveld repository](http://svnplot.googlecode.com/svn/trunk/examples/centralitytreemap/centralitytreemap.htm)

I am a novice to python, sqlite and matplotlib. So any suggestions on improvements are welcome.