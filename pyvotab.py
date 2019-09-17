from pprint import pprint


class PyvotabElement(dict):

	def __init__(self, parent, isNew, sourceID):
		self.parent = parent
		self.dimension = 0
		self.sourceID = sourceID
		self.oldValue = 'NaN'
		self.newValue = 'NaN'
		# 0= old, 1= unchanged, 2 = new
		if not isNew:
			self.changeState = 0
		else:
			self.changeState = 2

	def increaseDimension(self):
		self.dimension += 1
		if self.parent:
			self.parent.increaseDimension()

	def validateChangeState(self, isNew):
		''' recalculates the changeState
		'''

		if self.changeState == 1:  # signals old and new
			return
		# 0= old, 1= unchanged, 2 = new
		if not isNew:
			newChangeState = 0
		else:
			newChangeState = 2
		if self.changeState != newChangeState:
			print("changeState change:", self.changeState, newChangeState)
			self.changeState = 1  # marks

	def get_changeState(self):
		''' returns node changeState '''
		return self.changeState

	def add(self, value, isNew, sourceID):
		''' set value and calculates old/new/unchanged stage

		Parameters
		----------
		value : scalar
			value to set
		isNew : bool
			flag if this value is been seen as old or new
		sourceID
			identifier of the data source. Not used by program, but maintained as reference
			to tell the user where the resulting table cells are coming from
		'''
		self.validateChangeState(isNew)
		if self.sourceID == -1:  # it's one of the inital elements
			self.sourceID = sourceID
		self.increaseDimension()
		if not value in self:
			self[value] = PyvotabElement(self, isNew, sourceID)
			return self[value]
		else:
			self[value].validateChangeState(isNew)
			return self[value]

	def MakeValue(self, value, rowDt, colDt, isNew):
		''' set value and calculates old/new/unchanged stage

		Parameters
		----------
		value : scalar
			value to set
		rowDt : Pyvotab
			reference to the row Pyvotab table
		colDt : Pyvotab
			reference to the col Pyvotab table
		isNew : bool
			flag if this value is been seen as old or new
		'''

		self.rowDt = rowDt
		self.colDt = colDt
		if isNew:
			self.newValue = value
			print("changeState change state from:", self.changeState, "for value ", value)
			if self.oldValue != value:
				self.changeState = 2
			else:
				self.changeState = 1
			print("changeState change state to:", self.changeState)
		else:
			self.oldValue = value

	def getEndPoint(self, myhash):
		''' returns value cell object, if is endpoint, otherways None

		Parameters
		----------
		myhash : string
			hash representing the aligned row/col endpoint
		'''

		try:
			return self[hash(myhash)]
		except:
			return None

	def setEndPoint(self, newEndPoint, myhash):
		'''
		defines a node as an end point, means as bottom/rightmost object in the row/column header.

		Stores the hash of the aligned row/col endpoint 

		Parameters
		----------
		newEndPoint : object
			value cell object, containing all data about a value cell
		myhash : string
			hash representing the aligned row/col endpoint
		'''


		self[hash(myhash)] = newEndPoint
		self.isEndStup = True

	def setPrintCoords(self, startCoord, level, xDirection):
		'''
		set the final coordinate of a node 

		Parameters
		----------
		startCoord : int
			top/leftmost coordinate of that node, given by the parent nodes
		level : int
			entry level of that node
		xDirection : bool
			tells, if the object is located in the column header (True) or row header (False)
		'''


		if xDirection:
			self.printY = startCoord
			print("set Y {0} for {1}".format(startCoord, self.oldValue))
		else:
			self.printX = startCoord
			print("set X {0} for {1}".format(startCoord, self.oldValue))

	def calPrintCoords(self, startCoord, level, xDirection):
		'''
		calculates the final coordinate of a node 

		Parameters
		----------
		startCoord : int
			top/leftmost coordinate of that node, given by the parent nodes
		level : int
			entry level of that node
		xDirection : bool
			tells, if the object is located in the column header (True) or row header (False)
		'''

		self.startCoord = startCoord
		self.blockSize = startCoord
		self.level = level
		isEnd = False
		try:
			self.isEndStup
			isEnd = True
		except:  # this is no endstup
			startCoord -= 1  # reduce it, so that the return value is the same as the start in case this element and its subs covers only 1 row/column
		for index in sorted(self.keys()):
			if isEnd:
				self[index].setPrintCoords(startCoord, level, xDirection)
			else:
				startCoord += 1
				startCoord = self[index].calPrintCoords(
					startCoord, level+1, xDirection)
		self.blockSize = startCoord-self.blockSize+1
		return startCoord

	def depth(self, actLevel):
		'''
		calculates the child node depth of a node

		Parameters
		----------
		actLevel : int
			entry level of that node
		'''

		resultLevel = actLevel
		for index in self:
			try:
				self[index].isEndStup
				return actLevel
			except:
				newLevel = self[index].depth(actLevel+1)
				if newLevel > resultLevel:
					resultLevel = newLevel
		return resultLevel

	def fillPrintGridValue(self, multiplier, xDirection, fillFunction):
		'''
		calculates output table content and dimensions for a single cell

		Parameters
		----------
		multiplier : int
			tells, about how many cells the object is extended (based on the number of child object)
		xDirection : bool
			tells, if the object is located in the column header (True) or row header (False)
		fillFunction : function
			function which copies the content into the custom table
		'''
		
		value = "'{0}|{1}' ({2})".format(
				self.oldValue, self.newValue, self.changeState)
		fillFunction(value, self.printX, self.printY,
					 xDirection, 1, self.sourceID)

	def fillPrintGrid(self, multiplier, xDirection, fillFunction, old_style):
		'''
		calculates output table content and dimensions

		Parameters
		----------
		multiplier : int
			tells, about how many cells the object is extended (based on the number of child object)
		xDirection : bool
			tells, if the object is located in the column header (True) or row header (False)
		fillFunction : function
			function which copies the content into the custom table
		old_style
			style object to "style" old content
		'''

		for index in sorted(self.keys()):
			isEnd = False
			try:
				self.isEndStup
				isEnd = True
			except:
				pass
			if isEnd:
				self[index].fillPrintGridValue(
					multiplier, xDirection, fillFunction)
			else:
				# determine correct style based on, if the element is old or not
				if self[index].changeState == 0:
					this_style = old_style
				else:
					this_style = self[index].sourceID
				value = "'{0}' ({1})".format(index, self[index].get_changeState())

				if xDirection:
					fillFunction(
						value, self.level, self[index].startCoord, xDirection, self.blockSize, this_style)
				else:
					fillFunction(
						value, self[index].startCoord, self.level, xDirection, self.blockSize, this_style)
				self[index].fillPrintGrid(
					multiplier, xDirection, fillFunction, old_style)

	def pprint(self):
		''' debug print

		'''

		if self:
			for key, value in self.items():
				print("{{'{0}'".format(hex(id(value))), end='')
				if value.changeState == 0:
					print("-", end="")
				if value.changeState == 2:
					print("+", end="")
				print(": ", end='')
				value.pprint()
				print('}} ', end='')
		else:
			print("<{0}|{1}> {2}".format(self.oldValue,
										 self.newValue, self.changeState), end='')


