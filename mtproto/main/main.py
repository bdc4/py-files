
#Main
import tools.dicemachine as dicemachine
import tools.eventhandler as eventhandler
from easygui.easygui import *
import sys
import os


class Table:
    def __init__(self, name, minVal, maxVal):
        self.name = name
        self.minVal = minVal
        self.maxVal = maxVal
    def SetTable(self, minIn, maxIn):
        self.minVal = minIn
        self.maxVal = maxIn

class Sector:
    name = None
    eventTables = []
    dataFile = ""

    def setDataFile(self, dataFile: str):
        #fname = dataFile
        #this_file = os.path.abspath(__file__)
        #this_dir = os.path.dirname(this_file)
        #wanted_file = os.path.join(this_dir, "data/"+fname)
        self.dataFile = dataFile

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
            event = eventhandler.newDay(currentSector)
            self.phase = "END"
            return msgbox(event.title+"\n-----\n\n"+event.description)

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
            where = buttonbox("Where should "+self.name+" be moved?\n","Room Reassignment",MECS_LABELS)
            for room in ROOMS:
                if where == room.name:
                    oldRoom = self.room.name
                    self.room = room
                    msgbox(self.name+" has been moved from "+oldRoom+" to "+self.room.name)
                    return
            print("Room not found. Try again...")

def ShipStatus():
    choice = ""
    while choice != "Done":
        
        choice = buttonbox("What do you want to check on?","Ship Status",["Ship","Crew","Inventory","Done"])
        
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
            choice = buttonbox(textStr,"Ship Status",["Back","Done"])
        
        elif choice == "Crew":
            textStr = ""
            #textStr += ("\n-----\nCrew Status\n-----\n")
            for crew in CrewMembers:
                textStr += ("\n"+crew.name+"\n-- Room: "+crew.room.name+"\n-- Health: "+crew.GetHealth()+"\n")
            choice = buttonbox(textStr,"Crew Status",["Back","Done"])
        
        elif choice =="Inventory":
            textStr = ""
            #textStr += ("\n-----\nComponents\n-----\n")
            for comp in PECS:
                #msgbox(comp)
                textStr += (str(GC.comps[comp])+" "+comp+" Components\n")
            textStr += str(GC.meds)+" Medical Supplies"
            choice = buttonbox(textStr,"Crew Status",["Back","Done"])
                
def MoveCrew():
    while True:
        crewNames = []
        for crew in CrewMembers:
            crewNames.append(crew.name)
        who = buttonbox("Who would you like to move?","Pick Crew",crewNames)
        
        for crew in CrewMembers:
            if who == crew.name:
                crew.ChangeRoom()
                return
        
        print("Not a valid selection! Try again...")

def GetRandomCrew():
    return CrewMembers[dicemachine.RollD(4)-1]

def GetRandomPECs():
    roll = dicemachine.RollD(3)
    return PECS[roll-1]

def SetCrewNames():
    msg = "What are your crew members' names?"
    title = "Crew Names"
    fieldNames = ["Medbay Specialist","Engines Specialist","Comms Specialist","Systems Specialist"]
    fieldValues = []  # we start with blanks for the values
    fieldValues = multenterbox(msg,title, fieldNames)

    # make sure that none of the fields was left blank
    while True:
        if fieldValues is None: break
        errmsg = ""
        for i in range(len(fieldNames)):
            if fieldValues[i].strip() == "":
                errmsg += ('"%s" is a required field.\n\n' % fieldNames[i])
        if errmsg == "":
            break # no problems found
        fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)
    return fieldValues

#####Globals

#define global arrays
MECS_LABELS = ["Medbay","Engines","Comms","Systems"]
EVENT_TYPES = ["NOTHING","EVENTS","MEETINGS","OTHER"]
PECS = ["Physical","Electrical","Computerized"]

#init Sectors
Sector1 = Sector()
Sector1.name = "Alpha Sector"
Sector1.eventTables = [Table("NOTHING",1,20),Table("EVENTS",21,45),Table("MEETINGS",46,70),Table("OTHER",71,100)]
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
    qs = ynbox("Quick Start?")

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

def main():

    action = ""
    GC.phase = "START"
    
    while action != "exit":

        #Return option list depending on phase
        options = GC.GetOptions()

        #Get the user's input
        action = buttonbox("What would you like to do?","Day "+GC.phase+": "+str(GC.day),options)

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
            msgbox(GetRandomCrew().name)
        elif action == OPTIONS["RP"]:
            msgbox(GetRandomPECs())
        elif action == OPTIONS["X"]:
            if ynbox("Are you sure you want to quit?","Quit Program?"):
                sys.exit()

main()
