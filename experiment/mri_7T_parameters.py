#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
PARAMETERS MRI (localizers & RSA tasks)

conda install pyqt
pip install pyserial
"""

import os
from psychopy import core, event

"""
General parameters and functions for scanning
"""

debug_mode = False
fmri_mode  = False       # waits for trigger to start stimuli blocks
scanner    = False       # True: scanner pulses come in on the serial port; False: '5' key from the keyboard
buttons_serial = False   # True: button box on a serial port; False: button box in USB mode (= keyboard)
trigger_key    = ['5']

##########################
# Serial port settings
##########################
# Trigger from SerialPort: COM3, baudrate 115200, parity none, databits 8, stopbits 1, ASCII code 97 ('a')
BB_SERIAL_PORT_TRIGGER = "COM3"
TRIGGER_CODE = chr(97)  # 'a'

# Button box on a serial port (only used if buttons_serial = True)
BB_SERIAL_PORT_BUTTONS = "COM2"
# Map the characters your button box sends to the response keys used in the tasks ('1', '2').
# CHECK THIS on the scanner setup: press each button and see what is printed.
BUTTON_SERIAL_MAP = {'a': '1', 'b': '2'}

if not scanner:
    TRIGGER_CODE = trigger_key[0]  # wait for a '5' from the keyboard

trigger_port = None
button_port = None
pulse_log = []       # clock time (s) of EVERY scanner pulse received during the run
_button_queue = []   # serial button presses not yet collected: (key, time)


def open_ports():
    '''Open the serial ports once at the start of the run and keep them open.'''
    global trigger_port, button_port
    if scanner or buttons_serial:
        import serial
    if scanner:
        trigger_port = serial.Serial(BB_SERIAL_PORT_TRIGGER, baudrate=115200, timeout=0)
        trigger_port.reset_input_buffer()
    if buttons_serial:
        button_port = serial.Serial(BB_SERIAL_PORT_BUTTONS, baudrate=115200, timeout=0)
        button_port.reset_input_buffer()


def close_ports():
    for port in (trigger_port, button_port):
        if port is not None:
            port.close()


def poll(clock):
    '''Read everything waiting on the serial ports (or '5' keys) and timestamp it.
    Call this often: every frame, and inside every wait.'''
    t = clock.getTime()
    # scanner pulses
    if scanner:
        if trigger_port.in_waiting:
            data = trigger_port.read(trigger_port.in_waiting).decode('ascii', errors='ignore')
            pulse_log.extend([t] * data.count(TRIGGER_CODE))
    else:
        for key, key_time in event.getKeys(keyList=trigger_key, timeStamped=clock):
            pulse_log.append(key_time)
    # serial button box
    if buttons_serial and button_port.in_waiting:
        data = button_port.read(button_port.in_waiting).decode('ascii', errors='ignore')
        for ch in data:
            if debug_mode:
                print('button box sent: {!r}'.format(ch))
            if ch in BUTTON_SERIAL_MAP:
                _button_queue.append((BUTTON_SERIAL_MAP[ch], t))


def get_responses(clock, keyList):
    '''Like event.getKeys(keyList, timeStamped=clock), but also includes serial button presses.
    Returns a list of (key, time) sorted by time.'''
    poll(clock)
    pressed = event.getKeys(keyList=keyList, timeStamped=clock)
    pressed += [b for b in _button_queue if b[0] in keyList]
    del _button_queue[:]
    pressed.sort(key=lambda x: x[1])
    return pressed


def clear_responses(clock):
    '''Clear old key/button presses (pulses are logged first, so none are lost).'''
    poll(clock)
    event.clearEvents(eventType='keyboard')
    del _button_queue[:]


def wait(duration, clock):
    '''Replacement for core.wait(): keeps logging scanner pulses, 'q' quits.'''
    t_end = clock.getTime() + duration
    while clock.getTime() < t_end:
        if get_responses(clock, ['q']):
            close_ports()
            core.quit()


def waitForTrigger(clock):
    '''Wait for the NEXT scanner pulse (serial port, or '5' key when scanner = False).
    'q' will terminate. Returns [[TRIGGER_CODE, time_of_pulse]].'''
    poll(clock)  # log any pulses that already arrived, so only a new one counts
    event.clearEvents(eventType='keyboard')
    n_pulses = len(pulse_log)
    while len(pulse_log) == n_pulses:
        poll(clock)
        if event.getKeys(keyList=['q']):
            close_ports()
            core.quit()
    if debug_mode:
        print('MRI trigger received at {:.3f} s'.format(pulse_log[-1]))
    return [[TRIGGER_CODE, pulse_log[-1]]]


def save_pulses(filename, first_pulse):
    '''Save all pulse times (relative to the first pulse) to a tsv file.'''
    import pandas as pd
    df = pd.DataFrame({'pulse': range(len(pulse_log)),
                       'onset': [t - first_pulse for t in pulse_log],
                       'clock_time': pulse_log})
    df.to_csv(filename, sep='\t', index=False)

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

lh = 150   # letter size
ly = 6     # adjust letter up y-axis (pixels)
ww = 2000  # wrap width of instructions text
ih = 25    # size of instructions text

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
