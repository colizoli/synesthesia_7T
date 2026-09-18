# synesthesia_7T
code for the 7T fMRI experiment on synesthesia

anaconda environment psychopy

To test the experiment, run with sub-1. 

experiment/01_main_task_fMRI_7T.py: the main task with 5 conditions

experiment/02_color_localizer_fMRI_7T.py: the color localizer

experiment/03_vwfa_localizer_fMRI_7T.py: the visual word form area (VWFA) localizer

Counterbalancing and stimuli orders are predetermined. 
Generated with the experiment/generate_blocks.py function (works until N=60 participants then gets stuck in a while loop).
For all n=60 files, unzip the experiment/stimuli_blocks.zip file.

Add colors file for each subject to experiment/colors

False fonts were taken from the BACS OSF repository:
https://link.springer.com/article/10.3758/s13428-016-0844-8

The English words were taken from the SUBTLEXUS repository:
https://p.www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexus


