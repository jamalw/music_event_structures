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

# CHANGE FOR EVERY SUBJECT. ESPECIALLY THE PRESCAN FILE NAME
subj_id = 'MES_022817_0'
day = '1'

os.system("mkdir '/Users/jamalw/Desktop/PNI/music_event_structures/subjects/'" + subj_id)
subject_filename = '/Users/jamalw/Desktop/PNI/music_event_structures/subjects/' + subj_id + '/' + subj_id + '_prescan_num' + day + '.log'

def log_msg(msg, filename=subject_filename):
    print(msg)
    with open(filename, 'a') as f:
        f.write(msg + '\n')

log_msg('Log filename:' + subject_filename)

# Prepare music and questions
songs = glob.glob('/Users/jamalw/Desktop/PNI/music_event_structures/songs/*.wav')
print len(songs)
np.random.shuffle(songs)
white_noise ='/Users/jamalw/Desktop/PNI/music_event_structures/white_noise2_quieter.wav'
sound_white_noise = sound.Sound(white_noise)
f = open('/Users/jamalw/Desktop/PNI/music_event_structures/prompts/MES_prescan_instructions.txt','r')
engage = open('/Users/jamalw/Desktop/PNI/music_event_structures/prompts/engagement_prompt.txt','r')
enjoy = open('/Users/jamalw/Desktop/PNI/music_event_structures/prompts/enjoyability_prompt.txt','r')
familiar = open('/Users/jamalw/Desktop/PNI/music_event_structures/prompts/familiarity_prompt.txt','r')

file_contents = f.read()
engage = engage.read()
enjoy = enjoy.read()
familiar = familiar.read()


# settings for launchScan:
MR_settings = {
    'TR': 1.000,     # duration (sec) per whole-brain volume
    'volumes': 4000, #40,    # number of whole-brain 3D volumes per scanning run
    'sync': '6', # character to use as the sync timing event; assumed to come at start of a volume
    'skip': 0,       # number of volumes lacking a sync pulse at start of scan (for T1 stabilization)
    'sound': False    # in test mode: play a tone as a reminder of scanner noise
    }
infoDlg = gui.DlgFromDict(MR_settings, title='fMRI parameters', order=['TR', 'volumes'])
if not infoDlg.OK:
    core.quit()

win = visual.Window(fullscr=True)
globalClock = core.Clock()

# summary of run timing, for each key press:
output = u'vol    onset key\n'
for i in range(-1 * MR_settings['skip'], 0):
    output += u'%d prescan skip (no sync)\n' % i

# set window handler
counter = visual.TextStim(win, height=.15, pos=(0, 0), color=win.rgb + 0.5)

# set window handler for questions
questions = visual.TextStim(win, height=.06, pos=(0, 0), color=win.rgb + 0.5)

output += u"  0    0.000 sync  [Start of scanning run, vol 0]\n"

# launch: operator selects Scan or Test (emulate); see API docuwmentation
vol = launchScan(win, MR_settings, globalClock=globalClock,simResponses=None,mode=None,esc_key='escape',instr=file_contents)
#counter.setText(u"%d volumes\n%.3f seconds" % (0, 0.0))

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
q_idx = -1
in_q_phase = False
qphase_complete = False
qs = [engage, enjoy, familiar]
n_questions = len(qs)
did_respond_to_q = True
##
# main loop
while globalClock.getTime() < duration:
    
    if song_idx==-1 or current_song.status == -1: # the current song has stopped, i.e. it finished
        if (song_idx!=-1 and current_song.status == -1) and (not in_q_phase) and (not qphase_complete):
            # start the q period
            q_idx = -1
            in_q_phase = True
            did_respond_to_q = True
        elif in_q_phase:
            pass
        else:
            # start a new song
            song_idx += 1
            if song_idx == len(songs):
                break
            else:
                current_song = sound.Sound(songs[song_idx])
                song_t0 = time.time()
                did_play_white = False
                qphase_complete = False
                randt = get_randt(current_song)
                log_msg('will play white noise at {}'.format(randt))
                current_song.play() 
                log_msg(u'%3d  %7.3f playing song %d: %s\n' % (vol, globalClock.getTime(), song_idx, songs[song_idx]))

    
    if in_q_phase and did_respond_to_q:
        q_idx += 1
        if q_idx == n_questions:
            in_q_phase = False
            qphase_complete = True
            counter.setText('+')
            counter.draw()
            win.flip()
        else:
            questions.setText(qs[q_idx])
            questions.draw()
            win.flip()
            log_msg(u'%3d  %7.3f %s\n' % (vol, globalClock.getTime(), qs[q_idx]))
        did_respond_to_q = False
        
    
    # play white noise if necessary
    if time.time()-song_t0 >= randt and (not did_play_white):
        sound_white_noise.play()
        log_msg(u'%3d  %7.3f playing white noise\n' % (vol, globalClock.getTime()))
        did_play_white = True
        
    # check for key input on this iteration
    allKeys = event.getKeys()
    for key in allKeys:
        if key == MR_settings['sync']:
            onset = globalClock.getTime()
            # do your experiment code at this point if you want it sync'd to the TR
            # for demo just display a counter & time, updated at the start of each TR
            #counter.setText(u"%d volumes\n%.3f seconds" % (vol, onset))
            log_msg(u"%3d  %7.3f sync\n" % (vol, onset))
            vol += 1
        else:
            # handle keys (many fiber-optic buttons become key-board key-presses)
            log_msg(u"%3d  %7.3f %s\n" % (vol-1, globalClock.getTime(), unicode(key)))
            if key in ['1','2','3','4','5']:
                did_respond_to_q = True
            elif key == 'escape':
                #output += u'user cancel, '
                log_msg(u'user cancel, ')
                break

questions.setText('This concludes the listening session')
questions.draw()
win.flip()
time.sleep(5)

t = globalClock.getTime()
#win.flip()

#output += u"End of scan (vol 0..%d = %d of %s). Total duration = %7.3f sec" % (vol - 1, vol, MR_settings['volumes'], t)
#print(output)
log_msg("End of scan (vol 0..%d = %d of %s). Total duration = %7.3f sec" % (vol - 1, vol, MR_settings['volumes'], t))

win.close()
core.quit()

log_msg("Log file saved to: " + subject_filename)



# The contents of this file are in the public domain.