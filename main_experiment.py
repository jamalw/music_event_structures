#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Author: Jamal A. Williams
from __future__ import division
from psychopy import prefs
from psychopy import sound
prefs.general['audioLib'] = ['pygame']
from psychopy import visual, event, core, gui
from psychopy.hardware.emulator import launchScan
from psychopy import data
import glob, time
import random
import numpy as np
import os

# CHANGE FOR EVERY SUBJECT AND SECTION OF SCAN
subj_id = 'test'
run = '1'
subject_filename = '/Users/jamalw/Desktop/PNI/music_event_structures/subjects/' + subj_id + '/' + subj_id + '_' + 'main_experiment' + run + '.log'

def log_msg(msg, filename=subject_filename):
    print(msg)
    with open(filename, 'a') as f:
        f.write(msg + '\n')

log_msg('Log filename:' + subject_filename)

# Prepare music
#songs = glob.glob('/Users/jamalw/Desktop/PNI/music_event_structures/songs/*.wav')
song_dir = '/Users/jamalw/Desktop/PNI/music_event_structures/' + 'all_songs_part' + run + '.npy'
#song_dir = '/Users/jamalw/Desktop/PNI/music_event_structures/all_songs_part' + run + '.npy'
songs = np.load(song_dir)
white_noise ='/Users/jamalw/Desktop/PNI/music_event_structures/white_noise2_quieter.wav'
sound_white_noise = sound.Sound(white_noise)
f = open('/Users/jamalw/Desktop/PNI/music_event_structures/prompts/MES_instructions.txt','r')
file_contents = f.read()

# settings for launchScan:
MR_settings = {
    'TR': 1.000,     # duration (sec) per whole-brain volume
    'volumes': 8000,    # number of whole-brain 3D volumes per scanning run
    'sync': '5', # character to use as the sync timing event; assumed to come at start of a volume
    'skip': 0,       # number of volumes lacking a sync pulse at start of scan (for T1 stabilization)
    'sound': False    # in test mode: play a tone as a reminder of scanner noise
    }
infoDlg = gui.DlgFromDict(MR_settings, title='fMRI parameters', order=['TR', 'volumes'])
if not infoDlg.OK:
    core.quit()

win = visual.Window(fullscr=False)
globalClock = core.Clock()

# summary of run timing, for each key press:
output = u'vol    onset key\n'
for i in range(-1 * MR_settings['skip'], 0):
    output += u'%d prescan skip (no sync)\n' % i

counter = visual.TextStim(win, height=.15, pos=(0, 0), color=win.rgb + 0.5)

# set window handler for finish
finish = visual.TextStim(win, height=.06, pos=(0, 0), color=win.rgb + 0.5)

#instructions = visual.TextStim(win, height=.25, pos=(0, 0), color=win.rgb + 0.5)

output += u"  0    0.000 sync  [Start of scanning run, vol 0]\n"

# launch: operator selects Scan or Test (emulate); see API docuwmentation
vol = launchScan(win, MR_settings, globalClock=globalClock,simResponses=None,mode=None,esc_key='escape',instr=file_contents)
#counter.setText(u"%d volumes\n%.3f seconds" % (0, 0.0))

while True:
    if event.getKeys(MR_settings['sync']):
        onset = globalClock.getTime()
        counter.size = 10
        log_msg(u"%3d  %7.3f sync\n" % (vol, onset))
        vol += 1
        break
    else:
        time.sleep(0.001)

counter.setText("+")
counter.draw()
win.flip()

# Here we grab the first and last 20% of the song leaving us with the middle 60%
def get_randt(s):
    song_dur = np.round(s.getDuration())
    song_edges = np.round(song_dur * .2)
    song_dur_60 = np.arange(song_edges, song_dur - song_edges,1)
    randt = random.choice(song_dur_60)
    return randt

duration = MR_settings['volumes'] * MR_settings['TR']
# note: globalClock has been reset to 0.0 by launchScan()
##
song_idx = -1
##
while globalClock.getTime() < duration:
    
    if song_idx==-1 or current_song.status == -1: # the current song has stopped, i.e. it finished
        log_msg(u'%3d  %7.3f ending song %d:\n' % (vol, globalClock.getTime(), song_idx ))
        song_idx += 1
        if song_idx == len(songs):
            break
        current_song = sound.Sound(os.path.join(songs[song_idx]))
        song_t0 = time.time()
        did_play_white = False
        randt = get_randt(current_song)
        log_msg('will play at {}'.format(randt))
        current_song.play() 
        log_msg(u'%3d  %7.3f playing song %d: %s\n' % (vol, globalClock.getTime(), song_idx, songs[song_idx]))
    if time.time()-song_t0 >= randt and (not did_play_white):
        sound_white_noise.play()
        log_msg(u'%3d  %7.3f playing white noise\n' %(vol, globalClock.getTime()))
        did_play_white = True
    allKeys = event.getKeys()
    for key in allKeys:
        # handle keys (many fiber-optic buttons become key-board key-presses)
        log_msg(u"%3d  %7.3f %s\n" % (vol-1, globalClock.getTime(), unicode(key)))
        if key == 'escape':
            log_msg(u'user cancel, ')
            break
                
finish.setText('This concludes the scanning session')
finish.draw()
win.flip()
t = globalClock.getTime()
log_msg("End of scan (vol 0..%d = %d of %s). Total duration = %7.3f sec" % (vol - 1, vol, MR_settings['volumes'], t))
time.sleep(5)

win.close()
core.quit()

log_msg("Log file saved to: " + subject_filename)
