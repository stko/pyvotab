#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyvotab.pdsupport as pdsupport
import pandas as pd
import numpy as np

t2 = [
	['Vorname', 'Nachname', 'Ort', 'Str', 'Hausnummer'],
	['Hins', 'Mueller', 'Hamburg', 'Postweg', 8],
	['Klaus', 'Meier', 'Hamburg', 'Feldplatz', 6],
	['Klaus', 'Meier', 'Berlin', 'Burgallee', 4],
	['Klaus', 'Schulze', 'Berlin', 'Burgallee', 3],
	['Klaus', 'Schulze', 'Berlin', 'am Deich', 9],
	['Hans', 'Mueller', 'Berlin', 'am Deich', 10],
]

layout={}
# caution: indices are starting with 1 in Excel, not 0 as usual
layout['pivot_rows'] = [2]
layout['pivot_cols'] = [3]
layout['pivot_val'] = 5
layout['pivot'] = ['sum']
df1 = pdsupport.calculate_pivot(t2,layout)
print(df1)
