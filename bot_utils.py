import requests

def make_request(url, headers={}):
    response = requests.get(url, headers=headers)
    json = response.json()
    return json

async def send_exception(ctx, ex):
    await ctx.channel.send(f'{ctx.author.name}. {ex}')