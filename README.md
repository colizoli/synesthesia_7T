# synesthesia_7T
code for the 7T fMRI experiment on synesthesia

anaconda environment psychopy

experiment/01_main_task_fMRI_7T.py: the main task with 5 conditions
experiment/02_color_localizer_fMRI_7T.py: the color localizer
experiment/03_vwfa_localizer_fMRI_7T.py: the visual word form area (VWFA) localizer

Counterbalancing and stimuli orders are predetermined. 
Generated with the experiment/generate_blocks.py function (works until N=60 participants then gets stuck in a while loop).
For all n=60 files, unzip the experiment/stimuli_blocks.zip file.

To test the experiment, run with sub-1. 
Add colors file for each subject to experiment/colors
