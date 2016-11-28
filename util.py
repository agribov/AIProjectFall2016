"""
Artificial Intelligence Fall 2016
Final Project: NeverRed

Authors: Alex Gribov and Donovyn Pickler
File: util.py

This file is entirely the work of the authors
"""

import sys

def raiseNotDefined():
    fileName = inspect.stack()[1][1]
    line = inspect.stack()[1][2]
    method = inspect.stack()[1][3]

    print "*** Method not implemented: %s at line %s of %s" % (method, line, fileName)
    sys.exit(1)

def numToLane(n):
    return {1:"e3_0_1i", 2:"e3_0_2i", 3:"e3_0_3i", 4:"e3_0_4i"}[n]
