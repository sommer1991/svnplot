#!/usr/bin/env python
'''
svnlog2sqlite.py
Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com)

This module is part of SVNPlot (http://code.google.com/p/svnplot) and is released under
the New BSD License: http://www.opensource.org/licenses/bsd-license.php
--------------------------------------------------------------------------------------

python script to convert the Subversion log into an sqlite database
The idea is to use the generated SQLite database as input to Matplot lib for
creating various graphs and analysis. The graphs are inspired from graphs
generated by StatSVN/StatCVS.
'''

import datetime,calendar
import sys,os
import logging
import traceback
#from optparse import OptionParser

import svnlogiter
from svnlogclient import makeunicode
from configoptparse import ConfigOptionParser
from svnlogdb import SVNLogDB

BINARYFILEXT = [ 'doc', 'xls', 'ppt', 'docx', 'xlsx', 'pptx', 'dot', 'dotx', 'ods', 'odm', 'odt', 'ott', 'pdf',
                 'o', 'a', 'obj', 'lib', 'dll', 'so', 'exe',
                 'jar', 'zip', 'z', 'gz', 'tar', 'rar','7z',
                 'pdb', 'idb', 'ilk', 'bsc', 'ncb', 'sbr', 'pch', 'ilk',
                 'bmp', 'dib', 'jpg', 'jpeg', 'png', 'gif', 'ico', 'pcd', 'wmf', 'emf', 'xcf', 'tiff', 'xpm',
                 'gho', 'mp3', 'wma', 'wmv','wav','avi'
                 ]
    
