#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy

def calculate(mylist):
	return pd.DataFrame(mylist[1:],columns=mylist[0])


def calculate_pivot(table,layout):
	headers=table[0]
	df1 = pd.DataFrame(table[1:],columns=headers)
	index=[]
	pivot_header=['Pivot'] # this array is needed to calculate the header colnmn names for the final calculated pivot table
	pivot_header.append(headers[layout['pivot_val']-1]) # the second colums contains the name of the original colums from where the value is taken
	columns=[]
	for col in layout['pivot_cols']:
		columns.append(headers[col-1])
		pivot_header.append(headers[col-1])
	for row in layout['pivot_rows']:
		index.append(headers[row-1])
		pivot_header.append(headers[row-1])
	pivot_header.append('Value')
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
	arr = df2.values.tolist()
	cols = df2.columns.tolist()
	res=[pivot_header] # add the header line to the result
	pivot_res=df2.to_dict()
	for element, element_values in pivot_res.items():
		for value_name,value in element_values.items():
			if not pd.isnull(value):
				line=list(element) # element is a list of one or more cell contents
				if type(value_name) is str:
					line.append(value_name)
				else:
					line.extend(value_name) # value_name is a list of one or more cell contents
				line.append(str(value))
				res.append(line)
	return res