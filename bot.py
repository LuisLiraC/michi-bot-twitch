import os
import pyttsx3
from twitchio.ext import commands


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            irc_token=os.environ.get('TMI_TOKEN'),
            client_id=os.environ.get('CLIENT_ID'),
            nick=os.environ.get('BOT_NICK'),
            prefix=os.environ.get('BOT_PREFIX'),
            initial_channels=[os.environ.get('CHANNEL')])
        self.engine = pyttsx3.init()

    async def event_ready(self):
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[3].id)
        print(f'Miaw! {self.nick}')

    async def event_message(self, ctx):
        if ctx.author.name.lower() == self.nick or ctx.author.name.lower() == 'nightbot':
            return

        if ctx.content[0] == '!':
            await self.handle_commands(ctx)
            return

        if ctx.content.lower() == 'hola':
            await ctx.channel.send(f'¡Hola, {ctx.author.name}! :D')

        self.engine.say(ctx.content)
        self.engine.runAndWait()

    @commands.command(name='hello')
    async def hello(self, ctx):
        await ctx.channel.send(f'Hello {ctx.author.name}!')

    @commands.command(name='bonk')
    async def test(self, ctx):
        pass
