
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
    func = None 
    table = None
    actions = []

    def __init__(self, title = "No Name",
                 table = None, actions = []):
        self.title = title
        self.table = table
        self.actions = actions
        self.sysKeys = []
        self.resource = None

class Table:
    name = None
    minVal = None
    maxVal = None
    events = []
    
    def __init__(self, name, minVal, maxVal):
        self.name = name
        self.minVal = minVal
        self.maxVal = maxVal

    def getEvent(self, label=None, ind=None):
    
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

        def setValFromRow(rowVal, colVal):
            try:
                val = rows[rowVal][colVal].value
            except:
                val = "Empty"
            return val

        for i in range(0, len(rows[1])):
            e = Event()
            e.title = setValFromRow(1,i)
            e.func = setValFromRow(2,i)
            e.description = setValFromRow(3,i)
            e.actions = setValFromRow(4,i)
            e.sysKeys = setValFromRow(5,i)
            e.resource = setValFromRow(6,i)
            events.append(e)

            if e.actions != None: e.actions = e.actions.split(",")
            if e.sysKeys != None: e.sysKeys.split(",")

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

    def getTable(self, label=None, ind=None):
        eventTables = self.eventTables
        #select random table when no args provided
        if ind == None and label == None:

            #get the largest range of all the tables
            maxRange = 0
            for table in eventTables:
                if table.maxVal > maxRange:
                    maxRange = table.minVal

            ind = RollD(maxRange)

        #get table by index then label
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
    annoySound = False

    def NextDay(self):
        if self.phase == "END":
            
            for key,room in self.mecs.items():
                for key,sub in room.subsystems.items():
                    sub.AttemptRepair()

            self.day += 1
            self.phase = "START"
        else:
            #event = self.sector.newDay()
            event = self.sector.newDay()
            print(event.title)
            print(event.func)
            self.phase = "END"
            if event.func != None:
                return getattr(eventhandler, event.func)(self, event)
            else:
                return gui.msgbox(event.description)
            #return gui.msgbox(event.title+"\n-----\n\n"+event.description)

    def GetOptions(self):
        #Get possible option choices
        if self.phase == "START": keys = ["D","S","RES", "X"]
        else: keys = ["E","REP","S","M","RES","X"]

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
                    stateText = "IDLE" if crew.state == None else crew.state
                    textStr += ("\n"+crew.name+"\n-- Room: "+crew.room.name+"\n-- Health: "+crew.GetHealth()+"\n-- State: "+stateText+"\n")
            
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

            # make sure that none of the fields were left blank
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
                    break
            
            if who == None:
                continue

            if crew.ChangeRoom():
                return
            
            
            
            print("Not a valid selection! Try again...")
    
    def GetRandomCrew(self):
        return self.crew[RollD(4)-1]

    def GetCrewByName(self, name):
        for crew in self.crew:
            if crew.name == name:
                return crew

    def GetRandomPECs(self):
        roll = RollD(3)
        key = PECS_LABELS[roll-1]
        return key, self.inv[key[:1]]

    def RepairShip(self):
        noRepNeeded = True
        for key,room in self.mecs.items():
            for key,sub in room.subsystems.items():
                
                if sub.repair != None:
                    noRepNeeded = False
                    while True:
                        modRepair = gui.buttonbox("There is currently a repair in progress.\n\n"+
                        "Location: "+room.name+"\n"+
                                " ---- Subsystem: "+sub.name+"\n"+
                                " ---- Damage: "+sub.GetSeverity()+"\n\n"+
                                "Crew assigned to repair: "+str(sub.repair.crew.name)+"\n"+
                                "Number of "+sub.sid+" components to use: "+str(sub.repair.dice)+"\n"+
                                "Chance of repair per day: "+str(sub.repair.chance)+"%\n\n"+
                                "What would you like to do?","Repair in Progress: ("+room.name+","+sub.name+")",
                                ["Move Repairer","Add Resources","Continue"]
                                )
                        
                        if modRepair == "Move Repairer":
                            conf = gui.ynbox("WARNING! Moving the crew member performing the repairs will keep your repair progress,"+
                            " but you will lose any resources dedicated to the repair so far.\n\nAre your sure you would like to reassign "+sub.repair.crew.name+"?")
                            if conf:
                                crew = sub.repair.crew
                                sub.repair = None
                                crew.state = None
                                crew.ChangeRoom()
                                break
                        elif modRepair == "Add Resources":
                            addRes = gui.integerbox("How many "+sub.name+" Components should be allocated for repair?\n"+
                            "(Currently "+str(self.inv[sub.sid])+" "+sub.name+" Components in Inventory)", "Pick Components",0,0,self.inv[sub.sid])
                            if addRes == None or addRes == 0:
                                continue
                            else:
                                self.inv[sub.sid] -= addRes
                                sub.repair.dice += addRes
                                sub.repair.chance = sub.repair.GetChance(sub.sid)
                            break
                        else:
                            break      
                                
                if (sub.damage != 0 and sub.repair == None):
                    noRepNeeded = False
                    startRepair = False
                    while startRepair != True:
                        if gui.ynbox("The "+sub.name+" Subsystems in the "+room.name+" area appear to have taken damage.\n\n"+"Damage: "+sub.GetSeverity()+"\n\nWould you like to try and repair it?"):
                            crewNames = []
                            repStr = ""
                            for crew in self.crew:
                                crewNames.append(crew.name)
                                repStr += crew.GetRepairStats(sub.sid)
                            
                            while True:
                                repairCrew = self.GetCrewByName(gui.buttonbox("Who should be moved to repair the damage?\n\n"+repStr,
                                "Pick Crew",crewNames))
                                if repairCrew.state == "REPAIR":
                                    gui.msgbox("This crew member cannot be removed because they are already repairing another system. To move this crew member, finish or cancel the other repair.")
                                    continue
                                else:
                                    break                   
                            repairDice = gui.integerbox("How many "+sub.name+" Components should be allocated for repair?\n"+
                            "(Currently "+str(self.inv[sub.sid])+" "+sub.name+" Components in Inventory)", "Pick Components",0,0,self.inv[sub.sid])
                            
                            while repairDice == 0:
                                if not gui.ynbox("The number of resources allocated must be greater than 0 to start a repair. Would you like to cancel this repair?","Insufficent Resources Allocated!"):
                                    repairDice = gui.integerbox("How many "+sub.name+" Components should be allocated for repair?\n"+
                                    "(Currently "+str(self.inv[sub.sid])+" "+sub.name+" Components in Inventory)", "Pick Components",0,0,self.inv[sub.sid])
                                else:
                                    continue

                            if repairDice == None:
                                continue

                            startRepair = gui.ynbox("The following repair will take place:\n\n"+
                            "Location: "+room.name+"\n"+
                            " ---- Subsystem: "+sub.name+"\n"+
                            " ---- Damage: "+sub.GetSeverity()+"\n\n"+
                            "Crew assigned to repair: "+str(repairCrew.name)+"\n"+
                            "Number of "+sub.sid+" components to use: "+str(repairDice)+"\n"+
                            "Chance of repair per day: "+str(int(100*repairDice*(repairCrew.pecProf[sub.sid]/6)))+"%"+
                            "\n\nBegin Repair?","Begin Repair?")

                            if startRepair:
                                repairCrew.room = room
                                repairCrew.state = "REPAIR"
                                sub.repair = Repair(repairCrew,repairDice, sub.sid)
                                self.inv[sub.sid] -= repairDice

                        else:
                            break

        if noRepNeeded:
            return gui.msgbox("No repairs are needed. Keep up the good work!")

