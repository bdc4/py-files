
#Event Handler
import copy
import os
import tools.dicemachine as dicemachine
import easygui.easygui as gui
from openpyxl import load_workbook

def Probe(systems):
    choice = gui.buttonbox("There's an incoming probe. It appears to be derilict, but it could be a trap...\n\nWhat would you like to do?","Derilict Probe",["Search","Avoid"])
    if choice == "Avoid":
        if systems[1].SystemCheck() > 5:
            gui.msgbox("Successfully avoided the probe.")
        else:
            dam = "TODO"
            gui.msgbox("We were unable to dodge the probe and received "+str(dam))
    
