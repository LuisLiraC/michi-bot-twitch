import vlc
import time
import asyncio

class MusicPlayer:
    def __init__(self, songs_path):
        self.songs_path = songs_path
        self._playlist = []
        self._vlc_instance = vlc.Instance()
        self._player = self._vlc_instance.media_player_new()
        self.set_volume()

    async def play(self, media):
        self._player.set_media(media)

        self._player.play()
        await self.check_is_playing()

    async def check_is_playing(self):
        while True:
            await asyncio.sleep(2.0)

            if self._player.is_playing() == 0:
                await self.next()

    def pause(self):
        pass

    def stop(self):
        self._player.stop()

    async def next(self):
        if len(self._playlist) > 1:
            self._playlist = self._playlist[1:]
            await self.play(self._playlist[0])
        else:
            self.stop()

    async def add_to_playlist(self, song):
        media = self._vlc_instance.media_new(f'{self.songs_path}{song}')
        self._playlist.append(media)

        print(self._playlist)
        if self._player.is_playing() == 0:
            await self.play(media)
        

    def set_volume(self, volume=50):
        self._player.audio_set_volume(volume)