
#System
import sys, os, copy, pkg_resources
from os.path import abspath
from inspect import getsourcefile, getmodule, getsource

#Tools
import easygui.easygui as gui
import tools.eventhandler as eventhandler
from openpyxl import load_workbook
from tools.dicemachine import RollD


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
    inv = {"P":5,"E":5,"C":5,"M":10}
    mecs = {"M":None,"E":None,"C":None,"S":None}
    crew = [None]*4

    def NextDay(self):
        if self.phase == "END":
            self.day += 1
            self.phase = "START"
        else:
            currentSector = self.sector
            event = currentSector.newDay()
            self.phase = "END"
            return eventhandler.Probe(self)
            #return gui.msgbox(event.title+"\n-----\n\n"+event.description)

    def GetOptions(self):
        #Get possible option choices
        if self.phase == "START": keys = ["D","S","RC","RP", "X"]
        else: keys = ["E","S","M","X"]

        options = [OPTIONS[k] for k in keys]
        return options

    def ShipStatus(self):
        choice = gui.buttonbox("What do you want to check on?","Status Report",["Ship","Crew","Inventory","Done"])
        while choice != "Done":
            #This will be our report output
            textStr = ""

            #Get MECS status and any damaged subsystems
            if choice == "Ship":
                for room in self.mecs.items():
                    print(room)
                    room = room[1]
                    print(room.name)
                    textStr += ("-----\n"+room.name+"\n-----\n")
                    damStr = ""
                    for sub in room.subsystems.items():
                        sub = sub[1]
                        if sub.damage != 0:
                            damStr += ("\n"+sub.name+" Subsystems:\n"+"    Damage: "+sub.GetSeverity()+"\n")
                    if damStr == "":
                        textStr += "Nothing to report...\n"
                    else:
                        textStr += damStr
                    textStr += "\n"
            
            #Get crew status
            elif choice == "Crew":
                for crew in self.crew:
                    textStr += ("\n"+crew.name+"\n-- Room: "+crew.room.name+"\n-- Health: "+crew.GetHealth()+"\n")
            
            #Get inventory status
            elif choice =="Inventory":
                for name, number in self.inv.items():
                    textStr += (str(number)+" "+name+" Components\n")
            
            #Print report and check for another
            textStr += "\n\n"
            choice = gui.buttonbox(textStr+"What else do you want to check on?",choice+" Status",["Ship","Crew","Inventory","Done"])
    
    def InitGame(self):

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

        for label in MECS_LABELS:
            self.mecs[label[:1]] = MECS(label)

        #init Crew
        while None in self.crew:
            qs = gui.ynbox("Quick Start?")

            #Name crew members manually
            if qs == False:

                #returns array of str names or None if cancelled
                cnames = SetCrewNames()

                #Don't try to create Crew objects if name population was cancelled
                if cnames == None: continue

                #Otherwise, create Crew objects from the list of provided names
                for i in range(0, len(self.crew)):
                    self.crew[i] = Crew(cnames[i],self.mecs[MECS_LABELS[i][:1]])
                    
            #If quickstart is selected, auto-name crew members
            if qs == True:
                for i in range(0, len(self.crew)):
                    self.crew[i] = Crew("Jenkins "+str(i+1),self.mecs[MECS_LABELS[i][:1]])

    def MoveCrew(self):
        crewNames = []
        for crew in self.crew:
            crewNames.append(crew.name)
        
        while True:
            who = gui.buttonbox("Who would you like to move?","Pick Crew",crewNames)
            
            for crew in self.crew:
                if who == crew.name:
                    crew.ChangeRoom()
                    return
            
            print("Not a valid selection! Try again...")
    
    def GetRandomCrew(self):
        return self.crew[RollD(4)-1]

    def GetRandomPECs(self):
        roll = RollD(3)
        key = PECS_LABELS[roll-1]
        return key, self.inv[key[:1]]

class MECS:

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

    name = None

    def __init__(self, name):
        self.name = name
        self.subsystems = {"P":self.Subsystem("Physical"),"E":self.Subsystem("Electrical"),"C":self.Subsystem("Computerized")}
    
    def checkAssigned(self):
        for crew in GC.crew:
            if crew.room.name == self.name and crew.assigned == True:
                return crew
        return None

    def getScore(self):
        score = 0
        crew = self.checkAssigned()

        if crew != None and crew.special == self.name:
            score += 1
        subDamage = 0
        for sub in self.subsystems.items():
            sub = sub[1]
            if sub.damage != 0:
                subDamage += 1

        if subDamage == 0:
            score += 1
        elif subDamage == 1:
            score += 0
        elif subDamage >= 2:
            score -= 1

        return score

    def SystemCheck(self):
        total = 0
        sysScore = self.getScore()
        crew = self.checkAssigned()
        if crew != None:
            effMod = crew.effMod
        else:
            effMod = 0

        if sysScore >= 1:
            for i in range(0,sysScore):
                total += RollD(6)
            total += effMod

        if total < 0:
            total = 0
        return total

class Crew:
    name = None
    hp = 10
    effMod = 0
    
    def __init__(self, name, room):
        self.name = name
        self.room = room
        self.special = room.name
        self.assigned = True

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
            for room in GC.mecs.items():
                room = room[1]
                if where == room.name:
                    oldRoom = self.room.name
                    self.room = room
                    gui.msgbox(self.name+" has been moved from "+oldRoom+" to "+self.room.name)
                    return
            print("Room not found. Try again...")

#####Globals

#define global arrays
MECS_LABELS = ["Medbay","Engines","Comms","Systems"]
PECS_LABELS = ["Physical","Electrical","Computerized"]
test = MECS("test").Subsystem("test")
print(test)
#All possible menu options
OPTIONS = dict(E="Next Day", D="Start Day",S="Status Report",M="Move Crew Member",RC="Get Random Crew",RP="Get Random PECs",X="Exit Program")

#init Sectors
Sector1 = Sector()
Sector1.name = "Alpha Sector"
Sector1.eventTables = [Table("NOTHING",1,50),Table("EVENTS",51,71),Table("MEETINGS",72,92),Table("OTHER",93,100)]
Sector1.setDataFile("data/DailyEventsTable.xlsx")

#init Game Controller (GC)
GC = Controller()
GC.sector = Sector1
GC.phase = "START"

#####End Globals


def __main__():

    GC.InitGame()

    action = ""

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
            GC.ShipStatus()
        elif action == OPTIONS["M"]:
            GC.MoveCrew()
        elif action == OPTIONS["RC"]:
            gui.msgbox(GC.GetRandomCrew().name)
        elif action == OPTIONS["RP"]:
            gui.msgbox(GC.GetRandomPECs())
        elif action == OPTIONS["X"]:
            if gui.ynbox("Are you sure you want to quit?","Quit Program?"):
                sys.exit()

__main__()
