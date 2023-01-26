#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import importlib
import traceback

class PtWriter:
	def __init__(self, plugin_name):
		try:
			self.plugin_name=plugin_name
			myModule=importlib.import_module("pyvotab.ptp_" + plugin_name.lower())
			myPluginClass=getattr(myModule,"ptPlugin")
			self.plugin=myPluginClass()
		except:
			print("Can't load plugin "+plugin_name)
			self.plugin=None
			traceback.print_exc(file=sys.stdout)
	
	def load(self, file_name):
		try:
			return self.plugin.load( file_name)
		except :
			print("Can't load in plugin "+self.plugin_name)
			traceback.print_exc(file=sys.stdout)
	
	def save(self, tables, input_file_name, output_file_name, options):
		try:
			self.plugin.save( tables, input_file_name, output_file_name, options)
		except :
			print("Can't save in plugin "+self.plugin_name)
			traceback.print_exc(file=sys.stdout)
	
	def calculate_pyvotab_files(self, file_name_list, local_layout_string_list, pyvot_style):
		try:
			return self.plugin.calculate_pyvotab_files( file_name_list, local_layout_string_list, pyvot_style)
		except :
			print("Can't calculate_pyvotab_files in plugin "+self.plugin_name)
			traceback.print_exc(file=sys.stdout)
	
		

if __name__ == "__main__":
	pi=PtWriter('xls')
	pi.save({},"temp",[],{})

