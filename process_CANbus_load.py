# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 09:12:29 2024

@author: jc16287

This script grew out of an experiment to find out how much traffic MG data logger
adds to the CAN bus. to answer this broad question this script does a few things

1.creeping windows:
    this is a simple calculation where bus load is determined by finding the difference
    in time between a window of 'n' messages, it is creeping because it is iterated
    through the entire can log, creating a time series of bus load.

2.creeping windows on DMA and non-DMA intervals:
    from observing the log we know that DMA messages from the ECU to the MG are 
    sent with transport protocol messages. the transport protocol are scheduled
    onto the bus as fast as possible and dominate bus traffic within a certain
    time interval. these transport protocol bursts repeat every second corresponding
    to Mg samlping interval.
    the script finds the beginning and ending time stamps of each burst, splitting 
    the log into DMA and non_DMA intervals, creeping windows calculation is then
    run on these intervals.

3.Fix timestamp errors caused by inadequate CAN adapter:
    CAN logs created by CANsniff have the time stamp written by the CAN adapter. 
    the vector CANcase is the superior adapter, logs created with EDL have timestamp 
    errors where multiple messages have the same time stamp. this is called a 'stutter'
    in this script. this script can optionally fix stutters by replacing detected '0'
    intervals with min time intervals.
        EDL also does not start every log at '0', once you write enough logs the 
        timestamps overflow and this can be observed as the time stamp going to '0'
        in the middle of a log.
        The demo log used here is not a problem log.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tools_Parse_CAN_message
import tools_busload
import tools_fix_timestamps

number_of_msg_per_window=20     #the number of messages per window 
baud_rate=500000                
channel_of_interest=str(2)
dma_end_byte=0x5C               #the last message of the DMA transport protocol will always have the same 1st byte
bits_per_message=131
Reference_min_time_interval=(bits_per_message-3)/baud_rate  #used in 'fixing' time stamp errors

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

#file1=open(r"D:\027 unstable engine speed\ngpd_power_percent_comparison_06262024\generated_power_meter_003_290-350s_long.asc","r")
file1=open(r"D:\10_devX_ppg and even flos\JC_python_CAN_tools\demo_logs\CAN bus load\DMA_Z2215_400TGT_450MS_04232024_001.asc","r")
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

#find the starting time stamp
for line in all_lines:
    d8_result=line.find("d 8")
    if d8_result!=-1:
        first_time_stamp=float(line[slice(d8_result-32,d8_result-22)])
        break
    
CAN_message_object_list=[]      #create list of CAN message objects of every message
CAN_list_interested=[]          #create list of CAN messages on the right channel and rx/tx
CAN_list_mgdl_tp=[]             #create list of CAN message objects that contain the beginning and end of DMA burst

last_time_stamp=0.000000
previous_timestamp=0.000000
False_last_timestamp=0.000000

#convert the lines of log into list of CAN message objects

for line in all_lines:
    d8_result=line.find("d 8")
    space_result=line.find(" ")
    if d8_result == -1:
        continue

    current_message=tools_Parse_CAN_message.parse_pdu(line,message_indices)
    #CAN_message_object_list.append(current_message)
    
    #filter the messages during list creation for a list of relevant CAN message objects
    if current_message.channel == channel_of_interest and current_message.rxtx == "Rx":
        CAN_list_interested.append(current_message)
    firstbyte=line[slice(d8_result+4,d8_result+6)]
    
    #filter out the ending and stopping messages of the DMA blocks
    if current_message.PGN_SA == "EFFA00" and current_message.channel==channel_of_interest and (int(firstbyte,16)==0 or int(firstbyte,16)==int(dma_end_byte)):
        CAN_list_mgdl_tp.append(current_message)
        
    #Find out how long in duration(s) the log is
    if current_message.time_stamp>previous_timestamp:
        last_time_stamp=current_message.time_stamp
    #sometimes the timestamps reset at 0, '5' here as a comparator is kind of arbitrary
    if current_message.time_stamp+5<previous_timestamp:
        False_last_timestamp=previous_timestamp
    previous_timestamp=current_message.time_stamp

#finding the time length of log, continued:
if False_last_timestamp>0.000000:
    log_length_seconds=False_last_timestamp-first_time_stamp+last_time_stamp
else:
    log_length_seconds=last_time_stamp-first_time_stamp

CAN_list_interested.sort(key=tools_Parse_CAN_message.CAN_message.sort_priority)
#Sort here just in case adapter messed up some time stamps

'''
time stamps in CANsniff logs are written by the CAN adapter, during this test
the use of EDL v2 created stutters in the log, places where multiple CAN
messages were written in the log with the same timestamp, impossible on a
serial network. use of vector CANcase completely avoids this issue, below 
functions check log for stuttering and impute minimum time intervals if/when
stutter is found
'''

'''
Decide if we want to fix the stutters
'''
# stutter_list=tools_fix_timestamps.find_stutters(CAN_list_interested, number_of_msg_per_window)
# CAN_list_interested=tools_fix_timestamps.fix_stutters(CAN_list_interested)
# check_stutter_after=tools_Parse_CAN_message.show_CAN_list(CAN_list_interested)
'''
the following lines run creeping window on the entire log and present the result
'''


creep_all=tools_busload.creeping_window_func(number_of_msg_per_window, baud_rate,log_length_seconds,CAN_list_interested,bits_per_message)
creep_all[2].plot(x='Time_Stamp',y='Bus_Load_Percent', kind='scatter')
plt.xlabel('Time (s)')
plt.ylabel('Bus Load %')
plt.title('Bus Load Time Series of Entire Log')
plt.show()

