import sys
import os
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QTabWidget, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot

import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from pyvotab import Pyvotab
from ptViewer_ui import Ui_MainWindow
from ptWriter import PtWriter
from openpyxl.styles import Border, Side, PatternFill, Font, GradientFill, Alignment

class Main(object):

	def __init__(self,args):

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

		self.ui.label_2.setText("Please Select item in the QListView")
		self.index = 0
		self.entry = QtGui.QStandardItemModel()
		self.ui.file_list_listView.setModel(self.entry)
		self.ui.file_list_listView.clicked[QtCore.QModelIndex].connect(self.on_clicked)      

		self.ptlist = []
		self.tlist = []
		self.itemOld = QtGui.QStandardItem("text")
		self.firstClick = False  	#Bugfix fuer Up-Down-Button bevor ein Element ausgewaehlt wurde
		self.calculated = False 	#SaveAs darf nur nach "Calculated" aufgerufen werden
		
		

	def on_clicked(self, index):
		self.firstClick = True
		self.calculated = False
		self.index = index
		item = self.entry.itemFromIndex(index)
		self.ui.label_2.setText("on_clicked: itemIndex=`{}`, itemText=`{}`""".format(item.index().row(), item.text()))
		#item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0))) 
		#self.itemOld.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0))) 
		self.itemOld = item
		self.showMatrix(item)
	
	def showMatrix(self, item):
		self.ui.excel_tabWidget.clear()
		df = pd.ExcelFile(item.text())	
		#print (xls.sheet_names)
		for ele in df.sheet_names:
			#print (ele)
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
	
	def add_Tab(self, tabname):
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
		
		self.ui.excel_tabWidget.addTab(self.tab, tabname)
		self.excel_page_tableView.setModel(self.tableview)
		self.excel_page_tableView.resizeColumnsToContents()
	

	def add(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileNames(self.MainWindow, "QFileDialog.getOpenFileName()", "","Excel Files (*.xlsx *xlsm *.xls);; All Files (*)", options=options)
		
		if fileName:
			row = self.entry.rowCount()
			for file in fileName:
				it = QtGui.QStandardItem(file)
				self.entry.appendRow(it)
			
			point = self.entry.item(row)
			self.ui.file_list_listView.setCurrentIndex(point.index())
			self.index = point.index()
			self.showMatrix(point)
			self.firstClick = True
			self.calculated = False
		
	def up(self):
		if(self.firstClick):
			item = self.entry.itemFromIndex(self.index)
			position = item.row()
			if position > 0:
				item2 = self.entry.takeItem(item.row()-1)
				self.entry.setItem(position-1, self.entry.takeItem(item.row()))
				self.entry.setItem(position, item2)
				self.ui.file_list_listView.setCurrentIndex(item.index())
				self.index = item.index()
				self.showMatrix(item)
				self.calculated = False
		

	def down(self):
		if(self.firstClick):
			item = self.entry.itemFromIndex(self.index)
			position = item.row()
			if position < self.entry.rowCount()-1:
				item2 = self.entry.takeItem(item.row()+1)
				self.entry.setItem(position+1, self.entry.takeItem(item.row()))
				self.entry.setItem(position, item2)
				self.ui.file_list_listView.setCurrentIndex(item.index())
				self.index = item.index()
				self.showMatrix(item)
				self.calculated = False

		
	def remove(self):
		if(self.firstClick):
			item = self.entry.itemFromIndex(self.index)
			row = self.index.row()
			self.entry.removeRow(item.row())
			self.calculated = False
			self.ui.excel_tabWidget.clear()
			if row != 0:
				if row >= self.entry.rowCount():
					row = self.entry.rowCount()-1

				self.ui.file_list_listView.setCurrentIndex(self.entry.item(row).index())
				self.index = self.entry.item(row).index()
				self.showMatrix(self.entry.item(row))
				
	def isValidInput(self, str):
		#//?page=1&rows=2&newname=$_otg&cols=3,4&val=5
	
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
			
			print(substring)

		else:
			self.ui.label_2.setText("Wrong input in field.")

	
	def calculate(self):
		if(not self.firstClick):
			return

		inputtext = self.ui.expression_lineEdit.text()
		if(not self.isValidInput(inputtext)):
			return

		item = QtGui.QStandardItem()
		self.ui.excel_tabWidget.clear()
		self.tlist.clear()
		self.ptlist.clear()
		indexnr = self.index.row()
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
		
		#für jeden dateipfad der liste
		for i in range(self.entry.rowCount()):
			if(i > indexnr):
				break
				
			citem = self.entry.item(i)
			df = pd.ExcelFile(citem.text())	
			
			#für jedes sheet des dateipfads
			for excelSheetname in df.sheet_names:
				pt = 0
			
				#wenn dateipfad den sheet pt. ... enthält
				if(excelSheetname.startswith("pt.")):
					isInList = False
					#überprüfen ob pt. bereits in der tlist befindet 
					for tupl in self.tlist:
						if(tupl[0] == excelSheetname):
							pt = tupl[1]
							isInList = True
							break
						
					#wenn der pt. sheet noch nicht in der Liste tlist ist	
					if (isInList == False): 
						pt = Pyvotab(red, green, blue, yellow, lightblue, inputtext, debug=False)
						
						self.tlist.append((excelSheetname, pt))
						
					#den pt sheet des dateipfades auslesen 	
					df1 = pd.read_excel (df, excelSheetname)
					matrixlist = df1.as_matrix().tolist()
					matrixlist.insert(0, list(df1))
						
					#wenn die dateipfäde älter sind als der markierte dateipfad der liste
					if(citem.index().row() < indexnr):
						pt.InsertTable( matrixlist, False, default)
					else:
						pt.InsertTable( matrixlist, True, default)
		
		#für jeden ausgelesenen pt. sheet mit pyvotab in tlist
		for l in range(len(self.tlist)):
			pt = self.tlist[l][1]
			self.ptlist += pt.getPrintDict() # add result to global result table		
			
			self.tableview= QtGui.QStandardItemModel() # zeile, spalte
			#self.tableview.setHorizontalHeaderLabels(header)
			for pyvot_sheet in self.ptlist:
				sheetname=pyvot_sheet.name
				pt_table=pyvot_sheet.table
				self.tableview= QtGui.QStandardItemModel() # zeile, spalte
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
					
				
				#tele = self.tlist[l]	
				#self.add_Tab(tele[0])
				self.add_Tab(sheetname)
		self.calculated = True		
	
				
	def saveAs(self):
		if(not self.calculated):
			self.ui.label_2.setText("Bevor die Datei abgespeichert werden kann, muss sie zuerst berechnet werden!")
			return
			
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self.MainWindow, "QFileDialog.getSaveFileName()","","Excel Files (*.xlsx *xlsm *.xls);; All Files (*)", options=options)
		if fileName:
			self.excelsave(fileName)
			#f = open(fileName+".xlsx","w+")
			#f.write(self.entry.itemFromIndex(self.index).text())
			#f.close()
			#print(fileName)
	
	def excelsave(self, filename):
		pw=PtWriter('xls')
		pw.save(self.ptlist,filename, {})
	
	def show(self):
		self.MainWindow.show()

	def exit(self):
		sys.exit(self.app.exec_())

		
if __name__ == "__main__":
	main=Main(sys.argv)
	main.show()
	main.exit()		
