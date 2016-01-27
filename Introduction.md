# Introduction #

SVNPlot generates graphs similar to StatSVN.  The difference is in how the graphs are generated.  SVNPlot generates these graphs in two steps. First it converts the Subversion logs into a 'sqlite3' database.  Then it uses sql queries to extract the data from the database and then uses excellent Matplotlib plotting library to plot the graphs.

I believe using SQL queries to query the necessary data results in great flexibility in data extraction. Also since the sqlite3 is quite fast, it is possible to generate these graphs on demand.

# Installation #
## Requirements (Third party libraries) ##
You will need following additional libraries for using SVNPlot
  1. [sqlite3](http://www.sqlite.org/) - is default installed with python
  1. [pysvn](http://pysvn.tigris.org)- Python SVN bindings.

_If you are going to use Javascript canvas based graphs (svnplot-js.py), then you will need_,
  1. [JqPlot](http://www.jqplot.com) - Excellent JavaScript canvas based plotting library. It is included in the svnplot installation

_If you want to use Matplotlib based SVNPlot (svnplot.py), then you will need_
  1. [NumPy](http://numpy.scipy.org)- Matplotlib uses NumPy and SVNPlot uses Matplotlib for plotting.
  1. [Matplotlib](http://matplotlib.sourceforge.net)- You need at least version 0.98.5.2

## Installation Steps ##
Installation instructions for SVNPlot

  1. Download and Install  [Python 2.6.x or 2.7.x version](http://www.python.org/ftp/python/) (32 bits)
  1. Install [pysvn Extension](http://pysvn.tigris.org/servlets/ProjectDocumentList?folderID=1768)
  1. Install [NumPy](http://sourceforge.net/projects/numpy/files/NumPy/)
  1. Install [matplotlib](http://matplotlib.org/downloads.html)
  1. Download [SVNPlot](http://code.google.com/p/svnplot/downloads/list). For Windows download Installer exe For other platforms download .zip file

For Windows
  1. run the downloaded installer.

For Other platforms:
  1. Unzip SVNPlot-0.7.8.zip to a folder e.g. svnplot\_inst
  1. Goto 'svnplot\_inst' folder and run setup.py

By default svnplot scripts are installed in Python 

&lt;site-packages&gt;

 directory.

_NOTE : You have to install the 32 bits version and it must be version 2.7.x, since the 64 bits version is not recognized by the installers for some of the required libraries and version 3.2.x is not supported by some of the required libraries_

# Quick Start #

**Using SVNPlot is a two step process; first you have to pull data from svn to a SQLite database, then you run the analysis those data.**

Add python <site-packages/svnplot> folder in PATH environment variable or give the full path for executing svnlog2sqlite.py, svnplot.py, svnplotjs.py

1. First generate the sqlite database for your project.
> _svnlog2sqlite.py `[options] <svnrepo url> <sqlitedbpath>`_

> _`<svnrepo url>`_ can be any repository format supported by Subverson. If you are using the local repositories on windows use the [file:///d:/](file:///d:/)... format.

> NOTE : This is URL of repository **root**. For example, updating the SVN graphs for SVNPlot project use http://svnplot.googlecode.com/svn/. Using other urls like http://svnplot.googlecode.com/svn/trunk/ will result in error. (Upto version 0.5.4. This issue is fixed version 0.5.5, now svnrepo\_url can be any url inside the repository)

> _`<sqlitedbpath>`_ is sqlite database file path. Its a path on your local machine

> Options :
  * _`-l, --linecount`_ : Update the changed line count data also. By default line count data is NOT updated.
  * _`-g, --log`_ : enable logging of intermediate data and errors. _`Enable this option if you face any problems like line count not getting generated, no data in the generated sqlite database etc.`_
  * _`-v, --verbose`_ : Verbose output

2. Now generate the graphs.
> _svnplot.py `[options] <svnsqlitedbpath> <graphdir>`_
> OR
> _svnplot-js.py `[options] <svnsqlitedbpath> <output directory>`_

> `<graphdir>` is local directory on your machine. All the graphs will placed in this directory.  For svnplot-js.py, by default necessary jqplot JavaScript files are also copied to this directory.

> Following addition options are useful
  * _`-n '<reponame>', --name=<reponame>`_ :  This is name of repository (e.g. project name). It will use in generating the graph titles
  * _`-s '<searchpath>, --search=<searchpath>`_ : search path in the repository (e.g. _/trunk_)
  * _`-p '<template file path>', --template=<template file path>`_ :  Default svnplot uses its own standard report format. However, you can change report format using -p option.
  * _`-m, --maxdir <num>`_ : limits the number of directories on the graph to the `<num>` largest directories as with large numbers of dirs the graph gets blurry.
  * _`-v, --verbose`_ : verbose output
For svnplot-js.py,
  * _`-j or --copyjs`_ : copy the required excanvas,jQuery and jqPlot JavaScript and css file to output directory

3. Generating Graph with your own report template
> You can use your own report template for the generated graphs. One example of report template is available in 'svnplot-long.tmpl'. This template directly embed the generated graphs images in the report and doesnot use thumbnails. It is useful to get a printed report.

> For example,

> _svnplot.py -v --dpi 70 -p svnplot-long.tmpl -n "MyRepo" <sqlitedb path> <output directory>_
> OR
> _svnplot-js.py `[options] <svnsqlitedbpath> <output directory>`_

> _`TIP - Use 70 pixesl per inch resolution for better results with svnplot-long.tmpl template.`_

## IMPORTANT NOTE for migrating from 0.5.x to 0.6 ##
SVNPlot ver 0.6 sqlite database schema is different than 0.5.x schema. Hence for migrating from 0.5.x to 0.6 you will need to regenerate the sqlite database.