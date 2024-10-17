# -*- coding: utf-8 -*-
"""
This script has functions to filter out a piece of info from a CAN log, it is also 
set up to run the filtering on all logs in a folder

other functions include writing time series with real US central time using time stamps
and beginning times in each log

@author: jc16287
"""

import matplotlib.pyplot as plt
import pandas as pd
import tools_Parse_CAN_message
import tools_get_data
import tools_set_bytes
import tools_fix_timestamps
# from datetime import datetime as dt
# from datetime import timedelta
# import os


channel_of_interest=str(20)
meter_b=100
meter_c=108
meter_d=111
meter_e=114
engine_speed_desired=2200   #add from desired engspd eventually to be 100% right
baud_rate=500000   
bits_per_message=131
Reference_min_time_interval=(bits_per_message-3)/baud_rate

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

# file1=open(r"D:\049 def tank level ncca\zip-2024-05-07T14_05_40.421Z\Logger_c4-00-ad-7c-0c-1f_2023-12-07_220320_00129_GQM_split_00001.asc","r")
# all_lines=file1.readlines()

def calc_display_power(engspd,pctld):
    enginespeed_error=engine_speed_desired-engspd

    if enginespeed_error <=10:
        correction_factor=meter_b

    if enginespeed_error >10 and enginespeed_error<= 100:
        correction_factor=(enginespeed_error/100)*(meter_d-meter_b)+meter_b
        
    if enginespeed_error>100 and enginespeed_error <=200:
        correction_factor=(enginespeed_error/100)*(meter_e-meter_d)+meter_d
        
    if enginespeed_error>200:
        correction_factor=meter_e

    display_power_percent=correction_factor*pctld/100
    return display_power_percent

folder_w_logs='D:\\027 unstable engine speed\\e174815'
log_name='Defects 345 PM.asc'
all_lines=open(folder_w_logs+'\\'+log_name).readlines()

#Verify that messages are being parsed correctly
test_msgs=[]
for i in range(20,40):
    # d8_result=all_lines[i].find("d 8")
    message1=all_lines[i]
    print(all_lines[i])
    parsed_msg=tools_Parse_CAN_message.parse_pdu(all_lines[i],message_indices)
    test_msgs.append(parsed_msg)

unobject_test_msgs=tools_Parse_CAN_message.show_CAN_list(test_msgs)

CAN_message_all=[]

enginespeed_timeseries=[]
pctldspd_timeseries=[]
displayed_power_timeseries=[]

#what do displayed power percent high res messages look like?:
power_perc_chan="2"
power_perc_rxtx="Rx"
power_perc_priority="14"
power_perc_pgnsa="FFFB5B"
power_perc_pgn="FFFB"
power_perc_sa="5B"
power_perc_cmdbyte="01 15"

#decide what frequency in Hz we want to generate fake messages, can only choose lower than 
#percent load at current speed frequency
pct_load_counter=0
pctld_freq=50
hi_res_desired_frequency=5


#find the starting time stamp
for line in all_lines:
    d8_result=line.find("d 8")
    if d8_result!=-1:
        first_time_stamp=float(line[slice(d8_result-33,d8_result-22)])
        break

for line in all_lines:
    d8_result=line.find("d 8")
    if d8_result==-1:
        continue
    current_message=tools_Parse_CAN_message.parse_pdu(line, message_indices)
    #we can filter the time series based on time stamp
    if current_message.time_stamp>350 or current_message.time_stamp<290:
        continue
    
    # uncomment to delete original power meter messages
    # if commandbyte=="01 15":
    #     continue
    
    CAN_message_all.append(current_message)
    
    if current_message.PGN_SA == 'F00400':
        enginespeed=tools_get_data.calc_enginespeed(current_message.data_bytes)
        enginespeed_tuple=(current_message.time_stamp,enginespeed)
        enginespeed_timeseries.append(enginespeed_tuple)
    
    if current_message.PGN_SA == 'F00300':
        pctldspd=tools_get_data.calc_perc_load(current_message.data_bytes)
        pctldspd_tuple=(current_message.time_stamp,pctldspd)
        pctldspd_timeseries.append(pctldspd_tuple)
        
        displayed_power=calc_display_power(enginespeed,pctldspd)
        displayed_power_tuple=(current_message.time_stamp,displayed_power)
        displayed_power_timeseries.append(displayed_power_tuple)
        
        power_perc_data=tools_set_bytes.gen_power_percent_data_bytes(displayed_power)
        generated_power_perc_msg=tools_Parse_CAN_message.CAN_message(power_perc_pgnsa,power_perc_pgn, power_perc_sa, current_message.time_stamp, power_perc_cmdbyte, power_perc_data, power_perc_chan, power_perc_rxtx, current_message.time_stamp,power_perc_priority)

        # uncomment to actually write the generated messages at a given frequency
        # a counter has been added to modify fake mesg generation frequency
    
        if pct_load_counter%(pctld_freq/hi_res_desired_frequency)==0:
            CAN_message_all.append(generated_power_perc_msg)
        pct_load_counter+=1

#stutters_or_faked=find_stutters(CAN_message_all)

CAN_message_all.sort(key=tools_Parse_CAN_message.CAN_message.sort_priority)

Msg_timestamp_spaced=tools_fix_timestamps.fix_stutters(CAN_message_all, baud_rate,bits_per_message,first_time_stamp)
#check_things_out=show_CAN_list(CAN_message_all)

opened_log_original=tools_Parse_CAN_message.show_CAN_list(Msg_timestamp_spaced)
str_list_finish_CAN=[]

for message in Msg_timestamp_spaced:
    timestamp_str=f"{message.time_stamp_1:11.11}"
    log_this_line=timestamp_str+" "+message.channel+"  "+message.priority+message.PGN_SA+"x"+"    "+message.rxtx+"   d 8 "+message.data_bytes
    str_list_finish_CAN.append(log_this_line)
    
f = open('5Hz_power_meter_001_290-350s.asc', 'w')
f.writelines("\n".join(str_list_finish_CAN))
f.close()

enginespeed_timeseries_df=pd.DataFrame(enginespeed_timeseries,columns=['Time_Stamp','Engine_Speed'])
pctldspd_timeseries_df=pd.DataFrame(pctldspd_timeseries,columns=['Time_Stamp','Percent_Load_at_Speed'])
displayed_power_timeseries_df=pd.DataFrame(displayed_power_timeseries,columns=['Time_Stamp','Display_Power'])

enginespeed_timeseries_df.plot(x='Time_Stamp',y='Engine_Speed', kind='scatter')
pctldspd_timeseries_df.plot(x='Time_Stamp',y='Percent_Load_at_Speed', kind='scatter')
displayed_power_timeseries_df.plot(x='Time_Stamp',y='Display_Power', kind='scatter')
plt.show()