## Why I started svnplot ? ##
I was mainly using [StatSVN](http://www.statsvn.org/) to analyze the repositories. However, I wanted few additional capabilities not available in StatSVN (or other similar tools). That is the main reason I started svnplot.

  1. StatSVN requires a 'checked out copy' of the repository. If server hosts multiple repositories and you want to display the stats for all then, keeping  checked out copy of each repository becomes a huge headache. To me this was major limitation. I wanted SVNPlot to work on 'server' without any checked out copy. In fact, you can run svnlog2sqlite on server periodically (or even in post commit hook) and publish the results directly on server.
  1. StatSVN combines the 'data collection' and report generation in a single executable. It also writes its own code for data collection. Hence if you need a slightly 'different' slice/analysis of data, then you have to modify the StatSVN code. It is not possible to do any quick/ad-hoc analysis.
  1. In SVNPlot, data collection is a different step/script (svnlog2sqlite.py) and reporting is different step/script(svnplot.py or svnplog-js.py). svnlog2sqlite generates a 'sqlite database' from the commit history. Hence you can use standard 'sql queries' to query the data. It is easy to write your own tools on top of the sqlite database to query whatever data you need.
  1. In fact, Oscar Castaneda (one of the commiters of SVNPlot) did exactly that for his GSoC project. He wrote a script to export the svnlog2sqlite data to Gephi xml format for different kind of analysis on data (i.e. network analysis)
  1. Since report generation is separate you can easily add your templates for reports. Initially I used [matplotlib](http://matplotlib.sourceforge.net/) for generating various graphs. But the recent version also has another script (svnplot-js.py) which uses [jqPlot](http://www.jqplot.com/) library to generate graphs using Javascript.

Personally I think that adding new features in svnplot is easier
  * because it is a Python script
  * because querying the data means write an sql query than writing a complex code.
  * jqplot and matplotlib provide excellent plotting abilities and they are
constantly improved. Hence creating various kinds of graphs is also easy.