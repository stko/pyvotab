import sys
import os
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QTabWidget, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot
import xlrd 
from xlrd import XLRDError
import numpy as np
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from pyvotab import Pyvotab, pyvoSheet
from ptViewer_ui import Ui_MainWindow
from ptWriter import PtWriter
from openpyxl.styles import Border, Side, PatternFill, Font, GradientFill, Alignment

class Main(object):



	def __init__(self,args):

		"""Initiate windows parameters 

		Setting the default user interface parameters and
		first Initialisation of global Variables.

		global Variables
		----------
		index : Integer
		Index of file, which is chosen by the user, in GUI list
		
		pyvotab_list : List of pyvoSheet elements
		Content of list will be saved in an excel file.
		
		view_list : List of pyvoSheet elements
		Content of list will be displayed in the GUI.

		first_Click : Boolean
		Ensure that an excel file is chosen before moving it.
		
		savable : Boolean
		Ensure that an excel file is calculated before saving it.
		
		Returns
		-------
		no value
		"""

		self.all_s4ps={}
		self.app = QtWidgets.QApplication(args)
		self.MainWindow = QtWidgets.QMainWindow()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self.MainWindow)
		self.ui.add_file_pushButton.clicked.connect(self.add)
		self.ui.up_file_pushButton.clicked.connect(self.up)
		self.ui.down_file_pushButton.clicked.connect(self.down)
		self.ui.remove_file_pushButton.clicked.connect(self.remove)
		self.ui.calculate_pushButton.clicked.connect(self.calculate)
		self.ui.save_file_pushButton.clicked.connect(self.saveAs)

		self.ui.label_2.setText("Please press the \"Add\"-Button and select your files to compare.")
		self.entry = QtGui.QStandardItemModel()
		self.ui.file_list_listView.setModel(self.entry)
		self.ui.file_list_listView.clicked[QtCore.QModelIndex].connect(self.on_clicked)      

		self.index = 0 
		self.pyvotab_list = []
		self.view_list = []
		self.first_Click = False  	#Bugfix fuer Up-Down-Button bevor ein Element ausgewaehlt wurde
		self.savable = False 	#SaveAs darf nur nach "savable" aufgerufen werden
		
		

	def on_clicked(self, index):
	
		"""On_clicked Listener for QListView

		Setting the index of a excel file, which is chosen
		in the QListview by a user.	

		Parameters
		----------
		index : Integer
		Index of file, which is chosen by the user, in GUI list
		
		Returns
		-------
		no value
		"""
		
		self.first_Click = True
		self.savable = False
		self.index = index
		item = self.entry.itemFromIndex(index)
		self.showMatrix(item)
		self.ui.label_2.setText("Please write a command into the input field or press the \"Calculate\"-Button.")
	
	
	
	def showMatrix(self, item):
	
		"""Show the matrix in the GUI

		Content of excel file (item) will be displayed in the GUI.

		Parameters
		----------
		item : QStandardItem
		Contains path of an excel file, which is chosen by user.
		
		Returns
		-------
		no value
		"""
		
		self.ui.excel_tabWidget.clear()
		df = pd.ExcelFile(item.text())	

		for ele in df.sheet_names:

			df1 = pd.read_excel (df, ele)
			list = df1.as_matrix()
			
			header = df1.head()
			self.tableview= QtGui.QStandardItemModel(len(list),len(header)-1) # zeile, spalte
			self.tableview.setHorizontalHeaderLabels(header)
			for i in range(len(list)):
				for j in range(len(list[i])):
					item = QtGui.QStandardItem(str(list[i][j]))
					self.tableview.setItem(i, j, item)
				
			self.add_Tab(ele)
			
		
		
	def showMatrixSheet(self, update_tupel):

		"""Show the calculated matrix in the GUI

		Content of calculated excel file (item) 
		will be displayed in the GUI.

		Parameters
		----------
		update_tupel : Tupel(String, matrix)
		Contains excel title and excel matrix.
		
		Returns
		-------
		no value
		"""	
		
		list = update_tupel[1]
		
		self.tableview= QtGui.QStandardItemModel(len(list)-1,len(list[0])-1) # zeile, spalte
		self.tableview.setHorizontalHeaderLabels(list[0])
		for i in range(1, len(list)):
			for j in range(len(list[i])):
				item = QtGui.QStandardItem(str(list[i][j]))
				self.tableview.setItem(i-1, j, item)
			
		self.add_Tab(update_tupel[0])
		
	
	
	def add_Tab(self, tab_name):
	
		"""Create Tabs in the GUI

		Content of calculated or already available
		excel file will be displayed in the GUI.

		Parameters
		----------
		tab_name : String
		Title of a tab, which should be created.
		
		Returns
		-------
		no value
		"""	
		
		self.tab = QtWidgets.QWidget()
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.tab.sizePolicy().hasHeightForWidth())
		self.tab.setSizePolicy(sizePolicy)
		self.tab.setObjectName("tab")
		self.gridLayout = QtWidgets.QGridLayout(self.tab)
		self.gridLayout.setObjectName("gridLayout")
		self.excel_page_tableView = QtWidgets.QTableView(self.tab)
		self.excel_page_tableView.setObjectName("excel_page_tableView")
		self.gridLayout.addWidget(self.excel_page_tableView, 0, 0, 1, 1)
		
		self.ui.excel_tabWidget.addTab(self.tab, tab_name)
		self.excel_page_tableView.setModel(self.tableview)
		self.excel_page_tableView.resizeColumnsToContents()
	

	
	def add(self):
	
		"""Add an excel file into GUI

		Excel files, which are added, will be 
		displayed in the QListView.

		Parameters
		----------
		no value
		
		Returns
		-------
		no value
		"""		
		
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileNames(self.MainWindow, "QFileDialog.getOpenFileName()", "","Excel Files (*.xlsx *xlsm *.xls);; All Files (*)", options=options)
		
		if fileName:
			for file in fileName:
				it = QtGui.QStandardItem(file)
				self.entry.appendRow(it)

			point = self.entry.item(self.entry.rowCount()-1)
			self.ui.file_list_listView.setCurrentIndex(point.index())
			self.index = point.index()
			self.showMatrix(point)
			self.first_Click = True
			self.savable = False
			self.ui.label_2.setText("Please select the current item to compare in the List.")
		
		
		
	def up(self):
	
		"""Move an excel file up in the GUI

		Excel files, which are chosen by the user, 
		will be moved up in the QListView by 1.

		Parameters
		----------
		no value
		
		Returns
		-------
		no value
		"""	
		
		if(self.first_Click):
			item = self.entry.itemFromIndex(self.index)
			position = item.row()
			if position > 0:
				item2 = self.entry.takeItem(item.row()-1)
				self.entry.setItem(position-1, self.entry.takeItem(item.row()))
				self.entry.setItem(position, item2)
				self.ui.file_list_listView.setCurrentIndex(item.index())
				self.index = item.index()
				self.showMatrix(item)
				self.savable = False
		

		
	def down(self):
	
		"""Move an excel file down in the GUI

		Excel files, which are chosen by the user, 
		will be moved down in the QListView by 1.

		Parameters
		----------
		no value
		
		Returns
		-------
		no value
		"""		
	
		if(self.first_Click):
			item = self.entry.itemFromIndex(self.index)
			position = item.row()
			if position < self.entry.rowCount()-1:
				item2 = self.entry.takeItem(item.row()+1)
				self.entry.setItem(position+1, self.entry.takeItem(item.row()))
				self.entry.setItem(position, item2)
				self.ui.file_list_listView.setCurrentIndex(item.index())
				self.index = item.index()
				self.showMatrix(item)
				self.savable = False

		
		
	def remove(self):
		
		"""Remove an excel file from the GUI

		Excel files, which are chosen by the user, 
		will be removed from the QListView.

		Parameters
		----------
		no value
		
		Returns
		-------
		no value
		"""			
		
		if(self.first_Click):
			item = self.entry.itemFromIndex(self.index)
			row = self.index.row()
			self.entry.removeRow(item.row())
			self.savable = False
			self.ui.excel_tabWidget.clear()
			if row != 0:
				if row >= self.entry.rowCount():
					row = self.entry.rowCount()-1

				self.ui.file_list_listView.setCurrentIndex(self.entry.item(row).index())
				self.index = self.entry.item(row).index()
				self.showMatrix(self.entry.item(row))
				
	def isValidInput(self, str):
	
		"""
		mathod is not used atm	
		"""	
	
		#//?page=1&rows=2&newname=$_otg&cols=3,4&val=5
		#//?page=1&rows=1,2,3,4,5,6,7,8,9,10,11,12&newname=$_otg&cols=13,14,15&val=16
	
		if(not str):
			self.ui.label_2.setText("No input in field.")
			return False
			
		if("page" in str and "rows" in str and "cols" in str and "val" in str):
		
			#page
			substring = ""
			try:
				substring = str[(str.index("page=")+5): ]
				substring = substring[ :(substring.index("&"))]
				strlist = substring.split(',')
				for s in strlist:
					int(s)
					
			except ValueError:
				self.onlythesesheetswillbecalculated = substring #TODO
				return True
					
					
			#rows
			try:
				substring = str[(str.index("rows=")+5): ]
				substring = substring[ :(substring.index("&"))]
				strlist = substring.split(',')
				for s in strlist:
					int(s)
					
			except ValueError:
				self.ui.label_2.setText("Eingabefeld bei Rows enthaelt mindestens eine nicht valide Nummer!")
				return False
					
			#cols
			try:		
				substring = str[(str.index("cols=")+5): ]
				substring = substring[ :(substring.index("&"))]
				strlist = substring.split(',')
				for s in strlist:
						int(s)
			except ValueError:
				self.ui.label_2.setText("Eingabefeld bei Cols enthaelt mindestens eine nicht valide Nummer!")
				return False
			
			#val
			try:		
				substring = str[(str.index("val=")+4): ]
				strlist = substring.split(',')
				for s in strlist:
					int(s)
					
			except ValueError:
				self.ui.label_2.setText("Eingabefeld bei Val enthaelt mindestens eine nicht valide Nummer!")
				return False
			
			#print(substring)

		else:
			self.ui.label_2.setText("Wrong input in field.")

	
	
	def calculate(self):
	
		"""Compare excel files 

		This method compares excel files, which
		are added by the user into QListView, with
		each other. All excel files above the chosen
		one will be compared with the excel file, 
		which are chosen by the user. The result 
		will be displayed in the GUI and finally 
		is savable.

		Parameters
		----------
		no value
		
		Returns
		-------
		no value
		"""		
	
		if(not self.first_Click):
			return

		inputtext = self.ui.expression_lineEdit.text()
		ValidInput = False
		if(inputtext.strip()):
			ValidInput =True
			
		self.ui.label_2.setText("Calculation is in progress...")	
		
		self.ui.excel_tabWidget.clear() #refresh
		item = QtGui.QStandardItem()
		self.ui.excel_tabWidget.clear()
		self.view_list.clear()
		self.pyvotab_list.clear()
		indexnr = self.index.row()
		white={'internal_style':QtGui.QBrush(QtGui.QColor(255, 255, 255)),'xls':"FFFFFF"} 
		red={'internal_style':QtGui.QBrush(QtGui.QColor(255, 0, 0)),'xls':"FF0000"} 
		green={'internal_style':QtGui.QBrush(QtGui.QColor(0, 255, 0)) ,'xls':"00FF00"} 
		orange={'internal_style':QtGui.QBrush(QtGui.QColor(255, 165, 0)) ,'xls':"FF8000"} 
		default={'internal_style':None ,'xls':None} 
		blue={'internal_style':QtGui.QBrush(QtGui.QColor(0, 0, 255)) ,'xls':"0000FF"} 
		lightblue={'internal_style':QtGui.QBrush(QtGui.QColor(100, 100, 255)) ,'xls':"8080FF"} 
		yellow={'internal_style':QtGui.QBrush(QtGui.QColor(255, 255, 0)) ,'xls':"FFFF00"} 

		
		'''
		Beginn der Ausfuehrung
		'''
		pyvotabIsInList = False
		savelist = []
		pyvotabtuple = 0
		pt = 0
				
		citem = self.entry.item(indexnr)
		df = pd.ExcelFile(citem.text())			
		
		#für jedes sheet des dateipfads in pyvotab_list speichern
		for excelSheetname in df.sheet_names:

			df1 = pd.read_excel (df, excelSheetname)
			savelist = df1.as_matrix()
			header = []
			for col in df1.columns:
				header.append(col)
			
			#eingabebefehl in pyvotab speichern
			if(excelSheetname == "pyvotab"):
				pyvotabIsInList = True
				if(ValidInput):
					savelist = np.append(savelist, [[inputtext]], axis=0)	

			savelist = np.append([header], savelist, axis=0)
			pyvo = pyvoSheet(excelSheetname, savelist, "white", None)
			self.view_list.append(pyvo)
			
			if(excelSheetname == "pyvotab"):
				self.pyvotab_list.append(pyvo)
			
		
		#neues pyvotabsheet erstellen
		if(not pyvotabIsInList):
			header = [["layout"]]
			savelist[[]]
			if(ValidInput):
				savelist = [[inputtext]]
			savelist = np.append([header], savelist, axis=0)
			pyvo = pyvoSheet("pyvotab", savelist, "white", None)
			self.view_list.append(pyvo)
			self.pyvotab_list.append(pyvo)


		#Unterscheidung zwischen Abarbeiten aller Befehle vom Pyvotab und nur das Abarbeiten der Eingabe
		for pyvo in self.view_list:
			if(pyvo.name == "pyvotab"):
				if(ValidInput):
					savelist = [["layout"],[inputtext]]
				else:
					savelist = pyvo.table
				pyvotabtuple = savelist
				break
					
		#Alle Befehle in pyvotabtuple werden abgearbeitet		
		for i in range(1,len(pyvotabtuple)):
			if(type(pyvotabtuple[i][0]) is str):
				if(indexnr == 0):
					pt = Pyvotab(white, white, blue, yellow, lightblue, pyvotabtuple[i][0], debug=False)
				else:	
					pt = Pyvotab(red, green, blue, yellow, lightblue, pyvotabtuple[i][0], debug=False)
					
				pt_name=pt.get_url_parameter(pt.layout,"source","pt.1")
				for i in range(self.entry.rowCount()):

					if(i > indexnr):
						break
						
					citem = self.entry.item(i)
					df = pd.ExcelFile(citem.text())	
					df1 = pd.read_excel (df, pt_name)
					matrixlist = df1.as_matrix().tolist()
					matrixlist.insert(0, list(df1))	
					
					#wenn die dateipfäde älter sind als der markierte dateipfad der liste
					if(citem.index().row() < indexnr):
						pt.InsertTable( matrixlist, False, default)
					else:
						pt.InsertTable( matrixlist, True, default)

					
				printDict = pt.getPrintDict() # add result to global result table				
				self.pyvotab_list +=	printDict	
				self.view_list += printDict
		
		self.tableview= QtGui.QStandardItemModel() # noetig, wenn pyvotab_list keine sheets enthaelt

		for pyvot_sheet in self.view_list:
		
			sheetname=pyvot_sheet.name
			pt_table=pyvot_sheet.table
				
			self.tableview= QtGui.QStandardItemModel() # zeile, spalte

			try:
				self.tableview.setHorizontalHeaderLabels(header)
				for row in range(pt_table.ySize):
					for col in range(pt_table.xSize):
						try:
							cell_content=pt_table[col][row]
							if cell_content:
								item = QtGui.QStandardItem(str(cell_content["value"]))
								this_style=cell_content["style"]['internal_style']
								if this_style:
									item.setBackground(this_style)
								self.tableview.setItem(row, col, item)
						except KeyError:
							pass
				self.add_Tab(sheetname)	
			except AttributeError:
				self.showMatrixSheet([sheetname, pt_table])
					
		self.savable = True
		self.ui.label_2.setText("You can save your calculation now with the \"Save as...\"-Button.")		

		
		
	def saveAs(self):
	
		"""Save result of calculated files 

		Save the result of all calculated
		excel files in method calculated
		in one excel file.

		Parameters
		----------
		no value
		
		Returns
		-------
		no value
		"""		
	
		if(not self.savable):
			return
		
		self.ui.label_2.setText("Saving is in progress...")	
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self.MainWindow, "QFileDialog.getSaveFileName()","","Excel Files (*.xlsx *xlsm *.xls);; All Files (*)", options=options)
		if fileName:
			pw=PtWriter('xls')
			citem = self.entry.item(self.index.row())
			pw.save(self.pyvotab_list, citem.text(), filename, {})

		self.ui.label_2.setText("Saving finished!")	
	
	
	
	def show(self):
	
		"""Show GUI of application

		Show the GUI of ptViewer.

		Parameters
		----------
		no value
		
		Returns
		-------
		no value
		"""		
	
		self.MainWindow.show()

		
		
	def exit(self):
		
		"""Quit application

		Stop application and exit
		after using it.

		Parameters
		----------
		no value
		
		Returns
		-------
		no value
		"""			
		
		sys.exit(self.app.exec_())

		
		
if __name__ == "__main__":

		"""Starting point of application 

		This method starts the application 
		and shows the GUI. After closing
		the GUI this application 
		terminates.

		Parameters
		----------
		no value
		
		Returns
		-------
		no value
		"""	

	main=Main(sys.argv)
	main.show()
	main.exit()		