class SVNLog2Sqlite:
    def __init__(self, svnrepopath, sqlitedbpath,verbose=False,**kwargs):
        username=kwargs.pop('username', None)
        password=kwargs.pop('password',None)        
        logging.info("Repo url : " + svnrepopath)
        self.svnclient = svnlogiter.SVNLogClient(svnrepopath,BINARYFILEXT,username=username, password=password)
        self.db = SVNLogDB(dbpath = sqlitedbpath)
        self.verbose = verbose
        self.commit_after_numrev = kwargs.pop('commit_after_numrev', 10)
        self.filediff = kwargs.pop('filediff', False)
        if self.commit_after_numrev < 1:
            self.commit_after_numrev = 1
        
    def convert(self, svnrevstartdate, svnrevenddate, bUpdLineCount=True, maxtrycount=3):
        #First check if this a full conversion or a partial conversion
        self.db.connect()
        self.CreateTables()
        for trycount in range(0, maxtrycount):
            try:
                laststoredrev = self.getLastStoredRev()
                rootUrl = self.svnclient.getRootUrl()
                self.printVerbose("Root url found : %s" % rootUrl)
                (startrevno, endrevno) = self.svnclient.findStartEndRev(svnrevstartdate, svnrevenddate)
                self.printVerbose("Repository Start-End Rev no : %d-%d" % (startrevno, endrevno))
                startrevno = max(startrevno,laststoredrev+1)
                self.ConvertRevs(startrevno, endrevno, bUpdLineCount)
                #every thing is ok. Commit the changes.
                self.db.commit()
            except Exception, expinst:
                logging.exception("Found Error")
                self.svnexception_handler(expinst)
                print "Trying again (%d)" % (trycount+1)            
        
        self.closedb()
        
    def closedb(self):
        self.db.close()
        
    def svnexception_handler(self, expinst):
        '''
        decide to continue or exit on the svn exception.
        '''
        self.db.rollback()
        print "Found Error. Rolled back recent changes"
        print "Error type %s" % type(expinst)
        if( isinstance(expinst, AssertionError)):            
            exit(1)            
        exitAdvised = self.svnclient.printSvnErrorHint(expinst)
        if( exitAdvised):
            exit(1)
    
    def CreateTables(self):
        self.db.CreateTables()

    def getLastStoredRev(self):
        return self.db.getLastStoredRev()
        
    def getFilePathId(self, filepath):
        '''
        update the filepath id if required.
        '''
        return self.db.getFilePathId()
        
    def ConvertRevs(self, startrev, endrev, bUpdLineCount):
        self.printVerbose("Converting revisions %d to %d" % (startrev, endrev))
        if( startrev <= endrev):
            self.printVerbose("Conversion started")
            logging.info("Updating revision from %d to %d" % (startrev, endrev))
            svnloglist = svnlogiter.SVNRevLogIter(self.svnclient, startrev, endrev, bUseFileDiff=self.filediff)
            revcount = 0            
            lc_updated = 'N'
            if( bUpdLineCount == True):
                lc_updated = 'Y'
            lastrevno = 0
            bAddDummy=True
            
            for revlog in svnloglist:
                logging.debug("Revision author:%s" % revlog.author)
                logging.debug("Revision date:%s" % revlog.date)
                logging.debug("Revision msg:%s" % revlog.message)
                revcount = revcount+1
                
                addedfiles, changedfiles, deletedfiles = revlog.changedFileCount()                
                if( revlog.isvalid() == True):
                    self.db.addRevision(revlog, addedfiles, changedfiles, deletedfiles)
                    
                    for change in revlog.getDiffLineCount(bUpdLineCount):
                        self.db.addRevisionDetails(revlog.revno, change,lc_updated)
                        
                    if( bUpdLineCount == True and bAddDummy==True):
                        #dummy entries may add additional added/deleted file entries.
                        (addedfiles1, deletedfiles1) = self.addDummyLogDetail(revlog)
                        addedfiles = addedfiles+addedfiles1
                        deletedfiles = deletedfiles+deletedfiles1
                        self.db.updateNumFiles(revlog.revno, addedfiles,deletedfiles)
                            
                        #print "%d : %s : %s : %d : %d " % (revlog.revno, filename, changetype, linesadded, linesdeleted)
                    lastrevno = revlog.revno                    
                    #commit after every 10 revisions or number revisions is less than 10, commit after every revision
                    if( revcount % self.commit_after_numrev == 0):
                        self.db.commit()
                        self.printVerbose("Number revisions converted : %d (Rev no : %d)" % (revcount, lastrevno))
                logging.debug("Number revisions converted : %d (Rev no : %d)" % (revcount, lastrevno))
                
            if( self.verbose == False):            
                print "Number revisions converted : %d (Rev no : %d)" % (revcount, lastrevno)
                
    def __createRevFileListForDir(self, revno, dirname):
        '''
        create the file list for a revision in a temporary table.
        '''
        self.db.createRevFileListForDir(revno, dirname)
                    
    def addDummyLogDetail(self,revlog):
        '''
        add dummy log detail entries for getting the correct line count data in case of tagging/branching and deleting the directories.
        '''        
        addedfiles = 0
        deletedfiles = 0
        
        copied_dirlist = revlog.getCopiedDirs()
        deleted_dirlist = revlog.getDeletedDirs()
        
        if( len(copied_dirlist) > 0 or len(deleted_dirlist) > 0):
            #since we may have to query the existing data. Commit the changes first.
            self.db.commit()
            #Now create list of file names for adding dummy entries. There is
            #no  need to add dummy entries for directories.
            if( len(copied_dirlist) > 0):
                #now update the additions    
                #Path type is directory then dummy entries are required.
                #For file type, 'real' entries will get creaetd
                logging.debug("Adding dummy file addition entries")
                deleted_dirlist = self.db.createRevFileList(revlog, copied_dirlist, deleted_dirlist)
                addedfiles  = self.db.addDummyAdditionDetails(revlog.revno)                
            if len(deleted_dirlist) > 0:
                logging.debug("Adding dummy file deletion entries")
                for deleted_dir in deleted_dirlist:
                    deletedfiles = deletedfiles+ self.db.addDummyDeletionDetails(revlog.revno, deleted_dir.filepath())
                
        return(addedfiles, deletedfiles)
            
    def UpdateLineCountData(self):
        self.initdb()
        try:        
            self.__updateLineCountData()
        except Exception, expinst:            
            logging.exception("Error %s" % expinst)
            print "Error %s" % expinst            
        self.closedb()
        
    def __updateLineCountData(self):
        '''Update the line count data in SVNLogDetail where lc_update flag is 'N'.
        This function is to be used with incremental update of only 'line count' data.
        '''
        #first create temporary table from SVNLogDetail where only the lc_updated status is 'N'
        #Set the autocommit on so that update cursor inside the another cursor loop works.
                
        for revno, changedpath, changetype in self.getRevsLineCountNotUpdated():
            linesadded =0
            linesdeleted = 0
            self.printVerbose("getting diff count for %d:%s" % (revno, changedpath))
            
            linesadded, linesdeleted = self.svnclient.getDiffLineCountForPath(revno, changedpath, changetype)
            self.updateLineCount(revno,changedpath, linesadded,linesdeleted)
            
        self.db.commit()
                
    def printVerbose(self, msg):
        logging.info(msg)
        if( self.verbose==True):
            print msg            
                    