busload_wholelog_df=creep_all[2]
Busload_bins=np.linspace(0,100,41)
plt.figure(figsize=(11,5))
plt.hist(busload_wholelog_df['Bus_Load_Percent'], bins=Busload_bins, weights=busload_wholelog_df['Percent_time_of_Total'])
#histogram is weighted, each bus load data point has a weight equal to percent time of total log
plt.xlabel('Bus Load Bin')
plt.xticks(np.arange(0,105, 5.0))
plt.ylabel('Percent of time at Load')
plt.title('Bus Load Histogram of Entire Log 50hz sim')
plt.show()


#verify that the script picked up the DMA start stops
check_block_edges=tools_Parse_CAN_message.show_CAN_list(CAN_list_mgdl_tp) 
#the below code runs creeping window on pieces of the main log cut based on whether DMA is happening

dma_block_result_list=[]
less_dma_result_list=[]
dma_block_result_list_imp=[]
less_dma_result_list_imp=[]
number_of_DMA_blocks=0

for index, message in enumerate(CAN_list_mgdl_tp):
    if index<(len(CAN_list_mgdl_tp)-2) and index%2==0:
        #establish boundaries of the block
        dma_block_begin_time=CAN_list_mgdl_tp[index].time_stamp
        dma_block_end_time=CAN_list_mgdl_tp[index+1].time_stamp
        less_dma_begin_time=dma_block_end_time
        less_dma_end_time=CAN_list_mgdl_tp[index+2].time_stamp
        dma_block_message_list=[]
        less_dma_block_message_list=[]
        
        dma_block_length=dma_block_end_time-dma_block_begin_time
        less_dma_block_length=less_dma_end_time-less_dma_begin_time

        #carve the block out of the main log
        for message in CAN_list_interested:
            if message.time_stamp>=dma_block_begin_time and message.time_stamp<=dma_block_end_time:
                dma_block_message_list.append(message)
            if message.time_stamp>=less_dma_begin_time and message.time_stamp<=less_dma_end_time:
                less_dma_block_message_list.append(message)
        
        #run creeping windows *lite* on the blocks
        dma_block_result=tools_busload.creeping_window_func_lite(number_of_msg_per_window, baud_rate, dma_block_length , dma_block_message_list, bits_per_message)
        less_dma_block_result=tools_busload.creeping_window_func_lite(number_of_msg_per_window, baud_rate, less_dma_block_length, less_dma_block_message_list, bits_per_message)

        dma_block_result_list.append(dma_block_result)
        less_dma_result_list.append(less_dma_block_result)
        
        '''
        run creeping windows lite on the generated time stamps if desired
        '''
        # dma_block_result_imp=creeping_window_func_lite_impute(number_of_msg_per_window, baud_rate, dma_block_length , dma_block_message_list)
        # less_dma_block_result_imp=creeping_window_func_lite_impute(number_of_msg_per_window, baud_rate, less_dma_block_length, less_dma_block_message_list)
        
        # dma_block_result_list_imp.append(dma_block_result_imp)
        # less_dma_result_list_imp.append(less_dma_block_result_imp)
        
        #end optional lines
        
        number_of_DMA_blocks+=1
'''
the below lines present results of dma block analysis
'''

dma_block_result_list_df=pd.DataFrame(dma_block_result_list,columns=['Max_Busload','Avg_Busload','Block_length'])
less_dma_result_list_df=pd.DataFrame(less_dma_result_list,columns=['Max_Busload','Avg_Busload','Block_length'])

dma_block_result_list_df.plot(y='Avg_Busload',label='DMA blocks average Busload',kind='line')
plt.xlabel('Block')
plt.ylabel('Bus Load %')
plt.title('Bus Load Time Series of DMA blocks')
plt.show()

less_dma_result_list_df.plot(y='Avg_Busload',label='Less DMA blocks average Busload',kind='line')
plt.xlabel('Block')
plt.ylabel('Bus Load %')
plt.title('Bus Load Time Series of Less DMA blocks')
plt.show()

dma_block_average_of_average=dma_block_result_list_df.mean(axis=0)
less_dma_block_average_of_average=less_dma_result_list_df.mean(axis=0)


#the below lines present results of dma block analysis with generated timestamps
'''

dma_block_result_list_imp_df=pd.DataFrame(dma_block_result_list_imp,columns=['Max_Busload','Avg_Busload','Block_length'])
less_dma_result_list_imp_df=pd.DataFrame(less_dma_result_list_imp,columns=['Max_Busload','Avg_Busload','Block_length'])

dma_block_result_list_imp_df.plot(y='Avg_Busload',label='DMA blocks average Busload w Generated Timestamps',kind='line')
plt.xlabel('Block')
plt.ylabel('Bus Load %')
plt.title('Bus Load Time Series of DMA blocks')
plt.show()

less_dma_result_list_imp_df.plot(y='Avg_Busload',label='Less DMA blocks average Busload w Generated Timestamps',kind='line')
plt.xlabel('Block')
plt.ylabel('Bus Load %')
plt.title('Bus Load Time Series of Less DMA blocks')
plt.show()

dma_block_average_of_average_imp=dma_block_result_list_imp_df.mean(axis=0)
less_dma_block_average_of_average_imp=less_dma_result_list_imp_df.mean(axis=0)

check_dma_block=show_CAN_list(dma_block_message_list)

'''