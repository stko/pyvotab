
//https://examples.javacodegeeks.com/core-java/net/url/parse-url-example/
import java.net.MalformedURLException;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.Collections;
import java.util.ArrayList;
import java.util.List;



// creating enumerations using class 
enum States{ 
	old,
	unchanged,
	changed,
	newstate
}

public class PyvoSheet{

	String name;
	PivoTab table;
	Object style;
	String template;

	PyvoSheet(String name, PivoTab table, Object style, String template){
		this.name = name;
		this.table = table;
		this.style = style;
		this.template = template;
	}

	String toString(){
		return 'pyvoSheet(name='+this.name+ ')'
	}
	

    public interface FillFunction 
    {
        public void fillFunction(Object data);
    }


class PyvotabElement extends HashMap<String, PyvotabElement>{
	PyvotabElement parent;
	int dimension;
	Object source_style;
	String value;
	Pyvotab pyvotab;
	boolean debug;
	States change_state;
	PyvotabElement rowDt;
	PyvotabElement colDt;
	boolean isEndStup;
	int printY;
	int printX;
	int startCoord;
	int blockSize;
	int level;

	PyvotabElement ( String value, Pyvotab pyvotab, PyvotabElement parent,boolean isNew, Object source_style, boolean debug ){
		this.parent = parent;
		this.dimension = 0;
		this.source_style = source_style;
		this.value = value;
		this.pyvotab = pyvotab;
		this.debug = debug;
		if (! isNew){
			this.change_state = States.old;
		}else{
			this.change_state = States.newstate;
		}
	}

	void increaseDimension(){
		this.dimension += 1;
		if (this.parent!=null){
			this.parent.increaseDimension();
		}
	}

	void set_change_state(States child_state){
		/* recalculates the change_state
		*/

		if (this.change_state == States.changed) { // there's no more left to set
			return;
		}
		if (this.change_state==States.old && child_state==States.unchanged){
			this.change_state=States.unchanged;
		}
		if (this.change_state != child_state){
			System.out.printf("change_state change:%d %d" ,this.change_state, child_state);
			this.change_state = States.changed;
		}
		if (this.parent!=null){
			this.parent.set_change_state(this.change_state);
		}
	}

	PyvotabElement add(String value, boolean isNew, Object source_style){
		/* set value and calculates old/new/unchanged stage

		Parameters
		----------
		value : scalar
			value to set
		isNew : bool
			flag if this value is been seen as old or new
		source_style
			identifier of the data source. Not used by program, but maintained as reference
			to tell the user where the resulting table cells are coming from
		/*/
		this.source_style = source_style;
		this.increaseDimension();
		if (!this.containsKey(value)){
			this.put(value, PyvotabElement(value,this.pyvotab,this, isNew, source_style, this.debug));
		}
		return this.get(value);
	}

	void MakeValue(String value, PyvotabElement rowDt, PyvotabElement colDt, boolean isNew){
		/* set value and calculates old/new/unchanged stage

		Parameters
		----------
		value : scalar
			value to set ,use 'null' to mark an initial endpoint
		rowDt : Pyvotab
			reference to the row Pyvotab table
		colDt : Pyvotab
			reference to the col Pyvotab table
		isNew : bool
			flag if this value is been seen as old or new
		*/

		this.rowDt = rowDt;
		this.colDt = colDt;
		System.out.printf("change_state change state from: %d %d", this.change_state, "for value ", value);
		if (this.value!=null){
			if (this.change_state==States.old && isNew){
				this.change_state=States.unchanged;
			}
			if (this.value != value){
				this.change_state = States.changed;
			}
		}
		rowDt.set_change_state(this.change_state);
		colDt.set_change_state(this.change_state);
		this.value = value;
	}

	PyvotabElement getEndPoint(String myhash){
		/* returns value cell object, if is endpoint, otherways null

		Parameters
		----------
		myhash : string
			hash representing the aligned row/col endpoint
		*/

		try{
			return this.get((myhash));
		}catch(){
			return null;
		}
	}

