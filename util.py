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

#takes the wait times for the four lanes and writes it to an output file.
def stringWaitTimes(rawTime, lane1,lane2,lane3,lane4):
    time = getTime(rawTime)
    laneWE = lane1
    laneEW = lane2
    laneNS = lane3
    laneSN = lane4
    meanTime = (lane1 + lane2 + lane3 + lane4) / 4
    returnable = ["day:" , time[0] , "Time:" , time[1] , ":" , time[2] , ":" , time[3] , "laneWE:" , laneWE , "laneEW:" , laneEW , "laneNS:" , laneNS , "laneSN:" , laneSN , "meanTime:" , meanTime]
    return returnable
    
    
    

