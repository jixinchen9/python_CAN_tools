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

time_format='%H:%M:%S.%f'

# file1=open(r"D:\049 def tank level ncca\zip-2024-05-07T14_05_40.421Z\Logger_c4-00-ad-7c-0c-1f_2023-12-07_220320_00129_GQM_split_00001.asc","r")
# all_lines=file1.readlines()

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
            time_stamp_1,
            priority
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
        self.priority = priority
        #this attribute is for the purpose of generating time stamps
    def sort_priority(self):
        return self.time_stamp



def show_CAN_list(CAN_message_list):
    CAN_list_un_object=[]
    for message in CAN_message_list:
        CAN_list_un_object.append((message.time_stamp, message.time_stamp_1, message.channel, message.PGN_SA,message.data_bytes))
    return(CAN_list_un_object)

def calc_def_level(can_data_bytes):
    def_percent_bytes="0x"+can_data_bytes[slice(6,8)]
    def_tank_percent=int(def_percent_bytes,16)*0.4
    return def_tank_percent

def calc_perc_load(can_data_bytes):
    pctldspd_bytes="0x"+can_data_bytes[slice(6,8)]
    pctldspd=int(pctldspd_bytes,16)*1.0
    return pctldspd

def calc_enginespeed(can_data_bytes):
    engspd_bytes="0x"+can_data_bytes[slice(12,14)]+can_data_bytes[slice(9,11)]
    engspd=int(engspd_bytes,16)*0.125
    return engspd

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

def gen_power_percent_data_bytes (power_percent_float):

    data_hex_str=str.upper(
        hex(
            int(
                round(power_percent_float/.002,0)
                )
            )
        )

    DisplayedEnginePowerHighRes_data_bytes="01 15 "+data_hex_str[slice(4,6)]+" "+data_hex_str[slice(2,4)]+" FF FF FF FF"
    return DisplayedEnginePowerHighRes_data_bytes

def find_stutters(CAN_message_list):
    stutter_found_list=[]
    stutter_total_length=0

    length_of_interest_list=len(CAN_message_list)

    for index, message in enumerate(CAN_message_list):
        if index+1>=length_of_interest_list:
            break
        
        time_stamp_difference=CAN_message_list[index+1].time_stamp-message.time_stamp
        if time_stamp_difference ==0.000000:
            stutter_found_list.append((message.time_stamp,message.PGN_SA,message.data_bytes))
            stutter_total_length+=1
    return(stutter_found_list,stutter_total_length)

folder_w_logs='D:\\027 unstable engine speed\\e174815'
log_name='Defects 345 PM.asc'
all_lines=open(folder_w_logs+'\\'+log_name).readlines()



#uncomment this part to check if the script can slice/extract the object attributes correctly

# for i in range(2682204,2682224):
#     d8_result=all_lines[i].find("d 8")
#     space_result=all_lines[i].find(" ")
#     message1=all_lines[i]
#     print(all_lines[i])
#     print("d 8 index:",d8_result,"space index:",space_result)
#     print("timestamp is:", message1[slice(0,d8_result-22)])
#     print("PGN is:", message1[slice(d8_result-16,d8_result-12)])
#     print("SA is:", message1[slice(d8_result-12,d8_result-10)])
#     print("PGN_SA is:", message1[slice(d8_result-16,d8_result-10)])
#     print("cmd byte is:", message1[slice(d8_result+4,d8_result+9)])
#     print("data bytes is:", message1[slice(d8_result+4,d8_result+27)])
#     print("channel is:", message1[slice(d8_result-21,d8_result-20)])
#     print("rxtx is:", message1[slice(d8_result-5,d8_result-3)])
#     print("priority is:", message1[slice(d8_result-18,d8_result-16)])

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
    
    timestamp=float(line[slice(0,d8_result-22)])  
    pgn=line[slice(d8_result-16,d8_result-12)]
    sa=line[slice(d8_result-12,d8_result-10)]
    pgnsa=line[slice(d8_result-16,d8_result-10)]
    commandbyte=line[slice(d8_result+4,d8_result+9)]
    data=line[slice(d8_result+4,d8_result+27)]
    chan=line[slice(d8_result-21,d8_result-20)]
    receiver_trans=line[slice(d8_result-5,d8_result-3)]
    timestamp1=float(line[slice(0,d8_result-22)]) 
    priority=line[slice(d8_result-18,d8_result-16)]
    
    #we can filter the time series based on time stamp
    if timestamp>350 or timestamp<290:
        continue
    # uncomment to delete original power meter messages
    # if commandbyte=="01 15":
    #     continue
    
    current_message=CAN_message(pgnsa, pgn, sa, timestamp, commandbyte, data,chan,receiver_trans,timestamp1, priority)
    CAN_message_all.append(current_message)
    
    if pgnsa == 'F00400':
        enginespeed=calc_enginespeed(data)
        enginespeed_tuple=(timestamp,enginespeed)
        enginespeed_timeseries.append(enginespeed_tuple)
    
    if pgnsa == 'F00300':
        pctldspd=calc_perc_load(data)
        pctldspd_tuple=(timestamp,pctldspd)
        pctldspd_timeseries.append(pctldspd_tuple)
        
        displayed_power=calc_display_power(enginespeed,pctldspd)
        displayed_power_tuple=(timestamp,displayed_power)
        displayed_power_timeseries.append(displayed_power_tuple)
        
        power_perc_data=gen_power_percent_data_bytes(displayed_power)
        generated_power_perc_msg=CAN_message(power_perc_pgnsa,power_perc_pgn, power_perc_sa, timestamp, power_perc_cmdbyte, power_perc_data, power_perc_chan, power_perc_rxtx, timestamp1,power_perc_priority)
        '''
        uncomment to actually write the generated messages at a given frequency
        a counter has been added to modify fake mesg generation frequency
    
        '''
        
        if pct_load_counter%(pctld_freq/hi_res_desired_frequency)==0:
            CAN_message_all.append(generated_power_perc_msg)
        pct_load_counter+=1

