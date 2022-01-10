import os
import asyncio
import random
from datetime import datetime, timezone

from twitchio.ext import commands
from twitchio.ext.commands.errors import CommandNotFound
from playsound import playsound

from cats_api import CatsAPI
from riot_api import RiotAPI
from music_player import MusicPlayer
from music_dl import MusicDL

from bot_utils import send_exception
from custom_exceptions import ChampionException, RandomCatException, NotPlayedException, MaxDurationException, NotResultsException


class Bot(commands.Bot):
    def __init__(
        self,
        spam_time=600,
        spam_messages=[],
        custom_rewards=[],
        tts_engine=None,
        greeting_message=''
    ):
        super().__init__(
            irc_token=os.environ.get('TMI_TOKEN'),
            client_id=os.environ.get('CLIENT_ID'),
            nick=os.environ.get('BOT_NICK'),
            prefix=os.environ.get('BOT_PREFIX'),
            initial_channels=[os.environ.get('CHANNEL')],
            client_secret=os.environ.get('CLIENT_SECRET'))

        self.user_id = os.environ.get('TWITCH_USER_ID')
        self.ignore_users = [self.nick]
        self.only_owner_commands = ['dtts', 'atts']
        self.only_mod_commands = ['vol', 'next', 'stop']
        self.owner_nick = os.environ.get('CHANNEL').replace('#', '').lower()
        self.spam_time = spam_time
        self.spam_messages = spam_messages
        self.chatters_list = []
        self.custom_rewards = custom_rewards
        self.greeting_message = greeting_message

        self.riot_api = RiotAPI()
        self.cats_api = CatsAPI()
        self.tts_engine = tts_engine
        self.music_player = MusicPlayer(os.environ.get('DOWNLOADS_PATH'))
        self.music_dl = MusicDL(download_path=os.environ.get('DOWNLOADS_PATH'))

    async def event_ready(self):
        print(f'{self.nick} is ready')
        if len(self.spam_messages) > 0:
            await self.spam()

    async def event_command_error(self, message, ex):
        if ex.__class__ is CommandNotFound:
            await send_exception(message, 'No se reconoce el comando. Usa !c para ver todos los comandos.')
            return
        await send_exception(message, ex)

    async def event_raw_usernotice(self, channel, tags):
        print(tags)

    async def event_message(self, message):
        try:
            if message.author.name.lower() in self.ignore_users:
                return

            if message.author.name.lower() not in self.chatters_list:
                await message.channel.send(self.greeting_message.format(message.author.name))
                self.chatters_list.append(message.author.name)

            await self.handle_commands(message)
            await self.handle_custom_rewards(message)
        except Exception as ex:
            print(ex)

    async def handle_custom_rewards(self, message):
        try:
            reward_id = message.tags.get("custom-reward-id", None)

            if not reward_id:
                return
            if reward_id not in self.custom_rewards:
                return

            reward_action = self.custom_rewards[reward_id]

            if type(reward_action) == str:
                return

            reward_action(message)
        except Exception as ex:
            print(ex)

    async def spam(self):
        channel = self.get_channel(self.owner_nick)
        while True:
            await asyncio.sleep(self.spam_time)
            selected_message = random.choice(self.spam_messages)
            await channel.send(selected_message)

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
            keys = list(map(lambda c: f'!{c}' if c not in self.only_owner_commands and c not in self.only_mod_commands else '', [
                        *self.commands.keys()]))

            if message.author.is_mod:
                for c in self.only_mod_commands:
                    keys.append(f'{c}')

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
        if self.tts_engine is None:
            return
        if message.author.name.lower() == self.owner_nick:
            self.tts_engine.activate()

    @commands.command(name='dtts')
    async def deactivate_tts(self, message):
        if self.tts_engine is None:
            return
        if message.author.name.lower() == self.owner_nick:
            self.tts_engine.deactivate()

    @commands.command(name='bonk')
    async def bonk(self, message):
        playsound('./sounds/bonk.mp3')

    @commands.command(name='sr')
    async def song_request(self, message):
        try:
            user_input = message.content.replace('!sr', '').strip()
            if user_input == '':
                raise NotResultsException

            song_reference = self.music_dl.download(user_input)
            if song_reference is None:
                raise NotResultsException
            song_name = self.music_dl.get_song_name(song_reference)
            await self.music_player.add_to_playlist(song_reference, message, song_name)
        except MaxDurationException as ex:
            await send_exception(message, ex)
        except NotResultsException as ex:
            await send_exception(message, ex)
        except Exception as ex:
            print('----------')
            print(ex)
            print('----------')
            # I needed to do this because only this "fix" a weird bug
            # When the player stop and then play music again the volume change to -1 and it ignore every
            # validation that I do to change it again to the initial volume
            self.music_player = MusicPlayer(os.environ.get('DOWNLOADS_PATH'))
            print(f'[Music Player Restarted at {datetime.now()}]')
            print('----------')

    @commands.command(name='next')
    async def next_song(self, message):
        try:
            if message.author.is_mod:
                await self.music_player.next()
        except Exception as ex:
            print(ex)

    @commands.command(name='vol')
    async def volume(self, message):
        try:
            if message.author.is_mod:
                volume = message.content.replace('!vol ', '').strip()
                self.music_player.set_volume(volume)
        except Exception as ex:
            print(ex)

    @commands.command(name='currentsong')
    async def currentsong(self, message):
        try:
            reference = self.music_player.get_song_reference()
            song_name = self.music_dl.get_song_name(reference)

            if song_name is not None:
                await message.channel.send(f'{message.author.name}. La canción es: {song_name}')
        except Exception as ex:
            print(ex)

    @commands.command(name='stop')
    async def stop(self, message):
        try:
            if message.author.is_mod:
                self.music_player.stop()
        except Exception as ex:
            print(ex)
