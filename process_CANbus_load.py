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
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

number_of_msg_per_window=20     #the number of messages per window 
baud_rate=500000                
channel_of_interest=str(2)
dma_end_byte=0x5C               #the last message of the DMA transport protocol will always have the same 1st byte
bits_per_message=131
Reference_min_time_interval=(bits_per_message-3)/baud_rate  #used in 'fixing' time stamp errors

file1=open(r"D:\027 unstable engine speed\ngpd_power_percent_comparison_06262024\generated_power_meter_003_290-350s_long.asc","r")
all_lines=file1.readlines()

class CAN_message:
    def __init__(
            self,
            PGN_SA,
            PGN,
            SA,
            time_stamp,
            cmd_byte,
            data_bytes,
            channel,
            rxtx,
            time_stamp_1   #this is a false/blank timestamp added so that we have a parameter to add generated times tamps to if needed
            ):
        self.PGN_SA = PGN_SA
        self.PGN = PGN
        self.SA = SA
        self.time_stamp = time_stamp
        self.cmd_byte = cmd_byte
        self.data_bytes = data_bytes
        self.channel = channel
        self.rxtx = rxtx
        self.time_stamp_1 = time_stamp_1
    def sort_priority(self):
        return self.time_stamp


#uncomment this part to check if the script can slice/extract the object attributes correctly

for i in range(20):
    d8_result=all_lines[i].find("d 8")
    space_result=all_lines[i].find(" ")
    message1=all_lines[i]
    print(all_lines[i])
    print("d 8 index:",d8_result,"space index:",space_result)
    print("PGN_SA is:", message1[slice(d8_result-16,d8_result-10)])
    print("PGN is:", message1[slice(d8_result-16,d8_result-12)])
    print("SA is:", message1[slice(d8_result-12,d8_result-10)])
    print("timestamp is:", message1[slice(d8_result-32,d8_result-22)])
    print("cmd byte is:", message1[slice(d8_result+4,d8_result+9)])
    print("data bytes is:", message1[slice(d8_result+4,d8_result+27)])
    print("channel is:", message1[slice(d8_result-22,d8_result-20)])
    print("rxtx is:", message1[slice(d8_result-5,d8_result-3)])

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

    pgnsa=line[slice(d8_result-16,d8_result-10)]
    pgn=line[slice(d8_result-16,d8_result-12)]
    sa=line[slice(d8_result-12,d8_result-10)]
    timestamp=float(line[slice(d8_result-32,d8_result-22)])
    commandbyte=line[slice(d8_result+4,d8_result+9)]
    data=line[slice(d8_result+4,d8_result+27)]
    chan=line[slice(d8_result-21,d8_result-20)]
    receiver_trans=line[slice(d8_result-5,d8_result-3)]
    timestamp1=0.000000
    current_message=CAN_message(pgnsa, pgn, sa, timestamp, commandbyte, data,chan,receiver_trans,timestamp1)
    CAN_message_object_list.append(current_message)
    
    #filter the messages during list creation for a list of relevant CAN message objects
    if chan == channel_of_interest and receiver_trans == "Rx":
        CAN_list_interested.append(current_message)
    firstbyte=line[slice(d8_result+4,d8_result+6)]
    
    #filter out the ending and stopping messages of the DMA blocks
    # if pgnsa == "EFFA00" and chan==channel_of_interest and (int(firstbyte,16)==0 or int(firstbyte,16)==int(dma_end_byte)):
    #     CAN_list_mgdl_tp.append(current_message)
        
    #Find out how long in duration(s) the log is
    if timestamp>previous_timestamp:
        last_time_stamp=timestamp
    #sometimes the timestamps reset at 0, '5' here as a comparator is kind of arbitrary
    if timestamp+5<previous_timestamp:
        False_last_timestamp=previous_timestamp
    previous_timestamp=timestamp

#finding the time length of log, continued:
if False_last_timestamp>0.000000:
    log_length_seconds=False_last_timestamp-first_time_stamp+last_time_stamp
else:
    log_length_seconds=last_time_stamp-first_time_stamp

CAN_list_interested.sort(key=CAN_message.sort_priority)

