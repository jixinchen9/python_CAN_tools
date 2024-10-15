# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 10:52:52 2024

@author: jc16287
"""

def creeping_window_func(message_unit_measure,baud_rate,log_length,CAN_object_list,bits_per_message):
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

def creeping_window_func_lite(message_unit_measure,baud_rate,log_length,CAN_object_list,bits_per_message):
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

def creeping_window_func_lite_impute(message_unit_measure,baud_rate,log_length,CAN_object_list,bits_per_message):
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