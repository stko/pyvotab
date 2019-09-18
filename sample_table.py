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

pt = Pyvotab('lightgrey','lightgreen','yellow')

pt.insertTable(t1, 2, False, "orange")
pt.insertTable(t2, 2, True, "lightblue")


rowDepth = pt.headerrows()
colDepth = pt.headercols()
print("rowDepth", rowDepth)
print("colDepth", colDepth)
pt.layoutGrid()
printDict = pt.getPrintDict()
print("<table>")
for x in range(printDict.xSize+1):
	print("<tr>")
	for y in range(printDict.ySize+1):
		try:
			printDict[x][y]
		except:
			print("<td/> ", end='')
			continue
		print("<td ", end='')

		print('style="background-color:', end='')
		print(printDict[x][y]["style"]+'" ', end='')
		'''
		if printDict[x][y]["xDir"]:
			print('colspan="',end='')
		else:
			print('rowspan="',end='')
		print(str(printDict[x][y]["size"])+'" ',end='')
		'''
		print(">", end='')

		print(printDict[x][y]["value"]+"</td>", end='')
	print("</tr>")
print("</table>")
