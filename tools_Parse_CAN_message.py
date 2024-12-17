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

def parse_pdu_regex (line):

    import re
    
    byte_amount_regex = "d\s[0-9]"
    source_address_regex = "[0-9,a-z][0-9,a-z]x"
    timestamp_regex = "[0-9]+\.[0-9]+"
    channel_regex = " [0-9]+ "
    rxtx_regex = "[r-t]x"
    

    
    '''
    execute the regex querys
    '''
    
    byte_amount_query = re.search(byte_amount_regex , line)
    byte_amount_indices = byte_amount_query.span()
    
    source_address_query = re.search(source_address_regex , line, re.IGNORECASE)
    source_address_indices = source_address_query.span()
    
    rxtx_query = re.search(rxtx_regex, line, re.IGNORECASE)
    
    timestamp_query = re.search(timestamp_regex , line)
    
    channel_query = re.search(channel_regex , line)
    
    
    '''
    find parameters without use of regex
    '''
    #specify string indices of the pgn using the regex result of source address
    pgn_slice = slice(source_address_indices[0]-4,source_address_indices[0])
    priority_slice = slice(source_address_indices[0]-6,source_address_indices[0]-4)
    
    #find how many data bytes there are from the regex search result
    byte_amount_result = int(byte_amount_query.group()[-1:])
    
    #slice out data bytes starting from the end of byte number field and based on number 
    #of bytes. command bytes isnt rigorous (wont always be 2 bytes), will improve
    data_bytes_slice = slice(byte_amount_indices[1]+1,byte_amount_indices[1]+byte_amount_result*3)
    cmd_bytes_slice = slice(byte_amount_indices[1]+1,byte_amount_indices[1]+2*3)
    
    '''
    assign to CAN parameters using regex search results or other methods
    '''
    
    timestamp = float(timestamp_query.group())
    channel = channel_query.group().strip()
    source_address = source_address_query.group().rstrip('x')
    rxtx = rxtx_query.group()
    pgn = line[pgn_slice]
    pgn_and_sa = pgn + source_address
    priority = line[priority_slice]
    data_bytes = line[data_bytes_slice]
    cmd_bytes = line[cmd_bytes_slice]
    
    '''
    feed parsed strings into CAN_message objects
    '''
    current_message=CAN_message(pgn_and_sa, pgn, source_address, timestamp, cmd_bytes, data_bytes , channel ,rxtx ,timestamp, priority)
    #current_message = pgn_and_sa + " " + str(timestamp) + " " + data_bytes + "channel: " + channel + rxtx
    return(current_message)

test_line_01 = "   0.003325 1  08EFFF5Bx    Rx   d 8 64 57 2F FF FF 00 00 FF "
test_line_02 = "2619.825513 20  18FFF886x       Rx   d 8 9B FD 7C 04 64 80 1A 00"
test_output =  parse_pdu_regex(test_line_02)


def show_CAN_list(CAN_message_list):
    CAN_list_un_object=[]
    for message in CAN_message_list:
        CAN_list_un_object.append((message.time_stamp, message.time_stamp_1, message.channel, message.PGN_SA,message.data_bytes,message.cmd_byte))
    return(CAN_list_un_object)

'''
everything beyond here is old and obsolete; parse_pdu function will be deleted after last process is updated,
everything should use regex based parsing function
'''
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

'''
#the old parse pdu required a manual index data structure like this to work::
    
time_format='%H:%M:%S.%f'
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

#you could do something like this to check the output of manual parsing setup

#uncomment this part to check if the script can slice/extract the object attributes correctly
test_msgs=[]
for i in range(20,40):
    # d8_result=all_lines[i].find("d 8")
    message1=all_lines[i]
    print(all_lines[i])
    parsed_msg=tools_Parse_CAN_message.parse_pdu(all_lines[i],message_indices)
    test_msgs.append(parsed_msg)

unobject_test_msgs=tools_Parse_CAN_message.show_CAN_list(test_msgs)
# print("type of pgnsa att:", type(test_msgs[1].PGN_SA))


'''