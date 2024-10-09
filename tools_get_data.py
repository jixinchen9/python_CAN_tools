# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 09:06:13 2024

@author: jc16287

This file contains functions that translate data bytes into actual values 

"""
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

def get_dtc_spnfmi(can_data_bytes):
    from bitstring import Bits

    dtc_bytes_01=can_data_bytes[slice(9,11)]+can_data_bytes[slice(6,8)]
    dtc_bytes_02=can_data_bytes[slice(12,14)]

    spn_full_int=(Bits(hex=dtc_bytes_02).__rshift__(5)+Bits(hex=dtc_bytes_01)).int

    fmi_int=Bits(hex=dtc_bytes_02).__lshift__(3).__rshift__(3).intle
    
    return spn_full_int, fmi_int