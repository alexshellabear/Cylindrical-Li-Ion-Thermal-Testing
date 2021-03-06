# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 14:06:16 2019
@author: Alexander
"""
import os # Allow the creation of directories
import datetime # Used for datetime stamps
from DischargeClass import DischargeTestClass # Entropy testing

def MakeDirectory(FilePath):
    try:
            os.mkdir(FilePath)
    except OSError:
        print("ERROR: Creation of directory |"+FilePath+"| FAILED")
    else: 
        print("Success! for creating directory |"+FilePath+"|")
    
# Used to discharge the cell at different rates
class TestRunDischarge:
    def __init__(self,CBAExecutableFileLocation,BaseDirectory,MaxTemperature):
        if type(CBAExecutableFileLocation) == str:
            if type(BaseDirectory) == str:
                if type(MaxTemperature) == int:
                    now = datetime.datetime.now()
                    DateTimeStamp = str(now.year)+"-"+str(now.month)+"-"+str(now.day)+"_"+str(now.hour)+"-"+str(now.minute)+"-"+str(now.second)
                    
                    # Create the test directory
                    CurrentDirectory = BaseDirectory+os.sep+DateTimeStamp+"_Testing_Discharge"
                    MakeDirectory(CurrentDirectory)
                    
                    # Do the testing
                    DischargeTestClass(CBAExecutableFileLocation,CurrentDirectory,MaxTemperature)
                else:
                    print("ERROR[TestRunIntenalResistance], MaxTemperature is not an integer")
            else:
                print("ERROR[TestRunIntenalResistance], BaseDirectory is not a string")
        else:
            print("ERROR[TestRunIntenalResistance], CBAExecutableFileLocation is not a string")                    



















