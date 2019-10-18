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

#TODO
#matrix anpassen farbe,header
#tabs speichern	
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
		self.firstClick = False  #Bugfix fuer Up-Down-Button bevor ein Element ausgewaehlt wurde
		
		

	def on_clicked(self, index):
		self.firstClick = True
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

		
	def remove(self):
		if(self.firstClick):
			item = self.entry.itemFromIndex(self.index)
			row = self.index.row()
			self.entry.removeRow(item.row())
			if row != 0:
				if row >= self.entry.rowCount():
					row = self.entry.rowCount()-1

				self.ui.file_list_listView.setCurrentIndex(self.entry.item(row).index())
				self.index = self.entry.item(row).index()
				self.showMatrix(self.entry.item(row))
				
	def convertToInt(self, list):
		for i in range(len(list)):
			list[i] = int(list[i])
		
		return list		
			
	def calculate(self):
		if(not self.firstClick):
			return
			
		if(not self.ui.expression_lineEdit.text()):
			self.ui.label_2.setText("Wrong or no input in field. Use position numbers for: Sheet, {Rows}*, {Columns}*, value")
			return
		
		inputtext = self.ui.expression_lineEdit.text()
		inputlist = inputtext.split(',')

		if(len(inputlist) != 4):
			self.ui.label_2.setText("Wrong or no input in field. Use position numbers for: Sheet, {Rows}*, {Columns}*, value")
			return
		# a, 3 4 , 1 2, 5 
		try:
			inputlist[0] = int(inputlist[0])
		except:
			pass
		
		inputlist[1] = self.convertToInt(inputlist[1].strip().split(' '))
		inputlist[2] = self.convertToInt(inputlist[2].strip().split(' '))
		inputlist[3] = int(inputlist[3])
		
		item = QtGui.QStandardItem()
		self.ui.excel_tabWidget.clear()
		self.tlist.clear()
		self.ptlist.clear()
		indexnr = self.index.row()
		red={'internal_style':QtGui.QBrush(QtGui.QColor(255, 0, 0)),'excel_style':None} 
		green={'internal_style':QtGui.QBrush(QtGui.QColor(0, 255, 0)) ,'excel_style':None} 
		orange={'internal_style':QtGui.QBrush(QtGui.QColor(255, 165, 0)) ,'excel_style':None} 
		blue={'internal_style':QtGui.QBrush(QtGui.QColor(0, 0, 255)) ,'excel_style':None} 
		black={'internal_style':QtGui.QBrush(QtGui.QColor(0, 0, 0)) ,'excel_style':None} 
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
						pt = Pyvotab(red,green,blue) 
						self.tlist.append((excelSheetname, pt))
						
					#den pt sheet des dateipfades auslesen 	
					df1 = pd.read_excel (df, excelSheetname)
					matrixlist = df1.as_matrix().tolist()
					matrixlist.insert(0, list(df1))
						
					#wenn die dateipfäde älter sind als der markierte dateipfad der liste
					if(citem.index().row() < indexnr):
						pt.newInsertTable( matrixlist, inputlist[0] , { 'rows' : inputlist[1], 'cols' : inputlist[2], 'val' : inputlist[3] , 'filter': None, 'pivot': 'plain'}, False, orange)
					else:
						pt.newInsertTable( matrixlist, inputlist[0] , { 'rows' : inputlist[1], 'cols' : inputlist[2], 'val' : inputlist[3] , 'filter': None, 'pivot': 'plain'}, True, orange)
		
		#für jeden ausgelesenen pt. sheet mit pyvotab in tlist
		for l in range(len(self.tlist)):
			pt = self.tlist[l][1]
			self.ptlist.append(pt.getPrintDict())		
			
			self.tableview= QtGui.QStandardItemModel() # zeile, spalte
			#self.tableview.setHorizontalHeaderLabels(header)
			for sheetname, ptele in self.ptlist[-1].items():
				self.tableview= QtGui.QStandardItemModel() # zeile, spalte
				for i in range(ptele.xSize+1):
					for j in range(ptele.ySize+1):
						try:
							item = QtGui.QStandardItem(str(ptele[i][j]["value"]))
							item.setBackground(ptele[i][j]["style"]['internal_style'])
							self.tableview.setItem(i, j, item)
						except KeyError:
							pass
					
				
				#tele = self.tlist[l]	
				#self.add_Tab(tele[0])
				self.add_Tab(sheetname)
	
				
	def saveAs(self):
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
		if(not ".xls" in filename):
			filename = filename+".xlsx"
		
		writer = ExcelWriter(filename)
		'''
		qitemmodel = self.tableview
		#list = [["" for x in range(qitemmodel.rowCount())] for y in range(qitemmodel.columnCount())]
		list = []
		for i in range(qitemmodel.rowCount()):
			try:
				list[i] = list[i]
			except:
				list.append([])
				pass
				
			for j in range(qitemmodel.columnCount()):
				try:
					list[i][j] = qitemmodel.item(i,j).text()
				except IndexError:
					list[i].append(qitemmodel.item(i,j).text())
				except:	
					list[i].append("")
					pass
		'''
		
		for pyvotabmap in self.ptlist:
			for sheetname, ptele in pyvotabmap.items():
				list = []
				for i in range(ptele.xSize+1):
					try:
						list[i] = list[i]
					except:
						list.append([])
						pass
					for j in range(ptele.ySize+1):
						try:
							list[i].append(str(ptele[i][j]["value"]))
							#item = QtGui.QStandardItem(str(ptele[i][j]["value"]))
							#item.setBackground(ptele[i][j]["style"]['internal_style'])
							#self.tableview.setItem(i, j, item)
						except:
							list[i].append("")
							pass
				
		
				df = pd.DataFrame(list)
				#df = df.style.apply(self.highlight_cells()) TODO coloring
				df.to_excel(writer,sheetname,index=False)
				
				worksheet = writer.sheets[sheetname]
				for idx, col in enumerate(df):  # loop through all columns
					series = df[col]
					max_len = max((
						series.astype(str).map(len).max(),  # len of largest item
						len(str(series.name))  # len of column name/header
						)) + 1  # adding a little extra space
					worksheet.set_column(idx, idx, max_len)  # set column width
				

				
		
		writer.save()
	
	def highlight_cells(self):
		# provide your criteria for highlighting the cells here
		return ['background-color: yellow']
	
	def show(self):
		self.MainWindow.show()

	def exit(self):
		sys.exit(self.app.exec_())

		
if __name__ == "__main__":
	main=Main(sys.argv)
	main.show()
	main.exit()		
