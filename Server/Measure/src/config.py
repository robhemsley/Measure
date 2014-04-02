#/usr/bin/env python

"""
# Magical Config File For Jon
#
# Provides global variables for use across the service

@author: Rob Hemsley
@contact: hello@robhemsley.co.uk
@copyright: Rob Hemsley 2013
"""

DEBUG                   = False                                     #Enable/Disable Debugging - Displays CV stages
SERVER                  = "18.111.46.123:29819"#"measure.robhemsley.webfactional.com"     #The public address for the service
PORT                    = 29819                                     #Port Number the service is running on
OUTLINE_DIR             = "outline/"                                #The directory for the outline JPG file
SCANS_DIR               = "raw/"                                    #The down-sampled image from user
SVG_DIR                 = "svg/"                                    #The location for the SVG outline

ERROR_NO_RULER          = "Unable to find ruler..."                 #Error message for no ruler found

#Image Rec Params - Don't adjust unless you want to break it
FLANN_INDEX_KDTREE      = 1                                         
FLANN_INDEX_LSH         = 6                                         
FLANN_TABLE_NUM         = 6                                         
FLANN_KEY_SIZE          = 12
FLANN_MULTI_PROBE_LEVEL = 1
FLANN_MIN_MATCH_COUNT   = 4

#SVG settings
SVG_DOC_NAME            = "Material Template"
SVG_DISPLAY_CMD         = "open"                                    #When display is called the app the filename is passed to   
