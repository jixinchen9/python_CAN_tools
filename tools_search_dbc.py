# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 16:31:45 2024

@author: jc16287

find signal function can find all parameters for filtering and converting 
CAN signal to data from a vector format CAN dbc

"""


def find_signal(signal_name,dbc_file_path):
    
    import re
    
    dbc_file=open(dbc_file_path)
    dbc_lines=dbc_file.readlines()
    
    
    signal_search_string="SG_ "+signal_name
    
    cmdbyte_regex="[m][0-9]{1,5}"
    startbit_regex=":[^:|]*\|"
    bitlength_regex="\|[^@|]*@"
    scalefactor_regex="\(([^\,]+)\,"
    offset_regex="\,([^\)]+)\)"
    
    message_id_regex="\d{4,16}"
    look_for_msg=False
    
    startbit_result=None
    bitlength_result=None
    scalefactor_result=None
    offset_result=None
    cmdbyte_raw_result=None
    cmd_byte_space_result=None
    message_id_result=None
    pgnsa_result=None
        
    for dbc_index, line in enumerate(reversed(dbc_lines)):
        signal_result=re.search(signal_search_string,line)
        if signal_result:
            print(dbc_index,line)
            startbit_query=re.search(startbit_regex,line)
            startbit_result=int(startbit_query.group().strip(":| "))
            
            bitlength_query=re.search(bitlength_regex,line)
            bitlength_result=int(bitlength_query.group().strip("|@ "))
            
            scalefactor_query=re.search(scalefactor_regex,line)
            scalefactor_result=float(scalefactor_query.group().strip("(, "))
            
            offset_query=re.search(offset_regex,line)
            offset_result=float(offset_query.group().strip(",) "))
            
            cmdbyte_query=re.search(cmdbyte_regex,line)
            
            '''
            duct tape alert: the writing of cmd byte needs more rigour
            '''
            
            if cmdbyte_query!=None:
                cmdbyte_raw_result=hex(int(cmdbyte_query.group().strip("m: ")))
                print(cmdbyte_raw_result)
                
                if len(cmdbyte_raw_result)==6:
                    cmd_byte_space_result=cmdbyte_raw_result[4:6]+" "+cmdbyte_raw_result[2:4]
                
                if len(cmdbyte_raw_result)==4:
                    cmd_byte_space_result=cmdbyte_raw_result[2:4]
                    
                if len(cmdbyte_raw_result)==5:
                    cmd_byte_space_result=cmdbyte_raw_result[3:5] + " 0"+ cmdbyte_raw_result[2]
            
                cmd_byte_space_result = cmd_byte_space_result.upper()
                
            look_for_msg=True
        
        if look_for_msg==True:
            message_of_signal=re.search("BO_",line)
            if message_of_signal:
                print(dbc_index,line)
                
                message_id_query=re.search(message_id_regex,line)
                message_id_result=hex(int(message_id_query.group()))
                pgnsa_result=message_id_result[-6:].upper()
                look_for_msg=False
                
            else:
                message_id_result="problem: signal w-o message"
                        
    dbc_result={
                "start bit":startbit_result,
                "bit length":bitlength_result,
                "scale factor":scalefactor_result,
                "offset":offset_result,
                "cmd byte raw":cmdbyte_raw_result,
                "cmd byte":cmd_byte_space_result,
                "full message id":message_id_result,
                "pgnsa":pgnsa_result
                }
    return dbc_result

'''
a brief demonstration::
'''

dbc_file_path=r"D:\Generated_DBC_09262024\VehB1.dbc"
signal_name="HarvEngageCmds2 "           
test01=find_signal(signal_name, dbc_file_path)

dbc_file_path=r"D:\Generated_DBC_09262024\PodB1.dbc"
signal_name="EngineSpeed "           
test02=find_signal(signal_name, dbc_file_path)

def filter_signal(CAN_msg_obj,signal_dictionary):

    if CAN_msg_obj.PGN_SA==signal_dictionary["pgnsa"] and (signal_dictionary["cmd byte"]==None or signal_dictionary["cmd byte"]==CAN_msg_obj.cmd_byte or signal_dictionary["cmd byte"]==CAN_msg_obj.cmd_byte_singleton):
        #print(CAN_msg_obj.time_stamp,CAN_msg_obj.PGN_SA)
        msg_byte = CAN_msg_obj.data_bytes
        #turn the can obj data byte string into bits
        msg_bit_nospace=bin(int(msg_byte.replace(" ",""),16))[2:].zfill(64)
        msg_bit_le=""
        number_of_data_bytes=len(msg_bit_nospace)//8

        #bits within a byte are fully reversed to ease indexing for little endian    
        for i in range(number_of_data_bytes):
            bits_be=msg_bit_nospace[8*i:8*i+8]
            #print('big endian:',bits_be)
            bits_le=bits_be[::-1]
            #print('little endian:',bits_le)
            msg_bit_le+=bits_le

        signal_bit_be=msg_bit_nospace[signal_dictionary["start bit"]:signal_dictionary["start bit"]+signal_dictionary["bit length"]]
        signal_bit_le=msg_bit_le[signal_dictionary["start bit"]:signal_dictionary["start bit"]+signal_dictionary["bit length"]]

        #when signal spans multiple data bytes, the bits must be combined less significant byte first and then converted
        if signal_dictionary["bit length"]>8:
            reversed_bit=""
            
            for i in range(len(signal_bit_be)//8):
                add_bits=signal_bit_be[-8:]
                reversed_bit+=add_bits
                signal_bit_be=signal_bit_be[:-8]
                #print(add_bits)
            
            signal_value=int(reversed_bit,2)*signal_dictionary["scale factor"]+signal_dictionary["offset"]

        #when bit length of signal is less than byte, then the correct bits are reversed to be converted
        if signal_dictionary["bit length"]<=8:
            signal_value=int(signal_bit_le[::-1],2)*signal_dictionary["scale factor"]+signal_dictionary["offset"]
        
        #print(signal_value)
        return(signal_value)

def filter_signal_new(CAN_msg_obj,signal_dictionary):
     #borked somethin here...
     
    msg_bit_nospace=bin( int( CAN_msg_obj.data_bytes.replace( " " , "" ) , 16 ))[2:].zfill(64)
    
    if CAN_msg_obj.PGN_SA==signal_dictionary["pgnsa"] and (signal_dictionary["cmd byte"]==None or signal_dictionary["cmd byte"]==CAN_msg_obj.cmd_byte or signal_dictionary["cmd byte"]==CAN_msg_obj.cmd_byte_singleton):
      
        signal_value = get_signal_value( msg_bit_nospace , signal_dictionary )
        
        return(signal_value)


def reverse_bits_by_byte (no_space_bitstring):
    
    msg_bit_le=""
    number_of_data_bytes=len(no_space_bitstring)//8
    
    #bits within a byte are fully reversed to ease indexing for little endian    
    
    for i in range(number_of_data_bytes):
        bits_be = no_space_bitstring[ 8*i : 8*i+8 ]
        #print('big endian:',bits_be)
        bits_le=bits_be[::-1]
        #print('little endian:',bits_le)
        msg_bit_le+=bits_le
    
    return msg_bit_le

def get_signal_value ( msg_bit_nospace , signal_dictionary):
    
    #may be cleanup potential in actual conversion portion
    
    msg_bit_le = reverse_bits_by_byte ( msg_bit_nospace )
    
    signal_bit_be = msg_bit_nospace[ signal_dictionary["start bit"] : signal_dictionary["start bit"] + signal_dictionary["bit length"] ]
    signal_bit_le = msg_bit_le[ signal_dictionary["start bit"] : signal_dictionary["start bit"] + signal_dictionary["bit length"] ]
    
    #when signal spans multiple data bytes, the bits must be combined less significant byte first and then converted
    if signal_dictionary["bit length"]>8:
        reversed_bit=""
        
        for i in range(len(signal_bit_be)//8):
            add_bits=signal_bit_be[-8:]
            reversed_bit+=add_bits
            signal_bit_be=signal_bit_be[:-8]
            #print(add_bits)
        
        signal_value=int( reversed_bit , 2) * signal_dictionary["scale factor"] + signal_dictionary["offset"]

    #when bit length of signal is less than byte, then the correct bits are reversed to be converted
    if signal_dictionary["bit length"]<=8:
        signal_value=int( signal_bit_le[::-1] , 2 ) * signal_dictionary["scale factor"] + signal_dictionary["offset"]
    
    #print(signal_value)
    return(signal_value) 
def filter_signal_test(CAN_msg_obj,signal_dictionary):

    if CAN_msg_obj.PGN_SA==signal_dictionary["pgnsa"] and (signal_dictionary["cmd byte"]==None or signal_dictionary["cmd byte"]==CAN_msg_obj.cmd_byte):
        #print(CAN_msg_obj.time_stamp,CAN_msg_obj.PGN_SA)
        msg_byte=CAN_msg_obj.data_bytes
        #turn the can obj data byte string into bits
        msg_bit_nospace=bin(int(msg_byte.replace(" ",""),16))[2:].zfill(64)
        msg_bit_le=""
        number_of_data_bytes=len(msg_bit_nospace)//8

        #bits within a byte are fully reversed to ease indexing for little endian    
        for i in range(number_of_data_bytes):
            bits_be=msg_bit_nospace[8*i:8*i+8]
            #print('big endian:',bits_be)
            bits_le=bits_be[::-1]
            #print('little endian:',bits_le)
            msg_bit_le+=bits_le

        signal_bit_be=msg_bit_nospace[test01["start bit"]:test01["start bit"]+test01["bit length"]]
        signal_bit_le=msg_bit_le[test01["start bit"]:test01["start bit"]+test01["bit length"]]

        #when signal spans multiple data bytes, the bits must be combined less significant byte first and then converted
        if test01["bit length"]>8:
            reversed_bit=""
            
            for i in range(len(signal_bit_be)//8):
                add_bits=signal_bit_be[-8:]
                reversed_bit+=add_bits
                signal_bit_be=signal_bit_be[:-8]
                #print(add_bits)
            
            signal_value=int(reversed_bit,2)*test01["scale factor"]+test01["offset"]

        #when bit length of signal is less than byte, then the correct bits are reversed to be converted
        if test01["bit length"]<=8:
            signal_value=int(signal_bit_le[::-1],2)*test01["scale factor"]+test01["offset"]
        
        #print(signal_value)
        return(signal_value)
        #pick out the bits relevant to signal
        #convert bits using offset and factor
        #return the signal value and og can msg
    
        #return an error
#"F0 FF 98 9C 28 FF F0 FF"
