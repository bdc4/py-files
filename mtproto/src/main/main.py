
#Main
from tools.dicemachine import RollD
import easygui.easygui as gui
from openpyxl import load_workbook
import sys
import os
import copy
from inspect import getsourcefile, getmodule, getsource
from os.path import abspath
import pkg_resources

class Event:
    title = "None"
    description = "None"
    table = None
    actions = []

    def __init__(self, title = "No Name",
                 table = None, actions = []):
        self.title = title
        self.table = table
        self.actions = actions

class Table:
    name = None
    minVal = None
    maxVal = None
    events = []
    
    def __init__(self, name, minVal, maxVal):
        self.name = name
        self.minVal = minVal
        self.maxVal = maxVal

    def getEvent(self, ind=None, label=None):
    
        #select random event when no args provided
        if ind == None and label == None:
            ind = RollD(len(self.events))-1
            #print("D6ish: "+str(ind))

        #get event by index
        if ind != None:
            return self.events[ind]
        elif label != None:
            for event in self.events:
                if event.title == label:
                    return event

    def getEventsFromFile(self, workbook):

        frozen = 'not'
        if getattr(sys, 'frozen', False):
                # we are running in a bundle
                frozen = 'ever so'
                bundle_dir = sys._MEIPASS
        else:
                # we are running in a normal Python environment
                bundle_dir = os.path.dirname(os.path.abspath(__file__))
        print( 'we are',frozen,'frozen')
        print( 'bundle dir is', bundle_dir )
        print( 'sys.argv[0] is', sys.argv[0] )
        print( 'sys.executable is', sys.executable )
        print( 'os.getcwd is', os.getcwd() )
        
        wb = load_workbook(filename = bundle_dir+"/"+workbook)
        table = wb[self.name]
        rows = list(table.rows)
        
        events = []

        for i in range(0, len(rows[1])):
            e = Event()
            e.title = rows[1][i].value
            e.description = rows[2][i].value
            events.append(e)
        
        self.events = copy.copy(events)


class Sector:
    name = None
    eventTables = []
    dataFile = ""

    def setDataFile(self, dataFile):
        
        self.dataFile = dataFile
        eventTables = self.eventTables
        tableData = self.dataFile
        
        for table in eventTables:
            table.getEventsFromFile(tableData)

    def getTable(self, ind=None, label=None):
        eventTables = self.eventTables
        #select random table when no args provided
        if ind == None and label == None:

            #get the largest range of all the tables
            maxRange = 0
            for table in eventTables:
                if table.maxVal > maxRange:
                    maxRange = table.minVal

            ind = RollD(maxRange)

        #get table by index
        for table in eventTables:
            if ind != None:
                if table.minVal <= ind and table.maxVal >= ind:
                    return table
            elif label != None:
                if table.name == label:
                    return table

    def newDay(self):
        return self.getTable().getEvent()

class Controller:
    day = 0
    sector = None
    comps = {"Physical":5,"Electrical":5,"Computerized":5}
    meds = 10

    def NextDay(self):
        if self.phase == "END":
            self.day += 1
            self.phase = "START"
        else:
            currentSector = self.sector
            event = currentSector.newDay()
            self.phase = "END"
            return gui.msgbox(event.title+"\n-----\n\n"+event.description)

    def GetOptions(self):
        #Get possible option choices
        if self.phase == "START": keys = ["D","S","X"]
        else: keys = ["E","S","M","X"]

        options = [OPTIONS[k] for k in keys]

        return options
    
class Subsystem:
    name = None
    damage = 0
    sid = None

    def __init__(self, name):
        self.name = name
        self.sid = name[:1]
    
    def GetSeverity(self):
        if self.damage == 0:
            return "No Damage"
        else:
            return "Severity Level "+str(self.damage)
        
class MECS:
    name = None
    subsystems = [Subsystem("Physical"),Subsystem("Electrical"),Subsystem("Computerized")]

    def __init__(self, name):
        self.name = name



class Crew:
    name = None
    hp = 10
    room = None

    def __init__(self, name, room):
        self.name = name
        self.room = room

    def GetHealth(self):
        if self.hp >= 10:
            return "Perfect"
        elif self.hp >= 8:
            return "Great"
        elif self.hp >= 6:
            return "Fair"
        elif self.hp >= 4:
            return "Poor"
        elif self.hp >= 1:
            return "Terrible"
        else:
            return "Dead"
    
    def ChangeRoom(self):
        while True:
            where = gui.buttonbox("Where should "+self.name+" be moved?\n","Room Reassignment",MECS_LABELS)
            for room in ROOMS:
                if where == room.name:
                    oldRoom = self.room.name
                    self.room = room
                    gui.msgbox(self.name+" has been moved from "+oldRoom+" to "+self.room.name)
                    return
            print("Room not found. Try again...")