	void setEndPoint( PyvotabElement newEndPoint, String myhash){
		/*
		defines a node as an end point, means as bottom/rightmost object in the row/column header.

		Stores the hash of the aligned row/col endpoint 

		Parameters
		----------
		newEndPoint : object
			value cell object, containing all data about a value cell
		myhash : string
			hash representing the aligned row/col endpoint
		*/
		System.out.printf("Make an Endpoint");

		this.put(myhash, newEndPoint);
		this.isEndStup = true;
	}

	void setPrintCoords( int startCoord, int level, bool xDirection){
		/*
		set the final coordinate of a node 

		Parameters
		----------
		startCoord : int
			top/leftmost coordinate of that node, given by the parent nodes
		level : int
			entry level of that node
		xDirection : bool
			tells, if the object is located in the column header (True) or row header (False)
		*/


		if (xDirection){
			this.printY = startCoord;
		}else{
			this.printX = startCoord;
		}
	}

	int calPrintCoords(int startCoord, int level, bool xDirection){
		/*
		calculates the final coordinate of a node 

		Parameters
		----------
		startCoord : int
			top/leftmost coordinate of that node, given by the parent nodes
		level : int
			entry level of that node
		xDirection : bool
			tells, if the object is located in the column header (True) or row header (False)
		*/

		this.startCoord = startCoord;
		this.blockSize = startCoord;
		this.level = level;
		if (!this.isEndStup){
			startCoord -= 1;  // reduce it, so that the return value is the same as the start in case this element and its subs covers only 1 row/column
		}
		List<String> sortedKeys=new ArrayList(this.keySet());
		Collections.sort(sortedKeys);
		for (String index: sortedKeys){
			if (this.isEndStup){
				this.get(index).setPrintCoords(startCoord, level, xDirection);
			}else{
				startCoord += 1;
				startCoord = this.get(index).calPrintCoords(
					startCoord, level+1, xDirection);
			}
		}
		this.blockSize = startCoord-this.blockSize+1;
		return startCoord;
	}

	int depth( actLevel){
		/*
		calculates the child node depth of a node

		Parameters
		----------
		actLevel : int
			entry level of that node
		*/

		int resultLevel = actLevel;
		for (String index:  this){
			if(this.get( index).isEndStup){
				return actLevel;
			}else{
				newLevel = this.get(index).depth(actLevel+1);
				if (newLevel > resultLevel){
					resultLevel = newLevel;
				}
			}
		}
		return resultLevel;
	}

	void fillPrintGridValue( int multiplier, boolean xDirection, FillFunction fillFunction){
		/*
		calculates output table content and dimensions for a single cell

		Parameters
		----------
		multiplier : int
			tells, about how many cells the object is extended (based on the number of child object)
		xDirection : bool
			tells, if the object is located in the column header (True) or row header (False)
		fillFunction : function
			function which copies the content into the custom table
		*/
		String value;
		if (this.debug){
			value = String.format("'{0}' ({1})", this.value, this.change_state);
		}else{
			value = this.value;
		}
		Object this_style=this.source_style;
		if (this.change_state == States.old){
			this_style = this.pyvotab.old_style;
		}
		if (this.change_state == States.changed){
			this_style = this.pyvotab.change_style;
		}
		if (this.change_state == States.newstate){
			this_style = this.pyvotab.new_style;
		}
		// to have some space for the heading names, we move the value cells 1 row downwards (this.System.out.printfY + 1)
		fillfunction.fillFunction(value, this.printX , this.printY+1,
					 xDirection, 1, this_style);
	}

