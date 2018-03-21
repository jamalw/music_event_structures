from mayavi import mlab
from surfer import Brain, project_volume_data
import scipy
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np

"""
Bring up the visualization window.
"""
#mlab.options.backend = 'envisage'
view = "lateral"
hemi = "split"

K = np.arange(2,20)
#K = [3]

for i in K:
    brain = Brain("fsaverage", hemi, "inflated", title='K='+str(i),cortex='low_contrast',views=['lat','med'],background="white")

    """
    Get a path to the overlay file.
    """
    mri_file = '/Users/jamalw/Desktop/PNI/music_event_structures/avg_real_k' + str(i) + '_across_songs.nii.gz'
    reg_file = '/Applications/freesurfer/average/mni152.register.dat'

    data = nib.load(mri_file)
    #maxval = np.max(data.get_data())
    maxval = .266
    maxval = np.max(data.get_data())
    surf_data_lh = project_volume_data(mri_file,"lh",reg_file)
    surf_data_rh = project_volume_data(mri_file,"rh",reg_file)

    brain.add_overlay(surf_data_lh,min=0,max=maxval,name="thirty_sec_lh", hemi='lh',sign="pos")
    brain.add_overlay(surf_data_rh,min=0,max=maxval,name="thirty_sec_rh", hemi='rh',sign="pos")

#    for overlay in brain.overlays_dict["thirty_sec_lh"]:
#        overlay.remove()
#    for overlay in brain.overlays_dict["thirty_sec_rh"]:
#        overlay.remove()
#
#    brain.add_data(surf_data_lh, 0,maxval, colormap="CMRmap", alpha=.65,
#               hemi='lh')
#    brain.add_data(surf_data_rh, 0,maxval, colormap="CMRmap", alpha=.65,
#               hemi='rh')
#
#    brain.save_image('avg_real_K_' + str(i) + ".png")
#
mlab.show()

brain.show_view(view)