class MECS(object):
    #MECS vars
    name = None

    def checkAssigned(self):
        for crew in GC.crew:
            if crew.room.name == self.name and crew.state == "ACTIVE":
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

    def __init__(self, name):
        self.name = name
        self.subsystems = {"P":Subsystem("Physical",self),"E":Subsystem("Electrical",self),"C":Subsystem("Computerized",self)}

        

class Subsystem(MECS):

    #Subsystem Vars
    repair = None

    def __init__(self, name, room):
        self.name = name
        self.room = room
        self.sid = name[:1]
        self.damage = 0
    
    def GetSeverity(self):
        if self.damage == 0:
            return "No Damage"
        else:
            return "Severity Level "+str(self.damage)

    def AttemptRepair(self):
        if self.repair == None or self.damage == 0:
            return
        else:
            roll = RollD(100)
            if roll <= self.repair.chance:
                self.damage -= 1
                if self.damage == 0:
                    gui.msgbox(self.repair.crew.name+" completed repairs on the "+self.name+" Subsystems in the "+self.room.name)
                    self.repair.crew.state = None
                    self.repair.crew.ChangeRoom()
                    self.repair = None
                else:
                    gui.msgbox(self.repair.crew.name+" has reduced the damage level of the "+self.name+" Subsystems in the "+self.room.name+" to "+self.GetSeverity())
            else:
                gui.msgbox(self.repair.crew.name+" is still working on repairs to the "+self.name+" Subsystems in the "+self.room.name+" Area.")

