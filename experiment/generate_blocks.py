#!/usr/bin/python2
# -*- coding: utf-8 -*-
"""
Generate random blocks and task
O.Colizoli, 2026

anaconda environment psychopy
"""

import os
import itertools
import random
import pandas as pd
from IPython import embed as shell # for debugging only


def shuffle_no_adjacent_repeats(seq):
    """
    Randomly shuffle a sequence such that no two identical elements
    are adjacent to each other.

    Uses rejection sampling: repeatedly shuffles the sequence until
    an ordering with no adjacent duplicates is found. This is fast
    and reliable for sequences where duplicates are a small fraction
    of the total length (e.g., each value appearing twice), but may
    be slow or fail to terminate for sequences where avoiding
    adjacent repeats is difficult or impossible (e.g., a sequence
    where one value makes up more than half of all elements).

    Parameters
    ----------
    seq : list
        The sequence of elements to shuffle. Elements must support
        equality comparison (==).

    Returns
    -------
    list
        A new list containing the same elements as `seq`, randomly
        shuffled, with no two identical elements adjacent to each
        other. The original list is not modified.

    Examples
    --------
    >>> numbers = list(range(5)) * 2
    >>> result = shuffle_no_adjacent_repeats(numbers)
    >>> any(result[i] == result[i + 1] for i in range(len(result) - 1))
    False
    """
    seq = seq.copy()
    while True:
        random.shuffle(seq)
        if all(seq[i] != seq[i+1] for i in range(len(seq) - 1)):
            return seq


def shuffle_chunks_no_boundary_repeat(base, n_chunks):
    """Shuffle each chunk of 'base' independently, ensuring no chunk boundary
    has the same element on both sides (last of chunk i != first of chunk i+1)."""
    chunks = []
    for i in range(n_chunks):
        while True:
            chunk = base.copy()
            random.shuffle(chunk)
            # check boundary with previous chunk
            if i == 0 or chunk[0] != chunks[-1][-1]:
                chunks.append(chunk)
                break
    return [x for chunk in chunks for x in chunk]


def generate_full_coverage_color_pairs(n_items, n_blocks, reps_per_block):
    """
    Generate, for each block, a pair of colors per grapheme (matching
    reps_per_block occurrences), such that:
      - within each block, every color is used exactly reps_per_block
        times across all graphemes (balanced per block)
      - across all blocks, every grapheme is paired with EVERY color
        exactly once in total (full coverage of the color space)

    Requires n_blocks * reps_per_block == n_items.
    Returns a list of length n_blocks; each element maps grapheme -> [colors...]
    """
    assert reps_per_block == 2, "This construction is specific to reps_per_block=2"
    assert n_blocks * reps_per_block == n_items, "n_blocks * reps_per_block must equal n_items"

    half = n_items // 2

    # Random relabeling of grapheme/color identities (so it's not a trivial fixed pattern)
    item_perm = list(range(n_items))
    random.shuffle(item_perm)
    pos = {val: idx for idx, val in enumerate(item_perm)}

    # n_blocks offsets, one per residue 0..half-1, in random order
    offsets = list(range(half))
    random.shuffle(offsets)

    block_color_pairs = []
    for offset in offsets:
        pair_map = {}
        for g in range(n_items):
            p = pos[g]
            c1 = item_perm[(p + offset) % n_items]
            c2 = item_perm[(p + offset + half) % n_items]
            pair_map[g] = [c1, c2]
        block_color_pairs.append(pair_map)
    return block_color_pairs
    

def random_derangement(n):
    """Return a random permutation of range(n) with no fixed points (no i where perm[i] == i)."""
    while True:
        perm = list(range(n))
        random.shuffle(perm)
        if all(perm[i] != i for i in range(n)):
            return perm


