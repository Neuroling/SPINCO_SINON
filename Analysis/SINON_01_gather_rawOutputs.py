""" GATHER RAW OUTPUTS 
====================================
- Read raw downloads from Gorilla
- Rename Gorilla-provided strings to informative task label
- Create folder struct per task/subjectID , save table per task & subj
- Save also a table per task with concatenated subjects 
- Save csvs at each subjects folder


Created on Mon Jan 30 13:31:37 2023
@author: gfraga

"""
import os  # Commands to remember: os.getcwd(), os.listdir() 
import pandas as pd
import glob
import re
import sys as sys

# %%
# paths - Use current script path as reference 
thisScriptDir = os.path.dirname(os.path.abspath(__file__))
# define data dir
scripts_index = thisScriptDir.find('scripts')
dirinput = os.path.join(thisScriptDir[:scripts_index] + 'Data', 'raw','pilot_2','data_exp_116083-v2')
diroutput = os.path.join(thisScriptDir[:scripts_index] + 'Data', 'preprocessed','pilot_2','data_exp_116083-v2')
# %% 
 
# % find relevant files
files = [files for files in glob.glob(dirinput + '/**/*.csv' ,recursive=True) if re.search('task', files)]

# Decode identifiers of each task
filetags = { 'PM': ['krnm','ay71'], 
              '2FC':['uiag'],
              'LD': ['q399','7qgr']}



#%  for each task: find files, merge and add task tag to filename with merged tables
# ---------------------------------------
os.chdir(diroutput)

for taskname in filetags.keys():
    # find files for current 
    matching_files = [file for file in files if any(tag in file for tag in filetags[taskname])]

    #Read files of this taks and concatenate
    dfs = [pd.read_csv(taskfile) for taskfile in matching_files]
    concatenated_df = pd.concat(dfs, axis=0)
    
    # write to file 
    concatenated_df.to_csv('Concat_' + taskname + '.csv',index=False)

    #Split subjecs of each concatenated table (one table per task)
    concatenated_df['Participant Private ID'] = concatenated_df['Participant Private ID'].astype(str).str.replace('.0','')
    
    
    grouped =  concatenated_df.groupby('Participant Private ID')        
    for name, group in grouped:
        #make outputdirs
        if not os.path.exists(taskname):
            os.mkdir(taskname)            
        if not os.path.exists(os.path.join(taskname,name)):
            os.mkdir(os.path.join(taskname,name))         
        
        # save file 
        outputfile = os.path.join(taskname, name, taskname + '_' + name + '.csv')
        group.to_csv(outputfile, index=False)
        