	void fillPrintfGrid( int multiplier, boolean xDirection, FillFunction fillFunction){
		/*
		calculates output table content and dimensions

		Parameters
		----------
		multiplier : int
			tells, about how many cells the object is extended (based on the number of child object)
		xDirection : bool
			tells, if the object is located in the column header (True) or row header (False)
		fillFunction : function
			function which copies the content into the custom table
		*/

		List<String> sortedKeys=new ArrayList(this.keySet());
		Collections.sort(sortedKeys);
		for (String index: sortedKeys){
			if (this.isEndStup){
				this.get(index).fillPrintGridValue(multiplier, xDirection, fillFunction);
			}else{
				// determine correct style based on, if the element is old or not
				Object this_style = this.get(index).source_style;
				if (this.get(index).change_state == States.old){
					this_style = this.pyvotab.old_style;
				}
				if (this.get(index).change_state == States.changed){
					this_style = this.pyvotab.change_style;
				}
				if (this.get(index).change_state == States.new){
					this_style = this.pyvotab.new_style
				
				}if (this.debug){
					value = String.format( "'{0}' ({1}) {2}",index, this.get(index).change_state,this.get(index).blockSize);
				}else{
					value = index;
				}
				if (xDirection){
				fillFunction.fillFunction(
					// to have some space for the heading names, we move the value cells 1 row downwards (this.get(index).startCoord +1)
						value, this.level, this.get(index).startCoord +1, xDirection, this.get(index).blockSize, this_style);
						// in case we have a multiple cell span, we need to set some empty filler
					for (int i=1; i < this.get(index).blockSize;i++){
						fillFunction.fillFunction(
							null, this.level, this.get(index).startCoord+i+1, xDirection, this.get(index).blockSize, this_style);
					}
				}else{
					fillFunction.fillFunction(
						value, this.get(index).startCoord , this.level , xDirection, this.get(index).blockSize, this_style);
						// in case we have a multiple cell span, we need to set some empty filler
					for (int i=1; i < this.get(index).blockSize;i++){
						fillFunction.fillFunction(
							null, this.get(index).startCoord + 1 +i , this.level, xDirection, this.get(index).blockSize, this_style);
				}
				this.get(index).fillPrintGrid(
					multiplier, xDirection, fillFunction);
			}
		}
	}

class SingleTab{
	PyvotabElement rowTd;
	PyvotabElement colTd;
	Object old_style;
	Object new_style;
	Object row_header_style;
	Object col_header_style;
	Object change_style;
	String [] headers;
	boolean debug;

	SingleTab( String [] headers, Object old_style, Object new_style, Object change_style, Object row_header_style, Object col_header_style, boolean debug){
		/*
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
		*/

		this.rowTd = PyvotabElement("row",this,null, false, -1, debug);
		this.colTd = PyvotabElement("col",this,null, False, -1, debug);
		this.old_style = old_style;
		this.new_style = new_style;
		this.row_header_style = row_header_style;
		this.col_header_style = col_header_style;
		this.change_style = change_style;
		this.headers = headers;
		this.debug = debug;
	}

	Object get_sheet_style(){
		PyvotabElement first_element = this.rowTd.entrySet().iterator().next().getValue();
 		States initial_change_state=first_element.change_state;
		Object default_style=first_element.source_style;
		for (PyvotabElement element : this.rowTd.getValues()){
			if (initial_change_state != element.change_state){
				initial_change_state=States.changed;
				break;
			}
		}
		if (initial_change_state!=States.changed){
			for (PyvotabElement element : this.colTd.getValues()){
				if (initial_change_state != element.change_state){
					initial_change_state=States.changed;
					break;
				}
			}
		}
		if (initial_change_state == States.old){
			return this.old_style;
		}
		if (initial_change_state == States.changed){
			return this.change_style;
		}
		if (initial_change_state == States.newstate){
			return this.new_style;
		}
		return default_style;
	}

	int headerrows(){
		/*returns the number of cells  on top of the resulting table, before the data cells starts

		*/

		return this.rowTd.depth(1);
	}

	int headercols(){
		/*returns the number of cells  on the left side of the resulting table, before the data cells starts

		*/

		return this.colTd.depth(1);
	}

	void layoutGrid(){
		/* starts the process to transform the data tree into their table position and sizes

		*/

		this.rowTd.calSystem.out.printfCoords(this.colTd.depth(1), 0, true);
		this.colTd.calSystem.out.printfCoords(this.rowTd.depth(1), 0, false);
	}

	public void getPrintDict(){
		/* translates the internal data tree structure with it's calculated x/y positions (by layoutgrid()) into its x/y table representation for System.out.printfout

		*/
		int rowDepth = this.headerrows();
		int colDepth = this.headercols();
		this.ptdict = ptPrintDict();
		for (int index=0; index < this.headers.get("cols").length())){
			System.out.printf("write col header {0} to x:{1} y:{2}",this.headers.get("cols")[index], colDepth-1 , index ));
			this.printfunction(this.headers["cols"].get(index), colDepth-1 , index , false, 1, this.col_header_style);
		}
		for(int index=0; index < this.headers.get("rows").length())){
			System.out.printf("write row header {0} to x:{1} y:{2}",this.headers.get("rows")[index], index , rowDepth));
			this.System.out.printffunction(this.headers.get("rows")[index], index , rowDepth , false, 1, this.row_header_style);
		}
		this.rowTd.fillPrintGrid(1, true, this.printfunction);
		this.colTd.fillPrintGrid(1, false, this.printfunction);
	}

	void printfunction(String value, int px, int py, boolean xDirection, int blocksize, Object style){
		/*
			storage function to fill the result ptSystem.out.printfDict- Table by the x/y coords, the value, the cell direction, the row/col span and the wanted style
		*/

		if (!this.ptDict.containsKey(px)){
			this.ptdict.set(px) = new HashMap<>();
		}
		if (value!= null){
			this.ptdict.get(px).get(py)
			.put("value", value)
			.put("style", style)
			.put("size", blocksize)
			.put("xDir", xDirection);
		}else{
			this.ptdict.get(px).put(py, null);
		}
		if (this.ptdict.xSize < px + 1){
			this.ptdict.xSize = px +1;
		}
		if (this.ptdict.ySize < py + 1){
			this.ptdict.ySize = py +1;
		}
	}



