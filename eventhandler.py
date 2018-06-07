import dicemachine
import copy

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
    
    def __init__(self, EVENTS, TABLE_RANGES) -> dict:

        for i in range(len(list(EVENTS))):

            #init table-specific vars from lists
            label = list(EVENTS)[i]
            rmin = TABLE_RANGES[i][0]
            rmax = TABLE_RANGES[i][1]

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

                tab.addEvent(Event(eve["title"][j-1],tab.name,[]))
                #outTab.append(tab)
                #outTab[i].events = copy.copy(tab.events)
            for e in tab.events:
                print(e.title)
                
            self.tables.append(tab)
            self.tables[i].events = copy.copy(tab.events)

def getTable(masterTable, ind:int = -1, label=None):
    
    #select random table when no args provided
    if ind == -1 and label == None:
        ind = dicemachine.RollD(20)
        print("D20: "+str(ind))

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
        print("D6ish: "+str(ind))

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
    
def debugCreateDummyMasterTable():
    #TABLE_LABELS = ["Nothing","Events","Meetings","Other"]
    TABLE_RANGES = [[1,9],[10,12],[13,15],[16,20]]
    EVENTS = {
        "Nothing":{
            "title": ["Nothing Happened"],
            "range": [1,6]
            },
        "Events":{
            "title": ["Event #1","Event #2", "Event #3"],
            "range": [1,6]
            },
        "Meetings":{
            "title": ["Meetings #1","Meetings #2", "Meetings #3"],
            "range": [1,6]
            },
        "Other":{
            "title": ["Other #1","Other #2", "Other #3"],
            "range": [1,6]
            }
        }
    return MasterTable(EVENTS, TABLE_RANGES)

def debug():

    masterTable = debugCreateDummyMasterTable()
    for t in masterTable.tables:
        for e in t.events:
            print("")

    while True:
        action = input("Output log?")
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
            eve = getEvent(getTable(masterTable))
            print(eve.title) 

debug()

















