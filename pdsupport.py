#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd

def calculate(mylist):
	return pd.DataFrame(mylist[1:],columns=mylist[0])


def calculate_pivot(table,layout):
	headers=table[0]
	df1 = pd.DataFrame(table[1:],columns=headers)
	print(df1.head(3))
	index=[]
	for row in layout['pivot_rows']:
		index.append(headers[row-1])
	columns=[]
	for col in layout['pivot_cols']:
		columns.append(headers[col-1])
	print(repr(columns))
	df2= pd.pivot_table(df1, values=headers[layout['pivot_val']-1], 
						index=index, 
						columns=columns,
						aggfunc=[min,max])
	print(df2)
	arr = df2.values.tolist()
	cols = df2.columns.tolist()
	#rows = df2.rows.tolist()
	print('\nNumpy cols\n----------\n', cols)
	#print('\nNumpy rows\n----------\n', rows)
	print('\nNumpy Array\n----------\n', arr)
	res=[]
	pivot_res=df2.to_dict()
	for element, element_values in pivot_res.items():
		for value_name,value in element_values.items():
			if not pd.isnull(value):
				line=list(element)
				line.append(value_name)
				line.append(str(value))
				print(repr(value))
				print("\t".join(line))
				res.append(line)
	return res