# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 09:20:57 2024

@author: jc16287

This toolbox contains functions that can fix timestamp issues, certain CAN adapters
can write messages in CANsniff with the same time stamp, or even write messages
non-chronologically

"""
def find_stutters(CAN_message_list,number_of_msg_per_window):
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

def fix_stutters(CAN_message_list,baud_rate,bits_per_message,first_time_stamp):
    
    Reference_min_time_interval=(bits_per_message-3)/baud_rate 
    length_of_interest_list=len(CAN_message_list)
    beginning_interval_list=[]
    imputed_interval_list=[]

    for index, message in enumerate(CAN_message_list):
        if index+1>=length_of_interest_list:
            break
        

        time_stamp_difference=CAN_message_list[index+1].time_stamp-message.time_stamp
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