#stutters_or_faked=find_stutters(CAN_message_all)

def fix_stutters(CAN_message_list):
    
    length_of_interest_list=len(CAN_message_list)
    beginning_interval_list=[]
    imputed_interval_list=[]

    for index, message in enumerate(CAN_message_list):
        if index+1>=length_of_interest_list:
            break
        

        time_stamp_difference=CAN_message_list[index+1].time_stamp-message.time_stamp
        beginning_interval_list.append(time_stamp_difference)
        #the above build a list of all time stamp intervals for entire log
        if time_stamp_difference <=0.00005:
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
    return CAN_message_list



CAN_message_all.sort(key=CAN_message.sort_priority)

Msg_timestamp_spaced=fix_stutters(CAN_message_all)
#check_things_out=show_CAN_list(CAN_message_all)

opened_log_original=show_CAN_list(Msg_timestamp_spaced)
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

# #build the generation of the DEF tank percent into a pandas df
# def get_def_tank_level_1log(opened_log):
#     CAN_list_interested=[]
#     def_tank_level_timeseries=[]
    
#     for line in opened_log:
#         d8_result=line.find("d 8")
#         dec7_result=line.find("Dec")
        
#         if dec7_result !=-1:
#             beginning_time_day=int(line[slice(dec7_result+3,dec7_result+5)])
#             beginning_time_string=line[slice(dec7_result+6,dec7_result+14)]+".0"
#             beginning_time=dt.strptime(beginning_time_string,time_format)+timedelta(days=45265+beginning_time_day-7)
        
#         if d8_result==-1:
#             continue
        
#         pgnsa=line[slice(d8_result-19,d8_result-13)]
#         pgn=line[slice(d8_result-19,d8_result-15)]
#         sa=line[slice(d8_result-15,d8_result-13)]
#         timestamp=float(line[slice(0,d8_result-26)])
#         commandbyte=line[slice(d8_result+4,d8_result+9)]
#         data=line[slice(d8_result+4,d8_result+27)]
#         chan=line[slice(d8_result-25,d8_result-23)]
#         receiver_trans=line[slice(d8_result-5,d8_result-3)]
        
#         timestamp1=0.000000
        
#         current_message=CAN_message(pgnsa, pgn, sa, timestamp, commandbyte, data,chan,receiver_trans,timestamp1)
        
#         #CAN_message_object_list.append(current_message)
        
#         #filter the messages during list creation for a list of relevant CAN message objects
#         if chan == channel_of_interest and pgnsa == pgnsa_of_interest:
#             CAN_list_interested.append(current_message)
            
#             #calculate the def tank level from the data bytes and build the timeseries
#             def_tank_level_tuple=(timestamp,calc_def_level(data),beginning_time-timedelta(hours=6)+timedelta(seconds=timestamp))
#             def_tank_level_timeseries.append(def_tank_level_tuple)
#     def_tank_level_timeseries_df=pd.DataFrame(def_tank_level_timeseries,columns=['Log Timestamp','DEF tank Percent','USChicago Timestamp'])
#     return(CAN_list_interested,def_tank_level_timeseries_df)

'''
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
'''