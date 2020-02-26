#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import argparse

from ptWriter import PtWriter
from pyvotab import PyvoStyles


		
if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", help="input excel pivotab file", action='append')
	parser.add_argument("-l", "--layout", help="layout format string", action='append', default=[])
	parser.add_argument("-o", "--output", help="output file name")
	args = parser.parse_args()
	print(repr(args))
	white={'xls':"FFFFFF"} 
	red={'xls':"FF0000"} 
	green={'xls':"00FF00"} 
	orange={'xls':"FF8000"} 
	default={'xls':None} 
	blue={'xls':"0000FF"} 
	lightblue={'xls':"8080FF"} 
	yellow={'xls':"FFFF00"} 

	if len(args.input)< 2:
		pyvo_style = PyvoStyles(white, white, orange, yellow, lightblue)
	else:	
		pyvo_style = PyvoStyles(red, green, orange, yellow, lightblue)

	pyvotab_writer=PtWriter('xls')


	pyvotab_sheet_list ,view_sheet_list  = pyvotab_writer.calculate_pyvotab_files( args.input, args.layout, pyvo_style)
	pyvotab_writer.save(pyvotab_sheet_list, args.input[-1], args.output, {})
