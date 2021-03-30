import os

from custom_exceptions import RandomCatException
from bot_utils import make_request


class CatsAPI():
    def __init__(self):
        self.base_url = 'https://api.thecatapi.com'
        self.api_key = os.environ.get('CAT_API_KEY')

    def get_random_cat(self):
        url = f'{self.base_url}/v1/images/search?api_key={self.api_key}'
        response = make_request(url)

        if len(response) < 1:
            raise RandomCatException

        return response[0]['url']
