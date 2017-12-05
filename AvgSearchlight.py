import numpy as np
import sys
import os
import nibabel as nib
import glob
import scipy.stats as st

datadir = '/tigress/jamalw/MES/prototype/link/scripts/data/searchlight_output/'
searchlight_dir = sys.argv[1]
datadir_full = datadir + searchlight_dir + '/'

# Collect searchlight files
k = '2'
fn = glob.glob(datadir_full + '*_'+k+'.npy')

global_outputs_all = np.zeros((91,109,91,1001))

# Take average of searchlight results
for i in range(0,len(fn)):
    subj_data = np.load(fn[i])
    global_outputs_all[:,:,:,:] += subj_data/(len(fn)) 

# Save average results 
np.save(datadir_full + 'avg_data/globals_avg_n25_k'+k,global_outputs_all)

# Reshape data
z_scores_reshaped = np.nan_to_num(np.reshape(global_outputs_all,(91*109*91,1001)))
z_scores_reshaped_pval = np.nan_to_num(np.reshape(global_outputs_all,(91*109*91,1001)))

# Mask data with nonzeros
mask = z_scores_reshaped != 0
z_scores_reshaped[mask] = -np.log(st.norm.sf(z_scores_reshaped[mask]))
z_scores_reshaped_pval[mask] = st.norm.sf(z_scores_reshaped_pval[mask])

# Reshape data back to original shape
neg_log_p_values = np.reshape(z_scores_reshaped,(91,109,91,1001))
p_values = np.reshape(z_scores_reshaped_pval,(91,109,91,1001))

# Plot and save searchlight results
maxval = np.max(neg_log_p_values[~np.isnan(neg_log_p_values)])
minval = np.min(neg_log_p_values[~np.isnan(neg_log_p_values)])
img = nib.Nifti1Image(neg_log_p_values, np.eye(4))
img.header['cal_min'] = minval
img.header['cal_max'] = maxval
nib.save(img,datadir + searchlight_dir + '/avg_data/globals_avg_n25_k'+k+'_neglog.nii.gz')

maxval2 = np.max(p_values[~np.isnan(p_values)])
minval2 = np.min(p_values[~np.isnan(p_values)])
img2 = nib.Nifti1Image(p_values, np.eye(4))
img2.header['cal_min'] = minval2
img2.header['cal_max'] = maxval2
nib.save(img2,datadir + searchlight_dir + '/avg_data/globals_avg_n25_k'+k+'_pvals.nii.gz') 
