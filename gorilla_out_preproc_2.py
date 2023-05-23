    
def gorilla_out_preproc_2(df):
    import pandas as pd
    import numpy as np

    ## selects only rows of interest-------------------------------------------
    df = df[(df['Zone Type'] == 'response_keyboard') & (df['Screen Name'] == 'answer')]
    
    ## keeping only the list of sounds presented to each participant-----------
    # name of the counterbalance containing names of lists
    col_list = ["counterbalance-6nlr", "counterbalance-jqe2","counterbalance-6ion", "counterbalance-4g72","counterbalance-ckui"]
    df["the_list"] = np.nan # create a new column called "the_list" and fill it with the values from the first non-empty column in col_list
    # loop through each row and fill the "the_list" column with the first non-empty value from col_list for that row
    for i, row in df.iterrows():
        for col in col_list:
            if not pd.isna(row[col]):
                df.at[i, "the_list"] = row[col]
                break   
    # drop the columns in col_list that were not presented to the participant
    df.drop(columns=col_list, inplace=True)
    
    ## choosing only the list of stimuli used for each participant-------------
    # group the data by participant
    grouped = df.groupby("Participant Public ID")
    cols_to_compare = ["list_A1", "list_A2","list_A3", "list_A4","list_A5","list_B1", "list_B2","list_B3", "list_B4","list_B5"]
    dfs = []
    for participant, df_participant in grouped:
        cols_to_drop = set(cols_to_compare) - set([df_participant["the_list"].iloc[0]]) #select the relevant columns and drop the rest
        df_participant = df_participant.drop(cols_to_drop, axis=1)
        df_participant = df_participant.rename(columns={df_participant["the_list"].iloc[0]: "stimuli"}) #rename the selected column
        dfs.append(df_participant)
    
    ## reconstruct the preprocess df------------------------------------------
    df = pd.concat(dfs)
    # type of degradation
    df['TYPE'] = df['stimuli'].apply(lambda x: x.split('_')[0])
    # levels of degradation
    df.insert(len(df.columns),'LV',df['stimuli'].str.split('norm').str[1].str.replace('_','').str.replace('.wav','')) # use string split from filenames
    replace_map = {'-10db': 'L1','-7.5db': 'L2', '-5db': 'L3', '-2.5db': 'L4','0db': 'L5','15db':'catch',\
                           '0.7p': 'L1','0.75p': 'L2', '0.8p': 'L3', '0.85p': 'L4','0.9p': 'L5'}
    df['LV'] = df['LV'].map(replace_map)
    df['Task Name'] = df['Task Name'].str.replace('SINON_task_','')
    
    # some  formatting        
    df['block'] = df['block'].astype('object')
    df_participant['LV'] = df['LV'].astype('object')
    df_participant['Reaction Time'] = df['Reaction Time'].astype('float64')

    #keeping only columns of interest and changing their names
    df = df.loc[:, ['Participant Public ID','Task Name','Screen Name','Trial Number','Zone Type','Reaction Time',
                    'Correct','Incorrect','Timed Out','block','TYPE','LV','set','display','stimuli']]
    df = df.rename(columns={'Participant Public ID': 'SubjectID',
                            'Task Name': 'task',
                            'Trial Number': 'trial',
                            'Screen Name': 'Screen',
                            'Zone Type': 'Zone',
                            'Reaction Time': 'RT',
                            'Timed Out': 'Miss',
                            'Correct': 'Accuracy'})
    
    # recode blocks for clarity in plots (1 and 2 value only)
    df.loc[:,'block'] = df['block'].replace({1:1,2.0:1,3.0:2,4.0:2})  
    df.SubjectID = pd.Series(df.SubjectID,dtype="object")
    # reset index 
    df = df.reset_index(drop=True)
    return (df)