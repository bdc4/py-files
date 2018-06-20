
#Dice Machine: Select a die size from a range between 1-99 and roll it

import random
import sys

#functions

class Die:
    result = None
    size = None

def RollD(sides):
    result = random.randint(1, sides)
    #print ("You rolled a "+str(result)+" on a "+str(sides)+"-sided die.")

    return result

def SystemCheck(sysScore, effMod):
    total = 0
    if sysScore >= 1:
        for i in range(0,sysScore):
            total += RollD(6)
        total += effMod

    if total < 0:
        total = 0
    return total

def HealthCheck():
    result = 0
    check = RollD(6)
    if check <= 2:
        result -= (RollD(2)+1)
    elif check <= 4:
        result -= RollD(2)

    return result

def DebugSC():
    sysScore = int(input("sysScore:\n"))
    effMod = int(input("effMod:\n"))
    inp = ""
    while inp != "q":
        if inp == "r":
            sysScore = int(input("sysScore:\n"))
            effMod = int(input("effMod:\n"))
        print(SystemCheck(sysScore, effMod))
        inp = input("cont? cmds: enter r q \n")

def DebugHC():
    inp = ""
    while inp != "q":
        print("You have taken "+str(HealthCheck())+" points of damage.")
        inp = input("Cont?")
