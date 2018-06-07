import dicemachine
import copy
from openpyxl import load_workbook

class Event:
    title = "None"
    description = "None"
    table = None
    actions = []

    def __init__(self, title: str = "No Name",
                 table = None, actions: list = []):
        self.title = title
        self.table = table
        self.actions = actions

class Table:
    name = "Empty"
    events = list()
    rmin = -1
    rmax = -1
    ind = -1
    
    def __init__(self, name: str, ind: int = -1, rmin: int = -1, rmax: int = -1):
        self.name = name
        self.ind = ind
        self.rmin = rmin
        self.rmax = rmax

    def setRange(self, rmin, rmax):
        self.rmin = rmin
        self.rmax = rmax
    
    def addEvent(self, event: Event):
        event.table = self
        self.events.append(event)

class MasterTable:
    tables = []
    
    def __init__(self, EVENTS: dict) -> dict:

        for i in range(len(list(EVENTS))):

            #init table-specific vars from lists
            label = list(EVENTS)[i]
            rmin = EVENTS[label]["range"][0]
            rmax = EVENTS[label]["range"][1]

            #CREATE TABLE
            tab = Table(label, i, rmin, rmax)
            eve = EVENTS[label]
            rmin = 1
            rmax = len(eve["title"])

            #clear out previously populated events list because
            #python doesn't dump it automatically when reassigning to it
            del tab.events[:]

            #populate events list from provided EVENTS dict
            for j in range(rmin, rmax+1):
                inEve = Event(eve["title"][j-1],tab.name,[])
                inEve.description = eve["description"][j-1]
                tab.addEvent(inEve)
                #outTab.append(tab)
                #outTab[i].events = copy.copy(tab.events)
                
            self.tables.append(tab)
            self.tables[i].events = copy.copy(tab.events)

def getTable(masterTable, ind:int = -1, label=None):
    
    #select random table when no args provided
    if ind == -1 and label == None:
        ind = dicemachine.RollD(20)
        #print("D20: "+str(ind))

    #get table by index
    if ind != -1:
        for table in masterTable.tables:
            if table.rmin <= ind and table.rmax >= ind:
                return table
    elif label != None:
        for table in masterTable.tables:
            if table.name == label:
                return table
    else:
        print("Table not found!")
    
    return False

def getEvent(table, ind:int = -1, label=None):
    
    #select random event when no args provided
    if ind == -1 and label == None:
        ind = dicemachine.RollD(len(table.events))-1
        #print("D6ish: "+str(ind))

    #get event by index
    if ind != -1:
        return table.events[ind]
    elif label != None:
        for event in table.events:
            if event.title == label:
                return event
    else:
        print("Event not found!")
    
    return False


def getEventsFromFile(workbook: str, sheetName: str, tabRange: list):

    wb = load_workbook(filename = workbook)
    table = wb[sheetName]
    rows = list(table.rows)
    tabName = rows[0][0].value
    d = {}
    d[tabName] = {}
    eveTitles = []
    eveDescripts = []
    
    for i in range(0, len(rows[1])):
        eveTitles.append(rows[1][i].value)
        eveDescripts.append(rows[2][i].value)

    d[tabName]["title"] = eveTitles
    d[tabName]["description"] = eveDescripts
    d[tabName]["range"] = tabRange
    
    return d

def newDay(tabNames, tabRanges):

    events = {}
    for i in range(0, len(tabNames)):
        events.update(getEventsFromFile("DailyEventsTable.xlsx", tabNames[i], tabRanges[i]))

    masterTable = MasterTable(events)
    return getEvent(getTable(masterTable))

    for table in masterTable.tables:
        for event in table.events:
            return event.title, event.description

    #Debugging
    if __name__ == "__main__":
        for table in masterTable.tables:
            print("R min/max :\n"+str(table.rmin))
            print(table.rmax)
            for event in table.events:
                print(event.title)
        while True:
            input("Continue?")
            prEve =getEvent(getTable(masterTable)) 
            print(prEve.title)
            print(prEve.description)


#### --- DEBUGGING --- ####
def debugCreateDummyMasterTable():
    #TABLE_LABELS = ["Nothing","Events","Meetings","Other"]
    EVENTS = {
        "Nothing":{
            "title": ["Nothing Happened"],
            "description": [""],
            "range": [1,9]
            },
        "Events":{
            "title": ["Event #1","Event #2", "Event #3"],
            "description": ["","",""],
            "range": [10,12]
            },
        "Meetings":{
            "title": ["Meetings #1","Meetings #2", "Meetings #3"],
            "description": ["","",""],
            "range": [13,15]
            },
        "Other":{
            "title": ["Other #1","Other #2", "Other #3"],
            "description": ["","",""],
            "range": [16,20]
            }
        }
    return MasterTable(EVENTS)

def debug():

    #masterTable = debugCreateDummyMasterTable()

    while True:
        tn = input("set table name:\n")
        events = getEventsFromFile("DailyEventsTable.xlsx", tn, [int(input("rmin:\n")),int(input("rmax:\n"))])
        masterTable = MasterTable(events)
        action = input("pick: l = log; r = random event\n")

        if action == "l":
            for table in masterTable.tables:
                t = table
                print("Table Name: "+t.name)
                print("Table Range: "+str(t.rmin)+" - "+str(t.rmax))
                print("# of Events: "+str(len(t.events)))
                print("---\n")
                for e in t.events:
                    print(" --- Title: "+e.title)
                    print(" --- Description: "+e.description)
                    print(" --- Table: "+e.table.name)
                    print("")
                print("---")
        elif action == "r":
            while action != "x":                      
                re = getEvent(getTable(masterTable))
                print("")
                print(re.title)
                print(re.description)
                action = input("roll again?")
#debug()

















