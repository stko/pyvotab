import re
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Border, Side, PatternFill, Font, GradientFill, Alignment

class ptPlugin:

	def __init__(self):
		self.plugin_id='xls'

	def save(self, tables, new_tables, input_file_name, file_name, options):
		print("plugin:",file_name)
		if not file_name.lower().endswith('.xlsx'):
			file_name = file_name+".xlsx"
		
		wb = 0
		loadedWorkbook = False
		
		try:
			wb = load_workbook(input_file_name)
			loadedWorkbook = True
		except FileNotFoundError:
			wb = Workbook()
			wb.remove_sheet(wb.active)
			pass
		
		
		for i in range(len(tables)):
			sheet_name= re.sub('[^A-Za-z0-9._]+', '', tables[i].name)
			pt_table=tables[i].table
			
			if(sheet_name == "pt.1"):
				continue
				
			'''
			#wenn sheet_name schon existiert, unter berücksichtigung der Namenskonventionen (max 31. zechne, gross/klein egal usw), dann lösche erst die alte, existierende Seite
			if(not tables[i].name == "pt.1"):

				for j in range(i+1 ,len(tables)):
					if(self.containSheet(tables[i].name, tables[j].name)):
						sheet_name= re.sub('[^A-Za-z0-9._]+', '', tables[j].name)
						pt_table=tables[j].table
		'''
			print(str(i)+" sheetnames: " + str(wb.sheetnames)) #todo remove
			for datasheet in wb:
				if(datasheet.title == sheet_name and not sheet_name == "pt.1"):
					wb.remove_sheet(datasheet) #todo21.11
				
			ws = wb.create_sheet(title=sheet_name)

			try:
				for row in range(pt_table.ySize):
					for col in range(pt_table.xSize):
						try:
							cell_content=pt_table[col][row]
							if cell_content:
								this_cell=ws.cell(column=col+1, row=row+1)
								this_cell.value="{0}".format(str(cell_content["value"]))
								this_style=cell_content["style"][self.plugin_id]
								if this_style:
									this_cell.fill = PatternFill("solid", fgColor=this_style)
								if cell_content["size"]>1:
									if cell_content["xDir"]:
										ws.merge_cells(start_row=row+1, start_column=col+1, end_row=row+1+cell_content["size"]-1, end_column=col+1)
									else:
										ws.merge_cells(start_row=row+1, start_column=col+1, end_row=row+1, end_column=col+1+cell_content["size"]-1)
									this_cell.alignment = Alignment(horizontal="center", vertical="center")
						except KeyError:
							pass
			except AttributeError:

				for row in range(0, len(pt_table)):
					for col in range(len(pt_table[row])):#pt_table[i][j]
						this_cell=ws.cell(row=row+1,column=col+1)
						this_cell.value=str(pt_table[row][col])
						#this_cell.fill = PatternFill("solid", fgColor="white")
					
			if(tables[i].name == "pyvotab"):
				ws.cell(row=1, column=1).value = "made with pyvotab"
				ws.cell(row=1, column=1).hyperlink = "https://github.com/stko/pyvotab"
				ws.cell(row=1, column=1).style = "Hyperlink"	
			
		wb.save(filename = file_name)
		
	def convertToExcelString(self, text):
		text = re.sub('[^A-Za-z0-9._]+', '', text)
		return text[:30]
		
	def containSheet(self, sheetold, sheetnew):
		sheetold = self.convertToExcelString(sheetold)
		sheetnew = self.convertToExcelString(sheetnew)

		if(sheetold.upper() == sheetnew.upper()):
			return True
		else:
			return False
		