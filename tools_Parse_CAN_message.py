# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 09:02:59 2024

@author: jc16287

Collection of Basic CAN log parsing functions; including the CAN message class
and extraction of class parameters from one line of CAN log
"""

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

def parse_pdu(line,data_index):
    d8_result=line.find("d 8")
    if d8_result==-1:
        return None
    
    timestamp=float(line[slice(0,d8_result+data_index['tst_1'])])  
    pgn=line[slice(d8_result+data_index['pgn_0'],d8_result+data_index['pgn_3'])]
    sa=line[slice(d8_result+data_index['sa_0'],d8_result+data_index['sa_1'])]
    pgnsa=line[slice(d8_result+data_index['pgnsa_0'],d8_result+data_index['pgnsa_5'])]
    commandbyte=line[slice(d8_result+data_index['cmd_0'],d8_result+data_index['cmd_4'])]
    data=line[slice(d8_result+data_index['data_0'],d8_result+data_index['data_23'])]
    chan=line[slice(d8_result+data_index['channel_0'],d8_result+data_index['channel_1'])]
    receiver_trans=line[slice(d8_result+data_index['rxtx_0'],d8_result+data_index['rxtx_1'])]
    timestamp1=float(line[slice(0,d8_result+data_index['tst_1'])]) 
    priority=line[slice(d8_result+data_index['priority_0'],d8_result+data_index['priority_1'])]
    
    current_message=CAN_message(pgnsa, pgn, sa, timestamp, commandbyte, data,chan,receiver_trans,timestamp1, priority)
    return(current_message)
    

def show_CAN_list(CAN_message_list):
    CAN_list_un_object=[]
    for message in CAN_message_list:
        CAN_list_un_object.append((message.time_stamp, message.time_stamp_1, message.channel, message.PGN_SA,message.data_bytes,message.cmd_byte))
    return(CAN_list_un_object)
