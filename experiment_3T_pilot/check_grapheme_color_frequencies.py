"""
Check grapheme-color pair frequencies for the main task's condition #4
(non-inducing pseudo graphemes, colors spread equally) and condition #5
(inducing graphemes, incongruent colors), with explicit per-participant
validation.

For every subject found in 'stimuli_blocks/main_task/', this reads:
  - sub-{n}_letter_sequences_main_task.csv
  - sub-{n}_block_type_main_task.csv
  - sub-{n}_grapheme_color_map_main_task.csv

identifies which blocks are condition #4 (index 3) and condition #5
(index 4), counts how often each (grapheme, color) pair occurs across
those blocks, and checks per participant:

  Condition #4: every grapheme gets every color exactly equally
  (i.e. exactly once each, since 4 blocks x 2 reps = 8 slots = 8 colors).

  Condition #5: grapheme g never gets color g (own/congruent color),
  and among the other 7 colors, grapheme g's counts are as equal as
  possible (differing by at most 1, i.e. 6 colors once + 1 color twice).

Usage: run from the directory containing 'stimuli_blocks/'.
"""
import os
import glob
from collections import Counter
import pandas as pd

main_task_dir = os.path.join('stimuli_blocks', 'main_task')

# Find all subjects present, from the sequences files
seq_files = glob.glob(os.path.join(main_task_dir, 'sub-*_letter_sequences_main_task.csv'))
subject_ids = sorted(int(f.split('sub-')[1].split('_')[0]) for f in seq_files)

CONDITION_LABELS = {3: 'condition_4', 4: 'condition_5'}
N_ITEMS = 8  # number of graphemes / colors

pooled_counts = {3: Counter(), 4: Counter()}
per_subject_counts = {3: {}, 4: {}}


def check_condition4(subject_ID, counter):
    """Every grapheme must get every color exactly once (equally)."""
    problems = []
    for g in range(N_ITEMS):
        for c in range(N_ITEMS):
            n = counter.get((g, c), 0)
            if n != 1:
                problems.append(f'grapheme {g} -> color {c}: count={n} (expected exactly 1)')
    if problems:
        print(f'  Subject {subject_ID}: FAIL')
        for p in problems:
            print(f'    - {p}')
    else:
        print(f'  Subject {subject_ID}: PASS (every grapheme got every color exactly once)')
    return len(problems) == 0


def check_condition5(subject_ID, counter):
    """
    Grapheme g must never get color g. Among the other 7 colors,
    counts should differ by at most 1 (i.e. 6 colors once, 1 color twice).
    """
    problems = []
    for g in range(N_ITEMS):
        own_count = counter.get((g, g), 0)
        if own_count != 0:
            problems.append(f'grapheme {g} -> own color {g}: count={own_count} (expected 0, violation!)')

        other_counts = [counter.get((g, c), 0) for c in range(N_ITEMS) if c != g]
        if other_counts:
            spread = max(other_counts) - min(other_counts)
            if spread > 1:
                problems.append(
                    f'grapheme {g}: uneven distribution across other 7 colors {other_counts} (spread={spread}, expected <=1)'
                )

    if problems:
        print(f'  Subject {subject_ID}: FAIL')
        for p in problems:
            print(f'    - {p}')
    else:
        print(f'  Subject {subject_ID}: PASS (own color never used; other 7 colors as equal as possible)')
    return len(problems) == 0


for subject_ID in subject_ids:
    df_sequences = pd.read_csv(os.path.join(main_task_dir, 'sub-{}_letter_sequences_main_task.csv'.format(subject_ID)))
    df_condition = pd.read_csv(os.path.join(main_task_dir, 'sub-{}_block_type_main_task.csv'.format(subject_ID)))
    df_colormap = pd.read_csv(os.path.join(main_task_dir, 'sub-{}_grapheme_color_map_main_task.csv'.format(subject_ID)))

    block_sequence = df_condition.iloc[0].tolist()

    for cond_idx in (3, 4):
        subj_counter = Counter()
        blocks_this_cond = [b for b, c in enumerate(block_sequence) if c == cond_idx]

        for b in blocks_this_cond:
            col = f'block_{b}'
            graphemes = df_sequences[col].tolist()
            colors = df_colormap[col].tolist()
            for g, c in zip(graphemes, colors):
                pair = (g, c)
                subj_counter[pair] += 1
                pooled_counts[cond_idx][pair] += 1

        per_subject_counts[cond_idx][subject_ID] = subj_counter

# --- Per-participant validation ---
print('=' * 60)
print('PER-PARTICIPANT VALIDATION')
print('=' * 60)

print('\nCondition #4 (every grapheme gets every color exactly once):')
c4_results = [check_condition4(sid, per_subject_counts[3][sid]) for sid in subject_ids]

print('\nCondition #5 (own color never used; other 7 colors as equal as possible):')
c5_results = [check_condition5(sid, per_subject_counts[4][sid]) for sid in subject_ids]

print()
print(f'Condition #4: {sum(c4_results)}/{len(c4_results)} subjects passed')
print(f'Condition #5: {sum(c5_results)}/{len(c5_results)} subjects passed')

# --- Frequency report ---
print()
for cond_idx, label in CONDITION_LABELS.items():
    print('=' * 60)
    print(f'{label} (condition index {cond_idx}) -- grapheme-color pair frequencies')
    print('=' * 60)

    print('\nPooled across all subjects:')
    for pair, count in sorted(pooled_counts[cond_idx].items()):
        print(f'  grapheme {pair[0]} -> color {pair[1]}: {count}')

    print('\nPer subject:')
    for subject_ID, counter in per_subject_counts[cond_idx].items():
        print(f'  Subject {subject_ID}:')
        for pair, count in sorted(counter.items()):
            print(f'    grapheme {pair[0]} -> color {pair[1]}: {count}')
    print()

# --- Save frequency tables to CSV: pooled AND per subject ---
os.makedirs('checks', exist_ok=True)
for cond_idx, label in CONDITION_LABELS.items():
    # Pooled across all subjects
    rows = [{'grapheme': g, 'color': c, 'count': n} for (g, c), n in sorted(pooled_counts[cond_idx].items())]
    df_out = pd.DataFrame(rows)
    out_path = os.path.join('checks', f'{label}_grapheme_color_frequencies.csv')
    df_out.to_csv(out_path, index=False)
    print(f'Saved: {out_path}')

    # Per subject
    for subject_ID in subject_ids:
        counter = per_subject_counts[cond_idx][subject_ID]
        rows = []
        for g, c in sorted(counter.keys()):
            n = counter[(g, c)]
            if cond_idx == 3:
                valid = (n == 1)
            else:  # cond_idx == 4
                valid = (g != c)  # own color would be a violation
            rows.append({'grapheme': g, 'color': c, 'count': n, 'valid': valid})
        df_out = pd.DataFrame(rows)
        out_path = os.path.join('checks', f'{label}_sub-{subject_ID}_grapheme_color_frequencies.csv')
        df_out.to_csv(out_path, index=False)
        print(f'Saved: {out_path}')
