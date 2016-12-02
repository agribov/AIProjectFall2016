"""
Artificial Intelligence Fall 2016
Final Project: NeverRed

Authors: Alex Gribov and Donovyn Pickler
File: learningAgents.py

This file is entirely the work of the authors
"""

#class ReflexAgent(TrafficAgent):

#    def getAction(self, trafficState)
        
"""
Phase 2 is EW Green

Phase 3 is NS Green
"""

def evaluationFunction(state, phaseTime) :
    # returns a value -- If the value is negative, switch phase,
    # else, keep the phase
    
    PHASE_TIME_VAL = 1
    GREEN_NUM_CARS_VAL = 1
    RED_NUM_CARS_VAL = 1
    GREEN_DIST_VAL = 1
    RED_DIST_VAL = 1
    
    value = 0
    phase = state.traci().trafficlights.getPhase("0")

    value -= phaseTime * PHASE_TIME_VAL
    if phase == 2:
        greenLanes = [1, 2]
        redLanes = [3, 4]

    else:
        greenLanes = [3, 4]
        redLanes = [1, 2]

    for lane in greenLanes:
        value += state.getNumCars(lane) * GREEN_NUM_CARS_VAL
        #print lane
        for vehicle in state.getVehicleList(lane):
            dist = 500 - state.traci().vehicle.getLanePosition(vehicle)
            value += dist * GREEN_DIST_VAL

    for lane in redLanes:
        value -= state.getNumCars(lane) * RED_NUM_CARS_VAL
        for vehicle in state.getVehicleList(lane):
            dist = 500 - state.traci().vehicle.getLanePosition(vehicle)
            value -= (100 - dist) * RED_DIST_VAL
     
    return value