class Pyvotab{

	HashMap<String, SingleTab> result_tables;
	Object old_style;
	Object new_style;
	Object change_style;
	Object row_header_style;
	Object col_header_style;
	Object page;
	String source;
	String newname;
	String template;
	HashMap<String,Object> layout;
	boolean debug;


	Pyvotab(Object old_style, Object new_style, Object change_style, Object row_header_style, Object col_header_style, Object layout, boolean debug){
		/*
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
		*/
		
		this.result_tables=new HashMap<String, SingleTab>();
		this.old_style = old_style;
		this.new_style = new_style;
		this.change_style = change_style;
		this.row_header_style = row_header_style;
		this.col_header_style = col_header_style;
		if (layout instanceof String){
			System.out.printf("layout is string..%s",layout);
			layout=this.resolve_parameter_url(layout);
		}
		this.page = this.get_url_parameter(layout,"page","default");
		try { // is the page a string or an integer representation? if yes, convert it to int
			this.page=Integer.parseInt(this.page);
		}catch(Exception e){
		}
		this.source = this.get_url_parameter(layout,"source","pt.1");
		this.newname = this.get_url_parameter(layout,"newname","$");
		this.template = this.get_url_parameter(layout,"template",null);
		// transform the parameter string "1,2,3" into a int array [1 , 2 , 3]

		layout.put("rows", this.split_int_string( this.get_url_parameter(layout,"rows",new String[])));
		layout.put("cols", this.split_int_string( this.get_url_parameter(layout,"cols",new String[])));
		layout.put("val", Integer.parseInt(this.get_url_parameter(layout,"val",1)));
		this.layout = layout;
		this.debug = debug;
	}
	
	List<Integer> split_int_string(Object list_or_string){
		/* list_or_string is either a int list or a comma sepated string with integers

		RETURN
			int list
		*/
		if (list_or_string instanceof  String){
			List<Integer> result= new List<Integer>();
			for (String val : (String list_or_string).split(',')){
				result.add(Integer.parseInt(val))
			}
			return result;
		}else{
			return list_or_string;
		}
	}

	String get_source_name(){
		return this.newname;
	}