def generate_incongruent_color_pairs(n_items, n_blocks, reps_per_block):
    """
    Used for condition #5 (inducing graphemes, incongruent colors).
    Generate, for each block, a pair of colors per grapheme (matching
    reps_per_block occurrences), such that:
      - a grapheme is NEVER paired with its own ("congruent") color index
      - across all blocks, each grapheme gets 6 of the remaining 7 colors
        once, and exactly 1 of them twice (the "extra"), covering all
        7 allowed colors
      - the "extra" doubled color is different for every grapheme --
        i.e., each color serves as someone's extra exactly once, globally
      - within each block, every color is still used exactly reps_per_block
        times overall (balanced per block)
      - a grapheme's two occurrences within the SAME block always get
        different colors

    Requires n_blocks * reps_per_block == n_items.
    Returns a list of length n_blocks; each element maps grapheme -> [colors...]
    """
    assert reps_per_block == 2, "This construction is specific to reps_per_block=2"
    assert n_blocks * reps_per_block == n_items, "n_blocks * reps_per_block must equal n_items"

    # Random relabeling so it's not a fixed numeric pattern
    item_perm = list(range(n_items))
    random.shuffle(item_perm)
    pos = {val: idx for idx, val in enumerate(item_perm)}

    def relabeled_shift(k):
        return [item_perm[(pos[g] + k) % n_items] for g in range(n_items)]

    # n_items - 1 shift-derangements cover every off-diagonal (grapheme, color) pair exactly once
    shifts = [relabeled_shift(k) for k in range(1, n_items)]

    # One extra derangement determines which color is doubled for each grapheme.
    # Since it's a derangement (a bijection with no fixed points), every color
    # ends up as the "extra" for exactly one grapheme.
    e = random_derangement(n_items)

    all_slots = shifts + [e]  # n_items permutations total (= n_blocks * reps_per_block)
    assert len(all_slots) == n_items

    # Partition the n_items slots into n_blocks groups of reps_per_block,
    # rejecting any grouping where a grapheme's two slots in the same
    # group would give it the same color twice within one block.
    slot_indices = list(range(len(all_slots)))
    while True:
        random.shuffle(slot_indices)
        groups = [slot_indices[i*reps_per_block:(i+1)*reps_per_block] for i in range(n_blocks)]
        valid = True
        for group in groups:
            for g in range(n_items):
                colors_in_group = [all_slots[s][g] for s in group]
                if len(set(colors_in_group)) < len(colors_in_group):
                    valid = False
                    break
            if not valid:
                break
        if valid:
            break

    block_pair_maps = []
    for group in groups:
        pair_map = {g: [all_slots[s][g] for s in group] for g in range(n_items)}
        block_pair_maps.append(pair_map)

    return block_pair_maps
    
    
def counterbalancing_task_conditions(n_subjects):
    """
    Generate a subject-level counterbalancing scheme for three binary
    experimental factors:

    - color_start  : whether a subject's color localizer blocks begin
                      with 'color' or 'black'
    - vwfa_order   : whether the VWFA task presents 'word' or
                      'pseudo'
    - response_map : whether 'yes' responses are mapped to 'yes_left'
                      or 'yes_right'

    Rather than deriving each factor independently from subject
    parity (which risks confounding factors with each other, or with
    subject number), this function builds the full factorial of all
    2 x 2 x 2 = 8 possible combinations, shuffles their order once
    (governed by the global `random` seed set by the caller), and
    cycles through them subject by subject. This guarantees that
    every complete cycle of 8 subjects contains each combination
    exactly once, so each factor is balanced on its own and none of
    the three factors is confounded with another.

    Requires `random.seed(...)` to be set by the caller beforehand
    for a reproducible assignment across runs.

    Parameters
    ----------
    n_subjects : int
        Number of subjects to generate a counterbalancing assignment
        for. Subject numbers run from 1 to n_subjects. If n_subjects
        is not a multiple of 8, the final partial cycle will be
        slightly less balanced than a full cycle.

    Output
    ------
    Writes 'stimuli_blocks/counterbalancing.csv' with one row per
    subject and columns: subject, color_start, vwfa_order, response_map.
    """
    output_dir = os.path.join('stimuli_blocks')
    os.makedirs(output_dir, exist_ok=True)


    # All 8 combinations of the 3 binary factors
    combos = list(itertools.product([0, 1], repeat=3))

    # Shuffle order once, using whatever random seed the caller has set
    combos_shuffled = combos.copy()
    random.shuffle(combos_shuffled)

    rows = []
    for s in range(n_subjects):
        subject_number = s + 1
        combo = combos_shuffled[s % len(combos_shuffled)]
        rows.append({
            'subject': subject_number,
            'color_start':   'color' if combo[0] == 0 else 'black',
            'vwfa_order':    'word' if combo[2] == 0 else 'pseudo',
            'response_map':  'yes_left' if combo[1] == 0 else 'yes_right'
        })

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(output_dir, 'counterbalancing.csv'), index=False)
    print("success: counterbalancing_task_conditions")


