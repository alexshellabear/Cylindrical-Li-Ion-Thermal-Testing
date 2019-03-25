# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
Created on Fri Nov 30 08:34:45 2018
@author: Alexander Shellabear
Summary: This function is used to control the temperature of the battery.
"""

import serial # This imports serial communication which can be used
import time # Used to sleep temporarily
import os # Used for os.sep to be platform independent
import sys

class TemperatureClass:
    CJ_1 = []
    Thermo_1 = []
    CJ_2 = []
    Thermo_2 = []
    
    CJ_Ave = []
    Thermo_Ave = []
    TimeStamp = []
    status = "Initial Warming"
    setpoint = 45 # degrees celsius
    StartTime = 0
    def AddData(self, data):
        self.TimeStamp.append(time.time()-self.StartTime) # Add timestamp
        
        SplitData = data.split(',')
        self.CJ_1.append(float(SplitData[1]))
        self.CJ_2.append(float(SplitData[3]))
        self.Thermo_1.append(float(SplitData[2]))
        self.Thermo_2.append(float(SplitData[4]))
        
        self.CJ_Ave.append( (float(SplitData[1])+float(SplitData[3]))/2 )
        self.Thermo_Ave.append( (float(SplitData[2])+float(SplitData[4]))/2 )
    
    def ReachedSetPoint(self):
        if self.Thermo_Ave[-1] > self.setpoint:
            self.status = "Cool"
            return True
        else:
            if self.status == "Cool":
                self.status = "Heat"
            return False
        
    def WriteLine(self,FileObj):
        print(str(self.TimeStamp[-1]),file=FileObj,end="")
        print(",",file=FileObj,end="")
        print(str(self.status[-1]),file=FileObj,end="")
        print(",",file=FileObj,end="")
        print(str(self.Thermo_Ave[-1]),file=FileObj,end="")
        print(",",file=FileObj,end="")
        print(str(self.CJ_Ave[-1]),file=FileObj,end="")
        print(",",file=FileObj,end="")
        print(str(self.CJ_1[-1]),file=FileObj,end="")
        print(",",file=FileObj,end="")
        print(str(self.Thermo_1[-1]),file=FileObj,end="")
        print(",",file=FileObj,end="")
        print(str(self.CJ_2[-1]),file=FileObj,end="")
        print(",",file=FileObj,end="")
        print(str(self.Thermo_2[-1]),file=FileObj,end="")
        print("\n",file=FileObj,end="")
        
    def ReachedThreeDeg(self):
        if self.Thermo_Ave[-1] < self.CJ_Ave[-1] + 3:
            return True
        else:
            return False
        
# Used to find the three degree when you do not want to record data to the output file
def ReachedThreeDeg(SerialLineString):
    if type(SerialLineString) == str:
        SplitData = SerialLineString.split(',')      
        CJ_Ave = (float(SplitData[1])+float(SplitData[3]))/2 
        Thermo_Ave = (float(SplitData[2])+float(SplitData[4]))/2 
        
        if Thermo_Ave < CJ_Ave + 3:
            return True
        else:
            return False
    else:
        print("ERROR, SpecificHeatTestClass ReachedThreeDeg , SerialLineString is not a string")
            
class SpecificHeatTestClass:
    def __init__(self,CBAExecutableFileLocation,CurrentDirectory,MaxTemperature):
        TempData = TemperatureClass() # Initialize temperature data class        
        
        ser = serial.Serial() # A serial communications instance Called ser
        ser.baudrate = 9600 
        ser.port = 'COM3' # The Communications court will have to be changed depending upon the device used.
        
        # Check to see if the serial port can be opened
        try:
            ser.open()
        except:
            print("ERROR, SpecificHeatTestClass could not open serial port on "+str(ser.port))
        else:
            # Print output .csv to the designated location
            FileName = str( time.strftime("%b_%d_%Y-%H_%M_%S", time.localtime()) )
            FileName = FileName + "_Temp_Log_Set_Point_45.csv"
            FileObj = open(CurrentDirectory+os.sep+FileName,'w')
            
            # Print header to the file
            print("TIMESTAMP,STATE,AVERAGE TEMPERATURE,AVERAGE COLD JUNCTION,CJ1,Temp1,CJ2,Temp2",file=FileObj)
            FileObj.flush() # Force changes
                
            TempString = str(ser.readline())[2:][:-5] # Reads relevant information. When python reads serial communication and extra information. Describe remove extra information
            if TempString == "Starting": 
                print("Successfully started specific heat test... at "+str(time.time()))
                 
                t_end = time.time() + 60*60*10 #10hours
                TempData.equi_time = t_end
                
                while time.time() < t_end and ( TempData.equi_time + 60*60*3 ) > time.time() :
                    TempString = str(ser.readline())[2:][:-5] # Reads relevant information. When python reads serial communication and extra information. Describe remove extra information
                    TempData.AddData(TempString)
                    
                    if TempData.ReachedSetPoint():
                        # It is too hot, cool
                        if TempData.equi_time == t_end: # First time reaching it
                            TempData.equi_time = time.time()
                        ser.write(b'S') # You must indicate that you would like the data to be sent as bytes which is why there is a B out the front
                    else:
                        # It is too cold, heat
                        ser.write(b'H') # You must indicate that you would like the data to be sent as bytes which is why there is a B out the front
                TempData.StartTime = time.time()
                print("Reached end of equilibrium phase")
                ser.write(b'S') # You must indicate that you would like the data to be sent as bytes which is why there is a B out the front
                
                
                t_end = time.time() + 60*60*10  #10hours
                while time.time() < t_end and TempData.ReachedThreeDeg() == False:
                    TempString = str(ser.readline())[2:][:-5] # Reads relevant information. When python reads serial communication and extra information. Describe remove extra information
                    TempData.AddData(TempString)
                    TempData.WriteLine(FileObj)
                    FileObj.flush() # Force changes to be made to the file           
            
                FileObj.close()
                print("Ended test at "+str(time.time())+" equibrium reached at "+str(time.time()))
                
            else:
                print("ERROR SpecificHeatTestClass did not get first message as 'Starting...' from the arduino")
        ser.close()