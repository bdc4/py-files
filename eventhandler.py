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
    
    def __init__(self, TABLE_LABELS, TABLE_RANGES, EVENTS) -> dict:

        masterTable = []

        for i in range(len(TABLE_LABELS)):

            #init table-specific vars from lists
            label = TABLE_LABELS[i]
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
                masterTable.append(tab)
                masterTable[i].events = copy.copy(tab.events)

        self.tables = copy.copy(masterTable)

def getTable(tLabel, masterTable):
    return masterTable[tLabel]

def getRandomEvent(masterTable, tLabel):
    mRoll= dicemachine.RollD(20)
    for table in masterTable.tables:
        if table.rmin < mRoll and table.rmax > mRoll:
            eRoll=dicemachine.RollD(6)
            return table.event[eRoll]
    
def debugCreateDummyMasterTable():
    TABLE_LABELS = ["Nothing","Events","Meetings","Other"]
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

    return MasterTable(TABLE_LABELS, TABLE_RANGES, EVENTS)

def debug():

    masterTable = debugCreateDummyMasterTable()

    input("Output log?")
    for label in TABLE_LABELS:
        t = masterTable[label]
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
        
#debug()

















