"""
Artificial Intelligence Fall 2016
Final Project: NeverRed

Authors: Alex Gribov and Donovyn Pickler
File: trafficAgents.py

This file is entirely the work of the authors
"""

from util import *
import sys

class TrafficAgent:
    def __init__(self):
        util.raiseNotDefined()

    def getAction(self, state):
        util.raiseNotDefined()

class TrafficState:

    def __init__(self, traciObj, n = 4):
        self.traciData = traciObj
        self.numLanes = n
        self.vehicles = []
        for i in range(1,n+1):
            self.vehicles.append(self.traciData.multientryexit.getLastStepVehicleIDs(numToLane(i)))

    def getNumHalted(self, laneNum):
        return self.traciData.multientryexit.getLastStepHaltingNumber(numToLane(laneNum))

    def getNumCars(self, laneNum):
        return self.traciData.multientryexit.getLastStepVehicleNumber(numToLane(laneNum))

    def getVehicleList(self, laneNum):
        print laneNum
        print self.vehicles
        return self.vehicles[laneNum-1]

    def getLightState(self):
        return self.traciData.trafficlights.getPhase("0")

    def setLightState(self, nextState):
        return 0
    
    def traci(self):
        return self.traciData
