"""Rate how well search results match the search query."""

import pandas as pd
import os
from thefuzz import fuzz

i_filepath = os.path.join('data', 's3_search_ekg.jsonl')
ekg_df = pd.read_json(i_filepath, lines=True)

sel_cols = ['game', 'search_query', 'has_sr']
rating_df = ekg_df[sel_cols].drop_duplicates(ignore_index=True)
rating_df['match_rating'] = rating_df.apply(
    lambda x: fuzz.partial_token_sort_ratio(x['game'], x['search_query']) if x['has_sr'] else 0, axis=1)
rating_df['acceptable'] = rating_df['match_rating'].ge(70)
ekg_df = ekg_df.merge(rating_df, how='left', on=sel_cols)

finalg_df = ekg_df.loc[ekg_df['acceptable'], :].reset_index(drop=True)
finalg_df.drop(columns=['has_sr', 'is_ignore'], inplace=True)

finalg_df.to_csv(os.path.join('data', 's4_rate_results.csv'), index=False)