def define_blocks_color_localizer(n_subjects):
    """
    Define the color order, letter order, and signal present for
    each block of the color localizer, for every subject.

    Each subject's block order (color vs black, alternating) is
    determined by the 'color_start' assignment in
    'stimuli_blocks/counterbalancing.csv', rather than subject
    parity, so it stays consistent with the other counterbalanced
    factors generated by counterbalancing_task_conditions().

    Parameters
    ----------
    n_subjects : int
        Number of subjects to generate block sequences for. Subject
        numbers run from 1 to n_subjects.

    Requires
    --------
    counterbalancing_task_conditions(n_subjects) must be run first,
    so that 'stimuli_blocks/counterbalancing.csv' exists and covers
    at least this many subjects.

    Output
    ------
    Per subject, writes three CSVs to 'stimuli_blocks/color_localizer/':
    letter sequences, the signal-present (italics) mask, and the
    color/black block-type order.
    """
    # put output sequences here
    output_dir = os.path.join('stimuli_blocks', 'color_localizer')
    os.makedirs(output_dir, exist_ok=True)

    # Load subject-level counterbalancing (color_start, vwfa_order, response_map)
    # Must be generated first by counterbalancing_task_conditions()
    df_counterbalancing = pd.read_csv(os.path.join('stimuli_blocks', 'counterbalancing.csv'))

    n_blocks = 12           # need to be an even number to balance signal present in 50% of blocks
    numbers_per_block = 8   # how many unique letters/symbols 
    repeats_per_block = 2   #  how many times to repeat numbers_per_block per block, set to 1 if no repates

    for s in range(n_subjects):
        
        this_subject = s+1 # start with 1
        seq_data = {}
        mask_data = {}

        block_cols = [f'block_{b}' for b in range(n_blocks)]

        # Randomly choose half the blocks to contain the signal
        special_blocks = set(random.sample(block_cols, k=n_blocks // 2))

        for block in range(n_blocks):
            col = f'block_{block}'
            sequence = list(range(numbers_per_block)) * repeats_per_block # multiple stimuli if necessary
            sequence = shuffle_no_adjacent_repeats(sequence) # suffle and make sure no two-in-a-row
            seq_data[col] = sequence

            if col in special_blocks:
                special_idx = random.randrange(len(sequence))
                mask = [1 if i == special_idx else 0 for i in range(len(sequence))]
            else:
                mask = [0] * len(sequence)

            mask_data[col] = mask

        df_sequences = pd.DataFrame(seq_data)
        df_special = pd.DataFrame(mask_data)
        
        # Determine color vs black per block, alternating, starting type from counterbalancing file
        start_type = df_counterbalancing.loc[df_counterbalancing['subject'] == this_subject, 'color_start'].values[0]
        other_type = 'black' if start_type == 'color' else 'color'
        block_types = [start_type if b % 2 == 0 else other_type for b in range(n_blocks)]
        df_condition = pd.DataFrame([block_types], columns=block_cols)

        df_sequences.to_csv(os.path.join(output_dir, 'sub-{}_letter_sequences_color_localizer.csv'.format(this_subject)), index=False)
        df_special.to_csv(os.path.join(output_dir, 'sub-{}_letter_italics_color_localizer.csv'.format(this_subject)), index=False)
        df_condition.to_csv(os.path.join(output_dir, 'sub-{}_block_type_color_localizer.csv'.format(this_subject)), index=False)
        print(this_subject)
    print("success: define_blocks_color_localizer")


def define_blocks_vwfa_localizer(n_subjects):
    """
    Define the condition order, letter order, and signal present for
    each block of the VWFA localizer, for every subject.

    Each subject's block order (word vs pseudoword, alternating) is
    determined by the 'vwfa_order' assignment in
    'stimuli_blocks/counterbalancing.csv', rather than subject
    parity, so it stays consistent with the other counterbalanced
    factors generated by counterbalancing_task_conditions().

    The word and pseudoword conditions share the same underlying set
    of n_words/2 items (so each item appears once as a word and once
    as a matched pseudoword across the whole task), but each
    condition's presentation order is shuffled independently. Within
    each condition, words are drawn from a single pool covering all
    of that condition's blocks, guaranteeing a different item on
    every trial with no repeats.

    Parameters
    ----------
    n_subjects : int
        Number of subjects to generate block sequences for. Subject
        numbers run from 1 to n_subjects.

    Requires
    --------
    counterbalancing_task_conditions(n_subjects) must be run first,
    so that 'stimuli_blocks/counterbalancing.csv' exists and covers
    at least this many subjects. The stimuli lists used later must
    each contain at least (n_blocks * numbers_per_block) / 2 distinct
    items (words and matched pseudowords).

    Output
    ------
    Per subject, writes three CSVs to 'stimuli_blocks/vwfa_localizer/':
    letter sequences, the signal-present (italics) mask, and the
    word/pseudo word block-type order.
    """
    # put output sequences here
    output_dir = os.path.join('stimuli_blocks', 'vwfa_localizer')
    os.makedirs(output_dir, exist_ok=True)

    # Load subject-level counterbalancing (color_start, vwfa_order, response_map)
    # Must be generated first by counterbalancing_task_conditions()
    df_counterbalancing = pd.read_csv(os.path.join('stimuli_blocks', 'counterbalancing.csv'))

    n_blocks = 12           # need to be an even number to balance signal present in 50% of blocks
    numbers_per_block = 16  # how many unique words per block
    n_words = n_blocks * numbers_per_block   # 160
    n_words_half = n_words // 2              # 80, shared pool used by both conditions

    for s in range(n_subjects):
        
        this_subject = s+1 # start with 1
        seq_data = {}
        mask_data = {}

        block_cols = [f'block_{b}' for b in range(n_blocks)]

        # Randomly choose half the blocks to contain the signal
        special_blocks = set(random.sample(block_cols, k=n_blocks // 2))

        # Determine word vs pseudoword per block FIRST, since sequences depend on it
        start_type = df_counterbalancing.loc[df_counterbalancing['subject'] == this_subject, 'vwfa_order'].values[0]
        other_type = 'pseudo' if start_type == 'word' else 'word'
        block_types = [start_type if b % 2 == 0 else other_type for b in range(n_blocks)]
        df_condition = pd.DataFrame([block_types], columns=block_cols)

        # Same underlying set of items, shuffled independently per condition
        pool_word = list(range(n_words_half))
        random.shuffle(pool_word)

        pool_pseudo = list(range(n_words_half))
        random.shuffle(pool_pseudo)

        word_counter = 0
        pseudo_counter = 0
        for block in range(n_blocks):
            col = f'block_{block}'
            condition = block_types[block]

            if condition == 'word':
                sequence = pool_word[word_counter*numbers_per_block : (word_counter+1)*numbers_per_block]
                word_counter += 1
            else:
                sequence = pool_pseudo[pseudo_counter*numbers_per_block : (pseudo_counter+1)*numbers_per_block]
                pseudo_counter += 1

            seq_data[col] = sequence
            
            if col in special_blocks:
                special_idx = random.randrange(len(sequence))
                mask = [1 if i == special_idx else 0 for i in range(len(sequence))]
            else:
                mask = [0] * len(sequence)

            mask_data[col] = mask

        df_sequences = pd.DataFrame(seq_data)
        df_special = pd.DataFrame(mask_data)

        df_sequences.to_csv(os.path.join(output_dir, 'sub-{}_word_sequences_vwfa_localizer.csv'.format(this_subject)), index=False)
        df_special.to_csv(os.path.join(output_dir, 'sub-{}_word_italics_vwfa_localizer.csv'.format(this_subject)), index=False)
        df_condition.to_csv(os.path.join(output_dir, 'sub-{}_block_type_vwfa_localizer.csv'.format(this_subject)), index=False)
        print(this_subject)
    print("success: define_blocks_vwfa_localizer")
    
    
def define_blocks_main_task(n_subjects):
    """
    Define the condition order, letter order, and signal present for
    each block of the main task, for every subject.

    Each subject's block order (5 conditions, pseudorandomized) is
    determined by the 'condition' assignment in
    'stimuli_blocks/main_task.csv'

    Conditions:
    1. Inducing graphemes in black
    2. Non-inducing pseudo graphemes in black
    3. Inducing graphemes in congruent colors
    4. Non-inducing pseudo graphemes in colors from condition #3 equally
       spread across pseudo graphemes -- across the 4 repeats of this
       condition, every grapheme is paired with every one of the 8
       colors exactly once (full coverage; see
       generate_full_coverage_color_pairs).
    5. Inducing graphemes in incongruent colors from condition #3, equally
       spread across graphemes that are not corresponding -- a grapheme
       is never paired with its own color; across the 4 repeats, each
       grapheme gets 6 of the other 7 colors once and 1 of them twice,
       with the doubled color balanced so each color is "the extra" for
       exactly one grapheme overall (see generate_incongruent_color_pairs).

    Parameters
    ----------
    n_subjects : int
        Number of subjects to generate block sequences for. Subject
        numbers run from 1 to n_subjects.

    Output
    ------
    Per subject, writes four CSVs to 'stimuli_blocks/main_task/':
    letter sequences, the signal-present (italics) mask, the
    condition block-type order, and the grapheme-to-color map used
    for condition #4 and condition #5 blocks (same length as the
    letter sequences).
    """
    # put output sequences here
    output_dir = os.path.join('stimuli_blocks', 'main_task')
    os.makedirs(output_dir, exist_ok=True)

    n_conditions = 5        # need to be an even number to balance signal present in 50% of blocks
    n_repeat_conditions = 4 # how many times to repeat n_conditions
    numbers_per_block = 8   # how many unique letters/symbols
    repeats_per_block = 2   # how many times to repeat numbers_per_block per block, set to 1 if no repates

    for s in range(n_subjects):

        this_subject = s+1 # start with 1
        seq_data = {}
        mask_data = {}
        grapheme_color_map_data = {}

        block_cols = [f'block_{b}' for b in range(n_conditions*n_repeat_conditions)]
        # shuffle blocks in chunks while preventing same condition twice in a row
        block_sequence = shuffle_chunks_no_boundary_repeat(list(range(n_conditions)), n_repeat_conditions)
        # Randomly choose half the blocks to contain the signal
        special_blocks = set(random.sample(block_cols, k=len(block_cols) // 2))

        # Condition #4 (0-indexed: 3): full coverage, every grapheme gets all
        # 8 colors across its 4 blocks. Color maps for all 4 blocks are
        # generated TOGETHER (not independently) so pairings are guaranteed
        # to be maximally spread, rather than left to chance per block.
        condition4_block_indices = [b for b, c in enumerate(block_sequence) if c == 3]
        condition4_pair_maps = generate_full_coverage_color_pairs(
            numbers_per_block, len(condition4_block_indices), repeats_per_block
        )
        block_to_pair_map = dict(zip(condition4_block_indices, condition4_pair_maps))

        # Condition #5 (0-indexed: 4): incongruent, grapheme never gets its
        # own color, with the "extra" doubled color balanced across graphemes.
        condition5_block_indices = [b for b, c in enumerate(block_sequence) if c == 4]
        condition5_pair_maps = generate_incongruent_color_pairs(
            numbers_per_block, len(condition5_block_indices), repeats_per_block
        )
        block_to_pair_map.update(dict(zip(condition5_block_indices, condition5_pair_maps)))

        for block in range(len(block_cols)):
            col = f'block_{block}'
            sequence = list(range(numbers_per_block)) * repeats_per_block # multiple stimuli if necessary
            sequence = shuffle_no_adjacent_repeats(sequence) # suffle and make sure no two-in-a-row
            seq_data[col] = sequence

            if col in special_blocks:
                special_idx = random.randrange(len(sequence))
                mask = [1 if i == special_idx else 0 for i in range(len(sequence))]
            else:
                mask = [0] * len(sequence)

            mask_data[col] = mask

            # For condition #4 and #5 blocks, expand this block's grapheme->color
            # pair mapping to the full per-trial sequence length, so row i here
            # lines up with row i of seq_data/mask_data.
            if block in block_to_pair_map:
                pair_map = block_to_pair_map[block]
                occurrence_count = {g: 0 for g in range(numbers_per_block)}
                color_sequence = []
                for g in sequence:
                    idx = occurrence_count[g]
                    color_sequence.append(pair_map[g][idx])
                    occurrence_count[g] += 1
                grapheme_color_map_data[col] = color_sequence
            else:
                grapheme_color_map_data[col] = [''] * len(sequence)  # not applicable for this block

        df_sequences = pd.DataFrame(seq_data)
        df_special = pd.DataFrame(mask_data)

        # Output condition per block, alternating
        df_condition = pd.DataFrame([block_sequence], columns=block_cols)
        df_grapheme_color_map = pd.DataFrame(grapheme_color_map_data)

        df_sequences.to_csv(os.path.join(output_dir, 'sub-{}_letter_sequences_main_task.csv'.format(this_subject)), index=False)
        df_special.to_csv(os.path.join(output_dir, 'sub-{}_letter_italics_main_task.csv'.format(this_subject)), index=False)
        df_condition.to_csv(os.path.join(output_dir, 'sub-{}_block_type_main_task.csv'.format(this_subject)), index=False)
        df_grapheme_color_map.to_csv(os.path.join(output_dir, 'sub-{}_grapheme_color_map_main_task.csv'.format(this_subject)), index=False)
        print(this_subject)
    print("success: define_blocks_main_task")
    
    
if __name__ == "__main__":
    random.seed(42)
    n_subjects = 60
    # counterbalancing_task_conditions(n_subjects)
    define_blocks_color_localizer(n_subjects)
    define_blocks_vwfa_localizer(n_subjects)
    # define_blocks_main_task(n_subjects)