class Pyvotab:

	def __init__(self, old_style, new_style):
		self.rowTd = PyvotabElement(None, False, -1)
		self.colTd = PyvotabElement(None, False, -1)
		self.old_style = old_style
		self.new_style = new_style

	def headerrows(self):
		'''returns the number of cells  on top of the resulting table, before the data cells starts

		'''

		return self.rowTd.depth(1)

	def headercols(self):
		'''returns the number of cells  on the left side of the resulting table, before the data cells starts

		'''

		return self.colTd.depth(1)

	def insertTable(self, table, splitPoint, changeState, sourceID):
		'''
		transforms a "csv-like" table input into the internal tree representation.

		Into a data row, the first cells represents the row values, the remaining ones
		represent the col content, the last value is the table cell content itself.

		The splitPoint value defines the row array index where the row values ends
		and the col values begins

		Parameters
		----------
		table : list
			array of data rows
		splitPoint : int
		changeState : bool
			True, if that table is seen as a new input, otherways seen as old, original data
		sourceID
			identifier of the data source. Not used by program, but maintained as reference
			to tell the user where the resulting table cells are coming from
		'''

		for row in table:
			rowWidth = len(row)
			actRowDt = self.rowTd
			actColDt = self.colTd
			rowHash = ""
			colHash = ""
			for key, val in enumerate(row):
				if key == rowWidth-1:
					# remember: rows gets colhashes & vice versa
					rowEndPoint = actRowDt.getEndPoint(colHash)
					colEndPoint = actColDt.getEndPoint(rowHash)
					if rowEndPoint == None and colEndPoint == None:
						newEndPoint = PyvotabElement(None, changeState, sourceID)
						actRowDt.setEndPoint(newEndPoint, colHash)
						actColDt.setEndPoint(newEndPoint, rowHash)
					else:
						if rowEndPoint == None:
							newEndPoint = colEndPoint
							actRowDt.setEndPoint(newEndPoint, colHash)
						else:
							newEndPoint = rowEndPoint
							actColDt.setEndPoint(newEndPoint, rowHash)

					newEndPoint.MakeValue(
						val, actRowDt, actColDt, changeState)
				else:
					if key < splitPoint:
						actRowDt = actRowDt.add(val, changeState, sourceID)
						rowHash += ":"+val
					else:
						actColDt = actColDt.add(val, changeState, sourceID)
						colHash += ":"+val

	def layoutGrid(self):
		''' starts the process to transform the data tree into their table position and sizes

		'''

		self.rowTd.calPrintCoords(self.colTd.depth(1), 0, True)
		self.colTd.calPrintCoords(self.rowTd.depth(1), 0, False)

	def getPrintDict(self):
		''' translates the internal data tree structure with it's calculated x/y positions (by layoutgrid()) into its x/y table representation for printout

		'''

		self.ptdict = ptPrintDict()
		self.rowTd.fillPrintGrid(1, True, self.printfunction, self.old_style)
		self.colTd.fillPrintGrid(1, False, self.printfunction, self.old_style)
		return self.ptdict

	def printfunction(self, value, px, py, xDirection, blocksize, style):
		'''
			storage function to fill the result ptPrintDict- Table by the x/y coords, the value, the cell direction, the row/col span and the wanted style
		'''

		print("print:", value, px, py, xDirection, blocksize)
		try:
			self.ptdict[px]
		except:
			self.ptdict[px] = {}
		self.ptdict[px][py] = {
			"value": value, "style": style, "size": blocksize, "xDir": xDirection}
		print("gespeichert:", self.ptdict[px][py])
		if self.ptdict.xSize < px:
			self.ptdict.xSize = px
		if self.ptdict.ySize < py:
			self.ptdict.ySize = py


class ptPrintDict(dict):
	'''
	This dictionary represents the table field results stored by their x/y coordinates
	'''
	xSize = 0
	ySize = 0

