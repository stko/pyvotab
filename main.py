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
			
	def calculate(self):
		if(not self.firstClick):
			return
		
		item = QtGui.QStandardItem()
		self.ui.excel_tabWidget.clear()
		indexnr = self.index.row()
		tlist = []
		red=QtGui.QBrush(QtGui.QColor(255, 0, 0)) 
		green=QtGui.QBrush(QtGui.QColor(0, 255, 0)) 
		orange=QtGui.QBrush(QtGui.QColor(255, 165, 0)) 
		blue=QtGui.QBrush(QtGui.QColor(0, 0, 255)) 
		black=QtGui.QBrush(QtGui.QColor(0, 0, 0)) 
		
		#für jeden dateipfad der liste
		for i in range(self.entry.rowCount()):
			if(i > indexnr):
				break
				
			citem = self.entry.item(i)
			df = pd.ExcelFile(citem.text())	
			
			#für jedes sheet des dateipfads
			for ele in df.sheet_names:
				pt = 0
			
				#wenn dateipfad den sheet pt. ... enthält
				if(ele.startswith("pt.")):
					isInList = False
					
					for tupl in tlist:
						if(tupl[0] == ele):
							pt = tupl[1]
							#print(ele)
							isInList = True
							break
						
					if isInList == False:
						pt = Pyvotab(red,green,blue) #green
						tlist.append((ele, pt))
						
					df1 = pd.read_excel (df, ele)	
						
					#wenn die dateipfäde älter sind als der markierte dateipfad der liste
					if(citem.index().row() < indexnr):
						#print(citem.text()+" "+ele+" False")
						pt.insertTable(df1.as_matrix(), 2, False, orange)
					else:
						#print(citem.text()+" "+ele+" True")
						pt.insertTable(df1.as_matrix(), 2, True, orange)
		
		
		for l in range(len(tlist)):
			pt = tlist[l][1]
			pt.layoutGrid()
			list = pt.getPrintDict()	
				
			header = list[0]
			self.tableview= QtGui.QStandardItemModel(len(list),len(header)-1) # zeile, spalte
			#self.tableview.setHorizontalHeaderLabels(header)
			for i in range(len(list)):
				for j in range(len(list[i])):
					try:
						item = QtGui.QStandardItem(str(list[i][j]["value"]))
						item.setBackground(list[i][j]["style"])
						self.tableview.setItem(i, j, item)
					except:
						pass
					
					
					#item.setForeground(list[i][j]["style"])  #TODO object verschwindet
					
				
			tele = tlist[l]	
			self.add_Tab(tele[0])
	
				
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
		df = pd.DataFrame({'a':[1,3,5,7,4,5,6,4,7,8,9],
				   'b':[3,5,6,2,4,6,7,8,7,8,9]})

		writer = ExcelWriter(filename+".xlsx")
		df.to_excel(writer,'Sheet1',index=False)
		writer.save()
	
	def show(self):
		self.MainWindow.show()

	def exit(self):
		sys.exit(self.app.exec_())

		
if __name__ == "__main__":
	main=Main(sys.argv)
	main.show()
	main.exit()		
