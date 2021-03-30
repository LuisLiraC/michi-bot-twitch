import os
from twitchio.ext import commands

from cats_api import CatsAPI
from riot_api import RiotAPI
from tts_engine import TTSEngine

from bot_utils import send_exception
from custom_exceptions import ChampionException, RandomCatException, NotPlayedException


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            irc_token=os.environ.get('TMI_TOKEN'),
            client_id=os.environ.get('CLIENT_ID'),
            nick=os.environ.get('BOT_NICK'),
            prefix=os.environ.get('BOT_PREFIX'),
            initial_channels=[os.environ.get('CHANNEL')])

        self.riot_api = RiotAPI()
        self.cats_api = CatsAPI()
        self.tts_engine = TTSEngine()

    async def event_ready(self):
        print(f'Miaw! {self.nick}')

    async def event_command_error(self, ctx, ex):
        await send_exception(ctx, ex)

    async def event_message(self, ctx):
        if ctx.author.name.lower() == self.nick or ctx.author.name.lower() == 'nightbot':
            return

        if ctx.content[0] == '!':
            await self.handle_commands(ctx)
            return

        if ctx.content.lower() == 'hola':
            await ctx.channel.send(f'¡Hola, {ctx.author.name}! :D')

        self.tts_engine.read(ctx.content)

    @commands.command(name='cat')
    async def cat(self, ctx):
        try:
            cat_url = self.cats_api.get_random_cat()
            await ctx.channel.send(f'{ctx.author.name}, disfruta tu michi {cat_url}')
        except RandomCatException as ex:
            await self.send_exception(ctx, ex)
        except Exception as ex:
            print(ex)

    @commands.command(name='redes')
    async def social_media(self, ctx):
        social_media = [
            'https://twitter.com/Luis_LiraC',
            'https://www.youtube.com/c/luislira',
            'https://www.instagram.com/luislirac/',
        ]
        message = 'Me puedes seguir en:\n' + '\n'.join(social_media)
        await ctx.channel.send(message)

    @commands.command(name='mt')
    async def mastery(self, ctx):
        try:
            result = self.riot_api.get_mastery_info(ctx.message.content)
            await ctx.channel.send(f"""{ctx.author.name}. 
            Tengo {result['points']} puntos de maestría con {result['name']}.
            La última vez que lo jugué fue en {result['date']}
            """)
        except ChampionException as ex:
            await send_exception(ctx, ex)
        except NotPlayedException as ex:
            await send_exception(ctx, ex)
        except Exception as ex:
            print(ex)