class Repair(Subsystem):
    
    crew = None
    dice = 0

    def GetChance(self, sid):
        if self.crew != None:
            return int(100*self.dice*(self.crew.pecProf[sid]/6))
    
    def __init__(self, crew, dice, sid):
        self.crew = crew
        self.dice = dice
        self.chance = self.GetChance(sid)

    

class Crew:
    name = None
    hp = 10
    effMod = 0
    pecProf = {"P":1,"E":1,"C":1}
    state = None
    
    def __init__(self, name, room):
        self.name = name
        self.room = room
        self.special = room.name
        self.state = "ACTIVE"

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
    
    def GetRepairStats(self, subID):
        repStr = self.name+"\n--- Current Location: "+self.room.name+"\n--- "+subID+" Proficency Level: "+str(self.pecProf[subID])+"\n\n"
        return repStr

    def ChangeRoom(self):
        while True:
            
            if self.state == "REPAIR":
                gui.msgbox("This crew member cannot be moved because they are currently in the middle of a repair. "+
                "If you would like to reassign them, you must first cancel the repair.")
                return False
            elif self.state == "ACTIVE":
                if not gui.ynbox(self.name+" is actively manning the "+self.room.name+" Area. Are you sure you'd like to reassign them?"):
                    return False
            
            
            where = gui.buttonbox("Where should "+self.name+" be moved?\n\nName: "+self.name+"\nCurrent Location: "+self.room.name,"Room Reassignment",MECS_LABELS)
            oldState = self.state

            for key,room in GC.mecs.items():
                if where == room.name:

                    crew = room.checkAssigned()
                    if crew != None:
                        if crew != self and crew.state == "ACTIVE":
                            if gui.ynbox("The "+room.name+" Area is actively being manned by "+crew.name+
                            ".\n\nWould you like "+self.name+" to take over for them?"):
                                crew.state = None
                                self.state = "ACTIVE"
                            else:
                                self.state = None
                    else:
                        self.state = "ACTIVE"
                        if not gui.ynbox("Nobody is currently stationing the "+room.name+" Area.\n\nWould you like "+self.name+
                        " to station it?"):
                            self.state = None

                    stateText = "ASSIGNED" if self.state == "ACTIVE" else "MOVED"        
                    
                    oldRoom = self.room.name
                    self.room = room
                    if oldRoom != self.room.name:
                        gui.msgbox(self.name+" has been "+stateText+" from "+oldRoom+" to the "+self.room.name+" Area.")
                    elif oldState != self.state:
                        gui.msgbox(self.name+" has been "+stateText+" to the "+self.room.name+" Area.")
                    else:
                        gui.msgbox("Move cancelled.")
                    return True
            print("Room not found. Try again...")

#####Globals

#define global arrays
MECS_LABELS = ["Medbay","Engines","Comms","Systems"]
PECS_LABELS = ["Physical","Electrical","Computerized"]
#test = MECS("test").Subsystem("test")
#print(test)
#All possible menu options
OPTIONS = dict(E="End Day", D="Start Day",S="Status Report",M="Move Crew Member",REP="Repair Ship", RS="Damage Random System", RC="Get Random Crew",RP="Get Random PECs",RES="Reset",X="Exit Program")

#init Sectors
Sector1 = Sector()
Sector1.name = "Alpha Sector"
Sector1.eventTables = [Table("NOTHING",1,59),Table("EVENTS",60,75),Table("MEETINGS",76,90),Table("OTHER",90,100)]
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
        elif action == OPTIONS["REP"]:
            GC.RepairShip()
        elif action == OPTIONS["RS"]:
            eventhandler.systemDamage(GC)
        elif action == OPTIONS["RP"]:
            gui.msgbox(GC.GetRandomPECs())
        elif action == OPTIONS["RES"]:
            if gui.ynbox("Restart Program?", "Restart"):
                os.execl(sys.executable, sys.executable, *sys.argv)
        elif action == OPTIONS["X"]:
            if gui.ynbox("Are you sure you want to quit?","Quit Program?"):
                sys.exit()

__main__()
