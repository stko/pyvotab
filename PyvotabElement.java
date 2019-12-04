
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;

public class PyvotabElement extends HashMap<String, PyvotabElement> {

    PyvotabElement parent;
    int dimension;
    Object source_style;
    String value;
    SingleTab singletab;
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

    PyvotabElement(String value, SingleTab singletab, PyvotabElement parent, boolean isNew, Object source_style, boolean debug) {
        this.parent = parent;
        this.dimension = 0;
        this.source_style = source_style;
        this.value = value;
        this.singletab = singletab;
        this.debug = debug;
        if (!isNew) {
            this.change_state = States.old;
        } else {
            this.change_state = States.newstate;
        }
    }

    void increaseDimension() {
        this.dimension += 1;
        if (this.parent != null) {
            this.parent.increaseDimension();
        }
    }

    void set_change_state(States child_state) {
        /* recalculates the change_state
         */

        if (this.change_state == States.changed) { // there's no more left to set
            return;
        }
        if (this.change_state == States.old && child_state == States.unchanged) {
            this.change_state = States.unchanged;
        }
        if (this.change_state != child_state) {
            //System.out.printf("change_state change:%d %d" ,this.change_state, child_state);
            this.change_state = States.changed;
        }
        if (this.parent != null) {
            this.parent.set_change_state(this.change_state);
        }
    }

    PyvotabElement add(String value, boolean isNew, Object source_style) {
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
        if (!this.containsKey(value)) {
            this.put(value, new PyvotabElement(value, this.singletab, this, isNew, source_style, this.debug));
        }
        return this.get(value);
    }

    void MakeValue(String value, PyvotabElement rowDt, PyvotabElement colDt, boolean isNew) {
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
        // System.out.printf("change_state change state from: %s %s %s\n", this.change_state.toString(), "for value ", value);
        if (this.value != null) {
            if (this.change_state == States.old && isNew) {
                this.change_state = States.unchanged;
            }
            if (!this.value.equals(value)) {
                this.change_state = States.changed;
            }
        }
        rowDt.set_change_state(this.change_state);
        colDt.set_change_state(this.change_state);
        this.value = value;
    }

    PyvotabElement getEndPoint(String myhash) {
        /* returns value cell object, if is endpoint, otherways null

         Parameters
         ----------
         myhash : string
         hash representing the aligned row/col endpoint
         */

        try {
            return this.get((myhash));
        } catch (Exception e) {
            return null;
        }
    }

    void setEndPoint(PyvotabElement newEndPoint, String myhash) {
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

        this.put(myhash, newEndPoint);
        this.isEndStup = true;
    }

    void setPrintCoords(int startCoord, int level, boolean xDirection) {
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


        if (xDirection) {
            this.printY = startCoord;
        } else {
            this.printX = startCoord;
        }
    }

    int calPrintCoords(int startCoord, int level, boolean xDirection) {
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
        if (!this.isEndStup) {
            startCoord -= 1;  // reduce it, so that the return value is the same as the start in case this element and its subs covers only 1 row/column
        }
        ArrayList<String> sortedKeys = new ArrayList(this.keySet());
        Collections.sort(sortedKeys);
        for (String index : sortedKeys) {
            if (this.isEndStup) {
                this.get(index).setPrintCoords(startCoord, level, xDirection);
            } else {
                startCoord += 1;
                startCoord = this.get(index).calPrintCoords(
                        startCoord, level + 1, xDirection);
            }
        }
        this.blockSize = startCoord - this.blockSize + 1;
        return startCoord;
    }

    int depth(int actLevel) {
        /*
         calculates the child node depth of a node

         Parameters
         ----------
         actLevel : int
         entry level of that node
         */

        int resultLevel = actLevel;
        for (String index : this.keySet()) {
            if (this.get(index).isEndStup) {
                return actLevel;
            } else {
                int newLevel = this.get(index).depth(actLevel + 1);
                if (newLevel > resultLevel) {
                    resultLevel = newLevel;
                }
            }
        }
        return resultLevel;
    }

    void fillPrintGridValue(int multiplier, boolean xDirection, FillFunction fillFunction) {
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
        String actvalue;
        if (this.debug) {
            actvalue = String.format("'%s' (%s)", this.value, this.change_state.toString());
        } else {
            actvalue = this.value;
        }
        Object this_style = this.source_style;
        if (this.change_state == States.old) {
            this_style = this.singletab.old_style;
        }
        if (this.change_state == States.changed) {
            this_style = this.singletab.change_style;
        }
        if (this.change_state == States.newstate) {
            this_style = this.singletab.new_style;
        }
        // to have some space for the heading names, we move the value cells 1 row downwards (this.System.out.printfY + 1)
        fillFunction.fillFunction(actvalue, this.printX, this.printY + 1,
                xDirection, 1, this_style);
    }

    void fillPrintGrid(int multiplier, boolean xDirection, FillFunction fillFunction) {
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

        ArrayList<String> sortedKeys = new ArrayList(this.keySet());
        Collections.sort(sortedKeys);
        for (String index : sortedKeys) {
            if (this.isEndStup) {
                this.get(index).fillPrintGridValue(multiplier, xDirection, fillFunction);
            } else {
                // determine correct style based on, if the element is old or not
                Object this_style = this.get(index).source_style;
                if (this.get(index).change_state == States.old) {
                    this_style = this.singletab.old_style;
                }
                if (this.get(index).change_state == States.changed) {
                    this_style = this.singletab.change_style;
                }
                if (this.get(index).change_state == States.newstate) {
                    this_style = this.singletab.new_style;

                }
                if (this.debug) {
                    value = String.format("'%s' (%s) %d", index, this.get(index).change_state.toString(), this.get(index).blockSize);
                } else {
                    value = index;
                }
                if (xDirection) {
                    fillFunction.fillFunction(
                            // to have some space for the heading names, we move the value cells 1 row downwards (this.get(index).startCoord +1)
                            value, this.level, this.get(index).startCoord + 1, xDirection, this.get(index).blockSize, this_style);
                    // in case we have a multiple cell span, we need to set some empty filler
                    for (int i = 1; i < this.get(index).blockSize; i++) {
                        fillFunction.fillFunction(
                                null, this.level, this.get(index).startCoord + i + 1, xDirection, this.get(index).blockSize, this_style);
                    }
                } else {
                    fillFunction.fillFunction(
                            value, this.get(index).startCoord, this.level, xDirection, this.get(index).blockSize, this_style);
                    // in case we have a multiple cell span, we need to set some empty filler
                    for (int i = 1; i < this.get(index).blockSize; i++) {
                        fillFunction.fillFunction(
                                null, this.get(index).startCoord + 1 + i, this.level, xDirection, this.get(index).blockSize, this_style);
                    }
                }
                this.get(index).fillPrintGrid(
                        multiplier, xDirection, fillFunction);
            }
        }
    }
}
