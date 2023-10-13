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
import seaborn as sns
import matplotlib.pyplot as plt        

# %% 
doplots = 0

# paths - Use current script path as reference 
thisScriptDir = os.path.dirname(os.path.abspath(__file__))
baseDir = thisScriptDir[:thisScriptDir.find('scripts')]

dirinput = os.path.join(baseDir , 'Data', 'preprocessed','pilot_2','data_exp_116083-v2')
diroutput = os.path.join(baseDir , 'Analysis' , 'pilot_2')

# %% Find files with stats 

files = glob.glob(dirinput + '/**/*_stats.csv' ,recursive=True)

#Read files of this taks and concatenate
dfs = [pd.read_csv(fileinput) for fileinput in files]
concat_df = pd.concat(dfs, axis=0)    
#concat_df['SubjectID'] = concat_df['SubjectID'].astype('object')
#concat_df['block'] = concat_df['block'].astype('object')    
#concat_df['LV'] = concat_df['LV'].astype('object')    
concat_df.Accuracy = concat_df.Accuracy.replace('1.0','1').replace('0.0','0').replace(0.0,'0').replace(1.0,'1')


# %%  Save table
concat_df.to_csv(os.path.join(diroutput, 'Gathered_means.csv'), index = False)    

 # %% 
if doplots==1:
   os.chdir(dirinput)
   for currTask in concat_df.task.unique():
       concat_df = concat_df[concat_df['Accuracy']=='1']
       #%
       plt.close('all')
       d2plot = concat_df[concat_df['task']== currTask]
       
       g = sns.FacetGrid(d2plot, col="TYPE",  row="SubjectID")
       g.map(sns.lineplot, 'LV','propTrials','block',palette='Set2')
       g.map_dataframe(sns.lineplot, x ='LV',y=0.5, color='gray',linestyle='dotted')
       g.map_dataframe(sns.scatterplot, x='LV', y='propTrials', marker='o', hue='block',palette='Set2')
       g.map(sns.lineplot, 'LV','propTrials',color='black', ci = None)
       #g.map_dataframe(sns.scatterplot, x='LV', y='propTrials', marker='o', color='black')
       g.add_legend()
       g.fig.suptitle(currTask, fontsize=20, y=1.0, x= 0.08)
   
       # save     
       g.savefig('FIG_' + currTask + '_stats_Acc.jpg')
   # %% 
   os.chdir(dirinput)
   for currTask in concat_df.task.unique():
       concat_df = concat_df[concat_df['Accuracy']=='1']
       #%
       plt.close('all')
       d2plot = concat_df[concat_df['task']== currTask]
       
       g = sns.FacetGrid(d2plot, col="TYPE",  row="SubjectID")
       g.map(sns.lineplot, 'LV','RT_mean','block',palette='Set2')
       g.map_dataframe(sns.lineplot, x ='LV',y=0.5, color='gray',linestyle='dotted')
       g.map_dataframe(sns.scatterplot, x='LV', y='RT_mean', marker='o', hue='block',palette='Set2')
       g.map(sns.lineplot, 'LV','RT_mean',color='black', ci = None)
       g.add_legend()
       g.fig.suptitle(currTask, fontsize=20, y=1.0, x= 0.08)
   
       # save     
       g.savefig('FIG_' + currTask + '_stats_RT.jpg')

