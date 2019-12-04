
import java.io.UnsupportedEncodingException;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLDecoder;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;

public class Pyvotab {

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
    HashMap<String, Object> layout;
    boolean debug;

    Pyvotab(Object old_style, Object new_style, Object change_style, Object row_header_style, Object col_header_style, Object layout, boolean debug) {
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

        this.result_tables = new HashMap<>();
        this.old_style = old_style;
        this.new_style = new_style;
        this.change_style = change_style;
        this.row_header_style = row_header_style;
        this.col_header_style = col_header_style;
        HashMap<String, Object> param_object;
        param_object = new HashMap<>();
        if (layout instanceof String) {
            System.out.printf("layout is string..%s", layout);
            param_object = Pyvotab.resolve_parameter_url(layout.toString());
        } else {
            param_object = ((HashMap<String, Object>) layout);
        }
        this.page = Pyvotab.get_url_parameter(param_object, "page", "default");
        try { // is the page a string or an integer representation? if yes, convert it to int
            this.page = Integer.parseInt(this.page.toString());
        } catch (Exception e) {
        }
        this.source = (String) Pyvotab.get_url_parameter(param_object, "source", "pt.1");
        this.newname = (String) Pyvotab.get_url_parameter(param_object, "newname", "$");
        this.template = (String) Pyvotab.get_url_parameter(param_object, "template", null);
        // transform the parameter string "1,2,3" into a int array [1 , 2 , 3]

        param_object.put("rows", Pyvotab.split_int_string(Pyvotab.get_url_parameter(param_object, "rows", new ArrayList<String>())));
        param_object.put("cols", Pyvotab.split_int_string(Pyvotab.get_url_parameter(param_object, "cols", new ArrayList<String>())));
        param_object.put("val", Pyvotab.get_url_parameter(param_object, "val", 1));
        this.layout = param_object;
        this.debug = debug;
    }

    static ArrayList<Integer> split_int_string(Object list_or_string) {
        /* list_or_string is either a int list or a comma sepated string with integers

         RETURN
         int list
         */
        if (list_or_string instanceof String) {
            ArrayList<Integer> result = new ArrayList<>();
            for (String val : ((String) list_or_string).split(",")) {
                result.add(Integer.parseInt(val));
            }
            return result;
        } else {
            return ((ArrayList<Integer>) list_or_string);
        }
    }

    String get_source_name() {
        return this.newname;
    }

    public void InsertTable(ArrayList<ArrayList<String>> table, boolean change_state, Object source_style) {



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
         identifier of the data source. MAKE SURE that each input table has its own source_style
         object, even if the styles are all the same. The software uses the style object to distinglish
         between the different sources!
         Reference to tell the user where the resulting table cells are coming from
         */

        ArrayList<String> header_names = table.get(0);
        HashMap<String, ArrayList<String>> headers = new HashMap<>();
        ArrayList<String> list = new ArrayList<String>();
        headers.put("rows", list);
        for (int index : ((ArrayList<Integer>) this.layout.get("rows"))) {
            list.add(header_names.get(index - 1));
        }
        list = new ArrayList<String>();
        headers.put("cols", list);
        for (int index : ((ArrayList<Integer>) this.layout.get("cols"))) {
            list.add(header_names.get(index - 1));
        }

        for (int row_index = 1; row_index < table.size(); row_index++) {
            ArrayList<String> row = table.get(row_index);
            String rowHash = "";
            String colHash = "";
            String page_name;
            // is the page an int or a string, so single page or multipage
            if (this.page instanceof Integer) {
                page_name = row.get(((Integer) this.page) - 1);
            } else {
                page_name = this.page.toString();
            }
            // does that page table already exist?
            if (!this.result_tables.containsKey(page_name)) {
                this.result_tables.put(page_name, new SingleTab(headers, this.old_style, this.new_style, this.change_style, this.row_header_style, this.col_header_style, this.debug));
            }
            SingleTab this_tab = this.result_tables.get(page_name);
            PyvotabElement actRowDt = this_tab.rowTd;
            PyvotabElement actColDt = this_tab.colTd;
            String val;
            for (Integer index : ((ArrayList<Integer>) this.layout.get("rows"))) {
                val = row.get(index - 1);
                actRowDt = actRowDt.add(val, change_state, source_style);
                rowHash += ":" + val;
            }
            for (Integer index : ((ArrayList<Integer>) this.layout.get("cols"))) {
                val = row.get(index - 1);
                actColDt = actColDt.add(val, change_state, source_style);
                colHash += ":" + val;
            }
            // store the value as endpoint
            // remember: rows gets colhashes & vice versa
            PyvotabElement rowEndPoint = actRowDt.getEndPoint(colHash);
            PyvotabElement colEndPoint = actColDt.getEndPoint(rowHash);
            PyvotabElement newEndPoint;
            if (rowEndPoint == null && colEndPoint == null) {
                newEndPoint = new PyvotabElement(null, this_tab, null, change_state, source_style, this.debug);
                actRowDt.setEndPoint(newEndPoint, colHash);
                actColDt.setEndPoint(newEndPoint, rowHash);
            } else {
                if (rowEndPoint == null) {
                    newEndPoint = colEndPoint;
                    actRowDt.setEndPoint(newEndPoint, colHash);
                } else {
                    newEndPoint = rowEndPoint;
                    actColDt.setEndPoint(newEndPoint, rowHash);
                }
            }
            newEndPoint.MakeValue(row.get(((Integer) this.layout.get("val")) - 1), actRowDt, actColDt, change_state);
        }
    }

