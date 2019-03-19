# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 13:24:35 2019
@author: Alexander
Summary: Class used to measure the entropy coefficient as there is a change in
         temperature and consequentially the OCV. Each test must take 21 hours
Note to self: Remember to add '/test' before you describe what test type it is
Note to self: Add escape characters to file paths \\ not \
Note to self: Add shell=True and then pass a string
Note to self: executables that run through the shell will halt the program. Must use popen, call will block your program
Note to self: ser.readline also includes the new line char and carraige return, get rid of '/r/n' by using [:-2]
Note to self: When trying to write to a file using the print function you must specify that print("text",file=FILEOBJJ) otherwise it won't write
"""
import subprocess # Use so that you can call shell commands
import time
import serial
import os


from TemperatureClass import TemperatureClass

# Gives the battery type as a string
def BatteryType():
    capacity = 3.0
    ChemType = "Li-ion"
    return "/battery "+str(capacity)+",1,3.7,1,"+ChemType

class CBA_ConstantDischargeRate:
    def __init__(self,CBAExecutableFileLocation,CurrentDirectory,DischargeAmps):
        TestName = "/test discharge "+str(DischargeAmps)+" /cutoff 2.8 /samplerate 1000" # the cut off is always 2.8V
        GraphOptions = "/title \"Entropy Calculation At Power "+str(DischargeAmps)+" [W]\""
        FileLocation = "/open \""+CurrentDirectory+"\\EntropyCoefficientTest_"+str(DischargeAmps)+"_W.bt2\""
        CommandString = CBAExecutableFileLocation + " " + TestName + " " + BatteryType() + " " + GraphOptions + " " + FileLocation
        print(CommandString) # test
        subprocess.Popen(CommandString,shell=True)

class CBA_ConstantPowerDischargeRate:
    def __init__(self,CBAExecutableFileLocation,CurrentDirectory,PowerWatts):
        TestName = "/test power "+str(PowerWatts)+" /cutoff 2.8 /samplerate 1000" # the cut off is always 2.8V
        GraphOptions = "/title \"Entropy Calculation At Power "+str(PowerWatts)+" [W]\""
        FileLocation = "/open \""+CurrentDirectory+"\\EntropyCoefficientTest_"+str(PowerWatts)+"_W.bt2\""
        CommandString = CBAExecutableFileLocation + " " + TestName + " " + BatteryType() + " " + GraphOptions + " " + FileLocation
        print(CommandString) # test
        subprocess.Popen(CommandString,shell=True)

class CBA_Charge:
    def __init__(self,CBAExecutableFileLocation,CurrentDirectory,Amps,GraphExt):
        self.CutOff = 0.2
        Cycles = 1
        HighVoltage = 4.75
        TestName = "/test chargedischarge \"Charge\","+str(Cycles)+","+str(Amps)+","+str(HighVoltage)+" /chargeampmin 0.2 /chargerecovery 3 /dischargerecovery 3 /cutoff 2.8 /samplerate 1000 /graphcurrent"
        GraphOptions = "/title \"Charge At "+str(GraphExt)+" [W]\""
        FileLocation = "/open \""+CurrentDirectory+"\\ChargeFrom_"+str(GraphExt)+"_W.bt2\""
        CommandString = CBAExecutableFileLocation + " " + TestName + " " + BatteryType() + " " + GraphOptions + " " + FileLocation
        print(CommandString) # test
        subprocess.Popen(CommandString,shell=True)
        
class CBA_FirstCharge:
    def __init__(self,CBAExecutableFileLocation,CurrentDirectory,Amps):
        self.CutOff = 0.2
        Cycles = 1
        HighVoltage = 4.75
        TestName = "/test chargedischarge \"Charge\","+str(Cycles)+","+str(Amps)+","+str(HighVoltage)+" /chargeampmin 0.2 /chargerecovery 3 /dischargerecovery 3 /cutoff 2.8 /samplerate 1000 /graphcurrent"
        GraphOptions = "/title \"First Charge\""
        FileLocation = "/open \""+CurrentDirectory+"\\FirstCharge.bt2\""
        CommandString = CBAExecutableFileLocation + " " + TestName + " " + BatteryType() + " " + GraphOptions + " " + FileLocation
        print("command = "+CommandString)
        subprocess.Popen(CommandString,shell=True)
        
class DischargeTestClass:
    def __init__(self,CBAExecutableFileLocation,CurrentDirectory,MaxTemperature):
        self.CBAPID = "" # No CBA instance should be running
        self.MaxT = MaxTemperature # Maximum temperature before stopping the test
        self.PowerDischarge = [14,16,18] # Watts
        self.CurrentDischarge = [4.5,6] # Amps
        
        
        if self.DoesCBAExist() == True: # Checks to see if there are any instances of the CBA program running, if so it will kill them
            print("ERROR: THere are multiple instances of CBA when starting")
            self.KillExcessCBA()
            
        ser = serial.Serial() # A serial communications instance Called ser
        ser.baudrate = 9600 
        ser.port = 'COM3' # The Communications court will have to be changed depending upon the device used.
        ser.open()
        
        try: # Attmps to read and write to the serial port
            print("Opened the serial port successfully, delete me later")
            TempData = TemperatureClass() 
            
            TempString = ser.readline().decode("utf-8")[:-2] # remove new line characters at end '/r/n'
    
            if TempString == "Starting": # Check it has started properly
                TempString = ser.readline().decode("utf-8")[:-2] # remove new line characters at end '/r/n'
                
                TempData.AddData(TempString)
            else:
                print("ERROR, incorrect starting serial value")
                
            # First Charge
            CBA_FirstCharge(CBAExecutableFileLocation,CurrentDirectory,1.675)
            self.SetCBAPID()
            TempData.InitialTime = time.time() # Reset the time
    
            while self.DoesCBAExist() == True and TempData.Thermo_Ave[-1] < self.MaxT:
                TempString = ser.readline().decode("utf-8")[:-2] # remove new line characters at end '/r/n'
                TempData.AddData(TempString)
                
            print("Finished first charge...")
            
            DischargeRates = [3,4.5,6] # Watts
            for Amps in DischargeRates:
                
                CBA_ConstantDischargeRate(CBAExecutableFileLocation,CurrentDirectory,Amps)
                self.SetCBAPID()
                TempData.InitialTime = time.time() # Reset the time
                
                FileName = str( time.strftime("%b_%d_%Y-%H_%M_%S", time.localtime()) )
                FileName = FileName + "_Current_"+str(Amps)+"_A.csv"
                FileObj = open(CurrentDirectory+os.sep+FileName,'w')
                print("Successfully created a new file with the path "+CurrentDirectory+os.sep+FileName)
                
                print("TIMESTAMP,STATE,AVERAGE TEMPERATURE,AVERAGE COLD JUNCTION,CJ1,Temp1,CJ2,Temp2\n",file=FileObj)
                FileObj.flush()
    
                while self.DoesCBAExist() == True and TempData.Thermo_Ave[-1] < self.MaxT:
                    TempString = ser.readline().decode("utf-8")[:-2] # remove new line characters at end '/r/n'
                    TempData.AddData(TempString)
                    TempData.WriteLine(FileObj)
                    
                # Allow a cool down of 5 hours
                FileObj.close()
                
                TempData.status = "Cool Down"
                t_end = time.time() + 60*60*5 # Allow MAX 5 hours cool down
                t_end_min_wait = time.time() + 60*60*2 # Allow 2 hours for chemical equilibrium to be reached in the battery
                # Keep waiting for the 
                while time.time() < t_end and ( (TempData.Thermo_Ave[-1] - TempData.CJ_Ave[-1]) > 2 or time.time() < t_end_min_wait ): 
                    TempString = ser.readline().decode("utf-8")[:-2] # remove new line characters at end '/r/n'
                    TempData.AddData(TempString)
                           
                FileName = "Charging_From_Current_"+str(Amps)+".csv"
                FileObj = open(CurrentDirectory+os.sep+FileName,'w')
                print("TIMESTAMP,STATE,AVERAGE TEMPERATURE,AVERAGE COLD JUNCTION,CJ1,Temp1,CJ2,Temp2\n",file=FileObj)
                
                CBA_Charge(CBAExecutableFileLocation,CurrentDirectory,1.675,Amps)
                self.SetCBAPID()
                TempData.InitialTime = time.time() # Reset the time
    
                while self.DoesCBAExist() == True:
                    TempString = ser.readline().decode("utf-8")[:-2] # remove new line characters at end '/r/n'
                    TempData.AddData(TempString)
                    TempData.WriteLine(FileObj)
                    
                # Allow a cool down of 1 hour
                FileObj.close()
                
                TempData.status = "Cool Down"
    
                # Keep waiting for the temperature to be at least 2 degrees close to ambient
                while time.time() < t_end and ( (TempData.Thermo_Ave[-1] - TempData.CJ_Ave[-1]) > 2 or time.time() < t_end_min_wait ): 
                    TempString = ser.readline().decode("utf-8")[:-2] # remove new line characters at end '/r/n'
                    TempData.AddData(TempString)
        except:            
            print("Some error")
            ser.close() # close serial
        ser.close() # close serial
        print("finished...")
    # Checks to see if there is a CBA program running. Returns true if there is one or more instances running
    
    def DoesCBAExist(self):
        ReturnVariable = False # Assume worst case scenario
        command = "tasklist"
        TempValue = subprocess.run(command, stdout=subprocess.PIPE,shell=True)
        StringValue = TempValue.stdout.decode("utf-8")
        if "WMRCBA.exe" in StringValue:  # It has found it
            if self.CBAPID in StringValue:
                ReturnVariable = True
            if StringValue.count("WMRCBA.exe") > 1:
                print("ERROR: multiple instances of CBA programs")
    
        return ReturnVariable
    
    # Set the CBA PID, if there are two instances go for the last one and start an error
    def SetCBAPID(self):
        CBAIndex =  -1
        command = "tasklist"
        TempValue = subprocess.run(command, stdout=subprocess.PIPE,shell=True)
        StringValue = TempValue.stdout.decode("utf-8")
        for Line in StringValue.splitlines():
            if "WMRCBA.exe" in Line:  # It has found it
                CBAIndex += 1 # increment by one             
                LineParts = Line.split(" ")
                while "" in LineParts:
                    LineParts.remove("")
                PID = LineParts[1]                

                if CBAIndex == 0:
                    self.CBAPID = PID
                else:
                    print("ERROR: There are two instances of the CBA program")
                    subprocess.run("Taskkill /PID "+PID)
                    print("Killed program with PID = "+PID)

    def KillExcessCBA(self): 
        command = "tasklist"
        TempValue = subprocess.run(command, stdout=subprocess.PIPE,shell=True)
        StringValue = TempValue.stdout.decode("utf-8")
        for Line in StringValue.splitlines():
            if "WMRCBA.exe" in Line:  # It has found it   
                LineParts = Line.split(" ")
                while "" in LineParts:
                    LineParts.remove("")
                PID = LineParts[1]                

                if PID != self.CBAPID:
                    print("ERROR: There are two instances of the CBA program")
                    subprocess.run("Taskkill /PID "+PID+" /F")
                    print("Killed program with PID = "+PID)
                    
