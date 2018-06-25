
#Event Handler
import copy
import os
from tools.dicemachine import RollD
import easygui.easygui as gui
from openpyxl import load_workbook

def getRandomSystem(gc):
    sysNames = ["M","E","C","S"]
    result = RollD(4)-1
    result = sysNames[result]
    sys = gc.mecs[result]
    return sys

def getRandomSub(system):
    pecNames = ["P","E","C"]
    result = RollD(3)-1
    result = pecNames[result]
    pec = system.subsystems[result[:1]]
    return pec

def systemDamage(gc, sys = None):
    targeted = False
    if sys == None:
        sys = getRandomSystem(gc)
        print(sys)
    else:
        targeted = True
        sys = gc.mecs[sys]

    brokenPecs = []
    brokenMecs = []
    while True:
        sub = getRandomSub(sys)
        while sub in brokenPecs and len(brokenPecs) < 3:
            sub = getRandomSub(sys)
        
        if sub.damage == 0:
            dam = RollD(4)
            sub.damage = dam
            return sys
        
        if not targeted and len(brokenMecs) < 4:
            if len(brokenPecs) < 3:
                brokenPecs.append(sub)
                continue
            oldSys = sys
            brokenPecs = []
            while sys == oldSys:
                sys = getRandomSystem(gc)
            brokenMecs.append(oldSys)
        else:
            gui.msgbox("The "+sys.name+" system took damage, but it is already damaged beyond repair.")
            return False


def getResources(gc, resource):
    rolls = []
    for crew in gc.crew:
        if crew.assigned == True:
            rolls.append(RollD(6))
    print("Rolls: ",rolls)
    rich = 6 in rolls and 1 not in rolls
    print("Is Rich? "+str(rich))
    print(len(rolls))
    
    resNum = 0
    for i in range(0, len(rolls)):
        if rolls[i] >= 4:
            resNum += 1
    
    gc.inv[resource] += resNum
    return resNum

def RCO(gc,event):
    
    choice = None
    title = event.title
    msg = event.description
    actions = event.actions
    sysKeys = event.sysKeys
    resource = event.resource

    while choice == None:
        
        choice = gui.buttonbox(
            msg,
            title,
            actions
        )

        if choice == "Avoid":
            sCheck = gc.mecs["E"].SystemCheck()
            if sCheck >= 5:
                gui.msgbox("Successfully avoided the "+title+".")
            else:
                sys = systemDamage(gc)
                if sys != False:
                    gui.msgbox("We were unable to avoid the "+title+" and received damage to the "+sys.name+" area.")
            print("sysCheck result: "+str(sCheck), "\nSystem Scores (E,"+sysKeys[0]+"): ",gc.mecs["E"].getScore(), gc.mecs["S"].getScore())

        elif choice == "Search":
            sCheck = gc.mecs[sysKeys[0]].SystemCheck()
            if sCheck >= 6:
                gui.msgbox("We gathered "+str(getResources(gc, resource))+" "+resource+" components from the "+title)
            else:
                sys = systemDamage(gc)
                if sys != False:
                    gui.msgbox("While investigating the "+title+", there was an accident, damaging the "+sys.name+" area.")
            print("sysCheck result: "+str(sCheck), "\nSystem Scores (E,"+sysKeys[0]+"): ",gc.mecs["E"].getScore(), gc.mecs["S"].getScore())