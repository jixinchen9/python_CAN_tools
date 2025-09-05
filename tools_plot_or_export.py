# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 13:56:32 2025

@author: jc16287
"""

import matplotlib.pyplot as plt

def plot_single_signal(signal_name, signal_df):
    signal_df.plot(x = 'timestamp', y= signal_name, label=signal_name,kind='line')
    plt.xlabel('Time (s)')
    plt.ylabel(signal_name)
    plt.title('Signal_Interested')
    plt.show()

def combine_dfs_in_ds(result_ds):
    
    if len(result_ds) < 2:
        print("no merge needed")
        #return result_ds
    else:
        for i in range(len(result_ds)):
            if i == 0:
                combined_signals_df = result_ds[0]["df"]
            else:
                combined_signals_df = combined_signals_df.merge(result_ds[i]["df"], how='outer', on='timestamp')
    
    combined_signals_df = combined_signals_df.bfill()
    return combined_signals_df

def export_df_csv (df_out, log_name, folder_w_exports):
    
    export_label = "_lockup_sep_drive"
    export_name = folder_w_exports + log_name.replace(".asc","") + export_label + ".csv"
    df_out.to_csv(export_name)

