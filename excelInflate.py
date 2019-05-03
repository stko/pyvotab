import pandas as pd
from urllib.parse import urlparse , parse_qs
import sys

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
