from tkinter import *
#import numpy as np
#import matplotlib.pyplot as plt
#import pandas as pd
#import xlrd

# Die folgende Funktion soll ausgefuehrt werden, wenn
# der Benutzer den Button anklickt
def button_add():
    comparelabel.config(text="Ich wurde geändert!")

def button_up():
	anweisungs_label.config(text="Ich wurde geändert!")
	


def button_down():
	anweisungs_label.config(text="Ich wurde geändert!")
	
def button_remove():
	anweisungs_label.config(text="Ich wurde geändert!")
	
def button_calculate():	
	anweisungs_label.config(text="Ich wurde geändert!")
	
def input_layout():
	entry_text = eingabefeld.get()
	if (entry_text == ""):
		welcome_label.config(text="Gib zuerst einen Namen ein.")
	else:
		entry_text = "Welcome " + entry_text + "!" 
		welcome_label.config(text=entry_text)

def button_saveAs():
	anweisungs_label.config(text="Ich wurde geändert!")	

# Ein Fenster erstellen
fenster = Tk()
# Den Fenstertitle erstellen
fenster.title("ptViewer - [Preview] - Qt Designer")
fenster.geometry("920x700")

comparelabel = Label(fenster, text="Files to compare: ")
layoutlabel = Label(fenster, text="Layout Expression")

# In diesem Label wird nach dem Klick auf den Button der Benutzer
# mit seinem eingegebenen Namen begrüsst.
welcome_label = Label(fenster)

# Label und Buttons erstellen.
eingabefeld = Entry(fenster, bd=5, width=40)
eingabefeld1 = Entry(fenster, bd=5, width=40)
eingabefeldbottom = Entry(fenster, bd=5, width=40)

#Fensterelemente initialisieren
add_button = Button(fenster, text="Add", command=button_add)
up_button = Button(fenster, text="Up", command=input_layout)
down_button = Button(fenster, text="Down", command=input_layout)
remove_button = Button(fenster, text="Remove", command=input_layout)
calculate_button = Button(fenster, text="Calculate", command=input_layout)
saveAs_button = Button(fenster, text="Save as...", command=input_layout)
change_button = Button(fenster, text="ändern", command=button_add)
exit_button = Button(fenster, text="Beenden", command=fenster.quit)

anweisungs_label = Label(fenster, text="Ich bin eine Anweisung:\n\
Klicke auf 'aendern'.")

info_label = Label(fenster, text="Ich bin eine Info:\n\
Der Beenden Button schliesst das Programmaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.")

#Fensterelemente positionieren
comparelabel.place(x = 350, y = 10, width=100, height=20)
eingabefeld.place(x = 10, y = 40, width=400, height=600)
eingabefeld1.place(x = 510, y = 40, width=400, height=600)
add_button.place(x = 420, y = 40, width= 80, height=30)
up_button.place(x = 420, y = 310, width= 80, height=30)
down_button.place(x = 420, y = 350, width= 80, height=30)
remove_button.place(x = 420, y = 610, width= 80, height=30)
calculate_button.place(x = 420, y = 660, width= 80, height=30)
layoutlabel.place(x = 200, y = 640, width=100, height=20)
eingabefeldbottom.place(x = 10, y = 660, width=400, height=30)
saveAs_button.place(x = 510, y = 660, width= 400, height=30)


# In der Ereignisschleife auf Eingabe des Benutzers warten.
fenster.mainloop()
