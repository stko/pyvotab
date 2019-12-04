import sys
import os
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QTabWidget, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot
import xlrd 
from xlrd import XLRDError
import numpy as np
import pandas as panda
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
		self.show_Matrix(item)
		self.ui.label_2.setText("Please write a command into the input field or press the \"Calculate\"-Button.")
	
	
	
	def show_Matrix(self, item):
	
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
		data_file = panda.ExcelFile(item.text())	

		for element in data_file.sheet_names:

			data_file_element = panda.read_excel (data_file, element)
			list = data_file_element.as_matrix()
			
			header = data_file_element.head()
			self.table_view= QtGui.QStandardItemModel(len(list),len(header)-1) # zeile, spalte
			self.table_view.setHorizontalHeaderLabels(header)
			for i in range(len(list)):
				for j in range(len(list[i])):
					item = QtGui.QStandardItem(str(list[i][j]))
					self.table_view.setItem(i, j, item)
				
			self.add_Tab(element)
			
		
		
	def show_Matrix_Sheet(self, update_tupel):

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
		
		self.table_view= QtGui.QStandardItemModel(len(list)-1,len(list[0])-1) # zeile, spalte
		self.table_view.setHorizontalHeaderLabels(list[0])
		for i in range(1, len(list)):
			for j in range(len(list[i])):
				item = QtGui.QStandardItem(str(list[i][j]))
				self.table_view.setItem(i-1, j, item)
			
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
		self.excel_page_tableView.setModel(self.table_view)
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
		file_name, _ = QFileDialog.getOpenFileNames(self.MainWindow, "QFileDialog.getOpenFileName()", "","Excel Files (*.xlsx *xlsm *.xls);; All Files (*)", options=options)
		
		if file_name:
			for file in file_name:
				it = QtGui.QStandardItem(file)
				self.entry.appendRow(it)

			point = self.entry.item(self.entry.rowCount()-1)
			self.ui.file_list_listView.setCurrentIndex(point.index())
			self.index = point.index()
			self.show_Matrix(point)
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
				self.show_Matrix(item)
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
				self.show_Matrix(item)
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
				self.show_Matrix(self.entry.item(row))
				
	def isValidInput(self, string_text):
	
		"""
		mathod is not used atm	
		"""	
	
		#//?page=1&rows=2&newname=$_otg&cols=3,4&val=5
		#//?page=1&rows=1,2,3,4,5,6,7,8,9,10,11,12&newname=$_otg&cols=13,14,15&val=16
	
		if(not string_text):
			self.ui.label_2.setText("No input in field.")
			return False
			
		if("page" in string_text and "rows" in string_text and "cols" in string_text and "val" in string_text):
		
			#page
			substring = ""
			try:
				substring = string_text[(string_text.index("page=")+5): ]
				substring = substring[ :(substring.index("&"))]
				string_list = substring.split(',')
				for string_element in string_list:
					int(string_element)
					
			except ValueError:
				self.only_these_sheets_will_be_calculated = substring #TODO
				return True
					
					
			#rows
			try:
				substring = string_text[(string_text.index("rows=")+5): ]
				substring = substring[ :(substring.index("&"))]
				string_list = substring.split(',')
				for string_element in string_list:
					int(string_element)
					
			except ValueError:
				self.ui.label_2.setText("Eingabefeld bei Rows enthaelt mindestens eine nicht valide Nummer!")
				return False
					
			#cols
			try:		
				substring = string_text[(string_text.index("cols=")+5): ]
				substring = substring[ :(substring.index("&"))]
				string_list = substring.split(',')
				for string_element in string_list:
						int(string_element)
			except ValueError:
				self.ui.label_2.setText("Eingabefeld bei Cols enthaelt mindestens eine nicht valide Nummer!")
				return False
			
			#val
			try:		
				substring = string_text[(string_text.index("val=")+4): ]
				string_list = substring.split(',')
				for string_element in string_list:
					int(string_element)
					
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

		input_text = self.ui.expression_lineEdit.text()
		valid_input = False
		if(input_text.strip()):
			valid_input =True
			
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
		pyvotab_is_in_list = False
		save_list = []
		pyvotab_tuple = 0
		pyvotab = 0
				
		citem = self.entry.item(indexnr)
		data_file = panda.ExcelFile(citem.text())			
		
		#für jedes sheet des dateipfads in pyvotab_list speichern
		for excelSheetname in data_file.sheet_names:

			data_file_element = panda.read_excel (data_file, excelSheetname)
			save_list = data_file_element.as_matrix()
			header = []
			for col in data_file_element.columns:
				header.append(col)
			
			#eingabebefehl in pyvotab speichern
			if(excelSheetname == "pyvotab"):
				pyvotab_is_in_list = True
				if(valid_input):
					save_list = np.append(save_list, [[input_text]], axis=0)	

			save_list = np.append([header], save_list, axis=0)
			pyvo = pyvoSheet(excelSheetname, save_list, white, None)
			self.view_list.append(pyvo)
			
			if(excelSheetname == "pyvotab"):
				self.pyvotab_list.append(pyvo)
			
		
		#neues pyvotabsheet erstellen
		if(not pyvotab_is_in_list):
			header = [["layout"]]
			save_list[[]]
			if(valid_input):
				save_list = [[input_text]]
			save_list = np.append([header], save_list, axis=0)
			pyvo = pyvoSheet("pyvotab", save_list, "white", None)
			self.view_list.append(pyvo)
			self.pyvotab_list.append(pyvo)


		#Unterscheidung zwischen Abarbeiten aller Befehle vom Pyvotab und nur das Abarbeiten der Eingabe
		for pyvo in self.view_list:
			if(pyvo.name == "pyvotab"):
				if(valid_input):
					save_list = [["layout"],[input_text]]
				else:
					save_list = pyvo.table
				pyvotab_tuple = save_list
				break
					
		#Alle Befehle in pyvotab_tuple werden abgearbeitet		
		for i in range(1,len(pyvotab_tuple)):
			if(type(pyvotab_tuple[i][0]) is str):
				if(indexnr == 0):
					pyvotab = Pyvotab(white, white, blue, yellow, lightblue, pyvotab_tuple[i][0], debug=False)
				else:	
					pyvotab = Pyvotab(red, green, blue, yellow, lightblue, pyvotab_tuple[i][0], debug=False)
					
				pt_name=pyvotab.get_url_parameter(pyvotab.layout,"source","pyvotab.1")
				for i in range(self.entry.rowCount()):

					if(i > indexnr):
						break
						
					citem = self.entry.item(i)
					data_file = panda.ExcelFile(citem.text())	
					data_file_element = panda.read_excel (data_file, pt_name)
					matrixlist = data_file_element.as_matrix().tolist()
					matrixlist.insert(0, list(data_file_element))	
					
					#wenn die dateipfäde älter sind als der markierte dateipfad der liste
					if(citem.index().row() < indexnr):
						pyvotab.InsertTable( matrixlist, False, default)
					else:
						pyvotab.InsertTable( matrixlist, True, default)

					
				printDict = pyvotab.getPrintDict() # add result to global result table				
				self.pyvotab_list +=	printDict	
				self.view_list += printDict
		
		self.table_view= QtGui.QStandardItemModel() # noetig, wenn pyvotab_list keine sheets enthaelt

		for pyvot_sheet in self.view_list:
		
			sheetname=pyvot_sheet.name
			pt_table=pyvot_sheet.table
				
			self.table_view= QtGui.QStandardItemModel() # zeile, spalte

			try:
				self.table_view.setHorizontalHeaderLabels(header)
				for row in range(pt_table.ySize):
					for col in range(pt_table.xSize):
						try:
							cell_content=pt_table[col][row]
							if cell_content:
								item = QtGui.QStandardItem(str(cell_content["value"]))
								this_style=cell_content["style"]['internal_style']
								if this_style:
									item.setBackground(this_style)
								self.table_view.setItem(row, col, item)
						except KeyError:
							pass
				self.add_Tab(sheetname)	
			except AttributeError:
				self.show_Matrix_Sheet([sheetname, pt_table])
					
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
		file_name, _ = QFileDialog.getSaveFileName(self.MainWindow, "QFileDialog.getSaveFileName()","","Excel Files (*.xlsx *xlsm *.xls);; All Files (*)", options=options)
		if file_name:
			pyvotab_writer=PtWriter('xls')
			citem = self.entry.item(self.index.row())
			pyvotab_writer.save(self.pyvotab_list, citem.text(), file_name, {})

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

	main=Main(sys.argv)
	main.show()
	main.exit()		
