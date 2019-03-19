# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
@author: Alexander Shellabear
Summary: This class is used to intepret the temperature of the serial communications going through the ardunio
"""

import time # Used to sleep temporarily

class TemperatureClass:
    def __init__(self):
        self.CJ_1 = []
        self.Thermo_1 = []
        self.CJ_2 = []
        self.Thermo_2 = []
        
        self.ArdunioState = []
        self.CJ_Ave = []
        self.Thermo_Ave = []
        self.TimeStamp = []
        self.InitialTime = time.time()
        self.status = "Initial Warming"
    
    def AddData(self, data):
        self.TimeStamp.append(time.time()-self.InitialTime) # Number of seconds from start
        
        SplitData = data.split(',')

        self.ArdunioState.append(SplitData[0])
        self.CJ_1.append(SplitData[1])
        self.CJ_2.append(SplitData[3])
        self.Thermo_1.append(SplitData[2])
        self.Thermo_2.append(SplitData[4])
        
        self.CJ_Ave.append( float(float(SplitData[1])+float(SplitData[3]) )/2 )
        self.Thermo_Ave.append( float(float(SplitData[2])+float(SplitData[4]) )/2 )
        
    def WriteLine(self,fileObj):
        fileObj.write(str(round(self.TimeStamp[-1],3)))
        fileObj.write(',')
        fileObj.write(str(self.status))
        fileObj.write(',')
        fileObj.write(str(self.Thermo_Ave[-1]))
        fileObj.write(',')
        fileObj.write(str(self.CJ_Ave[-1]))
        fileObj.write(',')
        fileObj.write(str(self.CJ_1[-1]))
        fileObj.write(',')
        fileObj.write(str(self.Thermo_1[-1]))
        fileObj.write(',')
        fileObj.write(str(self.CJ_2[-1]))
        fileObj.write(',')
        fileObj.write(str(self.Thermo_2[-1]))
        fileObj.write('\n')
        fileObj.flush()
















