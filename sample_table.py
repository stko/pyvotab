from pprint import pprint

from pyvotab import Pyvotab, PyvoStyles

t1 = [
	['Hans', 'Mueller', 'Hamburg', 'Postweg', 8],
	['Klaus', 'Meier', 'Hamburg', 'Feldplatz', 5],
	['Klaus', 'Meier', 'Berlin', 'Burgallee', 4],
	['Klaus', 'Schulze', 'Berlin', 'Burgallee', 3],
]

t2 = [
	['Hins', 'Mueller', 'Hamburg', 'Postweg', 8],
	['Klaus', 'Meier', 'Hamburg', 'Feldplatz', 6],
	['Klaus', 'Meier', 'Berlin', 'Burgallee', 4],
	['Klaus', 'Schulze', 'Berlin', 'Burgallee', 3],
	['Klaus', 'Schulze', 'Berlin', 'am Deich', 9],
	['Hans', 'Mueller', 'Berlin', 'am Deich', 10],
]

t3 = [
	['Hans', 'Mueller', 'Hamburg', 'Postweg', 8]
]

t4 = [
	['Hins', 'Mueller', 'Hamburg', 'Postweg', 8]
]

t5 = [ # = t1 with column header
	['Vorname', 'Nachname', 'Stadt', 'Straße', 'Hausnummer'],
	['Hans', 'Mueller', 'Hamburg', 'Postweg', 8],
	['Klaus', 'Meier', 'Hamburg', 'Feldplatz', 5],
	['Klaus', 'Meier', 'Berlin', 'Burgallee', 4],
	['Klaus', 'Schulze', 'Berlin', 'Burgallee', 3],
]

t6 = [ # = t2 with column header
	['Vorname', 'Nachname', 'Stadt', 'Straße', 'Hausnummer'],
	['Hins', 'Mueller', 'Hamburg', 'Postweg', 8],
	['Klaus', 'Meier', 'Hamburg', 'Feldplatz', 5],
	['Klaus', 'Meier', 'Berlin', 'Burgallee', 4],
	['Klaus', 'Schulze', 'Berlin', 'Burgallee', 3],
	['Klaus', 'Schulze', 'Berlin', 'am Deich', 9],
	['Hans', 'Mueller', 'Berlin', 'am Deich', 10],
]
p1 = [ # Pivot test table
	['Product', 'Day', 'Sold'],
	['Soap', 'Mo', 8],
	['Soap', 'Mo', 8],
	['Water', 'Mo', 2],
	['Steaks', 'Mo', 4],
	['Soap', 'Tu', 1],
	['Water', 'Tu', 1],
	['Steaks', 'Tu', 7],
	['Soap', 'We', 2],
	['Water', 'We', 9],
	['Steaks', 'We', 7],
	['Soap', 'Th', 1],
	['Water', 'Th', 5],
	['Water', 'Tu', 2],
	['Salt', 'Th', 6],
]
p2 = [ # Pivot test table
	['Product', 'Day', 'Sold'],
	['Soap', 'Mo', 5], # changed value here 8 -> 5
	['Soap', 'Mo', 8],
	['Water', 'Mo', 2],
	['Steaks', 'Mo', 4],
	['Soap', 'Tu', 1],
	['Water', 'Tu', 1],
	['Steaks', 'Tu', 9],# changed value here 7 -> 9
	['Soap', 'We', 2],
	['Water', 'We', 9],
	['Steaks', 'We', 7],
	['Soap', 'Th', 1],
	['Water', 'Th', 5],
	['Water', 'Tu', 2],
	['Pepper', 'Th', 6], # changed Salt to Pepper
]

debug=False

pts= PyvoStyles('lightgrey','lightgreen','yellow','lightblue', 'aquamarine')
#pt = Pyvotab(pts, { 'page': 3, 'rows' : [ 3,4 ], 'cols' : [2, 1], 'val' : 5 , 'filter': None, 'pivot': 'plain'}, debug=debug)
#pt = Pyvotab(pts, { 'page': 3, 'rows' : [ 2 ], 'cols' : [3], 'val' : 5 ,'p_rows' : [ 1,2 ], 'p_cols' : [3], 'p_val' : 4 , 'filter': None, 'pivot': 'pivot'}, debug=debug)
#pt = Pyvotab(pts, { 'page': 'all', 'rows' : [ 1,2 ], 'cols' : [3], 'val' : 4 ,'p_rows' : [ 2 ], 'p_cols' : [3], 'p_val' : 5 , 'filter': None, 'pivot': 'pivot'}, debug=debug)

#pt.InsertTable( t5, False, "white")
#pt.InsertTable( t6, True, "white")

pt = Pyvotab(pts, { 'page': 'all', 'rows' : [ 3 ], 'cols' : [2], 'val' : 4 ,'p_rows' : [ 1 ], 'p_cols' : [2], 'p_val' : 3 , 'filter': None, 'pivot': 'cnt'}, debug=debug)

pt.InsertTable( p1, False, "white")
#pt.InsertTable( p2, True, "white")

'''
rowDepth = pt.headerrows()
colDepth = pt.headercols()
print("rowDepth", rowDepth)
print("colDepth", colDepth)
'''

for pyvot_sheet in pt.getPrintDict():
	page_name=pyvot_sheet.name
	pt_table=pyvot_sheet.table
	print("tabellen_name",page_name,pyvot_sheet.style)
	print('<table border="1">')
	for row in range(pt_table.ySize):
		print("<tr>")
		for col in range(pt_table.xSize):
			try:
				cell_content=pt_table[col][row]
			except:
				print("<td/> ", end='')
				continue
			if cell_content: # if content is None, then it's an empty filler element, needed to handle multicell html cells correctly
				print("<td ", end='')

				print('style="background-color:', end='')
				print(cell_content["style"]+'" ', end='')
				if cell_content["xDir"]:
					print('rowspan="',end='')
				else:
					print('colspan="',end='')
				print(str(cell_content["size"])+'" ',end='')
				print(">", end='')
				if debug:
					print(cell_content["value"]+" row:{0}/col:{1}".format(row,col) +"</td>", end='')
				else:
					print(cell_content["value"] +"</td>", end='')
		print("</tr>")
	print("</table>")
