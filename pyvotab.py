from pprint import pprint
import enum 
from urllib.parse import urlparse, parse_qs

# creating enumerations using class 
class States(enum.Enum): 
	old = 0
	unchanged = 1
	changed = 2
	new = 3

class pyvoSheet:
	def __init__(self, name, table, style, template):
		self.name = name
		self.table = table
		self.style = style
		self.template = template

	def __repr__(self):
		return {'name':self.name}

	def __str__(self):
		return 'pyvoSheet(name='+self.name+ ')'

class PyvotabElement(dict):

	def __init__(self, value, pyvotab, parent, isNew, source_style, debug ):
		self.parent = parent
		self.dimension = 0
		self.source_style = source_style
		self.value = value
		self.pyvotab = pyvotab
		self.debug = debug
		# 0= old, 1= unchanged, 2 = new
		if not isNew:
			self.change_state = States.old
		else:
			self.change_state = States.new

	def increaseDimension(self):
		self.dimension += 1
		if self.parent:
			self.parent.increaseDimension()

	def set_change_state(self, child_state):
		''' recalculates the change_state
		'''

		if self.change_state == States.changed:  # there's no more left to set
			return
		if self.change_state==States.old and child_state==States.unchanged:
			self.change_state=States.unchanged
		if self.change_state != child_state:
			print("change_state change:", self.change_state, child_state)
			self.change_state = States.changed
		if self.parent:
			self.parent.set_change_state(self.change_state)

	def add(self, value, isNew, source_style):
		''' set value and calculates old/new/unchanged stage

		Parameters
		----------
		value : scalar
			value to set
		isNew : bool
			flag if this value is been seen as old or new
		source_style
			identifier of the data source. Not used by program, but maintained as reference
			to tell the user where the resulting table cells are coming from
		'''
		self.source_style = source_style
		self.increaseDimension()
		if not value in self:
			self[value] = PyvotabElement(value,self.pyvotab,self, isNew, source_style, self.debug)
		return self[value]

	def MakeValue(self, value, rowDt, colDt, isNew):
		''' set value and calculates old/new/unchanged stage

		Parameters
		----------
		value : scalar
			value to set ,use 'None' to mark an initial endpoint
		rowDt : Pyvotab
			reference to the row Pyvotab table
		colDt : Pyvotab
			reference to the col Pyvotab table
		isNew : bool
			flag if this value is been seen as old or new
		'''

		self.rowDt = rowDt
		self.colDt = colDt
		print("change_state change state from:", self.change_state, "for value ", value)
		if self.value:
			if self.change_state==States.old and isNew:
				self.change_state=States.unchanged
			if self.value != value:
				self.change_state = States.changed
		rowDt.set_change_state(self.change_state)
		colDt.set_change_state(self.change_state)
		self.value = value

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
		print("Make an Endpoint")

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
			print("endpunkt gefunden in calPrintCoords")
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
			value = "'{0}' ({1})".format(
				self.value, self.change_state)
		else:
			value = self.value
		this_style=self.source_style
		if self.change_state == States.old:
			this_style = self.pyvotab.old_style
		if self.change_state == States.changed:
			this_style = self.pyvotab.change_style
		if self.change_state == States.new:
			this_style = self.pyvotab.new_style
		# to have some space for the heading names, we move the value cells 1 row downwards (self.printY + 1)
		fillFunction(value, self.printX , self.printY+1,
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
				this_style = self[index].source_style
				if self[index].change_state == States.old:
					this_style = self.pyvotab.old_style
				if self[index].change_state == States.changed:
					this_style = self.pyvotab.change_style
				if self[index].change_state == States.new:
					this_style = self.pyvotab.new_style
				if self.debug:
					value = "'{0}' ({1}) {2}".format(index, self[index].change_state,self[index].blockSize)
				else:
					value = index

				if xDirection:
					fillFunction(
					# to have some space for the heading names, we move the value cells 1 row downwards (self[index].startCoord +1)
						value, self.level, self[index].startCoord +1, xDirection, self[index].blockSize, this_style)
						# in case we have a multiple cell span, we need to set some empty filler
					for i in range(1,self[index].blockSize):
						fillFunction(
							None, self.level, self[index].startCoord+i+1, xDirection, self[index].blockSize, this_style)

				else:
					fillFunction(
						value, self[index].startCoord , self.level , xDirection, self[index].blockSize, this_style)
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
			for value in self.values():
				print("{{'{0}'".format(hex(id(value))), end='')
				if value.change_state == States.old:
					print("-", end="")
				if value.change_state == States.new:
					print("+", end="")
				print(": ", end='')
				value.pprint()
				print('}} ', end='')
		else:
			print("<{0}> {1}".format(self.value, self.change_state), end='')

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

		self.rowTd = PyvotabElement('row',self,None, False, -1, debug)
		self.colTd = PyvotabElement('col',self,None, False, -1, debug)
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
			print("write col header {0} to x:{1} y:{2}".format(self.headers['cols'][index], colDepth-1 , index ))
			self.printfunction(self.headers['cols'][index], colDepth-1 , index , False, 1, self.col_header_style)
		for index in range(len(self.headers['rows'])):
			print("write row header {0} to x:{1} y:{2}".format(self.headers['rows'][index], index , rowDepth))
			self.printfunction(self.headers['rows'][index], index , rowDepth , False, 1, self.row_header_style)
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
		if self.ptdict.xSize < px + 1:
			self.ptdict.xSize = px +1
		if self.ptdict.ySize < py + 1:
			self.ptdict.ySize = py +1

class Pyvotab:

	def __init__(self, old_style, new_style, change_style, row_header_style, col_header_style, layout, debug= False):
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
		layout : dict or string
			contains the layout parameters, either in an url coded string or an dict. The parameter are
				page: int or string
						If int, it's define the column which should be used as page. If string, it's handled as single page, refered py the page name
				source: string
					name of the excel sheet which should be used as data table source, can be read by get_source_name(). Only needed when handle e.g. excel files
					not used by pivotab itself
					Optional, default pt.1
				template: string
					name of an excel table sheet which should be used as empty but pre-formated sheet to fill the data in
					not used by pivotab itself
					optional, default is to create an fresh sheet
				newname: string
					definition of how the output page name shall be formed. Inside of newname a $ acts as place holder, so newname = "page_$" and original page name of "org" becomes "page_orig"
					Optional, default $
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
		if type(layout) is str:
			print("layout is string..",layout)
			layout=self.resolve_parameter_url(layout)
		self.page = self.get_url_parameter(layout,"page","default")
		try: # is the page a string or an integer representation? if yes, convert it to int
			self.page=int(self.page)
		except:
			pass
		self.source = self.get_url_parameter(layout,"source","pt.1")
		self.newname = self.get_url_parameter(layout,"newname","$")
		self.template = self.get_url_parameter(layout,"template",None)
		# transform the parameter string "1,2,3" into a int array [1 , 2 , 3]

		layout['rows'] = self.split_int_string( self.get_url_parameter(layout,"rows",[]))
		layout['cols'] = self.split_int_string( self.get_url_parameter(layout,"cols",[]))
		layout['val'] = int(self.get_url_parameter(layout,"val",1))
		self.layout = layout
		self.debug = debug

	def split_int_string(self,list_or_string):
		''' list_or_string is either a int list or a comma sepated string with integers

		RETURN
			int list
		'''
		if type(list_or_string) is str:
			return [int(v) for v in list_or_string.split(',')]
		else:
			return list_or_string

	def get_source_name(self):
		return self.newname


	def InsertTable(self, table, change_state, source_style):



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
		change_state : bool
			True, if that table is seen as a new input, otherways seen as old, original data
		source_style
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
				actRowDt = actRowDt.add(val, change_state, source_style)
				rowHash += ":"+val
			for index in self.layout['cols']:
				val=str(row[index-1])
				actColDt = actColDt.add(val, change_state, source_style)
				colHash += ":"+val
			# store the value as endpoint
			# remember: rows gets colhashes & vice versa
			rowEndPoint = actRowDt.getEndPoint(colHash)
			colEndPoint = actColDt.getEndPoint(rowHash)
			if rowEndPoint == None and colEndPoint == None:
				newEndPoint = PyvotabElement(None,self, None, change_state, source_style,self.debug)
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
				str(row[self.layout['val']-1]), actRowDt, actColDt, change_state)

	def getPrintDict(self):
		''' translates the internal data tree structure with it's calculated x/y positions (by layoutgrid()) into its x/y table representation for printout

		'''

		result={}
		for page_name, stab in self.result_tables.items():
			stab.layoutGrid()
			stab.getPrintDict()
			result[page_name]=stab.ptdict
		pyvoSheet_results=[]
		print(repr(result.keys()))
		for page_name in sorted(result.keys()):
			pyvoSheet_results.append(pyvoSheet(self.newname.replace('$',page_name), result[page_name],"white", self.template))
			print("Remember: correct sheet style not implemented yet")
		return pyvoSheet_results

	def resolve_parameter_url(self, url):
		'''does the inital parsing of the format url

		Parameters
		----------
		url : string
			url string as desribed in https://docs.python.org/3/library/urllib.parse.html

		Returns
		-------
		res: parameter dictionary
		'''
		parsed_url=urlparse(url)
		layout_with_array=parse_qs(parsed_url.query)
		layout={ k:v[0] for k,v in layout_with_array.items()}
		return layout

	def get_url_parameter(self, param_object,param_name,default_value):
		'''get parameters 

		Parameters
		----------
		url : string
			url string as desribed in https://docs.python.org/3/library/urllib.parse.html

		Returns
		-------
		res: ParseResult object
		'''
		print (param_object)
		if not param_name in param_object:
			return default_value
		else:
			return param_object[param_name]


class ptPrintDict(dict):
	'''
	This dictionary represents the table field results stored by their x/y coordinates
	'''
	xSize = 0
	ySize = 0


