import pandas as pd
import numpy as np
from urllib.parse import urlparse , parse_qs
import sys


def get_names_by_index(names,param,index_name):
	result=None
	print("look for  value ", index_name )
	try:
		index_value=param[index_name][0]
		print("find ", index_value )
		indicies=index_value.split(",")
		print(indicies)
		result=[]
		for index in indicies:
			print("add value ",names[int(index)-1]," to ", index_name )
			result.append(names[int(index)-1])
	except:
		print("Exeption")
		pass
	return result

def translate_pivot_2_csv(multi_index):
	#https://www.datacamp.com/community/tutorials/pandas-multi-index
	multi_index.sort_index(inplace=True)
	df_index=multi_index.index
	nr_of_rows=len(df_index.labels[0])
	nr_of_row_headers=len(df_index.labels)
	for row_count in range(nr_of_rows):
		row_array=[]
		for row_header_count in range(nr_of_row_headers):
			label_index=df_index.labels[row_header_count][row_count]
			row_array.append(df_index.levels[row_header_count][label_index])
		print(row_array)
		my_data=multi_index.loc[tuple(row_array)]
		print (my_data)



xl = pd.ExcelFile(sys.argv[1])
for sheetname in xl.sheet_names:
	print ("sheet:",sheetname)
	df = xl.parse(sheetname)
	#print(df.head())

try:
	page_list_df=xl.parse("pyvotab")
except:
	print("Error: no pyvotab definition sheet found!. Program terminates")
	sys.exit(1)
for index, row in page_list_df.iterrows():
	newSheetName=row['page']
	print(row['page'], row['layout'])
	url_split = urlparse(row['layout'])
	path_elements=url_split.path.split("/")
	# scheme://netloc/path;parameters?query#fragment
	print("scheme",url_split.scheme)
	print("netloc",url_split.netloc)
	print("path",url_split.path)
	print("query",url_split.query)
	print("fragment",url_split.fragment)
	params=parse_qs(url_split.query)
	for key, value in params.items():
		print(key, value)
	print("data source",path_elements[-1])
	data_source_df=xl.parse(path_elements[-1])
	columns=list(data_source_df)
	for value in columns:
		print( value)
	values_array=get_names_by_index(columns,params,"data")
	index_array=get_names_by_index(columns,params,"rows")
	columns_array=get_names_by_index(columns,params,"cols")
	pivoted = pd.pivot_table(data_source_df, values=values_array, index=index_array, columns=columns_array, aggfunc=np.sum)
	print(pivoted)
	#csv_style = pivoted.to_csv(sys.stdout)
	#print(csv_style)
	print(pivoted.index)
	translate_pivot_2_csv(pivoted)