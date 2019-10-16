from pprint import pprint

from pyvotab import Pyvotab

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
	['Klaus', 'Meier', 'Hamburg', 'Feldplatz', 6],
	['Klaus', 'Meier', 'Berlin', 'Burgallee', 4],
	['Klaus', 'Schulze', 'Berlin', 'Burgallee', 3],
	['Klaus', 'Schulze', 'Berlin', 'am Deich', 9],
	['Hans', 'Mueller', 'Berlin', 'am Deich', 10],
]


pt = Pyvotab('lightgrey','lightgreen','yellow','lightblue', 'aquamarine', 3 , { 'rows' : [3, 4 ], 'cols' : [1, 2], 'val' : 5 , 'filter': None, 'pivot': 'plain'}, debug=True)

pt.InsertTable( t5, False, "white")
pt.InsertTable( t6, True, "white")


'''
rowDepth = pt.headerrows()
colDepth = pt.headercols()
print("rowDepth", rowDepth)
print("colDepth", colDepth)
'''

for pyvot_sheet in pt.getPrintDict():
	page_name=pyvot_sheet.name
	printDict=pyvot_sheet.table
	print("tabellen_name",page_name)
	print('<table border="1">')
	for x in range(printDict.xSize+1):
		print("<tr>")
		for y in range(printDict.ySize+1):
			try:
				cell_content=printDict[x][y]
			except:
				print("<td/> ", end='')
				continue
			if cell_content: # if content is None, then it's an empty filler element, needed to handle multicell html cells correctly
				print("<td ", end='')

				print('style="background-color:', end='')
				print(cell_content["style"]+'" ', end='')
				if cell_content["xDir"]:
					print('colspan="',end='')
				else:
					print('rowspan="',end='')
				print(str(cell_content["size"])+'" ',end='')
				print(">", end='')

				print(cell_content["value"]+"</td>", end='')
		print("</tr>")
	print("</table>")
