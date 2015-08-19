__author__ = 'Kishan'

from data_retrieval.match_data import get_match_data
from data_retrieval import static_data
from data_retrieval.static_data import get_bw_minion_data
from data_analytics import data_aggregation
from config import config
import json
import os
import sys

regions = [(get_match_data.get_match_regions())[0]] #Only 'br'

print('\nMinions\n')

def main():
    minions_json = {}

    sys.stdout.write('Creating empty JSON...')
    sys.stdout.flush()
    create_champions_dict(minions_json)
    sys.stdout.write('\rCreating empty JSON...done!\n')
    sys.stdout.flush()


    sys.stdout.write('Populating dict...')
    sys.stdout.flush()
    populate_dict(minions_json)
    sys.stdout.write('\rPopulating dict...done!\n')
    sys.stdout.flush()

    sys.stdout.write('Writing champions JSON...')
    sys.stdout.flush()
    data_aggregation.write_json(minions_json, 'minions.json')
    sys.stdout.write('done!')
    sys.stdout.flush()


def create_champions_dict(minions_json):
    w = len(regions)
    for r in regions:
        minions_json[r] = {}
        minions = get_bw_minion_data.get_minions_by_id(r)
        upgrades = get_bw_minion_data.get_minion_upgrades_by_id(r)
        for hast in static_data.highest_achieved_season_tier:
            minions_json[r][hast] = {}
            for minion_id, minion_name in minions.items():
                minions_json[r][hast][minion_id] = \
                    {'name' : minion_name['name'], 'won' : 0, 'lost' : 0}
                for upgrade_id, upgarde_name in upgrades.items():
                    minions_json[r][hast][minion_id][upgrade_id] = \
                        {'name' : upgarde_name['name'], 'won' : 0, 'lost' : 0}


def populate_dict(minions_json):
    for r in regions:
        minions_and_upgrades = dict(get_bw_minion_data.get_minions_by_id(r))
        minions_and_upgrades.update(get_bw_minion_data.get_minion_upgrades_by_id(r))
        match_data_directory = os.path.join(config.match_data_directory, r.upper())
        matches = os.listdir(match_data_directory)
        progress_counter = len(matches)
        for m in matches:
            if not m.endswith('json'): continue
            match_data = os.path.join(match_data_directory, m)
            with open(match_data, 'r') as f: #open match file
                data = json.load(f) #load match file as json
                win_team_id = [t['teamId'] for t in data['teams'] if t['winner']][0]
                for p in data['participants']:
                    minion_bought = ''
                    tier = p['highestAchievedSeasonTier']
                    team_id = p['teamId']
                    for frame in data['timeline']['frames']:
                        if 'events' not in frame: continue
                        for event in frame['events']:
                            if event['eventType'] == 'ITEM_PURCHASED' \
                                    and event['participantId'] == p['participantId'] \
                                    and event['itemId'] in minions_and_upgrades:
                                item_id = event['itemId']
                                if minion_bought == '':
                                    if win_team_id == team_id: minions_json[r][tier][item_id]['won'] += 1
                                    else: minions_json[r][tier][item_id]['lost'] += 1
                                    minion_bought = item_id
                                else:
                                    if win_team_id == team_id: minions_json[r][tier][minion_bought][item_id]['won'] += 1
                                    else: minions_json[r][tier][minion_bought][item_id]['lost'] += 1
            progress_counter -= 1
            data_aggregation.progress_countdown(progress_counter, r)


if __name__ == '__main__':
    main()