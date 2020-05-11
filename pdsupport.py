#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy

def calculate(mylist):
	return pd.DataFrame(mylist[1:],columns=mylist[0])


def calculate_pivot(table,layout):
	headers=table[0]
	df1 = pd.DataFrame(table[1:],columns=headers)
	#print(df1.head(3))
	print(df1)
	index=[]
	pivot_header=['Pivot'] # this array is needed to calculate the header colnmn names for the final calculated pivot table
	columns=[]
	for col in layout['pivot_cols']:
		columns.append(headers[col-1])
		pivot_header.append(headers[col-1])
	for row in layout['pivot_rows']:
		index.append(headers[row-1])
		pivot_header.append(headers[row-1])
	pivot_header.append('Value')
	print(repr(columns))
	# calculate the aggretor functions
	aggfunc=[]
	for agg_func_name in layout['pivot']:
		if agg_func_name=='min':
			aggfunc.append(min)
			continue
		if agg_func_name=='max':
			aggfunc.append(max)
			continue
		if agg_func_name=='sum':
			aggfunc.append(sum)
			continue
		if agg_func_name=='avg':
			aggfunc.append(numpy.mean)
			continue
		if agg_func_name=='cnt':
			aggfunc.append(len)
			continue
		print("unknown aggregator name {0}".format(agg_func_name))
	df2= pd.pivot_table(df1, values=headers[layout['pivot_val']-1], 
						index=index, 
						columns=columns,
						aggfunc=aggfunc)
	print(df2)
	arr = df2.values.tolist()
	cols = df2.columns.tolist()
	#rows = df2.rows.tolist()
	print('\nNumpy cols\n----------\n', cols)
	#print('\nNumpy rows\n----------\n', rows)
	print('\nNumpy Array\n----------\n', arr)
	res=[pivot_header] # add the header line to the result
	pivot_res=df2.to_dict()
	for element, element_values in pivot_res.items():
		for value_name,value in element_values.items():
			if not pd.isnull(value):
				line=list(element)
				line.append(value_name)
				line.append(str(value))
				print("\t".join(line))
				res.append(line)
	return res