#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 12:00:32 2020

@author: rory
"""
import opendssdirect as dss
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pvlib
from feeder_scenario import feeder_scenario

ex = feeder_scenario(filePath = r'/Users/rory/python/opendss',
                     feederNum = 2 ,
                     networkNum = 4, 
                     pvNum = 50)
num = ex.customerNums()
x= ex.customerNums()
