package pyvotab;
public class PyvoSheet {

    public String name;
    public PtPrintDict table;
    public Object style;
    public String template;

    PyvoSheet(String name, PtPrintDict table, Object style, String template) {
        this.name = name;
        this.table = table;
        this.style = style;
        this.template = template;
    }
}