def creeping_window_func(message_unit_measure,baud_rate,log_length,CAN_object_list):
    length_of_interest_list=len(CAN_object_list)

    
    creeping_window_busload_timeseries=[]
    max_busload_creep=0.000000
    percent_sum_subset=0.000000
    creep_busload_avg_subset=0.000000
    
    for index, message in enumerate(CAN_object_list):
        if index+message_unit_measure>=length_of_interest_list:
            break

        time_stamp_difference=CAN_object_list[index+message_unit_measure-1].time_stamp-message.time_stamp
        # this line is in here so execution doesnt stop if there is a timestamp stutter
        # the value of 1e-6 is chosen to form a unrealistic high busload to alert the data reviewer
        if time_stamp_difference ==0.000000:
            time_stamp_difference=1e-6
        
        busload_this_window=100*(message_unit_measure*bits_per_message)/(time_stamp_difference*baud_rate)
        percent_timetotal_this_window=100*time_stamp_difference/(log_length*message_unit_measure)
        
        creep_window_busload_tuple=(message.time_stamp,busload_this_window,percent_timetotal_this_window)
        creeping_window_busload_timeseries.append(creep_window_busload_tuple)
        
        if busload_this_window > max_busload_creep:
            max_busload_creep=busload_this_window
        
        creep_busload_avg_subset+=busload_this_window*percent_timetotal_this_window*0.01
        percent_sum_subset+=percent_timetotal_this_window
            
    creep_busload_average_timebased=100*creep_busload_avg_subset/percent_sum_subset
    import pandas as pd

    creep_window_df=pd.DataFrame(creeping_window_busload_timeseries,columns=['Time_Stamp','Bus_Load_Percent','Percent_time_of_Total'])
    
    return(max_busload_creep,creep_busload_average_timebased,creep_window_df,percent_sum_subset,creep_busload_avg_subset,)

#function calls can just be
#a,b,c,d =function(args)
#if functions return A, B, C, D

def creeping_window_func_impute(message_unit_measure,baud_rate,log_length,CAN_object_list):
    #i think i separated these out before i came up with the time stamp generator
    #ignore for now
    length_of_interest_list=len(CAN_object_list)
    CAN_message_size=131
    
    creeping_window_busload_timeseries=[]
    max_busload_creep=0.000000
    percent_sum_subset=0.000000
    creep_busload_avg_subset=0.000000
    
    for index, message in enumerate(CAN_object_list):
        if index+message_unit_measure>=length_of_interest_list:
            break
        time_stamp_difference=CAN_object_list[index+message_unit_measure-1].time_stamp_1-message.time_stamp_1
        # this line is in here so execution doesnt stop if there is a timestamp stutter
        # the value of 1e-6 is chosen to form a unrealistic high busload to alert the data reviewer
        if time_stamp_difference ==0.000000:
            time_stamp_difference=1e-9
        
        busload_this_window=100*(message_unit_measure*CAN_message_size)/(time_stamp_difference*baud_rate)
        percent_timetotal_this_window=100*time_stamp_difference/(log_length*message_unit_measure)
        
        creep_window_busload_tuple=(message.time_stamp,busload_this_window,percent_timetotal_this_window)
        creeping_window_busload_timeseries.append(creep_window_busload_tuple)
        
        if busload_this_window > max_busload_creep:
            max_busload_creep=busload_this_window
        creep_busload_avg_subset+=busload_this_window*percent_timetotal_this_window*0.01
        percent_sum_subset+=percent_timetotal_this_window
            
    creep_busload_average_timebased=100*creep_busload_avg_subset/percent_sum_subset
    import pandas as pd

    creep_window_df=pd.DataFrame(creeping_window_busload_timeseries,columns=['Time_Stamp','Bus_Load_Percent','Percent_time_of_Total'])
    
    return(max_busload_creep,creep_busload_average_timebased,creep_window_df,percent_sum_subset,creep_busload_avg_subset,)

def creeping_window_func_lite(message_unit_measure,baud_rate,log_length,CAN_object_list):
    #this function is lite in that it does not return a time series for each block of messages
    #it is executed on, it only returns the avg and max busload, it is otherwise identical
    
    length_of_interest_list=len(CAN_object_list)
    
    max_busload_creep=0.000000
    creep_busload_avg_subset=0.000000
    percent_sum_subset=0.000000
    
    #declare block based 
    
    for index, message in enumerate(CAN_object_list):
        if index+message_unit_measure>=length_of_interest_list:
            break
        time_stamp_difference=CAN_object_list[index+message_unit_measure-1].time_stamp-message.time_stamp
        if time_stamp_difference ==0.000000:
            time_stamp_difference=1e-6
        busload_this_window=100*(message_unit_measure*bits_per_message)/(time_stamp_difference*baud_rate)
        percent_timetotal_this_window=100*time_stamp_difference/(log_length*message_unit_measure)

        if busload_this_window > max_busload_creep:
            max_busload_creep=busload_this_window
        
        creep_busload_avg_subset+=busload_this_window*percent_timetotal_this_window*0.01
        percent_sum_subset+=percent_timetotal_this_window
    
    creep_busload_average_timebased=100*creep_busload_avg_subset/percent_sum_subset
    return(max_busload_creep,creep_busload_average_timebased,log_length)

