"""
Artificial Intelligence Fall 2016
Final Project: NeverRed

Authors: Alex Gribov and Donovyn Pickler

Note: We based this off of the "runner.py" file fom SUMO's
TraCi TLS tutorial, and so we left the original header below
"""

#!/usr/bin/env python
"""
@file    runner.py
@author  Lena Kalleske
@author  Daniel Krajzewicz
@author  Michael Behrisch
@author  Jakob Erdmann
@date    2009-03-26
@version $Id: runner.py 19535 2015-12-05 13:47:18Z behrisch $

Tutorial for traffic light control via the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.dlr.de/
Copyright (C) 2009-2015 DLR/TS, Germany

This file is part of SUMO.
SUMO is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.
"""

import os
import sys
import optparse
import subprocess
import random
import basics
import learningAgents
import util
from datetime import datetime

"""
sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
    """

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append('/usr/share/sumo/tools')
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci
# the port used for communicating with your sumo instance
PORT = 8873


def generate_routefile():
    random.seed(42)  # make tests reproducible
    #N = 86400
    N = 691200 # number of time steps, one tick is one second.
    # 12/2/2016 Number of time steps taken chosen to represent eight days.
    #break points will be set at rush hour, end of day 1, start of day 8, rush hour day 

    trafficBase = .05

    # demand per second from different directions
    pWE = trafficBase #travel from a suburb into a city
    pEW = trafficBase #travel from a city into a suburb
    pNS = trafficBase * .7 #Uniform NS traffic the entire time
    pSN = trafficBase * .7 #Uniform SN traffic the entire time

    time = 0
    
    with open("data/cross.rou.xml", "w") as routes:
        print >> routes, """<routes>
        <vType id="typeWE" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>
        <vType id="typeNS" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>

        <route id="right" edges="51o 1i 2o 52i" />
        <route id="left" edges="52o 2i 1o 51i" />
        <route id="down" edges="54o 4i 3o 53i" />
        <route id="up" edges="53o 3i 4o 54i" />"""
        lastVeh = 0
        vehNr = 0
        for i in range(N):
            if random.uniform(0, 1) < pWE:
                print >> routes, '    <vehicle id="right_%i" type="typeWE" route="right" depart="%i" />' % (
                    vehNr, i)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pEW:
                print >> routes, '    <vehicle id="left_%i" type="typeWE" route="left" depart="%i" />' % (
                    vehNr, i)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pNS:
                print >> routes, '    <vehicle id="down_%i" type="typeNS" route="down" depart="%i" />' % (
                    vehNr, i)
                vehNr += 1
                lastVeh = i
            if random.uniform(0, 1) < pSN:
                print >> routes, '    <vehicle id="up_%i" type="typeNS" route="up" depart="%i" />' % (
                    vehNr, i)
                vehNr += 1
                lastVeh = i

            time = util.getTime(i)
            
            #Morning rush hour defined as starting around 7am and continuing until 9am, peaking at 8am, gradual increase and decrease.
            #Set to alter the value every minute
            if time[1] < 9 & time[1] > 7 & time[3] == 0:  
                if time[1] < 8:
                    pWE += .005
                else:
                    pWE -= .005

            #Afternoon rush hour defined as starting at 5pm and going until 7pm, sharp increase with slow taper.
            #Set to alter the value every minute
            if time[1] > 17 & time[1] < 19 & time[3] == 0:
                if time[1] == 5 & time[2] < 15:
                    pEW += .02
                else:
                    pEW -= .00125
                    
            #Resetting the traffic values to prevent weird things happening with floats.
            if time[1] == 0 & time[2] == 0 & time[3] == 0:
                pWE = trafficBase
                pEW = trafficBase
            #leave north to south / south to north traffic constant for the whole experiment.
            
        print >> routes, "</routes>"

# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#        <phase duration="31" state="GrGr"/>
#        <phase duration="6"  state="yryr"/>
#        <phase duration="31" state="rGrG"/>
#        <phase duration="6"  state="ryry"/>
#    </tlLogic>