def ShipStatus():
    choice = ""
    while choice != "Done":
        
        choice = gui.buttonbox("What do you want to check on?","Ship Status",["Ship","Crew","Inventory","Done"])
        
        if choice == "Ship":
            textStr = ""
            for room in ROOMS:
                textStr += ("-----\n"+room.name+"\n-----\n")
                damStr = ""
                for sub in room.subsystems:
                    if sub.damage != 0:
                        damStr += (sub.name+" Subsystems:\n"+"    Damage: "+sub.GetSeverity()+"\n")
                if damStr == "":
                    textStr += "Nothing to report...\n"
                textStr += "\n"
            choice = gui.buttonbox(textStr,"Ship Status",["Back","Done"])
        
        elif choice == "Crew":
            textStr = ""
            #textStr += ("\n-----\nCrew Status\n-----\n")
            for crew in CrewMembers:
                textStr += ("\n"+crew.name+"\n-- Room: "+crew.room.name+"\n-- Health: "+crew.GetHealth()+"\n")
            choice = gui.buttonbox(textStr,"Crew Status",["Back","Done"])
        
        elif choice =="Inventory":
            textStr = ""
            #textStr += ("\n-----\nComponents\n-----\n")
            for comp in PECS:
                #msgbox(comp)
                textStr += (str(GC.comps[comp])+" "+comp+" Components\n")
            textStr += str(GC.meds)+" Medical Supplies"
            choice = gui.buttonbox(textStr,"Crew Status",["Back","Done"])
                
def MoveCrew():
    while True:
        crewNames = []
        for crew in CrewMembers:
            crewNames.append(crew.name)
        who = gui.buttonbox("Who would you like to move?","Pick Crew",crewNames)
        
        for crew in CrewMembers:
            if who == crew.name:
                crew.ChangeRoom()
                return
        
        print("Not a valid selection! Try again...")

def GetRandomCrew():
    return CrewMembers[RollD(4)-1]

def GetRandomPECs():
    roll = RollD(3)
    return PECS[roll-1]

def SetCrewNames():
    msg = "What are your crew members' names?"
    title = "Crew Names"
    fieldNames = ["Medbay Specialist","Engines Specialist","Comms Specialist","Systems Specialist"]
    fieldValues = []  # we start with blanks for the values
    fieldValues = gui.multenterbox(msg,title, fieldNames)

    # make sure that none of the fields was left blank
    while True:
        if fieldValues is None: break
        errmsg = ""
        for i in range(len(fieldNames)):
            if fieldValues[i].strip() == "":
                errmsg += ('"%s" is a required field.\n\n' % fieldNames[i])
        if errmsg == "":
            break # no problems found
        fieldValues = gui.multenterbox(errmsg, title, fieldNames, fieldValues)
    return fieldValues

#####Globals

#define global arrays
MECS_LABELS = ["Medbay","Engines","Comms","Systems"]
EVENT_TYPES = ["NOTHING","EVENTS","MEETINGS","OTHER"]
PECS = ["Physical","Electrical","Computerized"]

#init Sectors
Sector1 = Sector()
Sector1.name = "Alpha Sector"
Sector1.eventTables = [Table("NOTHING",1,50),Table("EVENTS",51,71),Table("MEETINGS",72,92),Table("OTHER",93,100)]
Sector1.setDataFile("data/DailyEventsTable.xlsx")
#init Ship
ROOMS = [None]*4
CrewMembers = [None]*4

#init Game Controller (GC)
GC = Controller()
GC.sector = Sector1

#####End Globals

#Offer Quickstart

#init Rooms
for i in range(0, len(MECS_LABELS)):
    ROOMS[i] = MECS(MECS_LABELS[i])

#init Crew
while None in CrewMembers:
    qs = gui.ynbox("Quick Start?")

    #Name crew members manually
    if qs == False:

        #returns array of str names or None if cancelled
        cnames = SetCrewNames()

        #Don't try to create Crew objects if name population was cancelled
        if cnames == None: continue

        #Otherwise, create Crew objects from the list of provided names
        for i in range(0, len(ROOMS)):
            CrewMembers[i] = Crew(cnames[i],ROOMS[i])
            
    #If quickstart is selected, auto-name crew members
    if qs == True:
        for i in range(0, len(ROOMS)):
            CrewMembers[i] = Crew("Jenkins "+str(i+1),ROOMS[i])

#####
            
#All possible menu options
OPTIONS = dict(E="Next Day", D="Start Day",S="Status Report",M="Move Crew Member",RC="Get Random Crew",
               RP="Get Random PECs",X="Exit Program")

def __main__():

    action = ""
    GC.phase = "START"
    
    while action != "exit":

        #Return option list depending on phase
        options = GC.GetOptions()

        #Get the user's input
        action = gui.buttonbox("What would you like to do?","Day "+GC.phase+": "+str(GC.day),options)

        #Trigger quit prompt if prompt window is closed
        if action == None:
            action = OPTIONS["X"]
            
        #Take action on given player input:
        if action == OPTIONS["D"] or action == OPTIONS["E"]:
            GC.NextDay()
        elif action == OPTIONS["S"]:
            ShipStatus()
        elif action == OPTIONS["M"]:
            MoveCrew()
        elif action == OPTIONS["RC"]:
            gui.msgbox(GetRandomCrew().name)
        elif action == OPTIONS["RP"]:
            gui.msgbox(GetRandomPECs())
        elif action == OPTIONS["X"]:
            if gui.ynbox("Are you sure you want to quit?","Quit Program?"):
                sys.exit()

__main__()
