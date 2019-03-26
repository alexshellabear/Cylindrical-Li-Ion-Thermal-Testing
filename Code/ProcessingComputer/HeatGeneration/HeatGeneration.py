# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 09:54:36 2019
@author: Alexander

Summary: Creates a csv file and sorts the temperature logs with the cba
1. Get current file path, user entered
2. Create sub file "_ProcessedData"
3. find .bt2 files
    Ignore the bt2 files that are called firstcharge
    There should only be one file, (excluding the one called firstcharge)
    It does not matter what it's called
4. open both files 
    5. .csv, skip the first 2 lines, time (minus original time), cj ave and thermo ave
    6. .bt2 use html parser to find S tags and get attributes
    7.create a new csv file keeping track of how many seconds difference
8. other process
"""


from html.parser import HTMLParser # use parser
import os # File reading and directory creating
from LinearReg import LinearRegClass
#from GetFileNamesClass import GetFileNamesClass # Used to get file names

# Used to get all relevant files
class GetFileNamesClass:
    def __init__(self,WorkingDirectory):
        self.Bt2Files = []
        self.CsvFiles = []
        
        self.Error = True # Assume there are errors
        self.Bt2 = ''
        self.Csv = ''
        
        for RootFolder, Folders, Files in os.walk(WorkingDirectory):
            for File in Files:
                if File.lower().endswith('.bt2'):
                    if File != "firstcharge.bt2":
                        self.Bt2Files.append(File)
                elif File.lower().endswith('.csv'):
                    self.CsvFiles.append(File)
                        
            break # only want the top level files
        if len(self.Bt2Files) == 1:
            if len(self.CsvFiles) == 1:
                self.Error = False # Everything is okay
                self.Bt2 = self.Bt2Files[0]
                self.Csv = self.CsvFiles[0]
            else:
                print('ERROR: GetFileNamesClass, there is not exactly one csv file in |'+WorkingDirectory+'|')
        else:
            print('ERROR: GetFileNamesClass, there is not exactly one bt2 file in |'+WorkingDirectory+'|')
            
# Uses HTMLParser to read the bt2 file
class Bt2ParserClass(HTMLParser):
    Bt2Time = []
    Voltage = []
    Current = []
    
    def handle_starttag(self,Tag,Attribute):
        if Tag == 's':
            self.Bt2Time.append(Attribute[0][1])
            self.Voltage.append(Attribute[1][1])
            self.Current.append(Attribute[2][1])
            
# Takes in the full path name as a string and reads the file contents
def ReadBt2File(FullPathFileName):
    ReturnParserObject = None # Initially set the parser object to nothing
    if type(FullPathFileName) == str:
        try:
            Bt2FileObj = open(FullPathFileName, 'r')
        except OSError:
            print('ERROR: ReadBt2File, could not open |'+FullPathFileName+'| is not a string')
        else:
            Bt2Data = Bt2FileObj.read() # Read the file into a string
            
            Bt2FileObj.close() # Close the file as soon as possible
            
            ReturnParserObject = Bt2ParserClass() # Create an instance of the Bt2ParserClass which is a child of HTMLParser
            ReturnParserObject.feed(Bt2Data) # Read values from the bt2 file and arrange into time, voltage, and current
    else:
        print('ERROR: ReadBt2File, FullPathFileName is not a string')
    return ReturnParserObject

# Used to store the most important things from
class CsvTimeAndTempDataClass:
    CsvTime = []
    Thermo_Ave = []
    CJ_Ave = []
    def __init__(self,CsvLinesData):

        if len(CsvLinesData) >= 1:
            InitialTime = float(CsvLinesData[2].split(',')[0]) # Need to accommodate for difference in time. Subtract the first time from each other
            for Line in CsvLinesData[2:]: # Remove the first two lines
                Cells = Line.split(',') 
                self.CsvTime.append(str(float(Cells[0])-InitialTime)) # First column is the time
                self.Thermo_Ave.append(Cells[2])
                self.CJ_Ave.append(Cells[3])
        else:
            print('ERROR: CsvTimeAndTempDataClass, CsvLinesData does not have at least one datapoint')
            
# Takes in the csv full path file name 
def ReadCsvFile(FullPathFileName):
    ReturnCsvLines = [] # Initially set the parser object to nothing
    if type(FullPathFileName) == str:
        try:
            CsvFileObj = open(FullPathFileName, 'r')
        except OSError:
            print('ERROR: ReadBt2File, could not open |'+FullPathFileName+'| is not a string')
        else:
            CsvData = CsvFileObj.read() # Read the file into a string
            CsvFileObj.close() # Close the file as soon as possible
            ReturnCsvLines = CsvData.splitlines()
    else:
        print('ERROR: ReadBt2File, FullPathFileName is not a string')
    return ReturnCsvLines


# Has the parent class of CsvTimeAndTempDataClass
class FinalFileClass(CsvTimeAndTempDataClass,Bt2ParserClass):
    def __init__(self,UA,mCp):
        self.UA = UA
        self.mCp = mCp
        self.TotalAmpHour = 0.0
        
        self.FinalTime = self.Bt2Time
        self.FinalVoltage = self.Voltage
        self.FinalCurrent = self.Current
        self.FinalThermo = []
        self.FinalCJ = []
        self.FinalDoD = []
        
        # Extras are used for calculations but not printed to the final csv
        self.ExtraDeltaT = []
        self.ExtraAccumulatedDischarge = []
        self.ExtraUADT = [] # Float
    # Finds the linear interpolation between the .bt2 time and 
    # Internal resistance two tier R = (Vlow-Vhigh)/(Ilow-Ihigh)
    def FindInterpolatedCsvValues(self):
        # Loop through 
        StartRow = 0
        for i in range(0,len(self.Bt2Time)-1,1):        
            if i % 500 == 0:
                print("Percentage Complete["+str(i)+"] "+str(round(i/len(self.Bt2Time)*100))+"%... start row is "+str(StartRow))
        
            for j in range(StartRow,len(self.CsvTime)-1,1):
                if abs(float(self.Bt2Time[i]) - float(self.CsvTime[j])) < 0.00005: # Found exact match, compensate for string to float conversion
                    self.FinalThermo.append(self.Thermo_Ave[j])
                    self.FinalCJ.append(self.CJ_Ave[j])
                    self.ExtraDeltaT.append(str(float(self.Thermo_Ave[j])-float(self.CJ_Ave[j])))
                    break # Don't waste cpu
                elif float(self.CsvTime[j]) > float(self.Bt2Time[i]): # Gone above set time, use linear interpolation, [0]=0
                    X1 = float(self.CsvTime[j-1])
                    X2 = float(self.CsvTime[j])
                    X = float(self.Bt2Time[i])
                    Y1 = float(self.Thermo_Ave[j-1])
                    Y2 = float(self.Thermo_Ave[j])
                    ThermoAveTemp = Y1 + (X-X1)*(Y2-Y1)/(X2-X1)
                    self.FinalThermo.append(str(ThermoAveTemp))
                    Y1 = float(self.CJ_Ave[j-1])
                    Y2 = float(self.CJ_Ave[j])
                    CJAveTemp = Y1 + (X-X1)*(Y2-Y1)/(X2-X1)
                    self.FinalCJ.append(str(CJAveTemp))
                    self.ExtraDeltaT.append(str(float(self.Thermo_Ave[j])-float(self.CJ_Ave[j])))
                    StartRow = j-1
                    break # Don't waste cpu
    # Calculates extra values
    def CalculateValues(self):
        for i in range(0,len(self.FinalTime)-1,1):
            if i == 0:
                self.ExtraAccumulatedDischarge.append(self.Current[0])
            else:
                self.ExtraAccumulatedDischarge.append(str(float(self.Current[i])+float(self.ExtraAccumulatedDischarge[i-1])))
            self.TotalAmpHour = float(self.ExtraAccumulatedDischarge[-1])/3600
        print("Total amp hours = "+str(self.TotalAmpHour))
        for i in range(0,len(self.FinalTime)-1,1):
            self.FinalDoD.append(str(float(self.ExtraAccumulatedDischarge[i])/3600/self.TotalAmpHour))
            
            DeltaT = float(self.FinalThermo[i])-float(self.FinalCJ[i])
            self.ExtraUADT.append("$I$1*"+str(DeltaT))
            
def WriteCSVFileHeatGenVsDoD(MainSubDir,FinalClass,StepSize):
    FinalCsvFileObj = open(MainSubDir+'\\FinalHeatGen.csv','w')
    FinalClass.FindInterpolatedCsvValues()
    FinalClass.CalculateValues() # Calculate values
    
    # Print the header
    print('Time [s],Voltage [V],Current [A],Thermo Ave,CJ Ave,Depth Of Discharge [%],Heat Generated [W],'+str(mCp)+','+str(UA),file=FinalCsvFileObj)
    
    # Declare lists that would be used
    XList = range(0,40,1)
    YList = []
    
    FirstStep = True
    # Loop through
    for i in range(0,len(FinalClass.FinalTime)-1,1):
        # Check to see if it has reacdhed outside of the first step
        if (i % StepSize) == 0 and i != 0: # It is a step of 40
            if FirstStep == True:
                FirstStep = False
        # Do you need to add or print
        if FirstStep == True: # It has not gotten past the first 40 rows
            YList.append(float(FinalClass.FinalThermo[i]))
        else: # Not the first step,
            del YList[0]
            YList.append(float(FinalClass.FinalThermo[i]))
            LinRegObj = LinearRegClass(XList,YList)
            #                   mCp
            TotalHeatGenstr = '=$H$1*'+str(LinRegObj.Gradient)+'+'+FinalClass.ExtraUADT[i]
            print(FinalClass.FinalTime[i]+','+FinalClass.FinalVoltage[i]+','+\
                  FinalClass.FinalCurrent[i]+','+FinalClass.FinalThermo[i]+','+FinalClass.FinalCJ[i]+','+\
                  FinalClass.FinalDoD[i]+','+TotalHeatGenstr,file=FinalCsvFileObj)
        

    FinalCsvFileObj.close()
        
#        if (i % StepSize) == 0 or i == len(FinalClass.FinalTime)-1:
#            if i == 0:
#                TotalHeatGenstr = str(FinalClass.ExtraUADT[i])
#            else:
#                LinRegObj = LinearRegClass(XList,YList)
#                TotalHeatGenstr = '='+str(mCp)+'*'+str(LinRegObj.Gradient)+'+'+str(FinalClass.ExtraUADT[i])
#                
#            print(FinalClass.FinalTime[i]+','+FinalClass.FinalVoltage[i]+','+\
#                  FinalClass.FinalCurrent[i]+','+FinalClass.FinalThermo[i]+','+FinalClass.FinalCJ[i]+','+\
#                  FinalClass.FinalDoD[i]+','+TotalHeatGenstr,file=FinalCsvFileObj)
#            YList.clear()
#        else:
#            print(FinalClass.FinalTime[i]+','+FinalClass.FinalVoltage[i]+','+\
#                  FinalClass.FinalCurrent[i]+','+FinalClass.FinalThermo[i]+','+FinalClass.FinalCJ[i]+','+\
#                  FinalClass.FinalDoD[i],file=FinalCsvFileObj)
    
    
    
# TODO: Set these variables when editing values
# The directory that you would like to process    
Path = "C:\\Users\\Alexander\\Desktop\\ELECTRO\\Thermo_Testing\\3 Part Test\\_FIrst\\2019-2-27_18-48-9_Testing_Discharge\\6_a_discharge"
MainSubDir = Path + "\\_ProcessedData"
# Thermo Testing Variables
UA = 0.013 # The UA value of the 
mCp = 473.15*0.047
StepSize = 40 # Integer

# Internal Resistance Testing Variables
RestTime = 10 # seconds
LowOnTime = 10 #  seconds
HighOnTime = 4 # seconds
LowCurrent = 0.125 # amps
HighCurrent = 2.0 # amps

FinalClass = FinalFileClass(UA,mCp)

Files = GetFileNamesClass(Path)
if Files.Error == False:
    Bt2FullPathName = Path +'\\'+ str(Files.Bt2)
    Bt2DataObj = ReadBt2File(Bt2FullPathName)
    if Bt2DataObj is not None:
        CsvFullPathName  = Path +'\\'+ str(Files.Csv)
        CsvLines = ReadCsvFile(CsvFullPathName)
        if len(CsvLines) != 0:
            CsvTimeTempData = CsvTimeAndTempDataClass(CsvLines) # Assumed to be successful
            try:  
                os.mkdir(MainSubDir)
            except OSError:  
                print ("Creation of the directory "+MainSubDir+" failed")
            else:  
                WriteCSVFileHeatGenVsDoD(MainSubDir,FinalClass,StepSize)
                print('finished...')

















