# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 20:00:21 2019
@author: alexs
"""

# Import files for directory creation and naming
import os # Allow the creation of directories

# Import necessary files for testing
from Main_InternalResistance import TestRunIntenalResistance # Used to determine the DC internal resistance of the battery pack
from Main_Discharge import TestRunDischarge # Used to determine the discharge curves 
from Main_OCVEstimate import TestRunOCVEstimate # DEFUNCT
from Main_SpecificHeat import TestRunSpecificHeat


# Set variables for files
CBAExecutableFileLocation = "\"C:"+os.sep+"Program Files (x86)"+os.sep+"West Mountain Radio"+os.sep+"CBA Software"+os.sep+"WMRCBA.exe\""
BaseDirectory = "C:"+os.sep+"Users"+os.sep+"alexs"+os.sep+"Desktop" # TODO CHANGE ME if you change computers!
MaxTemperature = 100 # Change to determine the maximum temperature that tests are allowed to go to before cutting power

# Begin calling test routines.
# NOTE: Each routine creates it's own file with a date stamp
for i in range(0,1,1):
    TestRunSpecificHeat(CBAExecutableFileLocation,BaseDirectory,MaxTemperature)
    break

#for i in range(0,3,1):
    #TestRunIntenalResistance(CBAExecutableFileLocation,BaseDirectory,MaxTemperature)

#for i in range(0,3,1):
   #TestRunDischarge(CBAExecutableFileLocation,BaseDirectory,MaxTemperature)

# NOTE: OLD DEFUNCT CODE   
#for i in range(0,3,1):
    #TestRunOCVEstimate(CBAExecutableFileLocation,BaseDirectory,MaxTemperature)