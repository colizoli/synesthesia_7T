#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
PARAMETERS MRI (localizers & RSA tasks)

conda install pyqt
pip install pyserial
"""

import os
from psychopy import event

# BUTTON BOXES PUT ON USB MODE, CAN LISTEN AS NORMAL KEYBOARD
# http://p.www.psychopy.org/api/hardware/forp.html
# BB_SERIAL_PORT_BUTTONS = "COM1"
# from psychopy import hardware
# forp = hardware.forp.ButtonBox(serialPort=1, baudrate=19200)
# respond = forp,getEvents(returnRaw=False, asKeys=False, allowRepeats=False)

"""
General parameters and functions for scanning
"""

debug_mode = True
fmri_mode = False   # waits for trigger to start stimuli blocks
scanner = False     # everything coming in as keyboard
trigger_key = ['5']

if scanner: # when you are really scanning 
    ## Trigger from SerialPort: com3 SerialPort number, baudrate 115200, parity none, databits 8, stopbits 1, ASCIICODE 97
    BB_SERIAL_PORT_TRIGGER = "COM3"
    TRIGGER_CODE = 97
else: # wait for a '5' from the keyboard
    TRIGGER_CODE = trigger_key
    
def waitForTrigger(clock,): 
    '''  Need to listen on the serial port for the MRI start signal,
    Also/either wait for any key press ('q' will terminate). 
    https://groups.google.com/forum/#!topic/psychopy-users/TqxZYXx8aU4
    ''' 
    event.clearEvents(eventType='keyboard') # remove any keys waiting in the queue 
    while True: 
        if scanner == True: # set during the initial imports at the beginning of this module 
            SPORT = serial.Serial(BB_SERIAL_PORT_TRIGGER,115200) # OPEN PORT: port, baudrate, timeout (none)
            if (SPORT.inWaiting() > 0): # check for an MRI trigger signal on the serial port 
                print('MRI trigger received! {}'.format(SPORT.read())) 
                if (SPORT.read() == TRIGGER_CODE): # the MRI 'start' code, TRIGGER CODE
                    respond = [[TRIGGER_CODE, clock.getTime()]]
                    break # begin the experiment  
        else:
            respond = event.waitKeys(keyList=trigger_key+['q'], timeStamped=clock)
            # also check for a keyboard trigger
            if len(respond) > 0: 
                if respond == ['q']: core.quit() #  escape allows us to exit 
                break # else begin the experiment 
    return respond
    
################### 
# shared parameters
###################
# response buttons
keys = ['1','2']   # buttons 1 and 2, yes vs. no counterbalanced
#keys = ['b','y','g','r','w']

# timing
t_bold_baseline = 16          # bold baseline period in seconds, show fixation cross at the beginning and end of the run
t_fix           = [0.2, 0.24] # pre-grapheme fixation in seconds jittered 
t_grapheme      = 0.75        # presentation duration of grapheme in seconds 
t_word          = t_grapheme  # same duration in VWFA
t_rest          = 16          # duration of rest period in between blocks (fixation cross) in seconds
t_prompt_onset  = [2, 4]      # time to wait for signal present prompt in rest blocks
t_prompt        = 1.5         # time to present the prompt question in seconds

lh = 100   # letter size
ly = 6    # adjust letter up y-axis (pixels)
ww = 2000  # wrap width of instructions text          

scnWidth, scnHeight = (1920,1080) # MRI BOLDscreen 120Hz, # (1024,768) MRI stim computer, #(1280, 1024) # dummy scanner settings
screen_width        = 53.5 # centimeters
screen_dist         = 70.0
white               = [255,255,255] # background screen color
grey                = [128,128,128]
black               = [0,0,0] # background screen color

# define fonts
pseudo_regular = ['BACS2serif.otf', 'BACS2serif',] # False font regular
pseudo_italic = ['BACS2serif-Italic.otf', 'BACS2serif-Italic'] # False font italics 
english_regular = ['CourierNew.ttf', 'CourierNew'] # English regular
english_italic = ['CourierNew-Italic.ttf', 'CourierNew-Italic'] # English italics  


