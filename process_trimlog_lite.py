# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 11:24:31 2025

For now will just shoot for trimming a chunk of time stamps out of a log

@author: jc16287
"""
import regex as re

folder_w_logs='D:\\027 unstable engine speed\e174815'
log_name='Defects 345 PM.asc'

orig_lines=open(folder_w_logs+'\\'+log_name).readlines()

rxtx_regex = "[r-t]x"
timestamp_regex = "[0-9]+\.[0-9]+"
for line in orig_lines:

    if(re.search(rxtx_regex, line, re.IGNORECASE)):
        timestamp_query = re.search(timestamp_regex , line)
        timestamp = float(timestamp_query.group())
        if timestamp>280.0 and timestamp<680.0:
            with open('trimmed_345.asc','a') as f:
                f.write(line)

f.close()