    public ArrayList<PyvoSheet> getPrintDict() {
        /* translates the internal data tree structure with it's calculated x/y positions (by layoutgrid()) into its x/y table representation for System.out.printfout

         */
        HashMap<String, SingleTab> result = new HashMap<>();
        for (Map.Entry<String, SingleTab> me : this.result_tables.entrySet()) {
            String page_name = me.getKey();
            SingleTab stab = me.getValue();
            stab.layoutGrid();
            stab.getPrintDict();
            result.put(page_name, stab);
        }
        ArrayList<PyvoSheet> pyvoSheet_results = new ArrayList<>();
        //System.out.printf(repr(result.keys()))
        ArrayList<String> sortedKeys = new ArrayList(result.keySet());
        Collections.sort(sortedKeys);
        for (String page_name : sortedKeys) {
            pyvoSheet_results.add(new PyvoSheet(this.newname.replace("$", page_name), result.get(page_name).ptdict, result.get(page_name).get_sheet_style(), this.template));
        }
        return pyvoSheet_results;
    }

    static HashMap<String, Object> resolve_parameter_url(String url) {
        /*does the inital parsing of the format url

         Parameters
         ----------
         url : string
         url string as desribed in https://docs.python.org/3/library/urllib.parse.html

         Returns
         -------
         res: parameter dictionary
         */
        //for java: https://examples.javacodegeeks.com/core-java/net/url/parse-url-example/ and https://stackoverflow.com/a/13592567

        HashMap<String, Object> query_pairs = new LinkedHashMap<>();
        try {
            URL parsed_url = new URL(url);
            String protocol = parsed_url.getProtocol();
            String host = parsed_url.getHost();
            int port = parsed_url.getPort();
            String path = parsed_url.getPath();
            String query = parsed_url.getQuery();
            String[] pairs = query.split("&");
            for (String pair : pairs) {
                int idx = pair.indexOf("=");
                query_pairs.put(URLDecoder.decode(pair.substring(0, idx), "UTF-8"), URLDecoder.decode(pair.substring(idx + 1), "UTF-8"));
            }
        } catch (MalformedURLException e) {
            System.out.println("Malformed URL: " + e.getMessage());
        } catch (UnsupportedEncodingException e) {
            System.out.println("UnsupportedEncodingException Malformed URL: " + e.getMessage());
        }
        return query_pairs;
    }

    static Object get_url_parameter(HashMap<String, Object> param_object, String param_name, Object default_value) {
        /*get parameters 

         Parameters
         ----------
         url : string
         url string as desribed in https://docs.python.org/3/library/urllib.parse.html

         Returns
         -------
         res: ParseResult object
         */
        if (param_object.containsKey(param_name)) {
            return param_object.get(param_name);
        } else {
            return default_value;
        }
    }
}
