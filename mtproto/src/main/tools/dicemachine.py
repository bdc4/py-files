
#Dice Machine: Select a die size from a range between 1-99 and roll it

import random
import sys

#functions

def RollD(sides):
    result = random.randint(1, sides)
    #print ("You rolled a "+str(result)+" on a "+str(sides)+"-sided die.")

    return result

def SetSize():
    val = input("How many sides? (1-99)\n")

    try:
        val = int(val)
    except ValueError:
        print("Not a recognized number!")
        return SetSize()
    
    while val > 99 or val < 1:
        print("Value out of range; Please pick a value in range 1-99.")
        return SetSize()
    
    val = int(val)
    return val

def SetOptionsLabels(labels, keys):
    outArray = ["","","",""]

    for i in range(len(keys)):
        outArray[i] = "--"+str(labels[i])+" ("+str(keys[i])+")\n"

    return outArray

def GetOptions(arrayIn):
    optList = ""
    keyVals = ["","",""]
    
    for i in arrayIn:
        optList += options[i]
        keyVals[i] = keys[i]

    inp = input("What would you like to do?\n"+optList)
    while (inp in keyVals) == False:
        print("Not a valid option choice; try again!\n----")
        return GetOptions(arrayIn)

    return inp

class Die:
    result = None
    size = None
    
#MAIN
def main():
    print("Welcome to bdc4's dice machine!")
    action = GetOptions([1,2])

    while action != "q":
        if action == "n":
            die.size = SetSize()
            die.result = RollD(die.size)
            action = GetOptions([0,1,2])
        elif action == "r":
            if die.size != None:
                die.result = RollD(die.size)
                action = GetOptions([0,1,2])
            else:
                print("Die size could not be determined. Please roll a new die...")
                action = GetOptions([1,2])
        else:
            print("Something went wrong and caused the program to end early... Sorry!")
            action = "q"
    print("Thanks for using bdc4's random dice result generator!")
    return sys.exit()
#end main

#init global vars
keys = ["r","n","q"]
labels = ["Re-roll same die","Roll a new die","Quit program"]
options = SetOptionsLabels(labels, keys)
die = Die()

#start

#main()
