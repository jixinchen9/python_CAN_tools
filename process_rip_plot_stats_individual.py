# -*- coding: utf-8 -*-
"""
This script has functions to filter out a piece of info from a CAN log, that's about it'

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


log_name = 'condition2_run01.asc'
# 'D:\\085 100perc power at new default high idle'
# 'Logger_c4-00-ad-49-ec-fa_2025-02-18_173609_00282_GQM.asc'
dbc_file_path_00 = r"D:\Generated_DBC_09262024\PodB1.dbc"
dbc_file_path_01 = r"D:\Generated_DBC_09262024\VehB1.dbc"

all_lines=open(folder_w_logs+'\\'+log_name).readlines()

CAN_message_all=[]

'''
read into dictionary results of dbc lookup, including all filtering and conversion values
'''

signal_interested_0="EngineSpeed " #put in name of signal exactly as it appears in the CAN spreadsheet, with a space at end to exclude names which are subsets
signal_interested_0_dict=tools_search_dbc.find_signal(signal_interested_0, dbc_file_path_00)
signal_interested_val_0_timeseries=[]

signal_interested_1="DisplayedEnginePowerHighRes " #put in name of signal exactly as it appears in the CAN spreadsheet, with a space at end to exclude names which are subsets
signal_interested_1_dict=tools_search_dbc.find_signal(signal_interested_1, dbc_file_path_01)
signal_interested_val_1_timeseries=[]

start_time = 0
end_time = 800

for line in all_lines:
    if re.search("d\s[0-9]", line):
        
        current_message=tools_Parse_CAN_message.parse_pdu_regex(line)

        #we can filter the time series based on time stamp if we want
        if current_message.time_stamp < start_time or current_message.time_stamp > end_time:
            continue  

        #CAN_message_all.append(current_message)
        
        '''
        filter for the signals of interest and create a list of tuples of form (timestamp, result)
        '''
        
        signal_interested_val_0=tools_search_dbc.filter_signal(current_message, signal_interested_0_dict)
        if signal_interested_val_0 != None:
            signal_interested_val_0_timeseries.append((current_message.time_stamp, signal_interested_val_0))
            
        signal_interested_val_1=tools_search_dbc.filter_signal(current_message, signal_interested_1_dict)
        if signal_interested_val_1 != None:
            #print(current_message.time_stamp, current_message.PGN_SA, current_message.data_bytes, " le bit")
            signal_interested_val_1_timeseries.append((current_message.time_stamp, signal_interested_val_1))

signal_interested_0_df=pd.DataFrame(signal_interested_val_0_timeseries,columns=['timestamp',signal_interested_0])

signal_interested_1_df=pd.DataFrame(signal_interested_val_1_timeseries,columns=['timestamp',signal_interested_1])

Mean_displayed_engine_power = signal_interested_1_df[signal_interested_1].mean()

print("Mean DisplayedEnginePowerHighRes over interval is: ", Mean_displayed_engine_power)


tools_plot_or_export.plot_single_signal(signal_interested_0, signal_interested_0_df)
tools_plot_or_export.plot_single_signal(signal_interested_1, signal_interested_1_df)

folder_w_exports = 'D:\\088 a117040\\data\\CAN\\exported_channel\\'
export_name = folder_w_exports + log_name.replace(".asc","") + ".csv"
signal_interested_0_df.to_csv(export_name)