def creeping_window_func_lite_impute(message_unit_measure,baud_rate,log_length,CAN_object_list):
    length_of_interest_list=len(CAN_object_list)
    
    max_busload_creep=0.000000
    creep_busload_avg_subset=0.000000
    percent_sum_subset=0.000000
    
    #declare block based 
    
    for index, message in enumerate(CAN_object_list):
        if index+message_unit_measure<length_of_interest_list:
            time_stamp_difference=CAN_object_list[index+message_unit_measure-1].time_stamp_1-message.time_stamp_1
            # this line is in here so execution doesnt stop if there is a timestamp stutter
            # the value of 1e-6 is chosen to form a unrealistic high busload to alert the data reviewer
            if time_stamp_difference ==0.000000:
                time_stamp_difference=1e-9
            busload_this_window=100*(message_unit_measure*bits_per_message)/(time_stamp_difference*baud_rate)
            percent_timetotal_this_window=100*time_stamp_difference/(log_length*message_unit_measure)

            if busload_this_window > max_busload_creep:
                max_busload_creep=busload_this_window
            
            creep_busload_avg_subset+=busload_this_window*percent_timetotal_this_window*0.01
            percent_sum_subset+=percent_timetotal_this_window
    
    creep_busload_average_timebased=100*creep_busload_avg_subset/percent_sum_subset
    return(max_busload_creep,creep_busload_average_timebased,log_length)

def show_CAN_list(CAN_message_list):
    CAN_list_un_object=[]
    for message in CAN_message_list:
        CAN_list_un_object.append((message.time_stamp, message.time_stamp_1, message.channel, message.PGN_SA,message.data_bytes))
    return(CAN_list_un_object)

'''
time stamps in CANsniff logs are written by the CAN adapter, during this test
the use of EDL v2 created stutters in the log, places where multiple CAN
messages were written in the log with the same timestamp, impossible on a
serial network. use of vector CANcase completely avoids this issue, below 
functions check log for stuttering and impute minimum time intervals if/when
stutter is found
'''

def find_stutters(CAN_message_list):
    stutter_found_list=[]
    stutter_total_length=0

    length_of_interest_list=len(CAN_message_list)

    for index, message in enumerate(CAN_message_list):
        if index+number_of_msg_per_window>=length_of_interest_list:
            break
        
        time_stamp_difference=CAN_message_list[index+1].time_stamp-message.time_stamp
        if time_stamp_difference < 0.000200:
            stutter_found_list.append((message.time_stamp,message.PGN_SA,message.data_bytes))
            stutter_total_length+=1
    return(stutter_found_list,stutter_total_length)

#call the function to show the stutters

stutters_all=find_stutters(CAN_list_interested)
check_stutter_before=show_CAN_list(CAN_list_interested)

##fix stutters if we want

def fix_stutters(CAN_message_list):
    
    length_of_interest_list=len(CAN_message_list)
    beginning_interval_list=[]
    imputed_interval_list=[]

    for index, message in enumerate(CAN_message_list):
        if index+1>=length_of_interest_list:
            break
        

        time_stamp_difference=CAN_list_interested[index+1].time_stamp-message.time_stamp
        beginning_interval_list.append(time_stamp_difference)
        #the above build a list of all time stamp intervals for entire log
        if time_stamp_difference <=0.000000:
            imputed_interval_list.append(Reference_min_time_interval)
        else:
            imputed_interval_list.append(time_stamp_difference)
        #this part builds an alternate list of intervals, one where zeros
        #are replaced by the minimum time interval
    CAN_message_list[0].time_stamp_1=first_time_stamp
    
    for index, message in enumerate(CAN_message_list):    
        if index==1:
            CAN_message_list[index].time_stamp_1=first_time_stamp+imputed_interval_list[0]
        elif index>1:
            CAN_message_list[index].time_stamp_1=CAN_message_list[index-1].time_stamp_1+imputed_interval_list[index-1]
        #this part writes an alternate list of time stamps to the fake timestamp
        #parameter in the CAN_message object, it does this by adding the alternate
        #imputed interval list to the starting timestamp
    return(CAN_message_list)
