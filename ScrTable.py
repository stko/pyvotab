#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re


from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot, Qt


from yaml import load, dump
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper


ScriptPath = "../../Common"

# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))
import ScrLib


class ScrTable:
	def __init__(self, filepath, tableView):
		self.code_in_table_offset = 4
		self.part_filter_array=[]
		self.mfc_filter_array=[]
		self.mfc_filter_codes={}
		self.unused_mfcs=[]
		self.usage_lookup={}
		self.s4p_lookup={}
		self.s4p_timespot=None
		self.mfc_regex=re.compile('^['+ScrLib.get_mfc_charset()+']{5}$')
		self.scr_model = ScrLib.ScrModel.fromfilename(filepath)
		self.all_Mfc_groups = self.scr_model.get_all_Mfc_groups()
		for part_name in self.scr_model.partList:
			part = self.scr_model.get_part_by_name(part_name)
		# https://doc.qt.io/qtforpython/PySide2/QtCore/QSortFilterProxyModel.html
		# standard item model
		self.table_model = QtGui.QStandardItemModel(
			self.scr_model.count_usages+2, len(self.all_Mfc_groups)+4)
		self.table_model.setHorizontalHeaderLabels(
			['Part', 'Release', 'EffIn', 'EffOut']+self.all_Mfc_groups)
		self.all_Mfc_usages = self.scr_model.allMfcs
		self.fill_usage_row( 0, self.code_in_table_offset, self.all_Mfc_groups,
							self.all_Mfc_usages, self.all_Mfc_usages)
		row = 1
		for part_name in self.scr_model.partList:
			part = self.scr_model.get_part_by_name(part_name)

			for usage in part.usage_lines:
				item = QtGui.QStandardItem(usage.name)
				self.table_model.setItem(row, 0, item)
				try:
					release = usage._use["release"]["notice"]
					item = QtGui.QStandardItem(release)
					self.table_model.setItem(row, 1, item)
				except:
					pass
				item = QtGui.QStandardItem(
					usage.effInCode+" ("+str(usage.effInDate)+")")
				self.table_model.setItem(row, 2, item)
				item = QtGui.QStandardItem(
					usage.effOutCode+" ("+str(usage.effOutDate)+")")
				self.table_model.setItem(row, 3, item)
				self.fill_usage_row( row, self.code_in_table_offset, self.all_Mfc_groups,self.all_Mfc_usages, usage)
				self.usage_lookup[row]=usage._use["content"]
				self.s4p_lookup[row]={'in':usage._use["effInDate"],'out':usage._use["effOutDate"]}
				row += 1

		# filter proxy model
		self.filter_proxy_model = QtCore.QSortFilterProxyModel()
		self.filter_proxy_model.filterAcceptsRow = self.filterAcceptsRow
		self.filter_proxy_model.filterAcceptsColumn = self.filterAcceptsColumn

		# und bei geändertem Filter: void QSortFilterProxyModel::invalidateFilter()

		self.filter_proxy_model.setSourceModel(self.table_model)
		# filter_proxy_model.setFilterKeyColumn(0) # third column
		tableView.setModel(self.filter_proxy_model)
		 # set column width to fit contents
		tableView.resizeColumnsToContents()

	def fill_usage_row(self, row, offset, all_Mfc_groups, all_Mfcs_usages, thisUsageLine):
		for i in range(len(all_Mfc_groups)):
			item = QtGui.QStandardItem(ScrLib.mfc_group_string(
				all_Mfc_groups[i], all_Mfcs_usages, thisUsageLine))
			item.setTextAlignment(Qt.AlignCenter) # change the alignment
			self.table_model.setItem(row, offset+i, item)

	def setPartFilter(self,contentString):
		content_elements=contentString.split()
		if len(content_elements)==0:
			if self.part_filter_array!=[]:
				self.part_filter_array=[]
				self.filter_proxy_model.invalidateFilter()
			return True
		for element in content_elements:
			if len(element)<3: # allows only parts longer as 2 chars
				return False
		if content_elements!=self.part_filter_array:
			self.part_filter_array=content_elements
			self.filter_proxy_model.invalidateFilter()
		return True


	def setMfcFilter(self,contentString):
		content_elements=contentString.split()
		if len(content_elements)==0:
			if self.mfc_filter_array!=[]:
				self.mfc_filter_array=[]
				self.mfc_filter_codes={}
				self.filter_proxy_model.invalidateFilter()
			return True
		for element in content_elements:
			if not self.mfc_regex.match(element.upper()): # allows only MFC codes with 5 chars
				return False
		if content_elements!=self.mfc_filter_array:
			self.mfc_filter_array=content_elements
			self.mfc_filter_codes={}
			for element in content_elements:
				mfc_group=ScrLib.mfcToInt(element[:3].upper())
				mfc_code=ScrLib.mfcToInt(element[3:].upper())
				try:
					self.mfc_filter_codes[mfc_group].append(mfc_code)
				except:
					self.mfc_filter_codes[mfc_group]=[]
					self.mfc_filter_codes[mfc_group].append(mfc_code)

			self.filter_proxy_model.invalidateFilter()
		return True


	def filterAcceptsRow(self, row, parent):
		if row==0: # top row is always visible
			return True
		if self.s4p_timespot:
			try:
				if self.s4p_timespot < self.s4p_lookup[row]['in']:
					return False
			except:
				pass
			try:
				if self.s4p_timespot >=self.s4p_lookup[row]['out']:
					return False
			except:
				pass
		part_name_does_match=False
		if self.part_filter_array==[]: #no name restrictions
			part_name_does_match=True
		else:
			index = self.table_model.index(row, 0)
			# We suppose data are strings
			try:
				cell_value=self.table_model.data(index).lower()
				for element in self.part_filter_array:
					if element.lower() in cell_value:
						part_name_does_match=True
			except: # no valid cell content
				pass
		if self.mfc_filter_array==[] or not part_name_does_match: #no MFC restrictions 
			return part_name_does_match
		for mfc_group,mfc_group_codes in self.mfc_filter_codes.items():
			try: # some rows do not have parts, so self.usage_lookup[row] may cause an exeption
				if mfc_group in self.usage_lookup[row]:
					mfc_group_failes=True
					for mfc_code in mfc_group_codes:
						if mfc_code in self.usage_lookup[row][mfc_group]:
							mfc_group_failes=False
							break
					if mfc_group_failes:
						return False # requested codes are not covered
			except KeyError:
				pass
		return True # test loop passed, so code is covered
		

	def filterAcceptsColumn(self, column, parent):
		if column<4:
			return True
		header_code=self.all_Mfc_groups[column-4]
		# as this routine goes so nicely through all columns, we use it also for coloring
		if ScrLib.mfcToInt(header_code) in self.mfc_filter_codes:
			brush = QtGui.QBrush(QtGui.QColor(0, 255, 0))
		else:
			brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))

		self.table_model.horizontalHeaderItem(column).setBackground(brush)
		#self.table_model.horizontalHeaderItem(0).setBackgroundColor(QtGui.QColor(0,0,0));
		if not self.unused_mfcs or column <4:
			return True
		return header_code in self.unused_mfcs


	def set_unused_mfcs_filter(self,mfc_list):
		self.unused_mfcs=mfc_list
		self.filter_proxy_model.invalidateFilter()


	def set_s4p_timespot(self,s4p_date):
		self.s4p_timespot=s4p_date
		self.filter_proxy_model.invalidateFilter()


	def get_s4ps(self):
		s4p_table={}
		for s4p,s4pdate in self.scr_model.get_all_s4p_in_Dates().items():
			s4p_table[s4p]=s4pdate
		return s4p_table

	def get_all_Mfc_groups(self):
		return self.all_Mfc_groups