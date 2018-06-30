
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

def getRandomPEC():
    pecNames = ["P","E","C"]
    result = RollD(3)-1
    result = pecNames[result]
    return result

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
        if crew.state == "ACTIVE":
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

def FP(gc, event):
    crewList = []
    for crew in gc.crew:
        if crew.hp != 10:
            crewList.append(crew.name)

    if len(crewList) == 0:
        gui.msgbox("Your crew found a flavor packet, but nobody seems to want it. So they decide to give it to you!\n\nHow thoughtful :)")
    else:
        who = None
        while who == None:
            who = gui.buttonbox(event.description,event.title,crewList)
            who = gc.GetCrewByName(who)
            who.hp += 1
            gui.msgbox("You decide to give "+who.name+" the flavor packet. They look slightly better than before this divine gift entered their life.")

def AS(gc, event):
    if gc.annoySound:
        gui.msgbox("The annoying sound has finally stopped.\n\nYour crew breathes a sigh of relief and can now more effeciently focus on their work.")
        gc.annoySound = False
    else:
        gui.msgbox("The ship starts making an annoying sound, but nobody can seem to figure out where it's coming from.\n\nThe annoyance puts everyone just slightly more on edge.")
        gc.annoySound = True
        
def SF(gc,event):
    aux = None
    while aux == None:
        aux = gui.buttonbox(event.description,event.title,event.actions)
        if aux == None:
            continue
        for i in range(0, len(event.sysKeys)):
            if aux == event.actions[i]:
                sys = event.sysKeys[i]
                break
            elif aux == event.actions[3]:
                sys = None

        sChecks = [gc.mecs["M"].SystemCheck(),gc.mecs["E"].SystemCheck(),gc.mecs["S"].SystemCheck()]
        if sys == None:
            for check in sChecks:
                check += 2
        elif sys == "M":
            sChecks[0] += 4
        elif sys == "E":
            sChecks[1] += 4
        elif sys == "C":
            sChecks[2] += 4

        for check in sChecks:
            if check >= 10:
                gui.msgbox("We were able to successfully avoid any harmful radiation.")
                return

        for crew in gc.crew:
            crew.hp -= RollD(2)

        gui.msgbox("We were unable to avoid the radiation, damaging everyone's health on board.")
                
        

def SE(gc, event):
    if gui.ynbox(event.description):
        p1 = ""
        p2 = p1

        while p1 == p2:
            p1 = getRandomPEC()
            p2 = getRandomPEC()

        deal = None
        while deal == None:
            deal = gui.buttonbox("The merchant offers two deals:\n\nDeal 1: We can give 1 "+p1+" Component and get 1 "+p2+" in exchange.\nDeal 2: We can give 2 "+p1+" Component and get 3 "+p2+" Components in exchange.","Offer",
                                 ["Check Supplies","Deal 1","Deal 2","No Deal!"])
            if deal == "Check Supplies":
                gc.ShipStatus()
                deal = None
                continue
            elif deal == "Deal 1":
                if gc.inv[p1] >= 1:
                    gc.inv[p1] -= 1
                    gc.inv[p2] += 1
                    gui.msgbox("The merchant smiles, \"Pleasure doing business with you, traveler. Good luck on the trail!\"")
                else:
                    gui.msgbox("We don't have enough resources for this deal!")
                    deal = None
            elif deal == "Deal 2":
                if gc.inv[p1] >= 2:
                    gc.inv[p1] -= 2
                    gc.inv[p2] += 3
                    gui.msgbox("The merchant smiles, \"Pleasure doing business with you, traveler. Good luck on the trail!\"")
                else:
                    gui.msgbox("We don't have enough resources for this deal!")
                    deal = None
            elif deal == "No Deal!":
                gui.msgbox("The merchant shakes his head, \"What a shame... Perhaps you'll have changed your mind the next time we meet!\"")
            

def MYS(gc,event):
    msg = event.description
    if gui.ynbox(msg):
        check = RollD(6)
        if check == 1:
            sys = systemDamage(gc)
            return gui.msgbox("It's a trap! An unidentified assailant struck our ship, then fled. Damaging the "+sys.name+" Area.\n\nSo rude.")
        else:
            posEve = ["Derilict Probe","Abandoned spacecraft","Asteroid Field"]
            posEve = posEve[RollD(3)-1]
            event = gc.sector.eventTables[1].getEvent(posEve)
            gui.msgbox("Investigating the mysterious signal revealed a previously unnoticed "+event.title)
            return RCO(gc,event)

def MS(gc,event):
    msg = event.description
    room = gc.mecs[event.sysKeys[0]]

    sCheck = room.SystemCheck()
    
    if sCheck >= 6:
        msg += "\n\nDue to our excellent "+room.name+" Area, we were able to fix the problem before any serious damage could be done."
    else:
        for crew in gc.crew:
            if crew.room == room:
                crew.hp -= RollD(2)
        msg += "\n\nAs a result, everyone in the "+room.name+" Area has taken some damage."

    print("sCheck: "+str(sCheck))
    return gui.msgbox(msg)

    
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