def getLogfileName(sqlitedbpath):
    '''
    create log file in using the directory path from the sqlitedbpath
    '''
    dir, file = os.path.split(sqlitedbpath)
    pfile, ext = os.path.splitext(file) #finding the name of the database created database_file_name.db
    lognamefile = 'svnlog2sqlite.' + pfile + '.log' #creates a log file with the same name database_file_name.log
    logfile = os.path.join(dir, lognamefile)
    return(logfile)
    
def parse_svndate(svndatestr):
    '''
    Using simple dates '{YEAR-MONTH-DAY}' as defined in http://svnbook.red-bean.com/en/1.5/svn-book.html#svn.tour.revs.dates
    '''
    svndatestr = svndatestr.strip()
    svndatestr = svndatestr.strip('{}')
    svndatestr = svndatestr.split('-')    

    year = int(svndatestr[0])
    month = int(svndatestr[1])
    day = int(svndatestr[2])

    #convert the time to typical unix timestamp for seconds after epoch
    svntime = datetime.datetime(year, month, day)
    svntime = calendar.timegm(svntime.utctimetuple())
    
    return(svntime)

def getquotedurl(url):
    '''
    svn repo url specified on the command line can contain specs, special etc. We
    have to quote them to that svn log client works on a valid url.
    '''
    import urllib
    import urlparse
    urlparams = list(urlparse.urlsplit(url, 'http'))
    urlparams[2] = urllib.quote(urlparams[2])
    
    return(urlparse.urlunsplit(urlparams))
    
def RunMain():
    usage = "usage: %prog [options] <svnrepo root url> <sqlitedbpath>"
    parser = ConfigOptionParser(usage)
    parser.set_defaults(updlinecount=False)

    parser.add_option("-l", "--linecount", action="store_true", dest="updlinecount", default=False,
                      help="extract/update changed line count (True/False). Default is False")
    parser.add_option("-g", "--log", action="store_true", dest="enablelogging", default=False,
                      help="Enable logging during the execution(True/False). Name of generated logfile is svnlog2sqlite.log.")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="Enable verbose output. Default is False")
    parser.add_option("-u", "--username", dest="username",default=None, action="store", type="string",
                      help="username to be used for repository authentication")
    parser.add_option("-p", "--password", dest="password",default=None, action="store", type="string",
                      help="password to be used for repository authentication")
    parser.add_option("-c", "--commit", dest="commit_after_numrev",default=10, action="store", type="int",
                      help="Commit to sqlite database after given number of revisions (Default 10)")
    parser.add_option("", "--filediff", dest="filediff",default=False, action="store_true", 
                      help="Force use file diff to calculate line count (will be slow)")
    
    (options, args) = parser.parse_args()
    
    if( len(args) < 2 ):
        print "Invalid number of arguments. Use svnlog2sqlite.py --help to see the details."    
    else:
        svnrepopath = args[0]
        sqlitedbpath = args[1]
        svnrevstartdate = None
        svnrevenddate = None
        
        if( len(args) > 3):
            #more than two argument then start date and end date is specified.
            svnrevstartdate = parse_svndate(args[2])
            svnrevenddate = parse_svndate(args[3])
            
        if( not svnrepopath.endswith('/')):
            svnrepopath = svnrepopath+'/'
        
        svnrepopath = getquotedurl(svnrepopath)
        
        print "Updating the subversion log"
        print "Repository : " + svnrepopath            
        print "SVN Log database filepath : %s" % sqlitedbpath
        print "Extract Changed Line Count : %s" % options.updlinecount
        if( not options.updlinecount):
            print "\t\tplease use -l option. if you want to extract linecount information."
        if( svnrevstartdate):
            print "Repository startdate: %s" % (svnrevstartdate)
        if( svnrevenddate):
            print "Repository enddate: %s" % (svnrevenddate)
        
        if(options.enablelogging==True):
            logfile = getLogfileName(sqlitedbpath)
            logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=logfile,
                    filemode='w')
            print "Debug Logging to file %s" % logfile

        filediff = options.filediff
        conv = None            
        conv = SVNLog2Sqlite(svnrepopath, sqlitedbpath,verbose=options.verbose,
                username=options.username, password=options.password,
                commit_after_numrev=options.commit_after_numrev, filediff=filediff)
        conv.convert(svnrevstartdate, svnrevenddate, options.updlinecount)        
        
if( __name__ == "__main__"):
    RunMain()
    
