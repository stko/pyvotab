public class PyvoSheet {

    String name;
    PtPrintDict table;
    Object style;
    String template;

    PyvoSheet(String name, PtPrintDict table, Object style, String template) {
        this.name = name;
        this.table = table;
        this.style = style;
        this.template = template;
    }
}