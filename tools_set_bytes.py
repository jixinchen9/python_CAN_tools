# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 09:16:42 2024

@author: jc16287

This toolbox collects functions that write variable values into data bytes
"""

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