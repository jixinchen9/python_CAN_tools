# -*- coding: utf-8 -*-
"""
This script has functions to filter out a piece of info from a CAN log, it is also 
set up to run the filtering on all logs in a folder

@author: jc16287
"""



import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import os
import tools_Parse_CAN_message
import tools_get_data


channel_of_interest=str(20)
pgnsa_of_interest="FE5600"

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
                 'channel_0':-25,
                 'channel_1':-23,
                 'rxtx_0':-5,
                 'rxtx_1':-3,
                 'priority_0':-18,
                 'priority_1':-16,
                 }

file1=open(r"D:\049 def tank level ncca\zip-2024-05-07T14_05_40.421Z\Logger_c4-00-ad-7c-0c-1f_2023-12-07_220320_00129_GQM_split_00001.asc","r")
all_lines=file1.readlines()

#uncomment this part to check if the script can slice/extract the object attributes correctly
test_msgs=[]
for i in range(20,40):
    # d8_result=all_lines[i].find("d 8")
    message1=all_lines[i]
    print(all_lines[i])
    parsed_msg=tools_Parse_CAN_message.parse_pdu(all_lines[i],message_indices)
    test_msgs.append(parsed_msg)

unobject_test_msgs=tools_Parse_CAN_message.show_CAN_list(test_msgs)


#build the generation of the DEF tank percent into a pandas df
def get_def_tank_level_1log(opened_log):
    CAN_list_interested=[]
    def_tank_level_timeseries=[]
    
    for line in opened_log:
        d8_result=line.find("d 8")
        dec7_result=line.find("Dec")
        
        if dec7_result !=-1:
            beginning_time_day=int(line[slice(dec7_result+3,dec7_result+5)])
            beginning_time_string=line[slice(dec7_result+6,dec7_result+14)]+".0"
            beginning_time=dt.strptime(beginning_time_string,time_format)+timedelta(days=45265+beginning_time_day-7)
        
        if d8_result==-1:
            continue
        
        current_message=tools_Parse_CAN_message.parse_pdu(line, message_indices)
        
        #CAN_message_object_list.append(current_message)
        
        #filter the messages during list creation for a list of relevant CAN message objects
        if current_message.channel == channel_of_interest and current_message.PGN_SA == pgnsa_of_interest:
            CAN_list_interested.append(current_message)
            
            #calculate the def tank level from the data bytes and build the timeseries with generated time stamps
            def_tank_level_tuple=(current_message.time_stamp,tools_get_data.calc_def_level(current_message.data_bytes),beginning_time-timedelta(hours=6)+timedelta(seconds=current_message.time_stamp))
            def_tank_level_timeseries.append(def_tank_level_tuple)
    def_tank_level_timeseries_df=pd.DataFrame(def_tank_level_timeseries,columns=['Log Timestamp','DEF tank Percent','USChicago Timestamp'])
    return(CAN_list_interested,def_tank_level_timeseries_df)

folder_w_logs='D:\\049 def tank level ncca\\zip-2024-05-07T14_05_40.421Z'
log_filename_list=os.listdir(folder_w_logs)
log_fullpath_list=[]
all_logs_result=[]

for i in log_filename_list:
    log_fullpath_list.append(folder_w_logs+'\\'+i)
    lines=open(folder_w_logs+'\\'+i).readlines()
    this_log_result=get_def_tank_level_1log(lines)
    all_logs_result.append(this_log_result[1])
    print(i,"has been analysed for def_tank_level")

concat_logs_df=pd.concat(all_logs_result)
# def_message_check_unobj=show_CAN_list(this_log_result[0])

concat_logs_df.plot(x='USChicago Timestamp',y='DEF tank Percent', kind='scatter')
plt.figure(figsize=(10,10))
plt.xlabel('US Chicago Time')
plt.xticks(rotation='vertical')
plt.ylabel('DEF tank level %')
plt.show()

concat_logs_df.to_csv('12-07_def_tank_time_series.csv')

