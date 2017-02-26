import numpy as np
import nibabel as nib
import os
import glob
from scipy import stats
import sys

# argument is subject ID
subj = sys.argv[1]

# set data path
datapath = '/Users/jamalw/Desktop/PNI/music_event_structures/subjects/' + subj + '/'

# set datadir names
data = ['trans_filtered_func_data_run2.nii.gz']
#data = ['trans_filtered_func_data_run1.nii.gz','trans_filtered_func_data_run2.nii.gz']

for i in range(len(data)):
    fmri_filename = data[i]
    fmri_img = nib.load(datapath + fmri_filename)
    fmri_img_reshaped = np.reshape(fmri_img.get_data(),(91*109*91,fmri_img.get_data().shape[3]))
    fmri_img_reshaped_zscored = stats.zscore(fmri_img_reshaped)





