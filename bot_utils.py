import requests

def make_request(url, headers={}):
    response = requests.get(url, headers=headers)
    json = response.json()
    return json

async def send_exception(message, ex):
    await message.channel.send(f'{message.author.name}. {ex}')