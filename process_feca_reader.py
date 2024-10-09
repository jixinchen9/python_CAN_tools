# -*- coding: utf-8 -*-
"""
This script has functions to find FECA and FECB active and stored codes

@author: jc16287
"""



# import matplotlib.pyplot as plt
# import pandas as pd
# from datetime import datetime as dt
# from datetime import timedelta
# import os
import tools_Parse_CAN_message
import tools_get_data

channel_of_interest=str(20)
baud_rate=500000   
bits_per_message=131
Reference_min_time_interval=(bits_per_message-3)/baud_rate

time_format='%H:%M:%S.%f'
time_format='%H:%M:%S.%f'
message_indices={'tst_0':0,
                 'tst_1':-25,
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
# file1=open(r"D:\049 def tank level ncca\zip-2024-05-07T14_05_40.421Z\Logger_c4-00-ad-7c-0c-1f_2023-12-07_220320_00129_GQM_split_00001.asc","r")
file1=open(r"D:\CANlog_area\Machine_ECU_Comm_Issue10-4_20241008.121849.asc","r")
all_lines=file1.readlines()

#uncomment this part to check if the script can slice/extract the object attributes correctly

CAN_message_all=[]

for i in range(20,40):
    CAN_message_all.append(tools_Parse_CAN_message.parse_pdu(all_lines[i], message_indices))
    
parse_test=tools_Parse_CAN_message.show_CAN_list(CAN_message_all)

DTC_active_set=set()
DTC_stored_set=set()

for line in all_lines:
    d8_result=line.find("d 8")
    if d8_result==-1:
        continue

    #we can filter the time series based on time stamp
    
    # if timestamp>350 or timestamp<290:
    #     continue
        
    current_message=tools_Parse_CAN_message.parse_pdu(line, message_indices)
    CAN_message_all.append(current_message)
    
    if current_message.PGN == "FECA":
        dtc_sa=current_message.SA
        dtc_spn,dtc_fmi=tools_get_data.get_dtc_spnfmi(current_message.data_bytes)
        dtc_tuple=(dtc_sa,dtc_spn,dtc_fmi)
        print(dtc_tuple)
        dtc_exists_in_result=dtc_tuple in DTC_active_set
        if dtc_tuple[1] != 0 and dtc_exists_in_result == False:
            DTC_active_set.add(dtc_tuple)
    
    if current_message.PGN == "FECB":
        dtc_sa=current_message.SA
        dtc_spn,dtc_fmi=tools_get_data.get_dtc_spnfmi(current_message.data_bytes)
        dtc_tuple=(dtc_sa,dtc_spn,dtc_fmi)
        print(dtc_tuple)
        dtc_exists_in_result=dtc_tuple in DTC_stored_set
        if dtc_tuple[1] != 0 and dtc_exists_in_result == False:
            DTC_stored_set.add(dtc_tuple)
            
        
