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

channel_of_interest=str(20)
baud_rate=500000   
bits_per_message=131
Reference_min_time_interval=(bits_per_message-3)/baud_rate

time_format='%H:%M:%S.%f'
message_indices={'tst_0':0,
                 'tst_1':-25,
                 'pgn_0':-19,
                 'pgn_3':-15,
                 'sa_0':-15,
                 'sa_1':-13,
                 'pgnsa_0':-19,
                 'pgnsa_5':-13,
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

folder_w_logs='D:\\064 2006_14 sometimes\\Post install both machines'
log_name='Logger_c4-00-ad-ea-26-51_2024-09-19_210834_00084_GQM.asc'
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


CAN_message_all=[]
DTC_active_set=set()
DTC_stored_set=set()
authentication_response=[]

# enginespeed_timeseries=[]
# pctldspd_timeseries=[]


# #what do displayed power percent high res messages look like?:
# power_perc_chan="2"
# power_perc_rxtx="Rx"
# power_perc_priority="14"
# power_perc_pgnsa="FFFB5B"
# power_perc_pgn="FFFB"
# power_perc_sa="5B"
# power_perc_cmdbyte="01 15"


#find the starting time stamp
for line in all_lines:
    d8_result=line.find("d 8")
    if d8_result!=-1:
        first_time_stamp=float(line[slice(0,d8_result-25)])
        break

for line in all_lines:
    

    
      
    current_message=tools_Parse_CAN_message.parse_pdu(line, message_indices)
    
    if current_message is None:
        continue
    
    #we can filter the time series based on time stamp if we want
    # if current_message.time_stamp>350 or current_message.time_stamp<100:
    #     continue  
    
    CAN_message_all.append(current_message)
    
    if current_message.PGN == "EF06" and current_message.cmd_byte=="64 16":
        authentication_response.append(current_message)

authentication_response_unobject=tools_Parse_CAN_message.show_CAN_list(authentication_response)