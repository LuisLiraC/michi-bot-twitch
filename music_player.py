import vlc
import time
import asyncio
import re
from music_dl import MusicDL


class MusicPlayer:
    def __init__(self, songs_path, max_volume=60):
        self.songs_path = songs_path
        self._playlist = []
        self._vlc_instance = vlc.Instance()
        self._player = self._vlc_instance.media_player_new()
        self.max_volume = max_volume
        self.set_volume()
        self._current_song_reference = None

    async def play(self, media):
        self._player.set_media(media)
        match = re.search('([0-9A-Za-z]{32})', media.get_mrl())
        self._current_song_reference = match.group(1)

        self._player.play()
        await self.check_is_playing()

    async def check_is_playing(self):
        while True:
            await asyncio.sleep(1.0)

            if self._player.is_playing() == 0:
                await self.next()

    def stop(self):
        self._player.stop()
        self._player.release()
        self._playlist = []
        raise Exception('[Stop Music Player]')

    async def next(self):
        if len(self._playlist) > 1:
            self._playlist = self._playlist[1:]
            await self.play(self._playlist[0])
        else:
            self.stop()

    async def add_to_playlist(self, song, message, song_name):
        media = self._vlc_instance.media_new(f'{self.songs_path}{song}')

        for media_source in self._playlist:
            if song in media_source.get_mrl():
                await message.channel.send(f'{message.author.name}. La canción ya se encuentra en la playlist.')
                return

        self._playlist.append(media)
        await message.channel.send(f'{message.author.name}. Se agregó {song_name} a la playlist.')

        if self._player.is_playing() == 0:
            await self.play(media)

    def set_volume(self, volume=50):
        if isinstance(volume, int):
            self._player.audio_set_volume(volume)
        elif volume.isnumeric():
            num = int(volume)
            if num <= self.max_volume and num > 0:
                self._player.audio_set_volume(num)
            elif num > self.max_volume:
                self._player.audio_set_volume(self.max_volume)

    def get_song_reference(self):
        return self._current_song_reference
