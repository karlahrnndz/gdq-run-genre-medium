"""
Use Google Cloud's Enterprise Knowledge Graph API to search for run names and map them to URLs and IDs.
"""

from __future__ import annotations
from collections.abc import Sequence
from google.cloud import enterpriseknowledgegraph as ekg
import pandas as pd
import os
import json
from time import sleep
import html
from unidecode import unidecode


def search_sample(
    project_id: str,
    search_query: str,
    languages: Sequence[str] = None,
    types: Sequence[str] = ['VideoGame'],
    limit: int = 1,
    location: str = 'global',
):
    
    clean_run_dict = {'search_query': search_query,
                      'game': None,
                      'url': None,
                      'id': None,
                      'mid': None,
                      'qid': None,
                      'has_sr': False}
    
    # Create a client
    client = ekg.EnterpriseKnowledgeGraphServiceClient()

    # The full resource name of the location
    parent = client.common_location_path(project=project_id, location=location)

    # Initialize request argument(s)
    request = ekg.SearchRequest(
        parent=parent,
        query=search_query,
        languages=languages,
        types=types,
        limit=limit,
    )

    # Make the request
    response = client.search(request=request)

    if response.item_list_element:

        item = response.item_list_element[0]
        result = item.get("result")
        clean_run_dict['game'] = html.unescape(unidecode(result.get('name')))
        clean_run_dict['has_sr'] = True
        clean_run_dict['id'] = result.get('@id')

        detailed_description = result.get("detailedDescription")
        if detailed_description:
            clean_run_dict['url'] = detailed_description.get('url')

        for identifier in result.get("identifier"):
            if identifier.get('name') == 'googleKgMID':
                clean_run_dict['mid'] = identifier.get('value')

            elif identifier.get('name') == 'wikidataQID':
                clean_run_dict['qid'] = identifier.get('value')
        
            else:
                continue
            
        return clean_run_dict

    else:
        return clean_run_dict


if __name__ == '__main__':

    ekg_project_id = pd.read_json('ekg_project_id.json', lines=True)["ekg_project_id"].iloc[0]  # TODO - replace ekg_project_id with your project id
    o_filepath = os.path.join('data', 's3_search_ekg.jsonl')

    run_df = pd.read_json(os.path.join('data', 's2_clean_runs.jsonl'), lines=True)
    pc_df = run_df.loc[run_df['is_ignore'].eq(False), :]
    pc_lst = list(set(pc_df['clean_run']))
    clean_run_lst = []

    for _, row in pc_df.iterrows():
        # Get basic google search information
        sleep(1)
        clean_run_dict = search_sample(ekg_project_id, row['clean_run'])

        clean_run_dict = clean_run_dict | row.to_dict()

        with open(o_filepath, 'a+') as outfile:
            json.dump(clean_run_dict, outfile)
            outfile.write('\n')
