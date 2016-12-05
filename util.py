"""
Artificial Intelligence Fall 2016
Final Project: NeverRed

Authors: Alex Gribov and Donovyn Pickler
File: util.py

This file is entirely the work of the authors
"""

import sys
#import traci

def raiseNotDefined():
    fileName = inspect.stack()[1][1]
    line = inspect.stack()[1][2]
    method = inspect.stack()[1][3]

    print "*** Method not implemented: %s at line %s of %s" % (method, line, fileName)
    sys.exit(1)

def numToLane(n):
    return {1:"e3_0_1i", 2:"e3_0_2i", 3:"e3_0_3i", 4:"e3_0_4i"}[n]

def getTime(n):
    #1 day = 86400 time steps
    day = n / 86400
    #1 hour = 3600 time steps
    hour = (n - (day * 86400)) / 3600
    #1 minute = 60 time steps
    minute = (n - (day * 86400)- (hour * 3600)) / 60
    #1 second = 1 time step
    second = (n - (day * 86400)- (hour * 3600) - (minute * 60))
    return [day, hour, minute, second]


def getWaitTimes(n):
    time = getTime(n)
    print "day: " + time[0] + "  " + time[1] + ':' + time[2] + ':' + time[3]
    
    
