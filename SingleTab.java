
import java.util.ArrayList;
import java.util.HashMap;

public class SingleTab implements FillFunction {

    PyvotabElement rowTd;
    PyvotabElement colTd;
    Object old_style;
    Object new_style;
    Object row_header_style;
    Object col_header_style;
    Object change_style;
    HashMap<String, ArrayList<String>> headers;
    boolean debug;
    PtPrintDict ptdict;
    HashMap<String, Object> layout;
    String source;
    String newname;
    String template;

    SingleTab(HashMap<String, ArrayList<String>> headers, Object old_style, Object new_style, Object change_style, Object row_header_style, Object col_header_style, boolean debug) {
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

        this.rowTd = new PyvotabElement("row", this, null, false, -1, debug);
        this.colTd = new PyvotabElement("col", this, null, false, -1, debug);
        this.old_style = old_style;
        this.new_style = new_style;
        this.row_header_style = row_header_style;
        this.col_header_style = col_header_style;
        this.change_style = change_style;
        this.headers = headers;
        this.debug = debug;
    }

    Object get_sheet_style() {
        PyvotabElement first_element = this.rowTd.entrySet().iterator().next().getValue();
        States initial_change_state = first_element.change_state;
        Object default_style = first_element.source_style;
        for (PyvotabElement element : this.rowTd.values()) {
            if (initial_change_state != element.change_state) {
                initial_change_state = States.changed;
                break;
            }
        }
        if (initial_change_state != States.changed) {
            for (PyvotabElement element : this.colTd.values()) {
                if (initial_change_state != element.change_state) {
                    initial_change_state = States.changed;
                    break;
                }
            }
        }
        if (initial_change_state == States.old) {
            return this.old_style;
        }
        if (initial_change_state == States.changed) {
            return this.change_style;
        }
        if (initial_change_state == States.newstate) {
            return this.new_style;
        }
        return default_style;
    }

    int headerrows() {
        /*returns the number of cells  on top of the resulting table, before the data cells starts

         */

        return this.rowTd.depth(1);
    }

    int headercols() {
        /*returns the number of cells  on the left side of the resulting table, before the data cells starts

         */

        return this.colTd.depth(1);
    }

    void layoutGrid() {
        /* starts the process to transform the data tree into their table position and sizes

         */

        this.rowTd.calPrintCoords(this.colTd.depth(1), 0, true);
        this.colTd.calPrintCoords(this.rowTd.depth(1), 0, false);
    }

    public void getPrintDict() {
        /* translates the internal data tree structure with it's calculated x/y positions (by layoutgrid()) into its x/y table representation for System.out.printfout

         */
        int rowDepth = this.headerrows();
        int colDepth = this.headercols();
        this.ptdict = new PtPrintDict();
        for (int index = 0; index < this.headers.get("cols").size(); index++) {
            this.fillFunction(this.headers.get("cols").get(index), colDepth - 1, index, false, 1, this.col_header_style);
        }
        for (int index = 0; index < this.headers.get("rows").size(); index++) {
            this.fillFunction(this.headers.get("rows").get(index), index, rowDepth, false, 1, this.row_header_style);
        }
        this.rowTd.fillPrintGrid(1, true, this);
        this.colTd.fillPrintGrid(1, false, this);
    }

    public void fillFunction(String value, Integer px, Integer py, boolean xDirection, int blocksize, Object style) {
        /*
         storage function to fill the result ptSystem.out.printfDict- Table by the x/y coords, the value, the cell direction, the row/col span and the wanted style
         */

        if (!this.ptdict.containsKey(px)) {
            this.ptdict.put(px, new SmallPtPrintDict());
        }
        if (value != null) {
            PtPrintDictElement pdElement = new PtPrintDictElement();
            pdElement.put("value", value);
            pdElement.put("style", style);
            pdElement.put("size", blocksize);
            pdElement.put("xDir", xDirection);
            this.ptdict.get(px).put(py, pdElement);
        } else {
            this.ptdict.get(px).put(py, null);
        }
        if (this.ptdict.xSize < px + 1) {
            this.ptdict.xSize = px + 1;
        }
        if (this.ptdict.ySize < py + 1) {
            this.ptdict.ySize = py + 1;
        }
    }
}
