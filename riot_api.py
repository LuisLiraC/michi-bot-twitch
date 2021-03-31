import re
import os
from locale import format
from datetime import datetime

from custom_exceptions import ChampionException, NotPlayedException
from bot_utils import make_request


class RiotAPI():
    def __init__(self):
        # Get Summoner ID
        # https://<region>.api.riotgames.com/lol/summoner/v4/summoners/by-name/<summoner>?api_key=<api_key>
        self.riot_token = os.environ.get('RIOT_API_KEY')
        self.base_url = 'https://la1.api.riotgames.com/lol'
        self.ddragon_url = os.environ.get('DDRAGON_URL')

    def get_mastery_info(self, message):
        has_champion = re.search('!mt (.*)', message)

        if not has_champion:
            raise ChampionException

        champion_name = has_champion.group(1)

        champions_data = self.get_champions_ddragon()
        new_champion_name = None

        for champion in champions_data.items():
            if champion[1]['id'].lower() == champion_name.lower():
                new_champion_name = champion[1]['id']
                champion_id = champion[1]['key']
                break

        if new_champion_name is None:
            raise ChampionException

        summoner_id = os.environ.get('SUMMONER_ID')
        url = f'{self.base_url}/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}/by-champion/{champion_id}'
        headers = {
            'X-Riot-Token': self.riot_token
        }
        mastery_info = make_request(url, headers)

        if 'status' in mastery_info:
            raise NotPlayedException

        points = mastery_info['championPoints']
        last_play_unix = mastery_info['lastPlayTime']
        last_play_readable = datetime.fromtimestamp(
            last_play_unix/1000.0).strftime('%d-%m-%Y')
        formatted_points = format('%d', points, grouping=True)

        return {
            'name': new_champion_name,
            'date': last_play_readable,
            'points': formatted_points
        }

    def get_champions_ddragon(self):
        # Champions info
        # http://ddragon.leagueoflegends.com/cdn/11.7.1/data/en_US/champion.json
        champions = make_request(self.ddragon_url)
        return champions['data']
