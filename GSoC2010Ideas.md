# Introduction #
SVNPlot is developed in Python and currently being in various organizations to analyze subversion repositories. We are working on submitting SVNPlot as mentoring organization for Google Summber of Code 2010. Given below is partial list of ideas for GSoC.


# Ideas #

  1. Integrating svnplot as module into a django or other webframework with a tree view kind of display to select the directory and analyze that directory. It will give 'drill down' kind of analysis of repository.
  1. Treemap (or heatmap) display of folders in repository.
  1. Supporting database backends for svnplot (one option PostgreSQL with psycopg2,another option is to use sqlalchemy). If we sqlalchemy we  can support multiple database backends.
  1. Ability to store information about multiple repositories in single database (sqlite or other database backends). This will require changes in the current schema as well as change queries.
  1. Additional graphs/charts.
  1. Implement [libsna](http://www.libsna.org) into the code that was developed as part of GSoC09 and moving the code into 'trunk' to make it part of the SVNPlot release. This version would allow users to specify collection dates (time periods) and would produce useful SNA statistics, plus provide some utility scripts for collection of large numbers of networks.
  1. Support new VCS systems for analysis (e.g. Mercurial, CVS). SVNPlot works in two distinct phases - collecting the version control data in a sqlite database and then using sql queries to analyse the data and generate charts/graphs. By replacing the 'data' collection code for other VCS systems, it will possible to generate the same kind of analysis with SVNPlot. Check feasibility of the idea and come with the design/implementation.
  1. Features request from SVNPlot users. Check the Issues Page. Especially Issue Id 27, 32.