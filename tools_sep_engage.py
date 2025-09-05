# -*- coding: utf-8 -*-
"""
Created on Fri Sep  5 10:42:06 2025

clean up some functions specific to separator engagement

@author: jc16287
"""

def find_min_engine_speed (result_ds):
    for i in result_ds:
        if i["name"] == "EngineSpeed ":
            
            Min_EngineSpeed = i["df"][i["name"]].min()
            min_speed_idx = i["df"][i["name"]].idxmin()
            min_speed_tst = i["df"].loc[min_speed_idx, 'timestamp']

            print("Min EngineSpeed over interval is: ", Min_EngineSpeed)

            recovery_search_df = i["df"][min_speed_idx:]
            recovery_index = recovery_search_df[recovery_search_df[i["name"]]>1200].index[0]
            recovery_tst = recovery_search_df.loc[recovery_index, 'timestamp']

            print("Recovery Time is: ", recovery_tst - min_speed_tst)
            
        """
        find the rising edge of sep switch
        """

        if i["name"] == "HarvEngageCmds2 ":
            
            sep_switch_df = i["df"]
            sep_switch_name = i["name"]
            sep_switch_df[sep_switch_name] = sep_switch_df[sep_switch_name].astype(int)

            switch_on_idx = sep_switch_df[sep_switch_df[sep_switch_name] > 0].index[0]
            switch_on_tst = sep_switch_df.loc[switch_on_idx, 'timestamp']

            print("time btw switch flip and min engine speed is: ", switch_on_tst - min_speed_tst)
