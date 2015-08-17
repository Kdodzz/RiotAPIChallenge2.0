__author__ = 'Kishan'

import data_retrieval.match_data.get_match_data as matchdata
import data_retrieval.static_data as static_data
import data_retrieval.static_data.get_champion_keys as champ_keys
import config.config as config
import json
import os
import sys

regions = [(matchdata.get_match_regions())[0]] #Limit regions?

print('\nCHAMPIONS\n')

def main():
    champions_json = {}

    sys.stdout.write('Creating empty JSON...')
    sys.stdout.flush()
    create_champions_dict(champions_json)
    sys.stdout.write('done!\n')
    sys.stdout.flush()


    sys.stdout.write('Populating dict...')
    sys.stdout.flush()
    populate_dict(champions_json)
    sys.stdout.write('\rPopulating dict...done!\n')
    sys.stdout.flush()

    sys.stdout.write('Writing champions JSON...')
    sys.stdout.flush()
    write_champions_json(champions_json)
    sys.stdout.write('done!')
    sys.stdout.flush()


def create_champions_dict(champions_json):
    for r in regions:
        champions_json[r] = {}
        champion_keys = champ_keys.get_champion_key_by_id(r)
        for hast in static_data.highest_achieved_season_tier:
            champions_json[r][hast] = {}
            for key, value in champion_keys.items():
                champions_json[r][hast][key] = {'key': value, 'won': 0, 'lost': 0}


def populate_dict(champions_json):
    for r in regions:
        match_data_directory = os.path.join(config.match_data_directory, r.upper())
        matches = os.listdir(match_data_directory)
        progress_counter = len(matches)
        for m in matches:
            if not m.endswith('json'):
                continue
            else:
                match_data = os.path.join(match_data_directory, m)
                with open(match_data, 'r') as f: #open match file
                    data = json.load(f) #load match file as json
                    winner = 0
                    for t in range(2):
                        if data['teams'][t]['winner'] == True:
                            winner = data['teams'][t]['teamId']
                    for p in range(10):
                        tier = data['participants'][p]['highestAchievedSeasonTier']
                        champion_id = data['participants'][p]['championId']
                        team_id = data['participants'][p]['teamId']
                        if winner == team_id:
                            champions_json['br'][tier][str(champion_id)]['won'] += 1
                        else:
                            champions_json['br'][tier][str(champion_id)]['lost'] += 1
            progress_counter -= 1
            progress_countdown(progress_counter, r)


def write_champions_json(champions_json):
    os.chdir(os.path.dirname(__file__))
    with open('champions.json', 'w') as outfile:
        json.dump(champions_json, outfile)


def progress_countdown(progress_counter, region):
    sys.stdout.write('\rPopulating dict...' + region.upper() +
                             ' ' +  str(progress_counter))
    sys.stdout.flush()


if __name__ == '__main__':
    main()