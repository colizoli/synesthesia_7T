#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Participant instructions including a simple font-check display.
Shows 4 columns of 8 graphemes each, side by side on one screen:
    CourierNew | CourierNew-Italic | BACS2serif | BACS2serif-Italic

Press any key (or 'q') to close the window.
"""

import os
from psychopy import core, visual, event, gui, monitors
import pandas as pd
from IPython import embed as shell
import mri_7T_parameters as p # see for timing, stimuli and parameters
# -------------------------
# Params
# -------------------------

#########################################
##############   PARAMS   ###############
#########################################

#Get subject number
g = gui.Dlg()
g.addField('Subject Number:')
g.addField('Run:')
g.show()
subject_ID = int(g.data[0])
run = int(g.data[1])
# in case GUI doesn't work
# subject_ID = 1
# run = 1

if subject_ID:
    
    # get this subject's counterbalanced response key mapping (yes_left or yes_right)
    df_counterbalancing = pd.read_csv(os.path.join('stimuli_blocks', 'counterbalancing.csv'))
    response_map = df_counterbalancing.loc[df_counterbalancing['subject'] == subject_ID, 'response_map'].values[0]
    
    # key_to_answer: which key ('left'/'right') corresponds to which answer ('yes'/'no') for this subject
    if response_map == 'yes_left':
        key_to_answer = {'1': 'yes', '2': 'no'}
        yes_pos, no_pos = (-50, -50), (50, -50)
    else:  # 'yes_right'
        key_to_answer = {'1': 'no', '2': 'yes'}
        yes_pos, no_pos = (50, -50), (-50, -50)
    
    this_subject = pd.read_csv(os.path.join('colors', 'sub-{}_colors.csv'.format(subject_ID)))
    graphemes    = list(this_subject['inducing'])     # synesthesia inducing graphemes
    symbols      = list(this_subject['non_inducing']) # graphemes that don't induce synesthesia
    
    columns = [
        {'label': p.english_regular[1], 'font': p.english_regular[1], 'chars': graphemes},
        {'label': p.english_italic[1],  'font': p.english_italic[1],  'chars': graphemes},
        {'label': p.pseudo_regular[1],  'font': p.pseudo_regular[1],  'chars': symbols},
        {'label': p.pseudo_italic[1],   'font': p.pseudo_italic[1],   'chars': symbols},
    ]

    font_files = [
        os.path.join('font', p.pseudo_regular[0]), 
        os.path.join('font', p.pseudo_italic[0]), 
        os.path.join('font', p.english_regular[0]), 
        os.path.join('font', p.english_italic[0]), 
    ]

    letter_height = 40   # height of each letter, pix
    row_spacing   = 60   # vertical distance between graphemes, pix
    col_spacing   = 220  # horizontal distance between columns, pix
    label_height  = 18   # height of column header text, pix

    # -------------------------
    # Window
    # -------------------------
    mon = monitors.Monitor('myMac15', width=p.screen_width, distance=p.screen_dist)
    mon.setSizePix((p.scnWidth, p.scnHeight))
    win = visual.Window(
        (p.scnWidth, p.scnHeight),
        color = p.white,
        colorSpace = 'rgb255',
        monitor = mon,
        fullscr = not p.debug_mode,
        units = 'pix',
        allowStencil = True,
        autoLog = False
        )
    win.setMouseVisible(False)

    # -------------------------
    # Stimuli
    # -------------------------
    
    # Set-up stimuli and timing
    instr_top = visual.TextStim(win, color='black', pos=(0.0, 130), wrapWidth=p.ww)
    instr_bottom = visual.TextStim(win, color='black', pos=(0.0, -180), wrapWidth=p.ww)
    instr_center = visual.TextStim(win, color='black', pos=(0.0, 0.0), wrapWidth=p.ww)
    
    # Outer circle (grey)
    stim_fix_outer = visual.Circle(win, radius=5, fillColor='grey', lineColor='grey', edges=128)
    # Inner circle (black)
    stim_fix_inner = visual.Circle(win, radius=2, fillColor='black', lineColor='black', edges=128)
    
    stim_word = visual.TextStim(win, color ='black', pos=(0.0, 0.0), height=p.lh) # SET FONT HERE, SCALING
    
    # Signal present prompt
    stim_question = visual.TextStim(
        win,
        text='Symbol in italics?',
        pos=(0, 50),
        color='black',
        height=20,
        wrapWidth=p.ww
    )

    # Response options, positioned underneath (side depends on this subject's response_map)
    stim_yes = visual.TextStim(
        win,
        text='yes',
        pos=yes_pos,
        color='black',
        height=20
    )

    stim_no = visual.TextStim(
        win,
        text='no',
        pos=no_pos,
        color='black',
        height=20
    )
    
    # Register the font files once, up front
    dummy = visual.TextStim(win)
    dummy.fontFiles = font_files

    n_cols = len(columns)
    n_rows = len(graphemes)  # assumes graphemes and symbols are the same length (8)
    top_y = (n_rows - 1) / 2.0 * row_spacing + 60  # leave room for header
    start_x = -(n_cols - 1) / 2.0 * col_spacing

    stims = []

    for c, col in enumerate(columns):
        x = start_x + c * col_spacing

        # Column header
        header = visual.TextStim(
            win, text=col['label'], font='Arial',
            color='black', pos=(x, top_y + row_spacing),
            height=label_height, bold=True
        )
        stims.append(header)

        # 8 characters stacked vertically (graphemes for Courier columns,
        # symbols for BACS2serif columns - see 'chars' in each column dict)
        for r, letter in enumerate(col['chars']):
            y = top_y - r * row_spacing
            letter_stim = visual.TextStim(
                win, text=letter, font=col['font'],
                color='black', pos=(x, y),
                height=letter_height
            )
            stims.append(letter_stim)

    #########################################
    ############# INSTRUCTIONS ##############
    #########################################
    welcome_txt_center1 = "The scanner will start to make noises while it registers the position of your head.\
    \nWhile we wait, please read the instructions carefully:\
    \n\nFirst, it is crucial that you do not move (especially your head) during the ENTIRE time you are in the scanner.\
    \nEven when the scanner is quiet and you think it is not measuring anything, it is very important to stay completely still.\
    \nTiny movements of 1-2 mm can be deterimental to the data quality.\
    \nHowever, you may blink like normal throughout the experiment!\
    \n\nSecond, to reduce head motion, we also ask that you do not speak unless it's crucial to tell us something is wrong with the experiment.\
    \nWe will periodically ask if you are doing alright, and you can indicate YES by button press.\
    \nIf you want to end the experiment early at any time, press the ALARM BUTTON and we will take you out immediately.\
    \n\nFinally, there will be a small fixation cross at the center of the screen at all times during the experiment.\
    \nPlease maintain eye-fixation there even when there is nothing else on the screen (i.e., do not move your eyes around).\
    \nYou will have some short breaks when you can close your eyes. We will let you know!\
    \n\n[PUSH ANY BUTTON TO CONTINUE THE INSTRUCTIONS]"
    
    welcome_txt_center2 = "During this experiment, you will be presented with a few versions of the same task:\
    \nYou will see a sequence of letters, symbols, words and word-like strings in black and in color flashing one-by-one on screen.\
    \nYour task is always the same: monitor the sequence to see if you spot one instance in ITALICS.\
    \n\nThe series of stimuli are presented for ~16 seconds followed by a break where no stimuli is presented for an additional 16 seconds.\
    \nDuring this break period, you will be asked to indicate if you saw one of the stimuli in italics or not.\
    \nYou will use the button box to respond: yes/no. \
    \nIf you are unsure, just guess! You can still push the button even after the question prompt dissapears.\
    \n\nSo that you can get familiar with the stimuli and question prompt, we will show that to you now...\
    \n\n[PUSH ANY BUTTON TO CONTINUE THE INSTRUCTIONS]"
    

    welcome_txt_top = "You will see a series of symbols presented on screen.\
    \nYour task is to view the symbols and notice if any of them are presented in ITALICS.\
    \n\nA question will appear after each series of word strings, exactly like the example below:"

    welcome_txt_bottom = "At that time, you can respond with a button press.\
    \n\nMaintain eye-fixation at the center of the screen at all times\
    \n(even when there are no symbols/words).\
    \n\nLay as still as possible for the duration of the scan session\
    \n(that includes between scans!)\
    \n\n[Waiting for scanner...]"
    
    
    #####################################
    # Instructions, waiting for scanner #
    #####################################
    instr_top.setText(welcome_txt_top)
    instr_bottom.setText(welcome_txt_bottom)

    instr_top.draw()
    stim_fix_outer.draw()
    stim_fix_inner.draw()
    stim_question.draw()
    stim_yes.draw()
    stim_no.draw()
    instr_bottom.draw()
    win.flip()
    # -------------------------
    # Draw and wait
    # -------------------------
    for s in stims:
        s.draw()
    win.flip()

    event.waitKeys()
    
    
    win.close()
    core.quit()
