# -*- coding: utf-8 -*-
"""
Created on Sat Aug 29 16:35:36 2015

@author: work
"""

import requests
import json
import os

import pandas as pd

import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

def fetch_attendees(event_id, access_token):
    url = 'https://graph.facebook.com/v2.4/{event_id}/attending?access_token={access_token}'.format(event_id=event_id, access_token=access_token)
    attendees = []
    is_last_page = False
    num_people_done = 0
    while not is_last_page:
        num_people_done += 25
        print 'Got {num_people} people'.format(num_people=num_people_done)
        r = requests.get(url)
        content_as_dict = json.loads(r.content)
        attendees = attendees + content_as_dict['data']
        is_last_page = 'next' not in content_as_dict['paging'].keys()
        if not is_last_page:
            url = content_as_dict['paging']['next']
    print 'Total of {num_attending} people attending'.format(num_attending=len(attendees))
    return attendees


def make_table(attendees, path_to_table):
    attendees_table = pd.DataFrame.from_dict(attendees)
    attendees_table.loc[:, 'first_name'] = attendees_table.loc[:, 'name'].str.split().apply(lambda x: x[0]).str.lower()
    
    if not os.path.isdir('.cache'):
        os.mkdir('.cache')
    attendees_table.to_csv(path_to_table, index=False)

def fetch_attendees_table(given_name, event_id, access_token):
    path_to_table = os.path.join('.cache', given_name + '_EV_' + event_id + '.csv')
    
    if not os.path.isfile(path_to_table):
        attendees = fetch_attendees(event_id, access_token)
        make_table(attendees, path_to_table)
    table = pd.read_csv(path_to_table)
    return table

def analyse_language(table):
    languages = enriched_table['03_langage'].str.split(',')  
    languages.dropna(inplace=True)
    all_languages = pd.Series([x.strip() for x in languages.sum()])


def describe_table(attendees_table):
    table_of_names = pd.read_csv('prenoms.csv', index_col=0, sep=';')
    enriched_table = attendees_table.merge(table_of_names, left_on='first_name', right_index=True, how='left')
    
    print '\n************************\nTable: {table_name}\n'.format(table_name='TODO')
    print 'Num participants: {num_participants}'.format(num_participants=len(enriched_table))
    print 'Known girl to boy ratio:', (enriched_table['02_genre'] == 'f').sum() / float((enriched_table['02_genre'] == 'm').sum())
    print enriched_table['02_genre'].value_counts()


def count_common_participants(*tables):
    assert len(tables) >=2
    intersection = tables[0]
    for tab in tables[1:]:
        intersection = intersection.merge(tab, on = 'id', how='inner')
    print 'Number of common participants is', len(intersection)
    return intersection
       
def read_access_token():
    print 'If an error occurs, you might have an invalid token'
    with open('hidden_access_token.txt') as f:
        access_token = f.read()
    return access_token

if __name__ == '__main__': 
    all_defs = [{'event_id': '326355784121195', 'name': 'aoutside_iii'},\
                    {'event_id': '521072081281160', 'name': 'aoutside_iv'},\
                    {'event_id': '755288111181519', 'name': 'aoutside_v'},\
                    {'event_id': '1612257909059435', 'name': 'aoutside_vi'} 
                ]       
    
    access_token = read_access_token()
    event_id = '521072081281160'
    given_name = 'aoutside_iv'
        
    tab_1 = fetch_attendees_table(all_defs[0]['name'], all_defs[0]['event_id'], access_token)
    tab_2 = fetch_attendees_table(all_defs[1]['name'], all_defs[1]['event_id'], access_token)
    tab_3 = fetch_attendees_table(all_defs[2]['name'], all_defs[2]['event_id'], access_token)
    tab_4 = fetch_attendees_table(all_defs[3]['name'], all_defs[3]['event_id'], access_token)
          
    describe_table(tab_4)
    
    intersection = count_common_participants(tab_1, tab_2, tab_3, tab_4)









