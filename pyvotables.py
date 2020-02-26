#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

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
			print("PyvotDataRow commit",header)
			if not header in self:
				res.append("")
			else:
				res.append(self[header])
		print("commit result",repr(res))
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
		print("new row")
		return new_row

	def commit(self):
		'''
		translates the raw_rows into the final [d1,d2..] list reprentation

		call this if the PyvotDataTable is finished
		'''
		for rows in self.raw_rows:
			print("commit PyvotDataTable")

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
		print("PyvoTables new_table")
		return new_table

	def commit(self):
		'''
		translates the PyvoTables into the final [d1,d2..] list reprentation

		call this if the PyvoTables is finished
		'''

		print("pyvotables commit 1")

		for name, table in self.items():
			if not name=="pyvotab":
				print("pyvotables commit")
				table.commit()


if __name__ == "__main__":
	ptables=PyvoTables()
	ptables.add_layout("lala")
	ptable=ptables.new_table("logistic",["A","B","C"])
	ptrow=ptable.new_row()
	ptrow["A"]="A 1"
	ptrow["B"]="B 1"
	ptrow["C"]="C 1"
	ptrow=ptable.new_row()
	ptrow["A"]="A 2"
	ptrow["C"]="C 2"
	ptables.commit()
	print(repr(ptables))