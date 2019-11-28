# pyvotab
Pyvotab reads data provided in a nested array (other formats are possible, but not implemented yet):


```python
t1 = [
	['Hans', 'Mueller', 'Hamburg', 'Postweg', 8],
	['Klaus', 'Meier', 'Hamburg', 'Feldplatz', 5],
	['Klaus', 'Meier', 'Berlin', 'Burgallee', 4],
	['Klaus', 'Schulze', 'Berlin', 'Burgallee', 3],
]
```

and routes that data into an x/y matrix, defined by a layout instruction, referencing to the input data columns:

```python
	//?source=pt.1&page=3&rows=3,4&newname=$&cols=1,2&val=5
```


This is, so far, not very spectacular...


The magic of pyvotab comes in places when not just one single table is loaded, but two or more different revisions of the same data instead.

Pyvotab then overlays all these different tables into one resulting table and clearly marks all data elements if they have been deleted, added or changed.

These markers are fully generic; pyvotab only handle, but do not generate or modify them. So they can be defined e.g. as Excel style object (as the sample program ptViewer does), and the output from pyvotab can be used directly to transform it into e.g. an Excel workbook.

## Usage
Basically the usage of pyvotab consists of 3 steps:

### Initialisation: 

Create a pyvotab object by define the change marker object and the wanted result table layout

    pt = Pyvotab('lightgrey','lightgreen','yellow','lightblue', 'aquamarine', { 'page': 3, 'rows' : [ 3,4 ], 'cols' : [1, 2], 'val' : 5 , 'filter': None, 'pivot': 'plain'})

### Fill with data

Add one or more data set revions to it

    pt.InsertTable( t1, False, "white")
    pt.InsertTable( t2, True, "white")

### Get the Result Table

Pick up the resulting tables and iterate throught it:

    for pyvot_sheet in pt.getPrintDict():

