import os
from twitchio.ext import commands
from twitchio.ext.commands.errors import CommandNotFound

from datetime import datetime, timezone

import uuid
import csv
import shutil
from pytube import YouTube
from music_player import MusicPlayer

from cats_api import CatsAPI
from riot_api import RiotAPI
from tts_engine import TTSEngine

from bot_utils import send_exception
from custom_exceptions import ChampionException, RandomCatException, NotPlayedException

from playsound import playsound


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            irc_token=os.environ.get('TMI_TOKEN'),
            client_id=os.environ.get('CLIENT_ID'),
            nick=os.environ.get('BOT_NICK'),
            prefix=os.environ.get('BOT_PREFIX'),
            initial_channels=[os.environ.get('CHANNEL')],
            client_secret=os.environ.get('CLIENT_SECRET'))

        self.user_id = os.environ.get('TWITCH_USER_ID')
        self.ignore_users = [self.nick, 'nightbot']
        self.only_owner_commands = ['dtts', 'atts']
        self.owner_nick = os.environ.get('CHANNEL').replace('#', '').lower()

        self.riot_api = RiotAPI()
        self.cats_api = CatsAPI()
        self.tts_engine = TTSEngine()
        self.music_player = MusicPlayer(os.environ.get('DOWNLOADS_PATH'))

    async def event_ready(self):
        print(f'Miaw! {self.nick}')

    async def event_join(self, user):
        pass

    async def event_command_error(self, message, ex):
        if ex.__class__ is CommandNotFound:
            await send_exception(message, 'No se reconoce el comando. Usa !c para ver todos los comandos.')
            return
        await send_exception(message, ex)

    async def event_message(self, message):
        try:
            if message.author.name.lower() in self.ignore_users:
                return

            if message.content[0] in self.prefixes:
                await self.handle_commands(message)
                return

            if message.content.lower() == 'hola':
                await message.channel.send(f'¡Hola, {message.author.name}, muchas gracias por pasarte al stream! :D')

            self.tts_engine.read(message.content)
        except Exception as ex:
            print(ex)

    @commands.command(name='michi')
    async def cat(self, message):
        try:
            cat_url = self.cats_api.get_random_cat()
            await message.channel.send(f'{message.author.name}, disfruta tu michi {cat_url}')
        except RandomCatException as ex:
            await self.send_exception(message, ex)
        except Exception as ex:
            print(ex)

    @commands.command(name='redes')
    async def social_media(self, message):
        try:
            social_media = [
                'https://twitter.com/Luis_LiraC',
                'https://www.youtube.com/c/luislira',
                'https://www.instagram.com/luislirac/',
            ]
            response = 'Me puedes seguir en:\n' + '\n'.join(social_media)
            await message.channel.send(response)
        except Exception as ex:
            print(ex)

    @commands.command(name='mt')
    async def mastery(self, message):
        try:
            result = self.riot_api.get_mastery_info(message.message.content)
            await message.channel.send(f"""{message.author.name}. 
            Tengo {result['points']} puntos de maestría con {result['name']}.
            La última vez que lo jugué fue en {result['date']}
            """)
        except ChampionException as ex:
            await send_exception(message, ex)
        except NotPlayedException as ex:
            await send_exception(message, ex)
        except Exception as ex:
            print(ex)

    @commands.command(name='c')
    async def cmd(self, message):
        try:
            keys = list(map(lambda c: f'!{c}' if c not in self.only_owner_commands else '', [
                        *self.commands.keys()]))
            response = f'{message.author.name} Puedes usar estos comandos:\n' + \
                '\n'.join(keys)
            await message.channel.send(response)
        except Exception as ex:
            print(ex)

    @commands.command(name='followage')
    async def follow_age(self, message):
        try:
            follower_name = message.author.name.lower()
            followers_list = await self.get_followers(self.user_id)
            follow_date = None

            for follower in followers_list:
                if follower['from_name'].lower() == follower_name:
                    follow_date = follower['followed_at']
                    break

            if follow_date is None:
                await message.channel.send(f'{follower_name}, no me sigues :(')
                return

            utc_date = datetime.strptime(follow_date, '%Y-%m-%dT%H:%M:%SZ')
            date = utc_date.replace(tzinfo=timezone.utc).astimezone(tz=None)
            now = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(tz=None)
            following_days = (now - date).days

            if following_days == 1 or following_days == 0:
                await message.channel.send(f'{follower_name}, tienes 1 día siguiéndome. Muchas gracias 🥳')
            elif following_days > 1:
                await message.channel.send(f'{follower_name}, tienes {following_days} días siguiéndome. Muchas gracias 🥳')
        except Exception as ex:
            print(ex)

    @commands.command(name='atts')
    async def activate_tts(self, message):
        if message.author.name.lower() == self.owner_nick:
            self.tts_engine.is_active = True

    @commands.command(name='dtts')
    async def deactivate_tts(self, message):
        if message.author.name.lower() == self.owner_nick:
            self.tts_engine.is_active = False

    @commands.command(name='bonk')
    async def bonk(self, message):
        playsound('./sounds/bonk.mp3')

    @commands.command(name='sr')
    async def song_request(self, message):
        try:
            url = message.content.replace('!sr', '').strip()
            yt = YouTube(url)

            MAX_DURATION = 600
            if yt.length > MAX_DURATION:
                return

            song_reference = None

            with open('./songs.csv', 'r', encoding='utf-8') as songs:
                data = csv.reader(songs)
                for row in data:
                    if row[0] == yt.title:
                        song_reference = f'{row[1]}.webm'

            if song_reference is None:
                old_title = yt.title
                new_title = str(uuid.uuid4()).replace('-', '')
                yt.title = new_title

                with open('./songs.csv', 'a', encoding='utf-8') as songs:
                    songs.write(f'{old_title},{new_title}\n')

                streams = yt.streams.filter(only_audio=True)
                stream = streams[-1]
                stream.download()

                filename = f'{new_title}.webm'
                song_reference = filename
                shutil.move(f'./{filename}', f'{self.music_player.songs_path}{filename}')

            await self.music_player.add_to_playlist(song_reference)

        except Exception as ex:
            print(ex)

    @commands.command(name='next')
    async def next_song(self, ctx):
        await self.music_player.next()
