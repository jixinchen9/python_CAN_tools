# -*- coding: utf-8 -*-
"""
This script has functions to filter out a piece of info from a CAN log, that's about it'

@author: jc16287
"""



import matplotlib.pyplot as plt
import pandas as pd
# from datetime import datetime as dt
# from datetime import timedelta
# import os
import tools_Parse_CAN_message
import tools_search_dbc
import re

channel_of_interest=str(20)
baud_rate=500000   
bits_per_message=131
Reference_min_time_interval=(bits_per_message-3)/baud_rate

folder_w_logs='D:\\066 shutdown_all_629_31\dourado'
log_name='h2389_shutdown_log_001_07292024.asc'
dbc_file_path=r"D:\Generated_DBC_09262024\PodB1.dbc"

all_lines=open(folder_w_logs+'\\'+log_name).readlines()

CAN_message_all=[]

signal_interested_val_0_timeseries=[]

signal_interested_0="EngineSpeed " #put in name of signal exactly as it appears in the CAN spreadsheet, with a space at end to exclude names which are subsets
signal_interested_0_dict=tools_search_dbc.find_signal(signal_interested_0, dbc_file_path)

for line in all_lines:
    if re.search("d\s[0-9]", line):
        
        current_message=tools_Parse_CAN_message.parse_pdu_regex(line)

    #we can filter the time series based on time stamp if we want
    # if current_message.time_stamp>1 or current_message.time_stamp<10:
    #     continue  

        CAN_message_all.append(current_message)

        signal_interested_val_0=tools_search_dbc.filter_signal(current_message, signal_interested_0_dict)
        if signal_interested_val_0 != None:
            signal_interested_val_0_timeseries.append((current_message.time_stamp, signal_interested_val_0))

signal_interested_0_df=pd.DataFrame(signal_interested_val_0_timeseries,columns=['timestamp','EngineSpeed'])

signal_interested_0_df.plot(y='EngineSpeed',label='DMA blocks average Busload',kind='line')
plt.xlabel('Time')
plt.ylabel('EngineSpeed')
plt.title('Signal_Interested')
plt.show()