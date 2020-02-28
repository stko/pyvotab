#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from ptWriter import PtWriter
from pyvotab import PyvoStyles, Pyvotab, PyvoSheet

class PyvotDataRow(dict):
	def __init__(self, pyvot_data_table):
		self.pyvot_data_table=pyvot_data_table

	def commit(self):
		'''
		translates the original key:value into the final [d1,d2..] list reprentation

		call this if the row is finished
		'''

		res=[]
		for header in self.pyvot_data_table.headers:
			if not header in self:
				res.append("")
			else:
				res.append(self[header])
		if res:
			self.pyvot_data_table.append(res)



class PyvotDataTable(list):
	def __init__(self, table_headers):
		self.headers=table_headers
		self.raw_rows=[]

	def new_row(self):
		'''
		creates and adds a new row to the table

		Parameters
		----------
		layout : string
			pyvotab layout string

		Returns
		-------
		res: PyvotDataRow
		'''

		new_row=PyvotDataRow(self)
		self.raw_rows.append(new_row)
		return new_row

	def commit(self):
		'''
		translates the raw_rows into the final [d1,d2..] list reprentation

		call this if the PyvotDataTable is finished
		'''
		self.append(self.headers)
		for rows in self.raw_rows:
			rows.commit()


class PyvoTables(dict):
	'''
	Helper class to collect data first for later pyvotab layout calculation
	'''

	def __init__(self ):
		self.update({'pyvotab':["Layout"]})


	def add_layout(self, layout):
		'''
		adds a layout string to the tables

		Parameters
		----------
		layout : string
			pyvotab layout string
		'''

		self["pyvotab"].append(layout)

	def new_table(self, table_name, table_headers):
		'''
		adds a new table to the tables

		Parameters
		----------
		table_name : string
			name of the new table WITHOUT ! the leading "pt."
			
		table_headers : list of strings
			define the headers of the table

		Returns
		-------
		res: PyvotDataTable
		'''

		new_table=PyvotDataTable(table_headers)
		self["pt."+table_name] = new_table
		return new_table

	def commit(self):
		'''
		translates the PyvoTables into the final [d1,d2..] list reprentation

		call this if the PyvoTables is finished
		'''

		for name, table in self.items():
			if not name=="pyvotab":
				table.commit()

	def layout_tables(self):
		return layout_tables(self,self["pyvotab"][1:])

def layout_tables(pt_tables,layout_string_array):
	'''
	calculates the complete table set 

	Parameters
	----------
	
	pt_tables : dict (tablename:table) of tables (nested list of row/cols)
		contains the raw table data

	layout_string_array : list of string
		list of layout strings to be applied for the layout operation
		

	Returns
	-------
	res: PyvotDataTable
	'''

	white={'xls':"FFFFFF"} 
	red={'xls':"FF0000"} 
	green={'xls':"00FF00"} 
	orange={'xls':"FF8000"} 
	default={'xls':None} 
	blue={'xls':"0000FF"} 
	lightblue={'xls':"8080FF"} 
	yellow={'xls':"FFFF00"} 


	pyvot_style = PyvoStyles(white, white, orange, yellow, lightblue)
	pyvotab_sheet_list=[]
	# adding the layout sheets to the output
	# copy the layouts into a row/colums list
	layout_table=[]
	layout_table.append(["Layout"])
	for single_layout_string in layout_string_array:
		layout_table.append([single_layout_string])
	pyvo = PyvoSheet("pyvotab", layout_table, None, None)
	pyvotab_sheet_list.append(pyvo)

	for table_name, table in pt_tables.items():
		if table_name=="pyvotab":
			continue
		pyvo = PyvoSheet(table_name, table, None, None)
		pyvotab_sheet_list.append(pyvo)

	for actual_layout_string in layout_string_array:
		if type(actual_layout_string) is str and not actual_layout_string=="":
			pyvotab_model = Pyvotab(pyvot_style, actual_layout_string, debug=False)	
			pt_name=pyvotab_model.get_url_parameter(pyvotab_model.layout,"source","pt.1")
			try: 
				pyvotab_model.InsertTable( pt_tables[pt_name], False, None)
			except:
				print("Error: Can not load pivotab Sheet {0}".format(pt_name))
			printDict = pyvotab_model.getPrintDict() # add result to global result table				
			pyvotab_sheet_list +=	printDict	

	return pyvotab_sheet_list 




if __name__ == "__main__":
	from ptWriter import PtWriter

	ptables=PyvoTables()
	ptables.add_layout("//?source=pt.logistic&page=test&rows=1&newname=$&cols=2&val=3&template=template")
	ptable=ptables.new_table("logistic",["A","B","C"])
	ptrow=ptable.new_row()
	ptrow["A"]="A 1"
	ptrow["B"]="B 1"
	ptrow["C"]="C 1"
	ptrow=ptable.new_row()
	ptrow["A"]="A 2"
	ptrow["C"]="C 2"
	ptables.commit()
	pyvotab_sheet_list = ptables.layout_tables()
	pyvotab_writer=PtWriter('xls')
	pyvotab_writer.save(pyvotab_sheet_list, "", "test.xlsx", {})
