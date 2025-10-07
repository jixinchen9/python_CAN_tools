# -*- coding: utf-8 -*-
"""
This script has functions to filter several signals, and analyze them'

'right now it's tailored to look at x9 1200 data

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

folder_w_logs = r'D:\098 misc field issue\x9 1200 vpf min pitch'

log_name = 'trimmed_power_meter_1200.asc'

dbc_file_path_00 = r"D:\09 TOOLS\1200_07_oct\PodB1.dbc"
dbc_file_path_01 = r"D:\09 TOOLS\generated_dbc_7_179\VehB1.dbc"
dbc_file_path_02 = r"D:\09 TOOLS\generated_dbc_7_179\PodB1.dbc"

all_lines=open(folder_w_logs+'\\'+log_name).readlines()

CAN_message_all=[]

'''
read into dictionary results of dbc lookup, including all filtering and conversion values

you must put a space after signal name, that way signal names which are subsets of others dont trigger

put all this in a function, very clunky
'''

signals_ds_engage = [
    {"name": "EngineSpeed ", "dbc": dbc_file_path_00, "dict":{}, "time_series": []},
    {"name": "DisplayedEnginePowerHighRes ", "dbc": dbc_file_path_01, "dict":{}, "time_series": []},
    {"name": "EngTorqueDerateSetpnt ", "dbc": dbc_file_path_00, "dict":{}, "time_series": []},
    {"name": "PercentLoadAtCurrentSpeed ", "dbc": dbc_file_path_02, "dict":{}, "time_series": []},
    {"name": "EnginesDesiredOperatingSpeed ", "dbc": dbc_file_path_02, "dict":{}, "time_series": []},
    {"name": "ConsumerShaftSpeedSetpoint ", "dbc": dbc_file_path_00, "dict":{}, "time_series": []},
    {"name": "HybridShaftSpeed ", "dbc": dbc_file_path_00, "dict":{}, "time_series": []},
    {"name": "HybridShaftPctLoadAtCurrentSpd ", "dbc": dbc_file_path_00, "dict":{}, "time_series": []}
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
    
def calc_display_correction_factor (enginespeed_error):
    
    UseCase1EngineError = 10
    UseCase2EngineErrorMin = 0
    UseCase2SpeedHysteresis = 10
    UseCase2EngineErrorMax = 100
    UseCase3EngineErrorMin = 100
    UseCase3EngineErrorMax = 200
    UseCase4EngineError = 200
    
    StartDarkGreenB = 100
    StartRedD = 110
    EndRedE = 114
    
    correct_factor = 100
    
    if (enginespeed_error <= UseCase1EngineError):
        
        correct_factor = StartDarkGreenB
        
    elif (enginespeed_error > (UseCase2EngineErrorMin + UseCase2SpeedHysteresis)
          and enginespeed_error <= UseCase2EngineErrorMax):
        
        correct_factor = StartDarkGreenB + (enginespeed_error - UseCase2EngineErrorMin)*(StartRedD - StartDarkGreenB)/(UseCase2EngineErrorMax - UseCase2EngineErrorMin)
        
    elif (enginespeed_error > UseCase3EngineErrorMin and enginespeed_error <= UseCase3EngineErrorMax):
        
        correct_factor = StartRedD + (enginespeed_error - UseCase3EngineErrorMin) * (EndRedE - StartRedD) / (UseCase3EngineErrorMax - UseCase3EngineErrorMin)
        
    elif enginespeed_error > UseCase4EngineError:
        
        correct_factor = EndRedE
    
    return correct_factor
    
#tools_sep_engage.find_min_engine_speed(signals_ds_engage)


'''

Merge the dataframes and export if desired
'''
big_tabel = tools_plot_or_export.combine_dfs_in_ds(signals_ds_engage)

big_tabel['engine_speed_error'] = big_tabel['ConsumerShaftSpeedSetpoint '] - big_tabel['HybridShaftSpeed ']

big_tabel['calc_display_correction_factor'] = big_tabel['engine_speed_error'].apply(calc_display_correction_factor)

big_tabel['calc_power_percent'] = big_tabel['calc_display_correction_factor'] * big_tabel['HybridShaftPctLoadAtCurrentSpd '] / big_tabel ['EngTorqueDerateSetpnt ']

tools_plot_or_export.export_df_csv(big_tabel, log_name ,folder_w_logs)