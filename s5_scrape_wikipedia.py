"""Scrape Wikipedia for game genres."""

import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time


def get_genre(url):
    soup = BeautifulSoup(requests.get(url).content, "lxml")
    table = soup.find('table', attrs={'class': 'infobox'})
    rows = table.find_all('tr')


    att_dict = dict()
    for row in rows:

        th = row.find('th')
        if th and th.text == 'Genre(s)':
            att_dict[th.text] = [ele.text.lower() for ele in row.find('td').find_all('a')]

        else:
            continue


    return att_dict

i_filepath = os.path.join('data', 's4_rate_results.csv')
game_df = pd.read_csv(i_filepath)
game_df['has_wikipedia'] = game_df['url'].astype(str).str.startswith('https://en.wikipedia.org/wiki/')
game_df = game_df.loc[game_df['has_wikipedia'], :].reset_index(drop=True)

game_subdf = game_df.drop_duplicates(subset=['game'], keep='first', ignore_index=True)


lookup_lst = []
for _, row in game_subdf.iterrows():
    if row['has_wikipedia']:
        url = row['url']
        time.sleep(1)
        att_dict = get_genre(url)
        att_dict['game'] = row['game']
        lookup_lst.append(att_dict)
        print(att_dict)

    else:
        continue

lookup_df = pd.DataFrame(lookup_lst)
game_df = game_df.merge(lookup_df, how='left', on='game')

game_df.to_csv(os.path.join('data', 's5_scrape_wikipedia.csv'), index=False)
