# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 11:24:31 2025

For now will just shoot for trimming a chunk of time stamps out of a log

@author: jc16287
"""
import regex as re

folder_w_logs=r'C:\\Users\\jc16287\\Downloads\\WarmUp_4Dec2025'
log_name='WarmUp_4Dec2025.asc'

with open (folder_w_logs+'\\'+log_name) as f:
    orig_lines = f.readlines()
    f.close()

rxtx_regex = "(?i)[r-t]x"
timestamp_regex = "[0-9]+\.[0-9]+"

trim_begin = 100.0
trim_end = 200.0

keep_searching = True

for line in orig_lines:

    if(re.search(rxtx_regex, line, re.IGNORECASE)):
        timestamp_query = re.search(timestamp_regex , line)
        timestamp = float(timestamp_query.group())
    else:
        timestamp = -1
       
    if (timestamp > trim_begin) and (timestamp < trim_end):
        
        with open('trimmed_power_meter_1200.asc','a') as f:
            f.write(line)
        
        print(f"collected \t {line}")
        
    elif (timestamp > trim_end):
        break
    

        
