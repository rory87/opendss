#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 11:24:31 2020

@author: rory
"""

import opendssdirect as dss
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pvlib

class feeder_scenario:
    
    def __init__(self, filePath, networkNum, feederNum, pvNum):
        self.filePath = filePath
        self.networkNum = networkNum
        self.feederNum = feederNum
        self.pvNum = pvNum
    
    def customerNums(self):
        dss.run_command('new circuit.feeder')
        dss.run_command(('Redirect ' + self.filePath + '/lv-network-models/network_' + 
        str(self.networkNum) + '/Feeder_'+ str(self.feederNum) + '/Master2.txt'))
        dss.run_command('Edit Vsource.Source BasekV=11 pu=1.00  ISC3=3000  ISC1=2500')

        #add Monitors and meters
        dss.run_command('new monitor.tr_vi element=transformer.tr1 mode=0 terminal=2') #LV Side V and I
        dss.run_command('new monitor.tr_pq element=transformer.tr1 mode=1 terminal=1 ppolar=no') #HV Side P and Q
        dss.run_command('New EnergyMeter.SS1 Element=Transformer.TR1 action=SAVE')

        #solve
        dss.run_command('Solve')
        
        #determine number of loads and buses
        
        num = dss.Loads.Count()
        
        #get load data
        #load = getLoadData(num, self.filePath)
        
        return num
    
    # def getLoadData(num, path):
    #     loadAllClean = pd.read_csv((path +'/load_data.csv'), 
    #                                header=None).to_numpy()
    #     t = pd.date_range(start='1/3/2009', end='27/3/2009 23:30:00', freq='0.5H')
    #     load_all = pd.DataFrame(loadAllClean, index=t)
    #     ids= np.random.randint(283, size=num)
    #     load = loadAllClean[0:(day*48), ids]
        
    #     return load