# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 16:31:45 2024

@author: jc16287

find signal function can find all parameters for filtering and converting 
CAn signal to data from a vector format CAN dbc

"""

dbc_file_path=r"D:\Generated_DBC_09262024\PodB1.dbc"
signal_name="TransmissionCmdLimOp "


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
    cmdbyte_result=None
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
            
            if cmdbyte_query!=None:
                cmdbyte_result=hex(int(cmdbyte_query.group().strip("m: ")))
            
            look_for_msg=True
        
        if look_for_msg==True:
            message_of_signal=re.search("BO_",line)
            if message_of_signal:
                print(dbc_index,line)
                
                message_id_query=re.search(message_id_regex,line)
                message_id_result=hex(int(message_id_query.group()))
                pgnsa_result=message_id_result[-6:]
                look_for_msg=False
                
            else:
                message_id_result="problem: signal w-o message"
                        
    dbc_result={
                "start bit":startbit_result,
                "bit length":bitlength_result,
                "scale factor":scalefactor_result,
                "offset":offset_result,
                "cmd byte":cmdbyte_result,
                "full message id":message_id_result,
                "pgnsa":pgnsa_result
                }
    return dbc_result
            
test01=find_signal(signal_name, dbc_file_path)