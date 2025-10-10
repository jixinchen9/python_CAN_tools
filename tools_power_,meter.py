# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 08:41:02 2025

@author: jc16287
"""

def calc_display_correction_factor (enginespeed_error , torque_derate, pctload):
    
    UseCase1EngineError = 10
    UseCase2EngineErrorMin = 0
    UseCase2SpeedHysteresis = 10
    UseCase2EngineErrorMax = 100
    UseCase3EngineErrorMin = 100
    UseCase3EngineErrorMax = 200
    UseCase4EngineError = 200
    
    StartDarkGreenB = 100
    StartRedD = 110
    EndRedE = 114
    
    correct_factor = 100
    
    if (enginespeed_error <= UseCase1EngineError) or (abs(torque_derate - pctload) >= 2):
        
        correct_factor = StartDarkGreenB
        
    elif (enginespeed_error > (UseCase2EngineErrorMin + UseCase2SpeedHysteresis)
          and enginespeed_error <= UseCase2EngineErrorMax):
        
        correct_factor = StartDarkGreenB + (enginespeed_error - UseCase2EngineErrorMin)*(StartRedD - StartDarkGreenB)/(UseCase2EngineErrorMax - UseCase2EngineErrorMin)
        
    elif (enginespeed_error > UseCase3EngineErrorMin and enginespeed_error <= UseCase3EngineErrorMax):
        
        correct_factor = StartRedD + (enginespeed_error - UseCase3EngineErrorMin) * (EndRedE - StartRedD) / (UseCase3EngineErrorMax - UseCase3EngineErrorMin)
        
    elif enginespeed_error > UseCase4EngineError:
        
        correct_factor = EndRedE
    
    return correct_factor

def calc_display_correction_factor_wo_power_margin (enginespeed_error):
    
    UseCase1EngineError = 10
    UseCase2EngineErrorMin = 0
    UseCase2SpeedHysteresis = 10
    UseCase2EngineErrorMax = 100
    UseCase3EngineErrorMin = 100
    UseCase3EngineErrorMax = 200
    UseCase4EngineError = 200
    
    StartDarkGreenB = 100
    StartRedD = 110
    EndRedE = 114
    
    correct_factor = 100
    
    if (enginespeed_error <= UseCase1EngineError):
        
        correct_factor = StartDarkGreenB
        
    elif (enginespeed_error > (UseCase2EngineErrorMin + UseCase2SpeedHysteresis)
          and enginespeed_error <= UseCase2EngineErrorMax):
        
        correct_factor = StartDarkGreenB + (enginespeed_error - UseCase2EngineErrorMin)*(StartRedD - StartDarkGreenB)/(UseCase2EngineErrorMax - UseCase2EngineErrorMin)
        
    elif (enginespeed_error > UseCase3EngineErrorMin and enginespeed_error <= UseCase3EngineErrorMax):
        
        correct_factor = StartRedD + (enginespeed_error - UseCase3EngineErrorMin) * (EndRedE - StartRedD) / (UseCase3EngineErrorMax - UseCase3EngineErrorMin)
        
    elif enginespeed_error > UseCase4EngineError:
        
        correct_factor = EndRedE
    
    return correct_factor