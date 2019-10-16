from pprint import pprint
import enum 

# creating enumerations using class 
class States(enum.Enum): 
	old = 0
	unchanged = 1
	changed = 2
	new = 3

class pyvoSheet:
	def __init__(self, name, table, style):
		self.name = name
		self.table = table
		self.style = style

	def __repr__(self):
		return {'name':self.name}

	def __str__(self):
		return 'pyvoSheet(name='+self.name+ ')'

class PyvotabElement(dict):

	def __init__(self, pyvotab, parent, isNew, sourceID, debug ):
		self.parent = parent
		self.dimension = 0
		self.sourceID = sourceID
		self.oldValue = 'NaN'
		self.newValue = 'NaN'
		self.pyvotab = pyvotab
		self.debug = debug
		# 0= old, 1= unchanged, 2 = new
		if not isNew:
			self.changeState = States.old
		else:
			self.changeState = States.new

	def increaseDimension(self):
		self.dimension += 1
		if self.parent:
			self.parent.increaseDimension()

	def validateChangeState(self, isNew):
		''' recalculates the changeState
		'''

		if self.changeState == States.unchanged:  # signals old and new
			return
		# 0= old, 1= unchanged, 2 = new
		if not isNew:
			newChangeState = States.old
		else:
			newChangeState = States.new
		if self.changeState != newChangeState:
			print("changeState change:", self.changeState, newChangeState)
			self.changeState = States.unchanged  # marks

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
			self[value] = PyvotabElement(self.pyvotab,self, isNew, sourceID, self.debug)
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
				self.changeState = States.new
			else:
				self.changeState = States.unchanged
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
		else:
			self.printX = startCoord

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
		
		if self.debug:
			value = "'{0}|{1}' ({2})".format(
				self.oldValue, self.newValue, self.changeState)
		else:
			value = self.newValue
		this_style=self.sourceID
		if self.changeState == States.old:
			this_style = self.pyvotab.old_style
		if self.changeState == States.new:
			this_style = self.pyvotab.new_style
		# to have some space for the heading names, we move the value cells 1 row downwards (self.printX + 1)
		fillFunction(value, self.printX + 1, self.printY,
					 xDirection, 1, this_style)

	def fillPrintGrid(self, multiplier, xDirection, fillFunction):
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
				this_style = self[index].sourceID
				if self[index].changeState == States.old:
					this_style = self.pyvotab.old_style
				if self[index].changeState == States.new:
					this_style = self.pyvotab.new_style
				if self.debug:
					value = "'{0}' ({1}) {2}".format(index, self[index].get_changeState(),self[index].blockSize)
				else:
					value = index

				if xDirection:
					fillFunction(
						value, self.level, self[index].startCoord, xDirection, self[index].blockSize, this_style)
						# in case we have a multiple cell span, we need to set some empty filler
					for i in range(1,self[index].blockSize):
						fillFunction(
							None, self.level, self[index].startCoord+i, xDirection, self[index].blockSize, this_style)

				else:
					fillFunction(
					# to have some space for the heading names, we move the value cells 1 row downwards (self.printX + 1)

						value, self[index].startCoord + 1, self.level , xDirection, self[index].blockSize, this_style)
						# in case we have a multiple cell span, we need to set some empty filler
					for i in range(1,self[index].blockSize):
						fillFunction(
							None, self[index].startCoord + 1 +i , self.level, xDirection, self[index].blockSize, this_style)

				self[index].fillPrintGrid(
					multiplier, xDirection, fillFunction)

	def pprint(self):
		''' debug print

		'''

		if self:
			for key, value in self.items():
				print("{{'{0}'".format(hex(id(value))), end='')
				if value.changeState == States.old:
					print("-", end="")
				if value.changeState == States.new:
					print("+", end="")
				print(": ", end='')
				value.pprint()
				print('}} ', end='')
		else:
			print("<{0}|{1}> {2}".format(self.oldValue,
										 self.newValue, self.changeState), end='')

class SingleTab:
	def __init__( self, headers, old_style, new_style, change_style,row_header_style, col_header_style, debug):
		'''
		Creates a SingleTab object, representing a single output table

		Parameters
		----------
		header: dict
			contains the rows and cols header descriptions
		old_style,
		new_style,
		change_style,
		row_header_style,
		col_header_style : Object
			The style objects defines how the cells should be formated in the final table. These objects are not used or mofified 
			by pyvotab at all, there are only passed through into the result table to allow the user to define the wanted formats
		'''

		self.rowTd = PyvotabElement(self,None, False, -1, debug)
		self.colTd = PyvotabElement(self,None, False, -1, debug)
		self.old_style = old_style
		self.new_style = new_style
		self.row_header_style = row_header_style
		self.col_header_style = col_header_style
		self.change_style = change_style
		self.headers = headers
		self.debug = debug

	def headerrows(self):
		'''returns the number of cells  on top of the resulting table, before the data cells starts

		'''

		return self.rowTd.depth(1)

	def headercols(self):
		'''returns the number of cells  on the left side of the resulting table, before the data cells starts

		'''

		return self.colTd.depth(1)

	def layoutGrid(self):
		''' starts the process to transform the data tree into their table position and sizes

		'''

		self.rowTd.calPrintCoords(self.colTd.depth(1), 0, True)
		self.colTd.calPrintCoords(self.rowTd.depth(1), 0, False)

	def getPrintDict(self):
		''' translates the internal data tree structure with it's calculated x/y positions (by layoutgrid()) into its x/y table representation for printout

		'''
		rowDepth = self.headerrows()
		colDepth = self.headercols()
		self.ptdict = ptPrintDict()
		for index in range(len(self.headers['cols'])):
			self.printfunction(self.headers['cols'][index], colDepth , index , False, 1, self.col_header_style)
		for index in range(len(self.headers['rows'])):
			self.printfunction(self.headers['rows'][index], index , rowDepth-1 , False, 1, self.row_header_style)
		self.rowTd.fillPrintGrid(1, True, self.printfunction)
		self.colTd.fillPrintGrid(1, False, self.printfunction)


	def printfunction(self, value, px, py, xDirection, blocksize, style):
		'''
			storage function to fill the result ptPrintDict- Table by the x/y coords, the value, the cell direction, the row/col span and the wanted style
		'''

		try:
			self.ptdict[px]
		except:
			self.ptdict[px] = {}

		if value:
			self.ptdict[px][py] = {
			"value": value, "style": style, "size": blocksize, "xDir": xDirection}
		else:
			self.ptdict[px][py] = None
		if self.ptdict.xSize < px:
			self.ptdict.xSize = px
		if self.ptdict.ySize < py:
			self.ptdict.ySize = py

