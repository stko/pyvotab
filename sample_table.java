import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;


public class sample_table 
{

	public static void main (String[] args)
	{

		ArrayList<ArrayList<String>> t1 = new ArrayList<>();
		t1.add(new ArrayList(Arrays.asList(new String[]{"Hans", "Mueller", "Hamburg", "Postweg", "8"})));
		t1.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Meier", "Hamburg", "Feldplatz", "5"})));
		t1.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Meier", "Berlin", "Burgallee", "4"})));
		t1.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Schulze", "Berlin", "Burgallee", "3"})));


		ArrayList<ArrayList<String>>  t2 = new ArrayList<>();
		t2.add(new ArrayList(Arrays.asList(new String[]{"Hins", "Mueller", "Hamburg", "Postweg", "8"})));
		t2.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Meier", "Hamburg", "Feldplatz", "6"})));
		t2.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Meier", "Berlin", "Burgallee", "4"})));
		t2.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Schulze", "Berlin", "Burgallee", "3"})));
		t2.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Schulze", "Berlin", "am Deich", "9"})));
		t2.add(new ArrayList(Arrays.asList(new String[]{"Hans", "Mueller", "Berlin", "am Deich", "10"})));

		ArrayList<ArrayList<String>>  t3 =new ArrayList<>();
		t3.add(new ArrayList(Arrays.asList(new String[]{"Hans", "Mueller", "Hamburg", "Postweg", "8"})));

		ArrayList<ArrayList<String>> t4 = new ArrayList<>(); 
		t4.add(new ArrayList(Arrays.asList(new String[]{"Hins", "Mueller", "Hamburg", "Postweg", "8"})));

		ArrayList<ArrayList<String>>  t5 = new ArrayList<>(); // = t1 with column header
		t5.add(new ArrayList(Arrays.asList(new String[]{"Vorname", "Nachname", "Stadt", "Straße", "Hausnummer"})));
		t5.add(new ArrayList(Arrays.asList(new String[]{"Hans", "Mueller", "Hamburg", "Postweg", "8"})));
		t5.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Meier", "Hamburg", "Feldplatz", "5"})));
		t5.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Meier", "Berlin", "Burgallee", "4"})));
		t5.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Schulze", "Berlin", "Burgallee", "3"})));

		ArrayList<ArrayList<String>>  t6 =  new ArrayList<>(); // = t2 with column header
		t5.add(new ArrayList(Arrays.asList(new String[]{"Vorname", "Nachname", "Stadt", "Straße", "Hausnummer"})));
		t5.add(new ArrayList(Arrays.asList(new String[]{"Hins", "Mueller", "Hamburg", "Postweg", "8"})));
		t5.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Meier", "Hamburg", "Feldplatz", "5"})));
		t5.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Meier", "Berlin", "Burgallee", "4"})));
		t5.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Schulze", "Berlin", "Burgallee", "3"})));
		t5.add(new ArrayList(Arrays.asList(new String[]{"Klaus", "Schulze", "Berlin", "am Deich", "9"})));
		t5.add(new ArrayList(Arrays.asList(new String[]{"Hans", "Mueller", "Berlin", "am Deich", "10"})));


		HashMap<String,Object> param_object = new HashMap<> ();
		param_object.put("page", 3);
		param_object.put("rows",new ArrayList(Arrays.asList(new Integer[]  {3,4})));
		param_object.put("cols",new ArrayList(Arrays.asList(new Integer[]  {2,1})));
		param_object.put("val", 5);
		param_object.put("filter", null);
		param_object.put("pivot", "plain");
		Pyvotab pt = new Pyvotab("lightgrey","lightgreen","yellow","lightblue", "aquamarine", param_object,true);

		pt.InsertTable( t5, false, "white");
		pt.InsertTable( t6, true, "white");

		for (PyvoSheet pyvot_sheet : pt.getPrintDict()){
			String page_name=pyvot_sheet.name;
			PtPrintDict pt_table=pyvot_sheet.table;
			System.out.printf("tabellen_name %s %s",page_name,pyvot_sheet.style.toString());
			System.out.printf("<table border=\"1\">\n");
			for (int row = 0 ; row < pt_table.ySize; row++){
				System.out.printf("<tr>\n");
				for (int col=0; col < pt_table.xSize; col++){
                                    HashMap<String,Object> cell_content;
					try{
						cell_content=(HashMap<String,Object>)pt_table.get(col).get(row);
					}catch(Exception e){
						System.out.printf("<td/>");
						continue;
					}
					if (cell_content!=null){ // if content is None, then it"s an empty filler element, needed to handle multicell html cells correctly
						System.out.printf("<td ");

						System.out.printf("style=\"background-color:");
						System.out.printf(cell_content.get("style")+"\" ");
						if (((boolean)cell_content.get("xDir"))){
							System.out.printf("rowspan=\"");
						}else{
							System.out.printf("colspan=\"");
						}
						System.out.printf("%s",cell_content.get("size")+"\" ");
						System.out.printf(">");

						System.out.printf(cell_content.get("value")+String.format(" row:{0}/col:{1}",row,col) +"</td>");
					}
				}System.out.printf("</tr>");
			}
			System.out.printf("</table>");
			}
		}
}