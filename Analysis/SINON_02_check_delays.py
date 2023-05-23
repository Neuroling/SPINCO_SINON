# -*- coding: utf-8 -*-
""" CHECK GORILLA OUTPUT
============================================
- Check for messages indicating browser Issues in output files from Gorilla
Created on Thu Feb  9 10:47:12 2023

@author: gfraga
"""  
import os  # Commands to remember: os.getcwd(), os.listdir() 
import pandas as pd
import glob
import sys as sys
import re
import numpy as np
import csv

# %% 
# paths - Use current script path as reference 
thisScriptDir = os.path.dirname(os.path.abspath(__file__))

# define data dir
scripts_index = thisScriptDir.find('scripts')
dirinput = os.path.join(thisScriptDir[:scripts_index] + 'Data', 'preprocessed','pilot_2','data_exp_116083-v2')
diroutput = dirinput
 
# %% find relevant files 
validfiles= [files for files in glob.glob(dirinput + '/**/*.csv' ,recursive=True) if  '_nan.csv' not in files ] 
 
 
# %%  Log info about "Loading delays


for i,fileinput  in enumerate(validfiles):       
    # read data     
    dat = pd.read_csv(fileinput)     

    # start log file     
    log_file = open(os.path.join(diroutput,'LOG_delays.csv'), 'w')
    log_info = []
    
    # Count delays
    count =  np.sum(dat['Reaction Time'] == 'LOADING DELAY')
    events =  np.array(dat['Event Index'][dat['Reaction Time'] == 'LOADING DELAY'])
    log_info.append({'file': fileinput, 'delays_count': count,'EventIdx':events})
                                 
    # save log table 
    log_df = pd.DataFrame(log_info)
    outputfile = os.path.join(os.path.dirname(fileinput),'LOG_delays.csv')
    log_df.to_csv(outputfile, index=False)
    
    del log_df
