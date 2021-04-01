import requests
import re

def make_request(url, headers={}):
    response = requests.get(url, headers=headers)
    json = response.json()
    return json

def find_url(message):
    regex = re.compile(r'(http)?s?[:\/\/]?[www]?.*\..*', re.IGNORECASE)
    if re.match(regex, message) is None:
        return False

    return True

async def send_exception(message, ex):
    await message.channel.send(f'{message.author.name}. {ex}')
