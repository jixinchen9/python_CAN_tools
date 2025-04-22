# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 13:56:32 2025

@author: jc16287
"""

import matplotlib.pyplot as plt

def plot_single_signal(signal_name, signal_df):
    signal_df.plot(x = 'timestamp', y= signal_name, label='DMA blocks average Busload',kind='line')
    plt.xlabel('Time (s)')
    plt.ylabel(signal_name)
    plt.title('Signal_Interested')
    plt.show()