class Pyvotab:

	def __init__(self, old_style, new_style, change_style, row_header_style, col_header_style, page, layout,debug= False):
		'''
		Creates a Pyvotab object


		Parameters
		----------
		
		old_style,
		new_style,
		change_style,
		row_header_style,
		col_header_style : Object
			The style objects defines how the cells should be formated in the final table. These objects are not used or mofified 
			by pyvotab at all, there are only passed through into the result table to allow the user to define the wanted formats
		page: int or string
				If int, it's define the column which should be used as page. If string, it's handled as single page, refered py the page name
		layout : dict
			contains the layout parameters, which are
					as result there's a array of tables calculated, indexed by page names
				rows: Array of int
					defines the column indices which shall be used as rows
				cols: Array of int
					defines the column indices which shall be used as columns
				filter: 
					no idea for now, reserved for later extensions :-)
				pivot: string
					defines the pivot calculation method. 'plain' is the standard value for no special operation
		'''
		
		self.result_tables={}
		self.old_style = old_style
		self.new_style = new_style
		self.change_style = change_style
		self.row_header_style = row_header_style
		self.col_header_style = col_header_style
		self.page = page
		self.layout = layout
		self.debug = debug


	def InsertTable(self, table, changeState, sourceID):



		'''
		transforms a "csv-like" table input into the internal tree representation.

		Into a data row, the first cells represents the row values, the remaining ones
		represent the col content, the last value is the table cell content itself.

		The splitPoint value defines the row array index where the row values ends
		and the col values begins

		Parameters
		----------
		table : list
			array of data rows. the first row contains the column names 
		changeState : bool
			True, if that table is seen as a new input, otherways seen as old, original data
		sourceID
			identifier of the data source. Not used by program, but maintained as reference
			to tell the user where the resulting table cells are coming from
		'''
		header_names=table[0]
		headers={'rows':[],'cols':[]}
		for index in self.layout['rows']:
			headers['rows'].append( str( header_names[ index - 1 ] ) )
		for index in self.layout['cols']:
			headers['cols'].append( str( header_names[ index - 1 ] ) )

		for row in table[1:]:
			rowWidth = len(row)
			rowHash = ""
			colHash = ""
			# is the page an int or a string, so single page or multipage
			if type(self.page) is int:
				page_name=row[self.page-1]
			else:
				page_name=str(self.page)
			# does that page table already exist?
			if not page_name in self.result_tables:
				self.result_tables[page_name]=SingleTab(headers, self.old_style, self.new_style, self.change_style,self.row_header_style, self.col_header_style, self.debug )
			this_tab=self.result_tables[page_name]
			actRowDt = this_tab.rowTd
			actColDt = this_tab.colTd
			for index in self.layout['rows']:
				val=str(row[index-1])
				actRowDt = actRowDt.add(val, changeState, sourceID)
				rowHash += ":"+val
			for index in self.layout['cols']:
				val=str(row[index-1])
				actColDt = actColDt.add(val, changeState, sourceID)
				colHash += ":"+val
			# store the value as endpoint
			# remember: rows gets colhashes & vice versa
			rowEndPoint = actRowDt.getEndPoint(colHash)
			colEndPoint = actColDt.getEndPoint(rowHash)
			if rowEndPoint == None and colEndPoint == None:
				newEndPoint = PyvotabElement(self, None, changeState, sourceID,self.debug)
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
				str(row[self.layout['val']-1]), actRowDt, actColDt, changeState)

	def getPrintDict(self):
		''' translates the internal data tree structure with it's calculated x/y positions (by layoutgrid()) into its x/y table representation for printout

		'''

		result={}
		for page_name, stab in self.result_tables.items():
			stab.layoutGrid()
			stab.getPrintDict()
			result[page_name]=stab.ptdict
		pyvoSheet_results=[]
		for page_name in sorted(result.keys()):
			pyvoSheet_results.append(pyvoSheet(page_name, result[page_name],"white"))
		return pyvoSheet_results

class ptPrintDict(dict):
	'''
	This dictionary represents the table field results stored by their x/y coordinates
	'''
	xSize = 0
	ySize = 0

