# -*- coding: utf-8 -*-
#%reset -f #clear all ? 
"""
Created on Mon Oct 10 10:04:55 2022
@author: gfraga

"""
import os  # Commands to remember: os.getcwd(), os.listdir() 
import pandas as pd
import glob
import sys as sys
#import plotly.io as io
import matplotlib.pyplot as plt        
import seaborn as sns
import re
# %% 
# Fix for issue with spyder not showing plotly 
#io.renderers.default='browser'
# %% 
# paths

# paths - Use current script path as reference 
thisScriptDir = os.path.dirname(os.path.abspath(__file__))
baseDir = thisScriptDir[:thisScriptDir.find('scripts')]

dirinput = os.path.join(baseDir + 'Data', 'preprocessed','pilot_2','data_exp_116083-v2')
diroutput = os.path.join(baseDir + 'Data', 'preprocessed','pilot_2','data_exp_116083-v2')

# add custom functions 
sys.path.append(thisScriptDir + 'functions')
from functions import multiplot_lines,multiplot_lines_scatter,multiplot_rainclouds,gorilla_out_preproc,gorilla_out_summary



# %% find relevant files (Files have a number id before the extension. This is used in the reg exp matching)
validfiles= [files for files in glob.glob(dirinput + '/2FC/**/*.csv' ,recursive=True) if 
             'gathered/Concat' not in files and re.search(r'\d+\.csv', files)] # subject files here have a digit before extension 
 

# %%  Summary per subject
for fileinput in validfiles: 
    #fileinput = validfiles[0]
    
    os.chdir(os.path.dirname(fileinput))
    print('[-_-] >>>> Start ' +  fileinput )
    
    # %  DATA PREP
    #----------------------------------------------------------------
    # read data, select columns
    dat = pd.read_csv(fileinput)         
    
    # Preprocessing 
    df = gorilla_out_preproc(dat)        
    
    #descriptive statistics
    df_summary = gorilla_out_summary(df)
    
    # SAVE 
    #------------------------------------------------------------------
    # Tables 
    df_summary.to_csv(fileinput.replace('.csv','_stats.csv'), index = False)    
    
    print('---<< done summary ' +  fileinput +'. \n' )
    #del dat, df, accu, rt

    # %%  PLOTs
    #----------------------------------------------------------------
    plt.close('all')
    d2plot = df_summary[df_summary['Accuracy'] == 1].copy()
    g = sns.FacetGrid(d2plot, col="TYPE")
    g.map(sns.pointplot, "LV", "propTrials", "block",palette="Set2")
    g.map(sns.lineplot)
    g.refline(y = 0.5,color = "gray",lw = 1, linestyle='--')
    g.add_legend()
    g.fig.suptitle(os.path.basename(fileinput).replace('.csv',''))
    
    # Save figure    
    g.savefig(fileinput.replace('.csv','_stats.jpg'))


    










