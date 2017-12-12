import numpy as np
import brainiak.eventseg.event
from scipy.stats import norm,zscore,pearsonr,stats
from nilearn.image import load_img
import sys
from brainiak.funcalign.srm import SRM
import nibabel as nib

subjs = ['MES_022817_0','MES_030217_0','MES_032117_1','MES_040217_0','MES_041117_0','MES_041217_0','MES_041317_0','MES_041417_0','MES_041517_0','MES_042017_0','MES_042317_0','MES_042717_0','MES_050317_0','MES_051317_0','MES_051917_0','MES_052017_0','MES_052017_1','MES_052317_0','MES_052517_0','MES_052617_0','MES_052817_0','MES_052817_1','MES_053117_0','MES_060117_0','MES_060117_1']

#subjs = ['MES_022817_0','MES_030217_0','MES_032117_1']
k_sweeper = [3,6,9,12]

loo_idx = int(sys.argv[1])
subj = subjs[int(loo_idx)]
print('Subj: ', subj)

datadir = '/tigress/jamalw/MES/'
mask_img = load_img(datadir + 'data/mask_nonan.nii.gz')
mask = mask_img.get_data()
mask_reshape = np.reshape(mask,(91*109*91))
global_outputs_all = np.zeros((91,109,91))
results3d = np.zeros((91,109,91,1001))

def searchlight(X1,coords,K,mask,loo_idx):
    
    """run searchlight 

       Create searchlight object and perform voxel function at each searchlight location
    
       Parameters
       ----------
       data1  : voxel by time ndarray (2D); leftout subject run 1
       data2  : voxel by time ndarray (2D); average of others run 1
       data3  : voxel by time ndarray (2D); leftout subject run 2
       data4  : voxel by time ndarray (2D); average of others run 2
       coords : voxel by xyz ndarray (2D, Vx3)
       K      : # of events for HMM (scalar)
       
       Returns
       -------
       3D data: brain (or ROI) filled with searchlight function scores (3D)

    """

    stride = 5
    radius = 5
    min_vox = 10
    nPerm = 1000
    SL_allvox = []
    SL_results = []
    for x in range(np.random.randint(stride),np.max(coords, axis=0)[0]+stride,stride):
        for y in range(np.random.randint(stride),np.max(coords, axis=0)[1]+stride,stride):
           for z in range(np.random.randint(stride),np.max(coords, axis=0)[2]+stride,stride):
              D = np.sqrt(np.square(coords - np.array([x,y,z])[np.newaxis,:]).sum(1))
              SL_vox = D <= radius
              if np.sum(SL_vox) < min_vox:
                 continue
              SL_mask = np.zeros(X1[0].shape[:-1],dtype=bool)
              SL_mask[mask > 0] = SL_vox
              data = []
              SL_positions = np.transpose(np.nonzero(SL_mask))
              print("Assigning to Data Object")
              for i in range(len(X1)):
                  X1_i = np.zeros((SL_positions.shape[0],2511))
                  for v_ind in range(SL_positions.shape[0]):
                      X1_i[v_ind,:] = X1[i].dataobj[tuple([int(x) for x in SL_positions[v_ind]])]    
                  data.append(np.nan_to_num(stats.zscore(X1_i,axis=1,ddof=1)))
              print("Running Searchlight")
              SL_within_across = HMM(data,K,loo_idx)
              print('SL_within_across: ',SL_within_across)
              #if np.any(np.isnan(SL_within_across)):
              #   continue
              SL_results.append(SL_within_across)
              SL_allvox.append(np.array(np.nonzero(SL_vox)[0]))
    voxmean = np.zeros((coords.shape[0], nPerm+1))
    vox_SLcount = np.zeros(coords.shape[0])
    np.save('voxmean',voxmean)
    np.save('vox_SLcount',vox_SLcount)
    np.save('SL_results',SL_results)
    np.save('SL_allvox',SL_allvox)
    for sl in range(len(SL_results)):
       voxmean[SL_allvox[sl],:] += SL_results[sl]
       vox_SLcount[SL_allvox[sl]] += 1
    voxmean = voxmean / vox_SLcount[:,np.newaxis]
    vox_z = np.zeros((coords.shape[0], nPerm+1))
    for p in range(nPerm+1):
        vox_z[:,p] = (voxmean[:,p] - np.mean(voxmean[:,1:],axis=1))/np.std(voxmean[:,1:],axis=1) 
    return vox_z

