'''
Generate various graphs from the Subversion log data in the sqlite database.
It assumes that the sqlite file is generated using the 'svnlog2sqlite.py' script.

Graph types to be supported
1. Activity by hour of day bar graph (commits vs hour of day) -- Done
2. Activity by day of week bar graph (commits vs day of week) -- Done
3. Author Activity horizontal bar graph (author vs adding+commiting percentage) -- Done
4. Commit activity for each developer - scatter plot (hour of day vs date) -- Done
5. Contributed lines of code line graph (loc vs dates). Using different colour line
   for each developer -- Done
6. total loc line graph (loc vs dates) -- Done
7. file count vs dates line graph -- Done
8. average file size vs date line graph -- Done
9. directory size vs date line graph. Using different coloured lines for each directory
10. directory size pie chart (latest status) -- Done
11. Loc and Churn graph (loc vs date, churn vs date)- Churn is number of lines touched
	(i.e. lines added + lines deleted + lines modified)
12. Repository heatmap (treemap)

--- Nitin Bhide (nitinbhide@gmail.com)

Part of 'svnplot' project
Available on google code at http://code.google.com/p/svnplot/
Licensed under the 'New BSD License'

To use copy the file in Python 'site-packages' directory Setup is not available
yet.
'''

__revision__ = '$Revision:$'
__date__     = '$Date:$'

import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from matplotlib.ticker import FixedLocator, FormatStrFormatter
from matplotlib.font_manager import FontProperties
from optparse import OptionParser
import sqlite3
import calendar, datetime
import os.path, sys
import string

HTMLIndexTemplate ='''
<html>
<head><title>Subversion Stats Plot for $RepoName</title></head>
<body>
<h1 align="center">Subversion Statistics for $RepoName</h1>
<table border="1" align="center">
<tr>
    <td align="center" width="25%"><h3>Lines of Code</h3><br/>
    <a href="$LoC"><img src="$LoC" width="$thumbwid" height="$thumbht"></a>
    </td>
    <td align="center" width="25%"><h3>Contributed Lines of Code</h3><br/>
    <a href="$LoCByDev"><img src="$LoCByDev" width="$thumbwid" height="$thumbht"></a>
    </td>
    <td align="center" width="25%"><h3>Average File Size</h3><br/>
    <a href="$AvgLoC"><img src="$AvgLoC" width="$thumbwid" height="$thumbht"></a>
    </td>
    <td align="center" width="25%"><h3>File Count</h3><br/>
    <a href="$FileCount"><img src="$FileCount" width="$thumbwid" height="$thumbht"></a>
    </td>
</tr>
<tr>
    <td align="center" width="25%"><h3>Developer Commit Activity</h3><br/>
    <a href="$CommitAct"><img src="$CommitAct" width="$thumbwid" height="$thumbht"></a>
    </td>
    <td align="center" width="25%"><h3>Commit Activity By Day of Week </h3><br/>
    <a href="$ActByWeek"><img src="$ActByWeek" width="$thumbwid" height="$thumbht"></a>
    </td>
    <td align="center" width="25%"><h3>Commit Activity By Hour of Day</h3><br/>
    <a href="$ActByTimeOfDay"><img src="$ActByTimeOfDay" width="$thumbwid" height="$thumbht"></a>
    </td>
    <td align="center" width="25%"><h3>Author Activity</h3><br/>
    <a href="$AuthActivity"><img src="$AuthActivity" width="$thumbwid" height="$thumbht"></a>
    </td>
</tr>
<tr>
   <td align="center"><h3>Current Directory Size</h3><br/>
    <a href="$DirSizePie"><img src="$DirSizePie" width="$thumbwid" height="$thumbht"></a>
    </td>
    <td align="center"><h3>Directory Size</h3><br/>
    <a href="$DirSizeLine"><img src="$DirSizeLine" width="$thumbwid" height="$thumbht"></a>
    </td>
</tr>
</table>
</body>
</html>
'''

