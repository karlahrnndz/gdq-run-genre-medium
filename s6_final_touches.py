"""Format data for plotting by creating a csv file with columns: year, event, genre, count."""

import pandas as pd
import os
import numpy as np
import ast

usecols = ['game', 'event', 'Genre(s)']
game_df = pd.read_csv(os.path.join('data', 's5_scrape_wikipedia.csv'),
                       usecols=usecols)
game_df.rename(columns={'Genre(s)': 'genre'}, inplace=True)

# Fill in year
game_subdf = game_df.loc[game_df['genre'].notnull(), :]
game_subdf['year'] = np.where(game_subdf['event'].str.match('.*\d+$'),
                              game_subdf['event'].str[-4:],
                              None)

tofill_df = game_subdf.loc[game_subdf['year'].isnull(), ['event', 'year']].drop_duplicates()
tofill_dict = dict(zip(tofill_df['event'], tofill_df['year']))
tofill_dict['harvey relief done quick'] = '2017'
tofill_dict['corona relief done quick'] = '2020'
tofill_dict['awesome games done quick 2021 online'] = '2021'
tofill_dict['summer games done quick 2021 online'] = '2021'
tofill_dict['awesome games done quick 2022 online'] = '2022'

game_subdf['year'] = game_subdf.apply(lambda x: x['year']
                                      if x['year'] is not None
                                      else tofill_dict[x['event']], axis=1)

# clean genre
game_subdf['genre2'] = game_subdf['genre'].apply(lambda x: ast.literal_eval(x))
game_subdf = game_subdf.loc[game_subdf['genre2'].astype(bool), :]
game_subdf = game_subdf.explode('genre2')
game_subdf['delete_row'] = game_subdf['genre2'].str.match('\[\d+\]')
game_subdf = game_subdf.loc[~game_subdf['delete_row'], :]
game_subdf.drop(columns='delete_row', inplace=True)
game_subdf.sort_values(by='genre2', ascending=True, ignore_index=True)

# Apply manually created genre map
genre_df = pd.read_csv(os.path.join('data', 'genre_map.csv'))
game_subdf = game_subdf.merge(genre_df, how='left', on='genre2')
game_subdf['genre3'] = np.where(game_subdf['maps_to'].isna(),
                                game_subdf['genre2'],
                                game_subdf['maps_to'])
game_subdf.drop(columns=['genre', 'genre2', 'maps_to'], inplace=True)
game_subdf.rename(columns={'genre3': 'genre'}, inplace=True)

count_df = game_subdf.groupby(by=['year', 'event', 'genre'])['game'].count().reset_index()
count_df.rename(columns={'game': 'count'}, inplace=True)
count_df.sort_values(by=['year', 'genre'], ascending=True, ignore_index=True, inplace=True)
count_df['genre'] = count_df['genre'].str.title()
count_df['event'] = count_df['event'].str.title()

count_df.to_csv(os.path.join('data', 's6_final_touches.csv'), index=False)
