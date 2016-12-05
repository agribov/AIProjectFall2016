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

import util

def switchPhaseReflex(state, phaseTime) :
    eval = evaluationFunction(state, phaseTime)
    #currPhase = state.traci().trafficlights.getPhase("0")
    #print currPhase
    
    if eval > 0: return False
    else: return True

def evaluationFunction(state, phaseTime) :
    # returns a value -- If the value is negative, switch phase,
    # else, keep the phase
    
    PHASE_TIME_VAL = 1
    GREEN_NUM_CARS_VAL = 5
    RED_NUM_CARS_VAL = 10
    GREEN_DIST_VAL = 1
    RED_DIST_VAL = 5
    AVG_SPEED_VAL = 10

    averageSpeed = 0
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
            #averageSpeed += state.traci().vehicle.getLanePosition
        averageSpeed = state.traci().multientryexit.getLastStepMeanSpeed(util.numToLane(lane))
        value += averageSpeed * AVG_SPEED_VAL

    for lane in redLanes:
        value -= state.getNumCars(lane) * RED_NUM_CARS_VAL
        for vehicle in state.getVehicleList(lane):
            dist = 500 - state.traci().vehicle.getLanePosition(vehicle)
            value -= (100 - dist) * RED_DIST_VAL

    #print value
    return value


class LearningAgent:
    def __init__(self, discount = 1):
        self.DISCOUNT = discount

        self.belief = []
        self.updateCounter = []
        for i in range(1440):
            #for j in range(1, 4):
            #laneList = [0.25, 0.25, 0.25, 0.25, 0.25]
            self.belief.insert(i, list((0.25, 0.25, 0.25, 0.25, 0.25)))
            self.updateCounter.insert(i, 1)
            
    def switchPhase(self, state, time, phaseTime) :
        
        minute = (time % 86400) / 60
        #print(["Update #", self.updateCounter[minute]])
        #print("Belief: ", self.belief[minute])

        self.updateBelief2(state, minute)
        value = self.evaluationFunction(state, minute, phaseTime)
        
        if value > 0: return False
        else: return True

    def updateBelief(self, state, minute) :
        NEW_VAL = 1
    
        totalBelief = 0;
        lanes = [1, 2, 3, 4]

        # Calculate new beliefs based on values
        for lane in lanes:
            newBelief = self.belief[minute][lane] * self.DISCOUNT
            newBelief *= (state.getNumCars(lane) + 1) * NEW_VAL
            self.belief[minute][lane] = newBelief
            totalBelief += newBelief
            
        # Normalize the four lanes in relation to each other
        for lane in lanes:
            self.belief[minute][lane] /= totalBelief

        return 0

    def updateBelief2(self, state, minute) :
        NEW_VAL = 1
    
        totalBelief = 0;
        totalTemp = 0;
        lanes = [1, 2, 3, 4]
        tempBelief = [0, 0, 0, 0, 0,]

        # Calculate new beliefs based on values
        for lane in lanes:
            """
            newBelief = self.belief[minute][lane] * self.DISCOUNT
            newBelief *= (state.getNumCars(lane) + 1) * NEW_VAL
            self.belief[minute][lane] = newBelief
            totalBelief += newBelief
            """
            tempBelief[lane] = (state.getNumCars(lane) + 1) * NEW_VAL
            totalTemp += tempBelief[lane]
            
        #print ("Current layout: ", tempBelief)
            
        # Normalize the four lanes in relation to each other
        for lane in lanes:
            #print(tempBelief[lane], totalTemp)
            tempBelief[lane] = float(tempBelief[lane]) / totalTemp
            #self.belief[minute][lane] /= totalBelief
            print(self.updateCounter[minute])
            tempBelief[lane] += self.belief[minute][lane] * self.updateCounter[minute]
            #print(tempBelief[lane])
            totalBelief += tempBelief[lane]

        #print ("New Temp: ", tempBelief)
            
        for lane in lanes:
            self.belief[minute][lane] = tempBelief[lane] / totalBelief

        #print ("New Belief: ", self.belief[minute])
            
        self.updateCounter[minute] += 1
        return 0
    
    def evaluationFunction(self, state, minute, phaseTime) :
    # returns a value -- If the value is negative, switch phase,
    # else, keep the phase
    
        PHASE_TIME_VAL = 1
        GREEN_NUM_CARS_VAL = 5
        RED_NUM_CARS_VAL = 10
        GREEN_DIST_VAL = 1
        RED_DIST_VAL = 5
        AVG_SPEED_VAL = 10
        BELIEF_VALUE = 100

        averageSpeed = 0
        value = 0
        phase = state.traci().trafficlights.getPhase("0")
        greenBelief = 0
        redBelief = 0
        
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
                #averageSpeed += state.traci().vehicle.getLanePosition
            averageSpeed = state.traci().multientryexit.getLastStepMeanSpeed(util.numToLane(lane))
            value += averageSpeed * AVG_SPEED_VAL
            greenBelief += self.belief[minute][lane]

        for lane in redLanes:
            value -= state.getNumCars(lane) * RED_NUM_CARS_VAL
            for vehicle in state.getVehicleList(lane):
                dist = 500 - state.traci().vehicle.getLanePosition(vehicle)
                value -= (100 - dist) * RED_DIST_VAL

            redBelief += self.belief[minute][lane]

        if redBelief > greenBelief:
            value -= redBelief * BELIEF_VALUE
        else:
            value += greenBelief * BELIEF_VALUE
            
        print value
        return value
