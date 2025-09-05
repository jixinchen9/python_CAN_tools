# -*- coding: utf-8 -*-
"""
This script has functions to filter several signals, and analyze them'

'right now it's tailored to look at sep engagement data

@author: jc16287
"""

import matplotlib.pyplot as plt
import pandas as pd
import re
# from datetime import datetime as dt
# from datetime import timedelta
# import os
import tools_Parse_CAN_message
import tools_search_dbc
import tools_plot_or_export
import tools_sep_engage

folder_w_logs = 'D:\\101_a85854\\CAN_data'

log_name = '2310_cond9_run01.asc'

dbc_file_path_00 = r"D:\09 TOOLS\generated_dbc_7_179\PodB1.dbc"
dbc_file_path_01 = r"D:\09 TOOLS\generated_dbc_7_179\VehB1.dbc"

all_lines=open(folder_w_logs+'\\'+log_name).readlines()

CAN_message_all=[]

'''
read into dictionary results of dbc lookup, including all filtering and conversion values

you must put a space after signal name, that way signal names which are subsets of others dont trigger

put all this in a function, very clunky
'''

signals_ds_engage = [
    {"name": "EngineSpeed ", "dbc": dbc_file_path_00, "dict":{}, "time_series": []},
    {"name": "ThreshingSpeed ", "dbc": dbc_file_path_01, "dict":{}, "time_series": []},
    {"name": "SeparatorDrive ", "dbc": dbc_file_path_01, "dict":{}, "time_series": []}
    ]

signals_ds = [
    {"name": "EngineSpeed ", "dbc": dbc_file_path_00, "dict":{}, "time_series": []},
    {"name": "HarvEngageCmds2 ", "dbc": dbc_file_path_01, "dict":{}, "time_series": []}
    ]

'''
do the dbc search 
'''
for i in signals_ds_engage:
    i["dict"] = tools_search_dbc.find_signal(i["name"], i["dbc"])

start_time = 0
end_time = 800

for line in all_lines:
    if re.search("d\s[0-9]", line):
        
        current_message=tools_Parse_CAN_message.parse_pdu_regex(line)

        #we can filter the time series based on time stamp if we want
        if current_message.time_stamp < start_time or current_message.time_stamp > end_time:
            continue  

        #CAN_message_all.append(current_message)
        
        for j in signals_ds_engage:
            signal_possible = tools_search_dbc.filter_signal(current_message, j["dict"])
            
            if signal_possible != None:
                j["time_series"].append((current_message.time_stamp, signal_possible))
'''
now construct a dataframe to put the timeseries data into and add it to the list of dicts
'''

for k in signals_ds_engage:
    k["df"] = pd.DataFrame(k["time_series"], columns=['timestamp',k["name"]])
    tools_plot_or_export.plot_single_signal(k["name"], k["df"])
    
tools_sep_engage.find_min_engine_speed(signals_ds_engage)

'''
Merge the dataframes and export if desired
'''
big_tabel = tools_plot_or_export.combine_dfs_in_ds(signals_ds_engage)

tools_plot_or_export.export_df_csv(big_tabel, log_name ,r'../test_export/')