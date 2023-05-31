"""
Read scraped run names and apply basic cleaning logic (e.g., removing run modifiers like 'any%'
or marking preshow runs as runs to ignore).
"""

import pandas as pd
import os
import json
import re
import html
from unidecode import unidecode

filepath = os.path.join('data', 's1_scraped_runs.jsonl')
df = pd.read_json(filepath, lines=True)

# Looking at top 100 words in ct_df, manually create list of confirmed game modifiers
gme_mods_1w = ['any%', '100%', 'glitchless', 'ng+', 'ng', 'warpless', 'randomizer', 'glitches', '%', 'glitched', 'tasbot%']
gme_mods_other = ['no save & quit', 'no out of bounds', 'all bosses', 'all goals', 'all dungeons', 'no skips']
ignore_runs_with = ['finale', 'preshow', 'interview']
ignore_runs = ['bonus stream', 'tasbot takes total control of...', 'bonus games']


def clean_run(run):

    if run in ignore_runs:
        return {'clean_run': None, 'is_ignore': True}  # Return without cleaning and set is_ignore flag

    elif not ('bonus' in run or 'tasbot' in run) and any(substr in run for substr in ignore_runs_with):
        return {'clean_run': None, 'is_ignore': True}  # Return without cleaning and set is_ignore flag
    
    else:  

        # Standardize
        clean_run = html.unescape(unidecode(run))

        # Remove game mods with at least 2 words
        for ele in gme_mods_other:
            clean_run = re.sub(" +", " ", re.sub(ele, "", clean_run)).strip()

        # Remove game mods with 1 word
        clean_run = ' '.join([ele for ele in clean_run.split(' ') if ele not in gme_mods_1w]).strip()

        # clean bonus runs
        clean_run = clean_run.split('-').pop(-1).strip() if 'bonus' in clean_run else clean_run
        clean_run = clean_run.split('!').pop(-1).strip() if 'bonus' in clean_run else clean_run
        clean_run = clean_run.split(':').pop(-1).strip() if 'bonus' in clean_run else clean_run

        # Clean tasbot runs
        clean_run = clean_run.split('tasbot plays').pop(-1).strip() if 'tasbot' in clean_run else clean_run
        clean_run = run.split('tasbot vs').pop(-1).strip() if 'tasbot' in clean_run else clean_run
        clean_run = run.split('tasbot dominates').pop(-1).strip() if 'tasbot' in clean_run else clean_run

        # Remove anything within parentheses
        clean_run = re.sub("\(.*\)", "", clean_run).strip()

        # Final touches
        clean_run = clean_run.strip(',').strip('.').strip('-').strip()

        if not clean_run:
            is_ignore = True

        else:
            is_ignore = False

        return {'clean_run': clean_run, 'is_ignore': is_ignore}


run_lst = []
for _, row in df.iterrows():
    run_dict = clean_run(row['name'])
    run_dict = run_dict | row.to_dict()
    run_lst.append(run_dict)


filepath = os.path.join('data', 's2_clean_runs.jsonl')
with open(filepath, 'w') as outfile:
    for entry in run_lst:
        json.dump(entry, outfile)
        outfile.write('\n')
