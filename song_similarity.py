import subprocess as sp
import numpy as np
from scipy.signal import spectrogram
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import glob
from scipy import stats
import pydub

datadir = '/Users/jamalw/Desktop/PNI/music_event_structures/'
genres = ["classical","jazz"]
classical_fn = glob.glob(datadir + genres[0] + '/*.wav')
jazz_fn = glob.glob(datadir + genres[1] + '/*.wav')
all_songs_fn = jazz_fn + classical_fn
spects = []

# load data
#FFMPEG_BIN = "ffmpeg"

for j in np.arange(16):
    command = [ FFMPEG_BIN,
	    '-i', all_songs_fn[j],
	    '-f', 's16le',
	    '-acodec', 'pcm_s16le',
	    '-ar', '44100', # ouput will have 44100 Hz
	    '-ac', '2', # stereo (set to '1' for mono)
	    '-']
    pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)

    # convert raw_audio to audio arrays
    raw_audio = pipe.stdout.read(88200*4)
    audio_array = np.fromstring(raw_audio, dtype="int16")
    audio_array = audio_array.reshape((int(len(audio_array)/2),2))

    # combine channels
    audio_array = audio_array[:,0] * audio_array[:,1]
    spect = spectrogram(audio_array)[2]
    spects.append(spect)

spects_mean = np.vstack([np.mean(i,1) for i in spects])
spects_corr = np.corrcoef(spects_mean,spects_mean)[16:,:16]

plt.imshow(spects_corr) 
plt.colorbar()
plt.show()

# compute average section of avgCorrD
corr_eye = np.identity(8)
classical_within  = spects_corr[0:8,0:8]
classical_within_off  = classical_within[corr_eye == 0]
jazz_within       = spects_corr[8:16,8:16]
jazz_within_off       = jazz_within[corr_eye == 0]
classJazz_between = spects_corr[8:16,0:8]
classJazz_between_off = classJazz_between[corr_eye == 0]
jazzClass_between = spects_corr[0:8,8:16]
jazzClass_between_off = jazzClass_between[corr_eye == 0]

within = (classical_within + jazz_within)/2
between = (jazzClass_between + classJazz_between)/2
 
plt.figure(2,facecolor="1")
allComparisonsAvg = np.array([np.mean(within),np.mean(between)])
allComparisonsSem = np.array([stats.sem(np.reshape(within,(8*8))),stats.sem(np.reshape(between,8*8))])
N = 2
ind = np.arange(N)
width = 0.5
plt.bar(ind, allComparisonsAvg, width, color='k',yerr = allComparisonsSem,error_kw=dict(ecolor='lightseagreen',lw=3,capsize=0,capthick=0))
plt.ylabel('Pattern Similarity (r)',fontsize=15)
plt.title('Average Within and Between-Genre Similarity',fontweight='bold',fontsize=18)
labels = ['Within','Between']
plt.xticks(ind + width / 10,labels,fontsize=12)
plt.plot((0.5,1),(0,0),'k-')
plt.show()
