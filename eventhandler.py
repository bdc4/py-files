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

def CreateMasterTable(TABLE_LABELS: list(), TABLE_RANGES: list(), EVENTS: dict()) -> dict:

    masterTable = {}

    for i in range(len(TABLE_LABELS)):
        #input("Run on the "+TABLE_LABELS[i]+" table?")
        #print("\n-----\n")

        #init table
        label = TABLE_LABELS[i]
        rmin = TABLE_RANGES[i][0]
        rmax = TABLE_RANGES[i][1]

        #add events in table
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
            masterTable[label] = tab
            inEve = copy.copy(tab.events)
            masterTable[label].events = inEve

    return masterTable

        
def debug():
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

    masterTable = CreateMasterTable(TABLE_LABELS, TABLE_RANGES, EVENTS)

    input("Output log?")
    for label in TABLE_LABELS:
        t = masterTable[label]
        print("Table Name: "+t.name)
        print("length: "+str(len(t.events)))
        print("---\n")
        for e in t.events:
            print(" --- Title: "+e.title)
            print(" --- Description: "+e.description)
            print(" --- Table: "+e.table.name)
            print("")
        print("---")
        
debug()

