	public void InsertTable(List<List<String>> table, boolean change_state, Object source_style){



		/*
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
		*/

		String [] header_names=table[0];
		HashMap<String,List<String>> headers=new HashMap<String,List<String>>();
		List<String> list= headers.put("rows",new List<String>());
		for (int index:  this.layout.get("rows")){
			list.append( str( header_names[ index - 1 ] ) );
		}
		list= headers.put("cols",new List<String>());
		for (int index:  this.layout.get("cols")){
			list.append( str( header_names[ index - 1 ] ) );
		}

		for (int row_index =1;row_index < table.length; row_index++){
			List<String>row = table.get(row_index);
			rowHash = "";
			colHash = "";
			// is the page an int or a string, so single page or multipage
			if (this.page instanceof int){
				page_name=row[this.page-1];
			}else{
				page_name=str(this.page);
			}
			// does that page table already exist?
			if (!this.result_tables.containsKey(page_name)){
				this.result_tables.put(page_name, SingleTab(headers, this.old_style, this.new_style, this.change_style,this.row_header_style, this.col_header_style, this.debug )
			}
			this_tab=this.result_tables.get(page_name);
			actRowDt = this_tab.rowTd;
			actColDt = this_tab.colTd;
			for (int index :  this.layout.get("rows")){
				val=str(row[index-1])
				actRowDt = actRowDt.add(val, change_state, source_style)
				rowHash += ":"+val
			}
			for index in this.layout['cols']:
				val=str(row[index-1])
				actColDt = actColDt.add(val, change_state, source_style)
				colHash += ":"+val
			// store the value as endpoint
			// remember: rows gets colhashes & vice versa
			rowEndPoint = actRowDt.getEndPoint(colHash)
			colEndPoint = actColDt.getEndPoint(rowHash)
			if rowEndPoint == null and colEndPoint == null:
				newEndPoint = PyvotabElement(null,this, null, change_state, source_style,this.debug)
				actRowDt.setEndPoint(newEndPoint, colHash)
				actColDt.setEndPoint(newEndPoint, rowHash)
			else:
				if rowEndPoint == null:
					newEndPoint = colEndPoint
					actRowDt.setEndPoint(newEndPoint, colHash)
				else:
					newEndPoint = rowEndPoint
					actColDt.setEndPoint(newEndPoint, rowHash)

			newEndPoint.MakeValue(
				str(row[this.layout['val']-1]), actRowDt, actColDt, change_state)
	}

	def getSystem.out.printfDict(this):
		/* translates the internal data tree structure with it's calculated x/y positions (by layoutgrid()) into its x/y table representation for System.out.printfout

		/*

		result={}
		for page_name, stab in this.result_tables.items():
			stab.layoutGrid()
			stab.getSystem.out.printfDict()
			result[page_name]=stab//.ptdict
		pyvoSheet_results=[]
		System.out.printf(repr(result.keys()))
		for page_name in sorted(result.keys()):
			pyvoSheet_results.append(pyvoSheet(this.newname.replace('$',page_name), result[page_name].ptdict, result[page_name].get_sheet_style(), this.template))
			System.out.printf("Remember: correct sheet style not implemented yet")
		return pyvoSheet_results

	def resolve_parameter_url(this, url):
		/*does the inital parsing of the format url

		Parameters
		----------
		url : string
			url string as desribed in https://docs.python.org/3/library/urllib.parse.html

		Returns
		-------
		res: parameter dictionary
		/*
		parsed_url=urlparse(url)
		layout_with_array=parse_qs(parsed_url.query)
		layout={ k:v[0] for k,v in layout_with_array.items()}
		return layout

	def get_url_parameter(this, param_object,param_name,default_value):
		/*get parameters 

		Parameters
		----------
		url : string
			url string as desribed in https://docs.python.org/3/library/urllib.parse.html

		Returns
		-------
		res: ParseResult object
		/*
		System.out.printf (param_object)
		if not param_name in param_object:
			return default_value
		else:
			return param_object[param_name]
}

class ptSystem.out.printfDict(dict):
	/*
	This dictionary represents the table field results stored by their x/y coordinates
	/*
	xSize = 0
	ySize = 0


