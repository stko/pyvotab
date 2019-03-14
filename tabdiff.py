from pprint import pprint

class TabDiff(dict):
	
	def __init__(self,parent,isNew):
		self.parent=parent
		self.dimension=0
		self.oldValue='NaN'
		self.newValue='NaN'
		# 0= old, 1= unchanged, 2 = new
		if not isNew:
			self.state=0
		else:
			self.state=2
		
	def increaseDimension(self):
		self.dimension+=1
		if self.parent:
			self.parent.increaseDimension()
		
	def validateState(self,isNew):
		if self.state==1: # signals old and new
			return
		# 0= old, 1= unchanged, 2 = new
		if not isNew:
			newState=0
		else:
			newState=2
		if self.state!= newState:
			self.state=1 # marks	 
	 
	def add(self,value, isNew):
		self.increaseDimension()
		if not value in self:
			self[value]= TabDiff(self,isNew)
			return self[value]
		else:
			self[value].validateState(isNew)
			return self[value]

 
	def MakeValue(self, value,rowDt, colDt,isNew,counter):
		self.counter=counter
		self.rowDt=rowDt
		self.colDt=colDt
		if isNew:
			self.newValue=value
			if self.oldValue!=value:
				self.state=2
			else:
				self.state=1
		else:
			self.oldValue=value
		
	def getEndPoint(self,myhash):
		try:
			return self[hash(myhash)]
		except:
			return None

	def setEndPoint(self,newEndPoint,myhash):
		self[hash(myhash)]=newEndPoint
		self.isEndStup=True

	def setPrintCoords(self,startCoord, level, xDirection):
		if xDirection:
			self.printY=startCoord
			print("set Y {0} for {1}".format(startCoord,self.oldValue))
		else:
			self.printX=startCoord
			print("set X {0} for {1}".format(startCoord,self.oldValue))
 
	def calPrintCoords(self,startCoord, level, xDirection):
		self.startCoord=startCoord
		self.blockSize=startCoord
		self.level=level
		for index in sorted(self.keys()):
			try:
				self.isEndStup
				self[index].setPrintCoords(startCoord,level,xDirection)
				startCoord+=1
			except:
				startCoord=self[index].calPrintCoords(startCoord,level+1,xDirection)

		self.blockSize=startCoord-self.blockSize
		return startCoord

	def depth(self,actLevel):
		resultLevel=actLevel
		for index in self:
			try:
				self[index].isEndStup
				return actLevel
			except:
				newLevel=self[index].depth(actLevel+1)
				if newLevel>resultLevel:
					resultLevel=newLevel
		return resultLevel


	def fillPrintGridValue(self, multiplier, xDirection,  fillFunction):
		value="<{0}|{1}> {2}".format(self.oldValue,self.newValue,self.state)
		fillFunction(value,self.printX,self.printY,xDirection,1)

	def fillPrintGrid(self, multiplier, xDirection, fillFunction):
		for index in sorted(self.keys()):
			isEnd=False
			try:
				self.isEndStup
				isEnd=True
			except:
				pass
			if isEnd:
				self[index].fillPrintGridValue( multiplier, xDirection, fillFunction)
			else:
				if xDirection:
					fillFunction(index,self.level,self[index].startCoord,xDirection,self.blockSize)
				else:
					fillFunction(index,self[index].startCoord,self.level,xDirection,self.blockSize)
				self[index].fillPrintGrid( multiplier, xDirection, fillFunction)

	def pprint(self):
		if self:
			for key, value in self.items():
				print ("{{'{1}'".format(hex(id(value)),key),end='')
				if value.state==0:
					print("-",end="")
				if value.state==2:
					print("+",end="")
				print(": ",end='')
				value.pprint()
				print ('}} ',end='')
		else:
			print("<{0}|{1}> {2}.{3}".format(self.oldValue,self.newValue,self.state,self.counter),end='') 

t1=[
	['Hans', 'Mueller', 'Hamburg' , 'Postweg', 8], 
	['Klaus', 'Meier', 'Hamburg' , 'Feldplatz', 5], 
	['Klaus', 'Schulze', 'Berlin' , 'Burgallee', 3], 
]

t2=[
	['Hins', 'Mueller', 'Hamburg' , 'Postweg', 8], 
	['Klaus', 'Meier', 'Hamburg' , 'Feldplatz', 5], 
	['Klaus', 'Schulze', 'Berlin' , 'Burgallee', 3], 
]

t3=[
	['Hans', 'Mueller', 'Hamburg' , 'Postweg', 8]
]

t4=[
	['Hins', 'Mueller', 'Hamburg' , 'Postweg', 8]
]

counter=1

def insertTable(table, rowDt, colDt, splitPoint, state):
	global counter
	for row in table:
		rowWidth=len(row)
		actRowDt=rowDt
		actColDt=colDt
		rowHash=""
		colHash=""
		for key, val in enumerate(row):
			if key == rowWidth-1:
				rowEndPoint=actRowDt.getEndPoint(colHash) #remember: rows gets colhashes & vice versa
				colEndPoint=actColDt.getEndPoint(rowHash)
				if rowEndPoint == None and colEndPoint==None:
					newEndPoint=TabDiff(None,state)
					actRowDt.setEndPoint(newEndPoint,colHash)
					actColDt.setEndPoint(newEndPoint,rowHash)
				else:
					if rowEndPoint == None:
						newEndPoint=colEndPoint
						actRowDt.setEndPoint(newEndPoint,colHash)
					else:
						newEndPoint=rowEndPoint
						actColDt.setEndPoint(newEndPoint,rowHash)
				
				newEndPoint.MakeValue(val,actRowDt, actColDt,state,counter)
				counter+=1
			else:
				if key < splitPoint:
					actRowDt=actRowDt.add(val,state)
					rowHash+=":"+val
				else:
					actColDt=actColDt.add(val,state)
					colHash+=":"+val
		
rowTd=TabDiff(None,False)
colTd=TabDiff(None,False)
	
insertTable(t1,rowTd,colTd,2,False)	
insertTable(t2,rowTd,colTd,2,True)	
#insertTable(t3,rowTd,colTd,2,False)	
#insertTable(t4,rowTd,colTd,2,True)	
print("Start------>")
rowTd.pprint()
print()
colTd.pprint()
print()

printArray={}
maxX=0
maxY=0

def printfunction(value,px,py,xDirection,blocksize):
	global printArray
	global maxX
	global maxY
	print("print:",value,px,py,xDirection,blocksize)
	try:
		printArray[px]
	except:
		printArray[px]={}
	printArray[px][py]=value
	print("gespeichert:",printArray[px][py])
	if maxX<px:
		maxX=px
	if maxY<py:
		maxY=py

rowDepth=rowTd.depth(1)
colDepth=colTd.depth(1)
print("rowDepth",rowDepth)
print("colDepth",colDepth)
print("y-size:{0}".format(rowTd.calPrintCoords(colDepth,0,True)))
print("x-size:{0}".format(colTd.calPrintCoords(rowDepth,0,False)))
rowTd.fillPrintGrid( colDepth, True, printfunction)
colTd.fillPrintGrid( rowDepth, False, printfunction)

for x in range(maxX+1):
	for y in range(maxY+1):
		try:
			print(printArray[x][y],end='')
		except:
			pass
		print("\t",end='')
		#print(" # ",end='')
	print()