GraphNameDict = dict(ActByWeek="actbyweekday", ActByTimeOfDay="actbytimeofday",
                     LoC="loc", LoCChurn="churnloc", FileCount="filecount", LoCByDev="localldev",
                     AvgLoC="avgloc", AuthActivity="authactivity",CommitAct="commitactivity",
                     DirSizePie="dirsizepie", DirSizeLine="dirsizeline")
                     
def dirname(path, depth):
    #first split the path and remove the filename
    pathcomp = os.path.dirname(path).split('/')
    #now join the split path upto given depth only
    #since path starts with '/' and slice ignores the endindex, to get the appropriate
    #depth, slice has to be [0:depth+1]
    dirpath = '/'.join(pathcomp[0:depth+1])
    return(dirpath)
    
class SVNPlot:
    def __init__(self, svndbpath, dpi=100, format='png'):
        self.svndbpath = svndbpath
        self.dpi = dpi
        self.format = format
        self.reponame = ""
        self.verbose = False
        self.clrlist = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        self.commitGraphHtPerAuthor = 2 #In inches
        self.searchpath = '/%'
        self.dbcon = sqlite3.connect(self.svndbpath, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        #self.dbcon.row_factory = sqlite3.Row
        # Create the function "regexp" for the REGEXP operator of SQLite
        self.dbcon.create_function("dirname", 2, dirname)
        
        self.cur = self.dbcon.cursor()        
    
    def __del__(self):
        self.cur.close()
        self.dbcon.close()

    def SetRepoName(self, reponame):
        self.reponame = reponame
        
    def SetVerbose(self, verbose):       
        self.verbose = verbose

    def SetSearchPath(self, searchpath = '/%'):
        '''
        Set the path for searching the repository data.
        Default value is '/%' which searches all paths in the repository.
        Use self.SetSearchPath('/trunk/%') for searching inside the 'trunk' folder only
        '''
        self.searchpath = searchpath
        if( self.searchpath.endswith('%')==False):
            self.searchpath = self.searchpath + '%'
        self._printProgress("Set the search path to %s" % self.searchpath)
        
    def _printProgress(self, msg):
        if( self.verbose == True):
            print msg
            
    def AllGraphs(self, dirpath, svnsearchpath='/%', thumbsize=100):
        self.SetSearchPath(svnsearchpath) 
        self.ActivityByWeekday(self._getGraphFileName(dirpath, "ActByWeek"));
        self.ActivityByTimeOfDay(self._getGraphFileName(dirpath, "ActByTimeOfDay"));
        self.LocGraph(self._getGraphFileName(dirpath, "LoC"));
        self.LocChurnGraph(self._getGraphFileName(dirpath,"LoCChurn"));
        self.FileCountGraph(self._getGraphFileName(dirpath, "FileCount"));
        self.LocGraphAllDev(self._getGraphFileName(dirpath,"LoCByDev"));
        self.AvgFileLocGraph(self._getGraphFileName(dirpath, "AvgLoC"));
        self.AuthorActivityGraph(self._getGraphFileName(dirpath, "AuthActivity"));
        self.CommitActivityGraph(self._getGraphFileName(dirpath, "CommitAct"));
        depth=2
        self.DirectorySizePieGraph(self._getGraphFileName(dirpath,"DirSizePie"), depth);
        self.DirectorySizeLineGraph(self._getGraphFileName(dirpath, "DirSizeLine"),depth);

        graphParamDict = self._getGraphParamDict( thumbsize)
        dict(GraphNameDict)
        graphParamDict["thumbwid"]=str(thumbsize)
        graphParamDict["thumbht"]=str(thumbsize)
        graphParamDict["RepoName"]=self.reponame
        
        htmlidxTmpl = string.Template(HTMLIndexTemplate)        
        htmlidxname = os.path.join(dirpath, "index.htm")
        htmlfile = file(htmlidxname, "w")
        htmlfile.write(htmlidxTmpl.safe_substitute(graphParamDict))
        htmlfile.close()
                               
    def ActivityByWeekday(self, filename):
        self._printProgress("Calculating Activity by day of week graph")
           
        self.cur.execute("select strftime('%%w', SVNLog.commitdate), count(SVNLog.revno) from SVNLog, SVNLogDetail \
                         where SVNLog.revno = SVNLogDetail.revno and SVNLogDetail.changedpath like '%s' \
                         group by strftime('%%w', SVNLog.commitdate)" % self.searchpath)
        labels =[]
        data = []
        for dayofweek, commitcount in self.cur:
           data.append(commitcount)           
           labels.append(calendar.day_abbr[int(dayofweek)])

        ax = self._drawBarGraph(data, labels,0.5)
        ax.set_ylabel('Commits')
        ax.set_xlabel('Day of Week')
        ax.set_title('Activity By Day of Week')

        fig = ax.figure                        
        fig.savefig(filename, dpi=self.dpi, format=self.format)        

    def ActivityByTimeOfDay(self, filename):
        self._printProgress("Calculating Activity by time of day graph")
        
        self.cur.execute("select strftime('%%H', SVNLog.commitdate), count(SVNLog.revno) from SVNLog, SVNLogDetail \
                          where SVNLog.revno = SVNLogDetail.revno and SVNLogDetail.changedpath like '%s'\
                          group by strftime('%%H', SVNLog.commitdate)" % self.searchpath)
        labels =[]
        data = []
        for hourofday, commitcount in self.cur:
           data.append(commitcount)           
           labels.append(int(hourofday))

        ax = self._drawBarGraph(data, labels,0.5)
        ax.set_ylabel('Commits')
        ax.set_xlabel('Hour of Day')
        ax.set_title('Activity By Hour of Day')

        fig = ax.figure                        
        fig.savefig(filename, dpi=self.dpi, format=self.format)        
        
    def LocGraph(self, filename):
        self._printProgress("Calculating LoC graph")
        ax = self._drawLocGraph()
        ax.set_ylabel('Lines')        
        ax.set_title('Lines of Code')
        self._closeDateLineGraph(ax, filename)

    def LocGraphAllDev(self, filename):
        self._printProgress("Calculating Developer Contribution graph")
        ax = None
        authList = self._getAuthorList()
        for author in authList:
            ax = self._drawlocGraphLineByDev(author, ax)

        #Add the list of authors as figure legend.
        #axes legend is added 'inside' the axes and overlaps the labels or the graph
        #lines depending on the location 
        self._addFigureLegend(ax, authList)
        
        ax.set_title('Contributed Lines of Code')
        ax.set_ylabel('Lines')        
        self._closeDateLineGraph(ax, filename)
        
    def LocGraphByDev(self, filename, devname):
        ax = self._drawlocGraphLineByDev(devname)
        ax.set_title('Contributed LoC by %s' % devname)
        ax.set_ylabel('Line Count')
        self._closeDateLineGraph(ax, filename)

    def LocChurnGraph(self, filename):
        self._printProgress("Calculating LoC and Churn graph")
        ax = self._drawLocGraph()
        ax = self._drawDailyChurnGraph(ax)
        ax.set_title('LoC and Churn')
        ax.set_ylabel('Line Count')
        #ax.legend(loc='center right')
        self._closeDateLineGraph(ax, filename)
        
    def FileCountGraph(self, filename):
        self._printProgress("Calculating File Count graph")
        
        self.cur.execute("select strftime('%%Y', SVNLog.commitdate), strftime('%%m', SVNLog.commitdate),\
                         strftime('%%d', SVNLog.commitdate), sum(SVNLog.addedfiles), sum(SVNLog.deletedfiles) \
                         from SVNLog, SVNLogDetail \
                         where SVNLog.revno = SVNLogDetail.revno and SVNLogDetail.changedpath like '%s'\
                         group by date(SVNLog.commitdate)" % self.searchpath)
        dates = []
        fc = []
        totalfiles = 0
        for year, month, day, fadded,fdeleted in self.cur:
            dates.append(datetime.date(int(year), int(month), int(day)))
            totalfiles = totalfiles + fadded-fdeleted
            fc.append(float(totalfiles))
        
        ax = self._drawDateLineGraph(dates, fc)
        ax.set_title('File Count')
        ax.set_ylabel('Files')
        self._closeDateLineGraph(ax, filename)

    def AvgFileLocGraph(self, filename):
        self._printProgress("Calculating Average File Size graph")
        
        self.cur.execute("select strftime('%%Y', SVNLog.commitdate), strftime('%%m', SVNLog.commitdate),\
                         strftime('%%d', SVNLog.commitdate), sum(SVNLogDetail.linesadded), sum(SVNLogDetail.linesdeleted), \
                         sum(SVNLog.addedfiles), sum(SVNLog.deletedfiles) \
                         from SVNLog, SVNLogDetail \
                         where SVNLog.revno = SVNLogDetail.revno and SVNLogDetail.changedpath like '%s'\
                         group by date(SVNLog.commitdate)" % self.searchpath)
        dates = []
        avgloclist = []
        avgloc = 0
        totalFileCnt = 0
        totalLoc = 0
        for year, month, day, locadded, locdeleted, filesadded, filesdeleted in self.cur:
            dates.append(datetime.date(int(year), int(month), int(day)))
            totalLoc = totalLoc + locadded-locdeleted
            totalFileCnt = totalFileCnt + filesadded - filesdeleted
            avgloc = 0.0
            if( totalFileCnt > 0.0):
               avgloc = float(totalLoc)/float(totalFileCnt)
            avgloclist.append(avgloc)
            
        ax = self._drawDateLineGraph(dates, avgloclist)
        ax.set_title('Average File Size (Lines)')
        ax.set_ylabel('LoC/Files')
        
        self._closeDateLineGraph(ax, filename)

    def AuthorActivityGraph(self, filename):
        self._printProgress("Calculating Author Activity graph")
        
        self.cur.execute("select SVNLog.author, sum(SVNLog.addedfiles), sum(SVNLog.changedfiles), sum(SVNLog.deletedfiles) \
                         from SVNLog, SVNLogDetail \
                         where SVNLog.revno = SVNLogDetail.revno and SVNLogDetail.changedpath like '%s'\
                         group by SVNLog.author" % self.searchpath)

        authlist = []
        addfraclist = []
        changefraclist=[]
        delfraclist = []
        
        for author, filesadded, fileschanged, filesdeleted in self.cur:
            authlist.append(author)            
            activitytotal = float(filesadded+fileschanged+filesdeleted)
            
            if( activitytotal > 0.0):
               addfraclist.append(float(filesadded)/activitytotal*100)
               changefraclist.append(float(fileschanged)/activitytotal*100)
               delfraclist.append(float(filesdeleted)/activitytotal*100)
            else:
               addfraclist.append(0.0)
               changefraclist.append(0.0)
               delfraclist.append(0.0)

        dataList = [addfraclist, changefraclist, delfraclist]
        
        barwid = 0.2
        legendlist = ["Adding", "Modifying", "Deleting"]
        ax = self._drawStackedHBarGraph(dataList, authlist, legendlist, barwid)
        #set the x-axis format.                
        ax.set_xbound(0, 100)
        xfmt = FormatStrFormatter('%d%%')
        ax.xaxis.set_major_formatter(xfmt)
        #set the y-axis format
        plt.setp( ax.get_yticklabels(), visible=True, fontsize='small')
        
        ax.set_title('Author Activity')
        fig = ax.figure
        fig.savefig(filename, dpi=self.dpi, format=self.format)
        
    def CommitActivityGraph(self, filename):
        self._printProgress("Calculating Commit activity graph")
        
        authList = self._getAuthorList()
        authCount = len(authList)

        authIdx = 1
        refaxs = None
        for author in authList:
            axs = self._drawCommitActivityGraphByAuthor(authCount, authIdx, author, refaxs)
            authIdx = authIdx+1
            #first axes is used as reference axes. Since the reference axis limits are shared by
            #all axes, every autoscale_view call on the new 'axs' will update the limits on the
            #reference axes. Hence I am storing xmin,xmax limits and calculating the minimum/maximum
            # limits for reference axis everytime. 
            if( refaxs == None):
                refaxs = axs

        #Set the x axis label on the last graph
        axs.set_xlabel('Date')
        
        #Turn on the xtick display only on the last graph
        plt.setp( axs.get_xmajorticklabels(), visible=True)
        plt.setp( axs.get_xminorticklabels(), visible=True)
        
        #Y axis is always set to 0 to 24 hrs
        refaxs.set_ybound(0, 24)
        hrLocator= FixedLocator([0,6,12,18,24])
        refaxs.yaxis.set_major_locator(hrLocator)
        
        self._closeScatterPlot(refaxs, filename, 'Commit Activity')
        
    def DirectorySizePieGraph(self, filename, depth=2):
        '''
        depth - depth of directory search relative to search path. Default value is 2
        '''
        self._printProgress("Calculating current Directory size pie graph")
        
        sqlQuery = "select dirname(SVNLogDetail.changedpath, %d), sum(SVNLogDetail.linesadded), sum(SVNLogDetail.linesdeleted) \
                    from SVNLog, SVNLogDetail \
                    where SVNLog.revno = SVNLogDetail.revno and SVNLogDetail.changedpath like '%s' \
                    group by dirname(SVNLogDetail.changedpath, %d)" % (depth, self.searchpath, depth)
        self.cur.execute(sqlQuery)
            
        dirlist = []
        dirsizelist = []        
        for dirname, linesadded, linesdeleted in self.cur:
            dsize = linesadded-linesdeleted
            if( dsize > 0):
                dirlist.append(dirname)
                dirsizelist.append(dsize)
                
        if( len(dirsizelist) > 0):
           axs = self._drawPieGraph(dirsizelist, dirlist)
           axs.set_title('Directory Sizes')        
           fig = axs.figure
           fig.savefig(filename, dpi=self.dpi, format=self.format)
            
    def DirectorySizeLineGraph(self, filename, depth=2):
        '''
        depth - depth of directory search relative to search path. Default value is 2
        '''
        self._printProgress("Calculating Directory size line graph")
        
        sqlQuery = "select dirname(changedpath, %d) from SVNLogDetail where changedpath like '%s' \
                         group by dirname(changedpath, %d)" % (depth, self.searchpath, depth)
        self.cur.execute(sqlQuery)
        
        dirlist = [dirname for dirname, in self.cur]
        ax = None
        for dirname in dirlist:
            ax = self._drawDirectorySizeLineGraphByDir(dirname, ax)

        self._addFigureLegend(ax, dirlist, loc="center right", ncol=1)
            
        ax.set_title('Directory Size (Lines of Code)')
        ax.set_ylabel('Lines')        
        self._closeDateLineGraph(ax, filename)

    def _drawLocGraph(self):
        self.cur.execute("select strftime('%%Y', SVNLog.commitdate), strftime('%%m', SVNLog.commitdate),\
                         strftime('%%d', SVNLog.commitdate), sum(SVNLogDetail.linesadded), sum(SVNLogDetail.linesdeleted) \
                         from SVNLog, SVNLogDetail \
                         where SVNLog.revno = SVNLogDetail.revno and SVNLogDetail.changedpath like '%s'\
                         group by date(SVNLog.commitdate)" % self.searchpath)
        dates = []
        loc = []
        tocalloc = 0
        for year, month, day, locadded, locdeleted in self.cur:
            dates.append(datetime.date(int(year), int(month), int(day)))
            tocalloc = tocalloc + locadded-locdeleted
            loc.append(float(tocalloc))
            
        ax = self._drawDateLineGraph(dates, loc)
        return(ax)
    
    def _drawDailyChurnGraph(self, ax):
        self.cur.execute("select strftime('%%Y', SVNLog.commitdate), strftime('%%m', SVNLog.commitdate),\
                         strftime('%%d', SVNLog.commitdate), sum(SVNLogDetail.linesadded+SVNLogDetail.linesdeleted) as churn\
                         from SVNLog, SVNLogDetail \
                         where SVNLog.revno = SVNLogDetail.revno and SVNLogDetail.changedpath like '%s'\
                         group by date(SVNLog.commitdate)" % self.searchpath)
        dates = []
        loc = []
        tocalloc = 0
        for year, month, day, churn in self.cur:
            dates.append(datetime.date(int(year), int(month), int(day)))
            loc.append(float(churn))
        
        lines = ax.vlines(dates, [0.1], loc, color='r', label='Churn')
        
        return(ax)
            
    def _drawDirectorySizeLineGraphByDir(self, dirname, ax):
        sqlQuery = "select sum(SVNLogDetail.linesadded), sum(SVNLogDetail.linesdeleted), \
                    strftime('%%Y', SVNLog.commitdate), strftime('%%m', SVNLog.commitdate), strftime('%%d', SVNLog.commitdate) \
                         from SVNLog, SVNLogDetail \
                         where SVNLog.revno = SVNLogDetail.revno and SVNLogDetail.changedpath like '%s%%' \
                         group by date(SVNLog.commitdate)" % (dirname)

        self.cur.execute(sqlQuery)
        dates = []
        dirsizelist = []
        dirsize = 0
        for locadded, locdeleted, year, month, day in self.cur:
            dates.append(datetime.date(int(year), int(month), int(day)))
            dirsize= dirsize+locadded-locdeleted
            dirsizelist.append(max(0, float(dirsize)))

        ax = self._drawDateLineGraph(dates, dirsizelist, ax)
        return(ax)
        
    def _getAuthorList(self):
        #Find out the unique developers
        self.cur.execute("select author from SVNLog group by author")
        #get the auhor list and store it. Since LogGraphLineByDev also does an sql query. It will otherwise
        # get overwritten
        authList = [author for author, in self.cur]
        #if there is an empty string in author list, replace it by "unknown"
        authListFinal = []
        for author in authList:
            if( author == ""):
                author='unknown'
            authListFinal.append(author)
        return(authListFinal)

    def _getLegendFont(self):
        legendfont = FontProperties(size='x-small')
        return(legendfont)

    def _getGraphFileName(self, dirpath, graphname):
        filename = os.path.join(dirpath, GraphNameDict[graphname])
        #now add the extension based on the format
        filename = "%s.%s" % (filename, self.format)
        return(filename)
    
    def _getGraphParamDict(self, thumbsize):
        graphParamDict = dict()
        for graphname in GraphNameDict.keys():
            graphParamDict[graphname] = self._getGraphFileName(".", graphname)
            
        graphParamDict["thumbwid"]=str(thumbsize)
        graphParamDict["thumbht"]=str(thumbsize)
        graphParamDict["RepoName"]=self.reponame
        return(graphParamDict)

    def _addFigureLegend(self, ax, labels, loc="lower center", ncol=4):
        fig = ax.figure
        legendfont = self._getLegendFont()
        assert(len(labels) > 0)
        lnhandles =ax.get_lines()
        assert(len(lnhandles) > 0)
        #Fix for a bug in matplotlib 0.98.5.2. If the len(labels) < ncol,
        # then i get an error "range() step argument must not be zero" on line 542 in legend.py
        if( len(labels) < ncol):
           ncol = len(labels)
        fig.legend(lnhandles, labels, loc=loc, ncol=ncol, prop=legendfont)
                
    def _drawCommitActivityGraphByAuthor(self, authIdx, authCount, author, axs=None):
        sqlQuery = "select strftime('%%H', commitdate), strftime('%%Y', SVNLog.commitdate), \
                    strftime('%%m', SVNLog.commitdate), strftime('%%d', SVNLog.commitdate) \
                    from SVNLog where author='%s' group by date(commitdate)" % author
        self.cur.execute(sqlQuery)

        dates = []
        committimelist = []
        for hr, year, month, day in self.cur:
            dates.append(datetime.date(int(year), int(month), int(day)))
            committimelist.append(int(hr))
        #Plot title
        plotTitle = "Author : %s" % author
        axs = self._drawScatterPlot(dates, committimelist, authCount, authIdx, plotTitle, axs)
        
        return(axs)
            
    def _drawlocGraphLineByDev(self, devname, ax=None):
        sqlQuery = "select strftime('%%Y', SVNLog.commitdate), strftime('%%m', SVNLog.commitdate),\
                         strftime('%%d', SVNLog.commitdate), sum(SVNLogDetail.linesadded), sum(SVNLogDetail.linesdeleted) \
                         from SVNLog, SVNLogDetail \
                         where SVNLog.revno = SVNLogDetail.revno and SVNLogDetail.changedpath like '%s' and SVNLog.author='%s' \
                         group by date(SVNLog.commitdate)" % (self.searchpath, devname)
        self.cur.execute(sqlQuery)
        dates = []
        loc = []
        tocalloc = 0
        for year, month, day, locadded, locdeleted in self.cur:
            dates.append(datetime.date(int(year), int(month), int(day)))
            tocalloc = tocalloc + locadded-locdeleted
            loc.append(float(tocalloc))
            
        ax = self._drawDateLineGraph(dates, loc, ax)
        return(ax)
    
    def _drawBarGraph(self, data, labels, barwid):
        #create dummy locations based on the number of items in data values
        xlocations = [x*2*barwid+barwid for x in range(len(data))]
        xtickloc = [x+barwid/2.0 for x in xlocations]
        xtickloc.append(xtickloc[-1]+barwid)
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.bar(xlocations, data, width=barwid)
        ax.set_xticks(xtickloc)
        ax.set_xticklabels(labels)
        
        return(ax)

    def _drawStackedHBarGraph(self, dataList, labels, legendlist, barwid):
        assert(len(dataList) > 0)
        numDataItems = len(dataList[0])
        #create dummy locations based on the number of items in data values
        ymin = 0.0        
        ylocations = [y*barwid*2+barwid/2 for y in range(numDataItems)]
        ymax = ylocations[-1]+2.0*barwid
        ytickloc = [y+barwid/2.0 for y in ylocations]
        ytickloc.append(ytickloc[-1]+barwid)
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_color_cycle(self.clrlist)
        ax.set_yticks(ytickloc)
        ax.set_yticklabels(labels)
        
        clridx = 0
        maxclridx = len(self.clrlist)
        ax.barh(ylocations, dataList[0], height=barwid, color=self.clrlist[clridx], label=legendlist[0])
        leftlist = [0 for x in range(0, numDataItems)]
        
        for i in range(1, len(dataList)):
            clridx=clridx+1
            if( clridx >= maxclridx):
                clridx = 0
            leftlist = [x+y for x,y in zip(leftlist, dataList[i-1])]
            ax.barh(ylocations, dataList[i], left=leftlist, height=barwid,
                    color=self.clrlist[clridx], label=legendlist[i])
            
        ax.legend(loc='lower center',ncol=3)        
        ax.set_ybound(ymin, ymax)
        
        return(ax)
    
    def _drawScatterPlot(self,dates, values, plotidx, plotcount, title, refaxs):
        if( refaxs == None):
            fig = plt.figure()
            #1 inch height for each author graph. So recalculate with height. Else y-scale get mixed.
            fig.set_figheight(self.commitGraphHtPerAuthor*plotcount)
            fig.subplots_adjust(top=0.85, left=0.05, right=0.95)
        else:
            fig = refaxs.figure
            
        axs = fig.add_subplot(plotcount, 1, plotidx,sharex=refaxs,sharey=refaxs)
        axs.grid(True)
        axs.plot_date(dates, values, marker='.', xdate=True, ydate=False)
        axs.autoscale_view()
        
        #Pass None as 'handles' since I want to display just the titles
        axs.set_title(title, fontsize='small',fontstyle='italic')
        
        self._setXAxisDateFormatter(axs)        
        plt.setp( axs.get_xmajorticklabels(), visible=False)
        plt.setp( axs.get_xminorticklabels(), visible=False)
                    
        return(axs)
    
    def _closeScatterPlot(self, refaxs, filename,title):
        #Do not autoscale. It will reset the limits on the x and y axis
        #refaxs.autoscale_view()

        fig = refaxs.figure
        #Update the font size for all subplots y-axis
        for axs in fig.get_axes():
            plt.setp( axs.get_yticklabels(), fontsize='x-small')
                
        fig.suptitle(title)        
        fig.savefig(filename, dpi=self.dpi, format=self.format)
        
    def _drawPieGraph(self, slicesizes, slicelabels):
        fig = plt.figure()
        axs = fig.add_subplot(111, aspect='equal')        
        (patches, labeltext, autotexts) = axs.pie(slicesizes, labels=slicelabels, autopct='%1.1f%%')
        #Turn off the labels displayed on the Piechart. 
        plt.setp(labeltext, visible=False)
        plt.setp(autotexts, visible=False)
        axs.autoscale_view()
        #Reposition the pie chart so that we can place a legend on the right
        bbox = axs.get_position()        
        (x,y, wid, ht) = bbox.bounds
        wid = wid*0.8
        bbox.bounds = (0, y, wid, ht)
        axs.set_position(bbox)
        #Now create a legend and place it on the right of the box.        
        legendtext=[]
        for slabel, ssize in zip(slicelabels, autotexts):
           legendtext.append("%s : %s" % (slabel, ssize.get_text()))

        fontprop = self._getLegendFont()
        legend = axs.legend(patches, legendtext, loc=(1, y), prop=fontprop)
        
        return(axs)

    def _setXAxisDateFormatter(self, ax):
##        years    = YearLocator()   # every year
##        months   = MonthLocator(interval=3)  # every 3 month
##        yearsFmt = DateFormatter('%Y')
##        monthsFmt = DateFormatter('%b')
        # format the ticks
##        ax.xaxis.set_major_locator(years)
##        ax.xaxis.set_major_formatter(yearsFmt)
##        ax.xaxis.set_minor_locator(months)
##        ax.xaxis.set_minor_formatter(monthsFmt)
        plt.setp( ax.get_xmajorticklabels(), fontsize='small')
        plt.setp( ax.get_xminorticklabels(), fontsize='x-small')
        
    def _closeDateLineGraph(self, ax, filename):
        assert(ax != None)
        ax.autoscale_view()
        self._setXAxisDateFormatter(ax)
        ax.grid(True)
        ax.set_xlabel('Date')
        fig = ax.figure
        fig.savefig(filename, dpi=self.dpi, format=self.format)        
        
    def _drawDateLineGraph(self, dates, values, axs= None):
        if( axs == None):
            fig = plt.figure()            
            axs = fig.add_subplot(111)
            axs.set_color_cycle(self.clrlist)
            
        axs.plot_date(dates, values, '-', xdate=True, ydate=False)
        
        return(axs)

def RunMain():
    usage = "usage: %prog [options] <svnsqlitedbpath> <graphdir>"
    parser = OptionParser(usage)

    parser.add_option("-n", "--name", dest="reponame",
                      help="repository name")
    parser.add_option("-s","--search", dest="searchpath", default="/",
                      help="search path in the repository (e.g. /trunk)")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="display verbose progress")
    parser.add_option("-r", "--dpi", dest="dpi", default=100, type="int",
                      help="set the dpi of output png images")
    parser.add_option("-t", "--thumbsize", dest="thumbsize", default=100, type="int",
                      help="set the widht and heigth of thumbnail display (pixels)")
    (options, args) = parser.parse_args()
    
    if( len(args) < 2):
        print "Invalid number of arguments"
    else:        
        svndbpath = args[0]
        graphdir  = args[1]
        
        if( options.searchpath.endswith('%') == False):
            options.searchpath +='%'
            
        if( options.verbose == True):
            print "Calculating subversion stat graphs"
            print "Subversion log database : %s" % svndbpath
            print "Graphs will generated in : %s" % graphdir
            print "Repository Name : %s" % options.reponame
            print "Search path inside repository : %s" % options.searchpath
            print "Graph thumbnail size : %s" % options.thumbsize
            
        svnplot = SVNPlot(svndbpath, dpi=options.dpi)
        svnplot.SetVerbose(options.verbose)
        svnplot.SetRepoName(options.reponame)
        svnplot.AllGraphs(graphdir, options.searchpath, options.thumbsize)
    
if(__name__ == "__main__"):
    RunMain()
    