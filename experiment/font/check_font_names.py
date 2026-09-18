"""
Check the internal name-table entries of your font files.
This tells you the EXACT string PsychoPy/pyglet will register the font
under -- which may not match the filename at all.

Usage: run this in the same environment as PsychoPy, pointed at your
'font' folder.
"""
import os
from fontTools.ttLib import TTFont

font_files = [
        'BACS2serif.otf', 
        'BACS2serif-Italic.otf', 
        'CourierNew.ttf', 
        'CourierNew-Italic.ttf', 
]

for fname in font_files:
    path = os.path.join(fname)
    if not os.path.exists(path):
        print(f'{fname}: FILE NOT FOUND at {path}')
        continue

    tt = TTFont(path)
    name_table = tt['name']

    # nameID 1 = Font Family name, nameID 2 = Font Subfamily (style), nameID 4 = Full name, nameID 6 = PostScript name
    family = name_table.getDebugName(1)
    subfamily = name_table.getDebugName(2)
    full_name = name_table.getDebugName(4)
    ps_name = name_table.getDebugName(6)

    print(f'--- {fname} ---')
    print(f'  Family (nameID 1):     {family}')
    print(f'  Subfamily (nameID 2):  {subfamily}')
    print(f'  Full name (nameID 4):  {full_name}')
    print(f'  PostScript (nameID 6): {ps_name}')
    print()
