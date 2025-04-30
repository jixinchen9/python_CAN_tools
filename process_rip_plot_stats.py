# -*- coding: utf-8 -*-
"""
This script has functions to filter several signals, and analyze them'

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

folder_w_logs = 'D:\\088 a117040\\data\\CAN'

log_name = 'nom_condition7_run02.asc'

# 'D:\\085 100perc power at new default high idle'
# 'Logger_c4-00-ad-49-ec-fa_2025-02-18_173609_00282_GQM.asc'
dbc_file_path_00 = r"D:\Generated_DBC_09262024\PodB1.dbc"
dbc_file_path_01 = r"D:\Generated_DBC_09262024\VehB1.dbc"

all_lines=open(folder_w_logs+'\\'+log_name).readlines()

CAN_message_all=[]

'''
read into dictionary results of dbc lookup, including all filtering and conversion values

put all this in a function, very clunky
'''

signals_ds = [
    {"name": "EngineSpeed ", "dbc": dbc_file_path_00, "dict":{}, "time_series": []},
    {"name": "FlexpwrReq ", "dbc": dbc_file_path_00, "dict":{}, "time_series": []},
    {"name": "HarvEngageCmds2 ", "dbc": dbc_file_path_01, "dict":{}, "time_series": []}
    ]

signals_ds_other = [
    {"name": "EngineSpeed ", "dbc": dbc_file_path_00, "dict":{}, "time_series": []},
    {"name": "HarvEngageCmds2 ", "dbc": dbc_file_path_01, "dict":{}, "time_series": []}
    ]

for i in signals_ds:
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
        
        for j in signals_ds:
            signal_possible = tools_search_dbc.filter_signal(current_message, j["dict"])
            
            if signal_possible != None:
                j["time_series"].append((current_message.time_stamp, signal_possible))

for k in signals_ds:
    k["df"] = pd.DataFrame(k["time_series"], columns=['timestamp',k["name"]])
    tools_plot_or_export.plot_single_signal(k["name"], k["df"])
    

Min_EngineSpeed = signals_ds[0]["df"][signals_ds[0]["name"]].min()
min_speed_idx = signals_ds[0]["df"][signals_ds[0]["name"]].idxmin()
min_speed_tst = signals_ds[0]["df"].loc[min_speed_idx, 'timestamp']

print("Min EngineSpeed over interval is: ", Min_EngineSpeed)

recovery_search_df = signals_ds[0]["df"][min_speed_idx:]
recovery_index = recovery_search_df[recovery_search_df[signals_ds[0]["name"]]>1700].index[0]
recovery_tst = recovery_search_df.loc[recovery_index, 'timestamp']

print("Recovery Time is: ", recovery_tst - min_speed_tst)


'''
Merge the dataframes if desired
'''

'''
combined_signals_df = signals_ds[0]["df"].merge(signals_ds[1]["df"], how='outer', on='timestamp')
combined_signals_df = combined_signals_df.merge(signals_ds[2]["df"], how='outer', on='timestamp')
combined_signals_df = combined_signals_df.fillna(method='bfill')
'''
folder_w_exports = 'D:\\088 a117040\\data\\exported_channel\\'
export_label = "_lockup_sep_drive"
export_name = folder_w_exports + log_name.replace(".asc","") + export_label + ".csv"
#combined_signals_df.to_csv(export_name)