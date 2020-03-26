#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 19:51:05 2020

@author: rory
"""

# %% add packages
import os
import opendssdirect as dss
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
from interpolateLatLon import interpolateLatLon
from scipy.interpolate import griddata
from scipy.interpolate import interp1d
import pvlib
from pvPowerOut import pvPowerOut
import random

#directorys
baseDir = r'/Users/rory/python'
dssDir = r'/Users/rory/python/opendss'
netDir = r'/Users/rory/python/opendss/lv-network-models'
pvDir = r'/Users/rory/python/pvLibPython'

# function inputs
networkNum = 1
feederNum = 3
pvPer = 60


# %% import load data
os.chdir(dssDir)loa
loadAllClean = pd.read_csv('load_data.csv', header=None).to_numpy()

t = pd.date_range(start='1/3/2009', end='27/3/2009 23:30:00', freq='0.5H')
load_all = pd.DataFrame(loadAllClean, index=t)
t_target = pd.date_range(start='1/3/2016', end='27/3/2016 23:30:00', freq='H')


# %%compile circuit
os.chdir(netDir + r'/network_' + 
        str(networkNum) + r'/Feeder_'+ str(feederNum))
dss.run_command('clear')
dss.run_command('new circuit.main')
dss.run_command('Redirect Master2.txt')
dss.run_command('Edit Vsource.Source BasekV=11 pu=1.00  ISC3=1000  ISC1=500') #3000, 2500


#add Monitors and meters
dss.run_command('new monitor.tr_vi element=transformer.tr1 mode=0 terminal=2') #LV Side V and I
dss.run_command('new monitor.tr_pq element=transformer.tr1 mode=1 terminal=1 ppolar=no') #HV Side P and Q
dss.run_command('New EnergyMeter.SS1 Element=Transformer.TR1 action=SAVE')

#solve
dss.run_command('Solve')

#determine number of loads and buses
num = dss.Loads.Count()
bus=dss.Circuit.NumBuses()

# %% extract load info from text file
f = open('Loads.txt', 'r')
loadInfo = f.readlines()
f.close()

loadBus = np.zeros(len(loadInfo))
for i in range(0, len(loadInfo)):
    loadBus[i] = (float((loadInfo[i].split()[3].split('Bus1=')[1])))

# add pv generators to bus numbers and process pv data
if pvPer > 0:
    pvBus = random.choices(loadBus, k=round(num*(pvPer/100)))
    
    for i in range(0, len(pvBus)):
        dss.run_command('New Generator.PV_' + str(i) 
                        +' Bus1=' + str(float(pvBus[i]-1)) 
                        +' phases=1 kw=3 kV=0.415 pf=1 model=1')
        
    

# %% get pv data
os.chdir(pvDir)

finalData, hhFinalData, altitude = interpolateLatLon(latitude = 56.3, 
                                                     longitude = -2.3,
                                                     t_target = t_target)

p_acs = pvPowerOut(tmy_data = hhFinalData, 
                   latitude = 56.3,
                   longitude = -2.3,
                   altitude = altitude,
                   pRating = 10000)

pvData = (p_acs.to_numpy())/1000


# %% extract load data
ids= np.random.randint(283, size=num)
load = loadAllClean[0:, ids]

#reset mon
dss.Monitors.Reset()

#instantiate result arrays
d=dss.Circuit.AllBusDistances()
v1=np.zeros([len(load), bus])
v2=np.zeros([len(load), bus])
v3=np.zeros([len(load), bus])
losses = np.zeros([len(load), 2])

for halfhour in range(0, len(load)):
    iLoad = dss.Loads.First()
    ndeL = -1
    
    
    while iLoad > 0:
        ndeL = ndeL + 1
        dss.Loads.kW(load[halfhour, ndeL])
        iLoad = dss.Loads.Next()
    
    if pvPer > 0:
        iGen = dss.Generators.First()
        ndeG = -1
        while iGen > 0:
            ndeG = ndeG + 1
            dss.Generators.kW(pvData[halfhour])
            iGen = dss.Generators.Next()
        
        
    dss.run_command('Solve')
    dss.Monitors.SampleAll()
        
    v1[halfhour, 0:bus]=dss.Circuit.AllNodeVmagByPhase(1)
    v2[halfhour, 0:bus]=dss.Circuit.AllNodeVmagByPhase(2)
    v3[halfhour, 0:bus]=dss.Circuit.AllNodeVmagByPhase(3)
    
    losses[halfhour,0:] = dss.Circuit.LineLosses()
 
os.chdir(netDir + r'/network_' + 
        str(networkNum) + r'/Feeder_'+ str(feederNum))    
#Export Monitors
dss.run_command('export mon tr_pq')
dss.run_command('export mon tr_vi')

pq = pd.read_csv('main_Mon_tr_pq.csv')
vi = pd.read_csv('main_Mon_tr_vi.csv')

#plot active powers
plt.plot(t, pq[' P1 (kW)'])
plt.plot(t, pq[' P2 (kW)'])
plt.plot(t, pq[' P3 (kW)'])
plt.show()

plt.subplot(311)

phase1 = np.zeros([len(load), 2])
phase1[0:,0] = np.amax(v1[0:,1:], axis=1)
phase1[0:,1] = pq[' Q1 (kvar)'].to_numpy()

phase2 = np.zeros([len(load), 2])
phase2[0:,0] = np.amax(v2[0:,1:], axis=1)
phase2[0:,1] = pq[' Q2 (kvar)'].to_numpy()

phase3 = np.zeros([len(load), 2])
phase3[0:,0] = np.amax(v3[0:,1:], axis=1)
phase3[0:,1] = pq[' Q3 (kvar)'].to_numpy()


plt.scatter(phase1[0:,0], phase1[0:,1], c='b')
plt.scatter(phase2[0:,0], phase2[0:,1], c='r')
plt.scatter(phase3[0:,0], phase3[0:,1], c='g')