def run():
    """execute the TraCI control loop"""
    traci.init(PORT)
    step = 0
    timeCount = 0
    # we start with phase 2 where EW has green
    traci.trafficlights.setPhase("0", 2)
    evaluator = learningAgents.LearningAgent()

    
    #opening an output file.
    fileName = "Output.txt"
    outFile = open(fileName, 'w')

    """
    Lane IDs:
    West to East: 1i_0
    East to West: 2i_0
    South to North: 3i_0
    North to South: 4i_0
    """
    laneWE = 0
    laneEW = 0
    laneSN = 0
    laneNS = 0

    
    
    #phaseTimer # = 0 # Counts how many time steps have occured since the last phase change
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()        
        step += 1
        timeCount += 1
        # Functions from http://sumo.dlr.de/daily/pydoc/traci.html

        state = basics.TrafficState(traci)
        
        #newPhase = learningAgents.chooseActionReflex(state, 0)
        #traci.trafficlights.setPhase("0", newPhase)
        if step >= 32:
            step = 0
            print "Stepped"
            if evaluator.switchPhase(state, timeCount, 0):
                # we are not already switching
                #if traci.inductionloop.getLastStepVehicleNumber("0") > 0:
                if traci.trafficlights.getPhase("0") == 2:
                    # there is a vehicle from the north, switch
                    traci.trafficlights.setPhase("0", 3)
                else:
                    # otherwise try to keep green for EW
                    traci.trafficlights.setPhase("0", 2)
        
        
        
        time = util.getTime(timeCount)
        
        if time[1] >= 7 and time [1] < 9:
            laneWE = ((laneWE * (timeCount-1)) +traci.lane.getLastStepMeanSpeed('1i_0'))/timeCount
            laneEW = ((laneEW * (timeCount-1)) +traci.lane.getLastStepMeanSpeed('2i_0'))/timeCount
            laneSN = ((laneSN * (timeCount-1)) +traci.lane.getLastStepMeanSpeed('3i_0'))/timeCount
            laneNS = ((laneNS * (timeCount-1)) +traci.lane.getLastStepMeanSpeed('4i_0'))/timeCount
        
        
        if time[1] == 9 and time[2] == 0 and time[3] == 0:
            outFile.write(str(util.stringWaitTimes(timeCount, laneWE, laneEW, laneSN, laneNS)))
            outFile.write('\n')
            laneWE = 0
            laneEW = 0
            laneSN = 0
            laneNS = 0

        if time[1] >= 17 and time [1] < 19:
            laneWE = ((laneWE * (timeCount-1)) +traci.lane.getLastStepMeanSpeed('1i_0'))/timeCount
            laneEW = ((laneEW * (timeCount-1)) +traci.lane.getLastStepMeanSpeed('2i_0'))/timeCount
            laneSN = ((laneSN * (timeCount-1)) +traci.lane.getLastStepMeanSpeed('3i_0'))/timeCount
            laneNS = ((laneNS * (timeCount-1)) +traci.lane.getLastStepMeanSpeed('4i_0'))/timeCount
        
        
        if time[1] == 9 and time[2] == 0 and time[3] == 0:
            outFile.write(str(util.stringWaitTimes(timeCount, laneWE, laneEW, laneSN, laneNS)))
            outFile.write('\n')
            laneWE = 0
            laneEW = 0
            laneSN = 0
            laneNS = 0
        
        """
        #getting a wait time string
        if timeCount%60 == 0:
            #print util.getTime(timeCount)
            #print laneWE
            #print laneEW
            #print laneSN
            #print laneNS
            
            #outFile.write(util.stringWaitTimes(timeCount, laneWE, laneEW, laneSN, laneNS))
            
        """

        """
        if traci.trafficlights.getPhase("0") == 2:
            # we are not already switching
            #if traci.inductionloop.getLastStepVehicleNumber("0") > 0:
            if learningAgents.switchPhaseReflex(state, 0):
                # there is a vehicle from the north, switch
                traci.trafficlights.setPhase("0", 3)
            else:
                # otherwise try to keep green for EW
                traci.trafficlights.setPhase("0", 2)
        """

        step += 1
    outFile.close()
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    sumoProcess = subprocess.Popen([sumoBinary, "-c", "data/cross.sumocfg", "--tripinfo-output",
                                    "tripinfo.xml", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
    run()
    sumoProcess.wait()
