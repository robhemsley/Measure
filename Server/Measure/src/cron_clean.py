#!/usr/bin/env python

"""
cron_clean - Utility

Cleans out all the old files from the directories. 
If a file is older than 24 hours it is deleted.

@author: Rob Hemsley
@contact: hello@robhemsley.co.uk
@copyright: Rob Hemsley 2013
"""

#Module imports
import os, datetime, config

#Global variables
global del_total
del_total = 0

def cleanDir(dir_to_search):
    """
    cleanDir - Function
    @summary: Iterates over the passed director and removes the file if older than 24 hours
    @param dir_to_search: The top level directory to search through
    @type dir_to_search: String 
    """
    global del_total
    for dirpath, dirnames, filenames in os.walk(dir_to_search):
        for file_dir in filenames:
            curpath = os.path.join(dirpath, file_dir)
            file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
            if datetime.datetime.now() - file_modified > datetime.timedelta(hours = 24):
                print "Removing: ", curpath
                del_total += 1
                os.remove(curpath)
                
if __name__ == "__main__":
    #The directories to clean (Loaded from Config)
    dirs = [os.path.abspath(config.OUTLINE_DIR), os.path.abspath(config.SCANS_DIR), os.path.abspath(config.SVG_DIR)]
    for dir in dirs:
        if (os.path.exists(dir)):
            print "CLeaning: ", dir
            cleanDir(dir)
            
    print "Cleaning Finished"
    print "Deleted %d Files"% (del_total)
    