'''
Decide if we want to fix the stutters
'''

# CAN_list_interested=fix_stutters(CAN_list_interested)
# check_stutter_after=show_CAN_list(CAN_list_interested)

#the following lines run creeping window on the entire log and present the result

creep_all=creeping_window_func(number_of_msg_per_window, baud_rate,log_length_seconds,CAN_list_interested)
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

#the following lines plot results of series with generated time stamps
'''
creep_all_imputed=creeping_window_func_impute(number_of_msg_per_window, baud_rate,log_length_seconds,CAN_list_interested)
creep_all_imputed[2].plot(x='Time_Stamp',y='Bus_Load_Percent', kind='scatter')
plt.xlabel('Time (s)')
plt.ylabel('Bus Load %')
plt.title('Bus Load Time Series of Entire Log using generated Timestamps')
plt.show()

busload_wholelog_df_imp=creep_all_imputed[2]
Busload_bins=np.linspace(0,100,41)
plt.figure(figsize=(11,5))
plt.hist(busload_wholelog_df_imp['Bus_Load_Percent'], bins=Busload_bins, weights=busload_wholelog_df_imp['Percent_time_of_Total'])
plt.xlabel('Bus Load Bin')
plt.xticks(np.arange(0,105, 5.0))
plt.ylabel('Percent of time at Load')
plt.title('Bus Load Histogram of Entire Log using generated Timestamps')
plt.show()

check_block_edges=show_CAN_list(CAN_list_mgdl_tp) 

'''
#verify that the script picked up the DMA start stops

#the below code runs creeping window on pieces of the main log cut based on whether DMA is happening

dma_block_result_list=[]
less_dma_result_list=[]
dma_block_result_list_imp=[]
less_dma_result_list_imp=[]
number_of_DMA_blocks=0

# for index, message in enumerate(CAN_list_mgdl_tp):
#     if index<(len(CAN_list_mgdl_tp)-2) and index%2==0:
#         #establish boundaries of the block
#         dma_block_begin_time=CAN_list_mgdl_tp[index].time_stamp
#         dma_block_end_time=CAN_list_mgdl_tp[index+1].time_stamp
#         less_dma_begin_time=dma_block_end_time
#         less_dma_end_time=CAN_list_mgdl_tp[index+2].time_stamp
#         dma_block_message_list=[]
#         less_dma_block_message_list=[]
        
#         dma_block_length=dma_block_end_time-dma_block_begin_time
#         less_dma_block_length=less_dma_end_time-less_dma_begin_time

#         #carve the block out of the main log
#         for message in CAN_list_interested:
#             if message.time_stamp>=dma_block_begin_time and message.time_stamp<=dma_block_end_time:
#                 dma_block_message_list.append(message)
#             if message.time_stamp>=less_dma_begin_time and message.time_stamp<=less_dma_end_time:
#                 less_dma_block_message_list.append(message)
        
#         #run creeping windows *lite* on the blocks
#         dma_block_result=creeping_window_func_lite(number_of_msg_per_window, baud_rate, dma_block_length , dma_block_message_list)
#         less_dma_block_result=creeping_window_func_lite(number_of_msg_per_window, baud_rate, less_dma_block_length, less_dma_block_message_list)

#         dma_block_result_list.append(dma_block_result)
#         less_dma_result_list.append(less_dma_block_result)
        
#         '''
#         run creeping windows lite on the generated time stamps if desired
#         '''
#         dma_block_result_imp=creeping_window_func_lite_impute(number_of_msg_per_window, baud_rate, dma_block_length , dma_block_message_list)
#         less_dma_block_result_imp=creeping_window_func_lite_impute(number_of_msg_per_window, baud_rate, less_dma_block_length, less_dma_block_message_list)
        
#         dma_block_result_list_imp.append(dma_block_result_imp)
#         less_dma_result_list_imp.append(less_dma_block_result_imp)
        
#         #end optional lines
        
#         number_of_DMA_blocks+=1
'''
the below lines present results of dma block analysis
'''
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

'''
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