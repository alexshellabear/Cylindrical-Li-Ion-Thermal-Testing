# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 09:54:36 2019
@author: Alexander

Summary: Creates a csv file and sorts the temperature logs with the cba
1. Get current file path, user entered
2. Create sub file "_ProcessedData"
3. Find files and sort into pairs
    Discharge, .bt2 after first '_' then stopped by '_'|Charge, .csv going from right ended by "_"
4. Loop through pairs, open both 
    5. .csv, skip the first 2 lines, time (minus original time), cj ave and thermo ave
    6. .bt2 use html parser to find S tags and get attributes
    7.create a new csv file keeping track of how many seconds difference
8. other process
"""

from html.parser import HTMLParser # use parser
import os # File reading and directory creating

class Bt2AndCsvFilesClass():
    Bt2 = []
    Csv = []
    
class FilePairClass():
    def __init__(self,Bt2Name,CsvName,PowerWatts):
        self.Bt2 = Bt2Name
        self.Csv = CsvName
        self.Power = PowerWatts
    
class PairedFilesClass():
    Charge = []
    Discharge = []
    

def GetBt2AndCsvFileNames(WorkingDirectory):
    ReturnFiles = Bt2AndCsvFilesClass()
    
    for RootFolder, Folders, Files in os.walk(WorkingDirectory):
        for File in Files:
            if File.lower().endswith('.bt2'):
                if File != "firstcharge.bt2":
                    ReturnFiles.Bt2.append(File)
            elif File.lower().endswith('.csv'):
                ReturnFiles.Csv.append(File)
        break # only want the top level files
    return ReturnFiles

def FindIdentifier(Bt2FileName):
    Identifier = ""
    if Bt2FileName.lower().endswith('.bt2'):
        if "chargefrom" in Bt2FileName: # charging
            Identifier = "Charging_From_Power_" + Bt2FileName.split("_")[1]
        elif "entropycoefficienttest" in Bt2FileName:
            Identifier = "Power_" + Bt2FileName.split("_")[1]
        else:
            print("ERROR")
    else:
        print("ERROR")
    return Identifier

def IsCharge(Bt2FileName):
    RetVariable = False
    if Bt2FileName.lower().endswith('.bt2'):
        if "chargefrom" in Bt2FileName: # charging
            RetVariable = True
        elif "entropycoefficienttest" in Bt2FileName:
            RetVariable = False
        else:
            print("ERROR")
    else:
        print("ERROR")
    return RetVariable
    
def PairFiles(Files):
    OrderedPairs = PairedFilesClass()
    for Bt2File in Files.Bt2:
        PowerWatts = Bt2File.split('_')[1]
        for CsvFile in Files.Csv:
           if FindIdentifier(Bt2File) in CsvFile:
               if IsCharge(Bt2File):
                   OrderedPairs.Charge.append(FilePairClass(Bt2File,CsvFile,PowerWatts))
               else:
                   if not ("Charging_From" in CsvFile):
                       OrderedPairs.Discharge.append(FilePairClass(Bt2File,CsvFile,PowerWatts))
    return OrderedPairs

class Bt2FileParserClass(HTMLParser):
    Time = []
    Voltage = []
    Current = []
    
    def handle_starttag(self,Tag,Attribute):
        if Tag == 's':
            self.Time.append(Attribute[0][1])
            self.Voltage.append(Attribute[1][1])
            self.Current.append(Attribute[2][1])
            
class TempReturn():
    def __init__(self, Thermo,CJ):
        self.Thermo = Thermo
        self.CJ = CJ
# Summary: Attempts to find an exact match of time, other wise it uses linear interpolation from the nearest two
#          data points to approximate the solution.
# SetTime = The second recorded by the CBA
# CsvLines = The list of csv line
def InterpolateCsvTemperature(SetTime,CsvLines):
    Time = float(SetTime)
    InitialTime = float(CsvLines[0].split(',')[0]) # zero out initial time
    RetThermo = ""
    RetCJ = ""
    
    if SetTime == "0":
        RetThermo = CsvLines[0].split(',')[2]
        RetCJ  = CsvLines[0].split(',')[3]
        #print('Found beginning[0] SetTime='+SetTime+',RetThermo='+str(RetThermo)+',RetCJ='+str(RetCJ))
    else:
        for i in range(1,len(CsvLines)-1,1):
            CSVTime = float(CsvLines[i].split(',')[0])-InitialTime
            #print('['+str(i)+']Time == CSVTime: '+str(Time == CSVTime)+',Time > CSVTime: '+str(Time > CSVTime))
            if abs(Time - CSVTime) < 0.0005: # Found exact match return coorresponding values, account for rounding error
                RetThermo = CsvLines[i].split(',')[2]   
                RetCJ  = CsvLines[i].split(',')[3]
                #print('Found equal['+str(i)+'] SetTime='+SetTime+',CsvTime[i]=,'+str(CSVTime)+'RetThermo='+str(RetThermo)+',RetCJ='+str(RetCJ))    
                break
            elif CSVTime > Time: # Gone above set time, use linear interpolation, [0]=0
                Step = float(CsvLines[i].split(',')[0])-float(CsvLines[i-1].split(',')[0])
                
                Low = float(CsvLines[i-1].split(',')[0])- InitialTime
                High = CSVTime
                
                # Opposite to what you think
                HighPortion = (Time - Low)/Step
                LowPortion = (High - Time)/Step
                
                RetThermo = str( float(CsvLines[i-1].split(',')[2])*LowPortion + float(CsvLines[i].split(',')[2])*HighPortion)
                RetCJ = str( float(CsvLines[i-1].split(',')[3])*LowPortion + float(CsvLines[i].split(',')[3])*HighPortion)
                #print('Found interpolation['+str(i)+'] SetTime='+SetTime+'CsvTime[i]=,'+str(CSVTime)+',Step='+str(Step)+',LowPortion='+str(LowPortion)+',HighPortion='+str(HighPortion)+',RetThermo='+str(RetThermo)+',RetCJ='+str(RetCJ))
                break
    return RetThermo, RetCJ

# Summary: 
# Note: WriteChargeFiles is a boolean, True = Charge, False = Discharge
def WriteFiles(Path,MainSubDir,OrderedPairs,WriteChargeFiles):
    if WriteChargeFiles == True:
        FinalDir = MainSubDir + "\\Charge"
        Pairs = OrderedPairs.Charge
        TitleDescription = '_Charge_From_'
    else:
        FinalDir = MainSubDir + "\\Discharge"            
        Pairs = OrderedPairs.Discharge
        TitleDescription = '_From_'
        
    # loop and open File pairs
    for i in range(0,len(Pairs),1):
        CsvLines = [] # muteable
        Bt2Data = ""
        
        Bt2FileObj = open(Path+'\\'+Pairs[i].Bt2, 'r')
        CsvFileObj = open(Path+'\\'+Pairs[i].Csv, 'r')
        print('file = '+OrderedPairs.Charge[i].Csv)
        CsvLines = CsvFileObj.readlines()[2:]
        Bt2Data = Bt2FileObj.read()
        
        Parser = Bt2FileParserClass()
        Parser.feed(Bt2Data)
        
        try:  
            CombinedFileObj = open(FinalDir+'\\'+Pairs[i].Csv[:20]+TitleDescription+Pairs[i].Power+'_W.csv','w')
        except OSError:  
            print ("Creation of the file "+str(CombinedFileObj)+" failed")
        else:  
            print ("Successfully created the file "+str(CombinedFileObj))
            print("Time [s],Voltage [V],Current [A],Thermo Ave [C],CJ Ave [C]",file=CombinedFileObj)
            
            for k in range(0,len(Parser.Time)-1,1):
                # use linear interpolation
                InterThermo, InterCJ = InterpolateCsvTemperature(Parser.Time[k],CsvLines)
                print(Parser.Time[k]+','+Parser.Voltage[k]+','+Parser.Current[k]+','+InterThermo+','+InterCJ,file=CombinedFileObj)
            CombinedFileObj.close()  
        CsvFileObj.close()
        Bt2FileObj.close()
        
        # Clear lists, so they do not add
        CsvLines.clear()
        Parser.Time.clear()
        Parser.Voltage.clear()
        Parser.Current.clear()
        
Path = "C:\\Users\\Alexander\\Desktop\\ELECTRO\\Thermo_Testing\\Entropy_Measurement_Constant_Power\\2019-2-3_15-45-39_Testing"
MainSubDir = Path + "\\_ProcessedData"
ChargeDir = MainSubDir + "\\Charge"
DischargeDir = MainSubDir + "\\Discharge"
UnorderedFiles = GetBt2AndCsvFileNames(Path)
OrderedPairs = PairFiles(UnorderedFiles)


try:  
    os.mkdir(MainSubDir)
except OSError:  
    print ("Creation of the directory "+MainSubDir+" failed")
else:  
    print ("Successfully created the directory "+MainSubDir)
    try:  
        os.mkdir(ChargeDir)
        os.mkdir(DischargeDir)
    except OSError:  
        print ("Creation of the directory "+DischargeDir+" or "+ChargeDir+" failed")
    else:  
        print ("Successfully created the directory "+DischargeDir+" and "+ChargeDir)
        WriteFiles(Path,MainSubDir,OrderedPairs,True)
        WriteFiles(Path,MainSubDir,OrderedPairs,False)











