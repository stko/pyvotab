#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QTabWidget,
                             QWidget)

from ptViewer_ui import Ui_MainWindow
from ptWriter import PtWriter
from pyvotab import PyvoStyles


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
		self.input_file_list = QtGui.QStandardItemModel()
		self.ui.file_list_listView.setModel(self.input_file_list)
		self.ui.file_list_listView.clicked[QtCore.QModelIndex].connect(self.on_clicked)      

		self.index = None
		self.pyvotab_sheet_list = []
		self.view_sheet_list = []
		self.first_Click = False  	#Bugfix fuer Up-Down-Button bevor ein Element ausgewaehlt wurde
		self.savable = False 	#SaveAs darf nur nach "savable" aufgerufen werden
		self.pyvotab_writer=PtWriter('xls')

		

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
		item = self.input_file_list.itemFromIndex(index)
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

		for tab_name,data_file_element in self.pyvotab_writer.load(item.text()).items():
			list = data_file_element.as_matrix()
			header = data_file_element.head()
			self.table_view= QtGui.QStandardItemModel(len(list),len(header)-1) # zeile, spalte
			self.table_view.setHorizontalHeaderLabels(header)
			for i in range(len(list)):
				for j in range(len(list[i])):
					item = QtGui.QStandardItem(str(list[i][j]))
					self.table_view.setItem(i, j, item)
				
			self.add_Tab(tab_name)


		
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
				self.input_file_list.appendRow(it)

			point = self.input_file_list.item(self.input_file_list.rowCount()-1)
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
		
		if self.first_Click:
			item = self.input_file_list.itemFromIndex(self.index)
			position = item.row()
			if position > 0:
				item2 = self.input_file_list.takeItem(item.row()-1)
				self.input_file_list.setItem(position-1, self.input_file_list.takeItem(item.row()))
				self.input_file_list.setItem(position, item2)
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
	
		if self.first_Click:
			item = self.input_file_list.itemFromIndex(self.index)
			position = item.row()
			if position < self.input_file_list.rowCount()-1:
				item2 = self.input_file_list.takeItem(item.row()+1)
				self.input_file_list.setItem(position+1, self.input_file_list.takeItem(item.row()))
				self.input_file_list.setItem(position, item2)
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
		
		if self.first_Click:
			item = self.input_file_list.itemFromIndex(self.index)
			row = self.index.row()
			self.input_file_list.removeRow(item.row())
			self.savable = False
			self.ui.excel_tabWidget.clear()
			if row != 0:
				if row >= self.input_file_list.rowCount():
					row = self.input_file_list.rowCount()-1

				self.ui.file_list_listView.setCurrentIndex(self.input_file_list.item(row).index())
				self.index = self.input_file_list.item(row).index()
				self.show_Matrix(self.input_file_list.item(row))
				
	def isValidInput(self, string_text):
	
		"""
		mathod is not used atm	
		"""	
	
		#//?page=1&rows=2&newname=$_otg&cols=3,4&val=5
		#//?page=1&rows=1,2,3,4,5,6,7,8,9,10,11,12&newname=$_otg&cols=13,14,15&val=16
	
		if not string_text:
			self.ui.label_2.setText("No input in field.")
			return False
			
		if "page" in string_text and "rows" in string_text and "cols" in string_text and "val" in string_text:
		
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
	
		if not self.first_Click:
			return

		input_text = self.ui.expression_lineEdit.text().strip()

		self.ui.label_2.setText("Calculation is in progress...")	
		
		self.ui.excel_tabWidget.clear() #refresh
		item = QtGui.QStandardItem()
		self.ui.excel_tabWidget.clear()
		self.view_sheet_list.clear()
		self.pyvotab_sheet_list.clear()
		selected_file_row_index = self.index.row()
		white={'internal_style':QtGui.QBrush(QtGui.QColor(255, 255, 255)),'xls':"FFFFFF"} 
		red={'internal_style':QtGui.QBrush(QtGui.QColor(255, 0, 0)),'xls':"FF0000"} 
		green={'internal_style':QtGui.QBrush(QtGui.QColor(0, 255, 0)) ,'xls':"00FF00"} 
		orange={'internal_style':QtGui.QBrush(QtGui.QColor(255, 165, 0)) ,'xls':"FF8000"} 
		default={'internal_style':None ,'xls':None} 
		blue={'internal_style':QtGui.QBrush(QtGui.QColor(0, 0, 255)) ,'xls':"0000FF"} 
		lightblue={'internal_style':QtGui.QBrush(QtGui.QColor(100, 100, 255)) ,'xls':"8080FF"} 
		yellow={'internal_style':QtGui.QBrush(QtGui.QColor(255, 255, 0)) ,'xls':"FFFF00"} 

		if selected_file_row_index == 0 :
			pyvo_style = PyvoStyles(white, white, orange, yellow, lightblue)
		else:	
			pyvo_style = PyvoStyles(red, green, orange, yellow, lightblue)

		# todo: Diese Schleife geht doch auch einfacher, oder?
		input_file_name_list=[]
		for i in range(self.input_file_list.rowCount()):
			if i > selected_file_row_index :
				break
			selected_file_item = self.input_file_list.item(i)
			input_file_name_list.append(selected_file_item.text())
		

		self.pyvotab_sheet_list ,self.view_sheet_list  = self.pyvotab_writer.calculate_pyvotab_files( input_file_name_list, [input_text], pyvo_style)

		self.table_view= QtGui.QStandardItemModel() # noetig, wenn pyvotab_list keine sheets enthaelt


		##### Write the results into the QTable

		for pyvot_sheet in self.view_sheet_list:
			sheetname=pyvot_sheet.name
			pt_table=pyvot_sheet.table
			self.table_view= QtGui.QStandardItemModel() # zeile, spalte
			try:
				#self.table_view.setHorizontalHeaderLabels(header)
				for row in range(pt_table.ySize):
					for col in range(pt_table.xSize):
						try:
							cell_content=pt_table[col][row]
							if cell_content:
								item = QtGui.QStandardItem(str(cell_content["value"]))
								try:
									this_style=cell_content["style"]['internal_style']
									if this_style:
										item.setBackground(this_style)
								except:
									pass # no style set
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
	
		if not self.savable:
			return
		self.ui.label_2.setText("Saving is in progress...")	
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		file_name, _ = QFileDialog.getSaveFileName(self.MainWindow, "QFileDialog.getSaveFileName()","","Excel Files (*.xlsx *xlsm *.xls);; All Files (*)", options=options)
		if file_name:
			citem = self.input_file_list.item(self.index.row())
			self.pyvotab_writer.save(self.pyvotab_sheet_list, citem.text(), file_name, {})
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
