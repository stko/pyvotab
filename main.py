import sys
import os
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot

import pandas as pd
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
		#self.ui.add_file_pushButton.clicked.connect(self.add)

		self.ui.label_2.setText("Please Select item in the QListView")
		self.index = 0
		self.entry = QtGui.QStandardItemModel()
		self.ui.file_list_listView.setModel(self.entry)
		self.ui.file_list_listView.clicked[QtCore.QModelIndex].connect(self.on_clicked)
		# When you receive the signal, you call QtGui.QStandardItemModel.itemFromIndex() 
		# on the given model index to get a pointer to the item        

		for text in ["D:\\Urmel\\UrmelProjects\\pyvotab\\pyvoTab_Macro.xlsm","D:\\Urmel\\UrmelProjects\\pyvotab\\pyvoTab_Macro - Copy.xlsm"
				,"D:\\Urmel\\UrmelProjects\\pyvotab\\pyvoTab_Macro - Copy (2).xlsm", "D:\\Urmel\\UrmelProjects\\pyvotab\\pyvoTab_Macro - Copy (3).xlsm"]:
			it = QtGui.QStandardItem(text)
			self.entry.appendRow(it)
		self.itemOld = QtGui.QStandardItem("text")

		header = ["a","b","c","d"]
		data =[("aa","bb","cc","dd"),("aaa","bbv","ccv","ddc"),("aa1","bb1","cc1","dd1"),("a2a","b2b","c2c","d2d")]
		self.tableview = MyTableModel(data,header)
		self.ui.excel_page_tableView.setModel(self.tableview)
		
	def on_clicked(self, index):
		self.index = index
		item = self.entry.itemFromIndex(index)
		self.ui.label_2.setText("on_clicked: itemIndex=`{}`, itemText=`{}`""".format(item.index().row(), item.text()))
		#item.setForeground(QBrush(QColor(255, 0, 0))) 
		#self.itemOld.setForeground(QBrush(QColor(0, 0, 0))) 
		self.itemOld = item
		
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
		
	def up(self):
		item = self.entry.itemFromIndex(self.index)
		position = item.row()
		if position > 0:
			item2 = self.entry.takeItem(item.row()-1)
			self.entry.setItem(position-1, self.entry.takeItem(item.row()))
			self.entry.setItem(position, item2)
			self.ui.file_list_listView.setCurrentIndex(item.index())
			self.index = item.index()
		

	def down(self):
		item = self.entry.itemFromIndex(self.index)
		position = item.row()
		if position < self.entry.rowCount()-1:
			item2 = self.entry.takeItem(item.row()+1)
			self.entry.setItem(position+1, self.entry.takeItem(item.row()))
			self.entry.setItem(position, item2)
			self.ui.file_list_listView.setCurrentIndex(item.index())
			self.index = item.index()

		
	def remove(self):
		item = self.entry.itemFromIndex(self.index)
		row = self.index.row()
		self.entry.removeRow(item.row())
		if row != 0:
			if row >= self.entry.rowCount():
				row = self.entry.rowCount()-1

			self.ui.file_list_listView.setCurrentIndex(self.entry.item(row).index())
			self.index = self.entry.item(row).index()
			
	def calculate(self):
		pt = Pyvotab('lightgrey','lightgreen','yellow')
		
		self.comparelist = []
		
		for i in range(self.entry.rowCount()):
			df = pd.read_excel (self.entry.item(i).text())
			print (df)
			self.comparelist.append(df.as_matrix())
		
		for elem in self.comparelist:
			pt.insertTable(elem, 2, False, "orange")

		#pt.layoutGrid()
		#printDict = pt.getPrintDict()
		print(self.ui.expression_lineEdit.text())
		
		t2 = [
			['Hins', 'Mueller', 'Hamburg', 'Postweg', 8],
			['Klaus', 'Meier', 'Hamburg', 'Feldplatz', 6],
			['Klaus', 'Meier', 'Berlin', 'Burgallee', 4],
			['Klaus', 'Schulze', 'Berlin', 'Burgallee', 3],
			['Klaus', 'Schulze', 'Berlin', 'am Deich', 9],
			['Hans', 'Mueller', 'Berlin', 'am Deich', 10],
		]
		print(t2)
		
	def saveAs(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self.MainWindow, "QFileDialog.getSaveFileName()","","All Files (*)", options=options)
		if fileName:
			f = open(fileName+".txt","w+")
			f.write(self.entry.itemFromIndex(self.index).text())
			f.close()
			print(fileName)
		
	def show(self):
		self.MainWindow.show()

	def exit(self):
		sys.exit(self.app.exec_())
		
if __name__ == "__main__":
	main=Main(sys.argv)
	main.show()
	main.exit()		
