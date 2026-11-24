"""
Rename the internal family/full/PostScript names of your font files so
each one has a UNIQUE name that exactly matches the string used in
stim_word.font = '...' in your task script.

Run this from inside your 'font' folder. It writes renamed copies
alongside the originals (does not overwrite them), so nothing is lost.
"""
from fontTools.ttLib import TTFont

# (original_filename, new_unique_family_name, output_filename)
renames = [
    # ('CourierNew.ttf',   'CourierNew',   'CourierNew_fixed.ttf'),
    ('BACS2serif.otf',        'BACS2serif',        'BACS2serif_fixed.otf'),
    ('BACS2serif-Italic.otf',        'BACS2serif-Italic',        'BACS2serif-Italic_fixed.otf'),
    
]

for src_file, new_name, out_file in renames:
    tt = TTFont(src_file)
    name_table = tt['name']

    # nameID 1 = Family, 4 = Full name, 6 = PostScript name
    # PostScript name (6) cannot contain spaces, so strip any just in case
    ps_name = new_name.replace(' ', '')

    for record in name_table.names:
        if record.nameID == 1:
            record.string = new_name
        elif record.nameID == 4:
            record.string = new_name
        elif record.nameID == 6:
            record.string = ps_name

    tt.save(out_file)
    print(f'{src_file} -> {out_file}  (family renamed to "{new_name}")')

print()
print('Done. Update your fontFiles list to point at the _fixed.ttf files')
print('(HebrewUniversal.ttf can stay as-is, since it already matched).')
