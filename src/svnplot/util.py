'''
util.py
Copyright (C) 2009 Nitin Bhide (nitinbhide@gmail.com)

This module is part of SVNPlot (http://code.google.com/p/svnplot) and is released under
the New BSD License: http://www.opensource.org/licenses/bsd-license.php
--------------------------------------------------------------------------------------
various utility functions used by other stats classes
'''

import logging
import itertools
import os.path

def filetype(path):
    '''
    get the file type (i.e. extension) from the path
    '''
    (root, ext) = os.path.splitext(path)
    return(ext)

def dirname(searchpath, path, depth):
    '''
    get directory name till given depth (relative to searchpath) from the full file path
    '''
    assert(searchpath != None and searchpath != "")
    assert(path.startswith(searchpath) == True)
    #replace the search path and then compare the depth
    path = path.replace(searchpath, "", 1)
    #first split the path and remove the filename
    pathcomp = os.path.dirname(path).split('/')
    #now join the split path upto given depth only
    dirpath = '/'.join(pathcomp[0:depth])
    #Now add the dirpath to searchpath to get the final directory path
    dirpath = searchpath+dirpath
    return(dirpath)

def parent_dirname(path):
    '''
    get parent directory name.
    '''
    return(os.path.dirname(path))

def pairwise(iterable):
    "s -> (0, s0,s1), (1, s1,s2), (2, s2, s3), ..."
    a, b = itertools.tee(iterable)
    #goto next item in the iterable b.
    b.next()    
    return itertools.izip(itertools.count(0), a, b)

def strip_zeros(dates, data):
    '''
    strips the dates with data is zero at start of the list
    '''
    filtered_dates = dates
    filtered_data = data
    if( len(data) > 0 and data[0] == 0):
        filtered_dates = []
        filtered_data = []
        filter=True
        for dt, datedata in zip(dates, data):
            if( filter == True and datedata == 0):
                continue
            filter=False
            filtered_dates.append(dt)
            filtered_data.append(datedata)
    return(filtered_dates, filtered_data)

def timedelta2days(tmdelta):
    return(tmdelta.days + tmdelta.seconds/(3600.0*24.0))