def HMM(X,K,loo_idx):
    
    """fit hidden markov model
  
       Fit HMM to average data and cross-validate with leftout subject using within song and between song average correlations              

       Parameters
       ----------
       A: voxel by time ndarray (2D)
       B: voxel by time ndarray (2D)
       C: voxel by time ndarray (2D)
       D: voxel by time ndarray (2D)
       K: # of events for HMM (scalar)
 
       Returns
       -------
       z: z-score after performing permuted cross-validation analysis      

    """
    
    w = 10
    nPerm = 1000
    within_across = np.zeros(nPerm+1)
    run1 = [X[i] for i in np.arange(0, int(len(X)/2))]
    run2 = [X[i] for i in np.arange(int(len(X)/2), len(X))]
    print('Building Model')
    srm = SRM(n_iter=10, features=5)   
    print('Training Model')
    srm.fit(run1)
    print('Testing Model')
    shared_data = srm.transform(run2)
    print('Shared Data Size: ',len(shared_data))
    shared_data = stats.zscore(np.dstack(shared_data),axis=1,ddof=1)
    others = np.mean(shared_data[:,:,np.arange(shared_data.shape[-1]) != loo_idx],axis=2)
    loo = shared_data[:,1480:1614,loo_idx] 
    nTR = loo.shape[1]

    # Fit to all but one subject
    ev = brainiak.eventseg.event.EventSegment(K)
    ev.fit(others[:,1480:1614].T)
    events = np.argmax(ev.segments_[0],axis=1)

    # Compute correlations separated by w in time
    corrs = np.zeros(nTR-w)
    for t in range(nTR-w):
        corrs[t] = pearsonr(loo[:,t],loo[:,t+w])[0]
    _, event_lengths = np.unique(events, return_counts=True)
       
    # Compute within vs across boundary correlations, for real and permuted bounds
    for p in range(nPerm+1):
        within = corrs[events[:-w] == events[w:]].mean()
        across = corrs[events[:-w] != events[w:]].mean()
        within_across[p] = within - across
        print('Score: ',within_across[p])        

        np.random.seed(p)
        perm_lengths = np.random.permutation(event_lengths)
        np.random.seed(p)
        events = np.zeros(nTR, dtype=np.int)
        events[np.random.choice(nTR,K-1,replace=False)] = 1
        events = np.cumsum(events)

    return within_across

runs = []

# Load functional data and mask data
for j in range(len(subjs)):
    data_run1 = nib.load(datadir + 'subjects/' + subjs[j] + '/analysis/run1.feat/trans_filtered_func_data.nii')
    runs.append(data_run1)
    
for j in range(len(subjs)):
    data_run2 = nib.load(datadir + 'subjects/' + subjs[j] + '/analysis/run2.feat/trans_filtered_func_data.nii')
    runs.append(data_run2)

for i in k_sweeper:
    # create coords matrix
    x,y,z = np.mgrid[[slice(dm) for dm in runs[0].shape[0:3]]]
    x = np.reshape(x,(x.shape[0]*x.shape[1]*x.shape[2]))
    y = np.reshape(y,(y.shape[0]*y.shape[1]*y.shape[2]))
    z = np.reshape(z,(z.shape[0]*z.shape[1]*z.shape[2]))
    coords = np.vstack((x,y,z)).T 
    coords_mask = coords[mask_reshape>0]
    print('Running Distribute...')
    voxmean = searchlight(runs, coords_mask,i,mask,loo_idx) 
    results3d[mask>0] = voxmean
    print('Saving ' + subj + ' to Searchlight Folder')
    np.save(datadir + 'prototype/link/scripts/data/searchlight_output/HMM_searchlight_K_sweep_srm/globals_loo_' + subj + '_K_' + str(i), results3d)



