import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt

songs = ['Pauls','I Love Music','Moonlight Sonata','Change of the Guard','Waltz of the Flowers','The Bird','Island','Allegro Moderato','Finlandia','Early Summer','Capriccio Espagnole','Symphony - Fantastique','Boogie Stop Shuffle','My Favorite Things','Blue Monk','All Blues']

#songs = ['Allegro Moderato']

subjs = ['SS_021618_0','SS_021618_1','SS_021718_0','SS_021718_2','SS_021818_0','SS_021818_1','SS_021818_2']

durs = np.array([90,180,180,89,134,179,180,224,225,134,90,135,225,225,89,134])

datadir = '/Users/jamalw/Desktop/PNI/music_event_structures/subjects/'
# initialize our final output: which is a list where each element is a matrix corresponding to a song. the shape of each matrix is nSubjs x nTRs and contains ones at TRs where there was a button press and zeros everywhere else
allPressTimes = []

for i in range(len(songs)):
    # initialize song specific button press time holder (nSubjs x nTrs)
    songPressTimes = np.array([])
    for j in range(len(subjs)):
        # load in subject data. here i load the full csv file AND timestamps column only into two separate variables.  
        data = pd.read_csv(datadir + 'beh/' + subjs[j] + '/' + subjs[j] + '_subjective_segmentation.csv',na_values=" NaN")
        timestamps = pd.read_csv(datadir + 'beh/' + subjs[j] + '/' + subjs[j] + '_subjective_segmentation.csv',index_col='timestamp')

        # grab song end and start times (with event type and info)
        song_end_and_start = data[(data['info'].str.contains(songs[i],na=False))]

        # store start and end time separately
        start = song_end_and_start['timestamp'].iloc[0]
        end = song_end_and_start['timestamp'].iloc[1]

        # compute number of TRs and initialize subject-specific button press vector (vector of zeros that will be replaced with ones according to timestep index) 
        #nTRs = np.round(end - start)
        nTRs = durs[i]
        subj_press_vector = np.zeros((int(nTRs)))
        # grab full range of rows and colums between start and end time 
        button_presses_full = timestamps[start:end]

        # grab only button press timesteps including song start and end time
        button_presses = np.round(button_presses_full[(button_presses_full['info'].str.contains('j',na=False))].index.values.tolist())

        # compute distances between button presses and sum to get cumulative press time distribution
        distance_btwn_presses = np.cumsum(np.diff(button_presses)[:-1]).astype(int)
        if distance_btwn_presses[-1] == nTRs:
            distance_btwn_presses[-1] = nTRs - 1
        print(distance_btwn_presses)
        # replace zeros with ones where presses occurred and store vector in song specific button press time holder
        subj_press_vector[distance_btwn_presses] = 1
        songPressTimes = np.concatenate([songPressTimes,subj_press_vector],axis=0)

    allPressTimes.append(np.reshape(songPressTimes,(len(subjs),int(nTRs))))
