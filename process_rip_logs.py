# -*- coding: utf-8 -*-
"""
This script has functions to filter out a piece of info from a CAN log, that's about it'

@author: jc16287
"""



# import matplotlib.pyplot as plt
# import pandas as pd
# from datetime import datetime as dt
# from datetime import timedelta
# import os
import tools_Parse_CAN_message
import tools_search_dbc

channel_of_interest=str(20)
baud_rate=500000   
bits_per_message=131
Reference_min_time_interval=(bits_per_message-3)/baud_rate

time_format='%H:%M:%S.%f'
message_indices={'tst_0':0,
                 'tst_1':-22,
                 'pgn_0':-16,
                 'pgn_3':-12,
                 'sa_0':-12,
                 'sa_1':-10,
                 'pgnsa_0':-16,
                 'pgnsa_5':-10,
                 'cmd_0':4,
                 'cmd_4':9,
                 'data_0':4,
                 'data_23':27,
                 'channel_0':-21,
                 'channel_1':-20,
                 'rxtx_0':-5,
                 'rxtx_1':-3,
                 'priority_0':-18,
                 'priority_1':-16,
                 }

folder_w_logs='D:\\066 shutdown_all_629_31\dourado'
log_name='h2389_shutdown_log_001_07292024.asc'
dbc_file_path=r"D:\Generated_DBC_09262024\PodB1.dbc"

all_lines=open(folder_w_logs+'\\'+log_name).readlines()

#uncomment this part to check if the script can slice/extract the object attributes correctly
test_msgs=[]
for i in range(20,40):
    # d8_result=all_lines[i].find("d 8")
    message1=all_lines[i]
    print(all_lines[i])
    parsed_msg=tools_Parse_CAN_message.parse_pdu(all_lines[i],message_indices)
    test_msgs.append(parsed_msg)

unobject_test_msgs=tools_Parse_CAN_message.show_CAN_list(test_msgs)
# print("type of pgnsa att:", type(test_msgs[1].PGN_SA))

CAN_message_all=[]
DTC_active_set=set()
DTC_stored_set=set()
authentication_response=[]

signal_interested_val_0_timeseries=[]

#find the starting time stamp
for line in all_lines:
    d8_result=line.find("d 8")
    if d8_result!=-1:
        first_time_stamp=float(line[slice(0,d8_result-25)])
        break

signal_interested_0="FlexpwrReq " #put in name of signal exactly as it appears in the CAN spreadsheet, with a space at end to exclude names which are subsets
signal_interested_0_dict=tools_search_dbc.find_signal(signal_interested_0, dbc_file_path)

for line in all_lines:
    
    current_message=tools_Parse_CAN_message.parse_pdu(line, message_indices)
    
    if current_message is None:
        continue
    
    #we can filter the time series based on time stamp if we want
    # if current_message.time_stamp>1 or current_message.time_stamp<10:
    #     continue  
    
    #print(line)
    CAN_message_all.append(current_message)
    # try:
    signal_interested_val_0=tools_search_dbc.filter_signal(current_message, signal_interested_0_dict)
    if signal_interested_val_0 != None:
        signal_interested_val_0_timeseries.append(signal_interested_val_0)
    # except:
    #     continue

    # if current_message.PGN == "EF06" and current_message.cmd_byte=="64 16":
    #     authentication_response.append(current_message)

authentication_response_unobject=tools_Parse_CAN_message.show_CAN_list(authentication_response)