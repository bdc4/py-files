
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


def Probe(gc):
    choice = gui.buttonbox("There's an incoming probe. It appears to be derilict, but it could be a trap...\n\nWhat would you like to do?","Derilict Probe",["Search","Avoid"])
    if choice == "Avoid":
        if gc.mecs["E"].SystemCheck() > 5:
            gui.msgbox("Successfully avoided the probe.")
        else:
            sys = systemDamage(gc)
            if sys != False:
                gui.msgbox("We were unable to dodge the probe and received damage to the "+sys.name+" system.")
    
