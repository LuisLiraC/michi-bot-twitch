import csv
import shutil
import uuid
import os

from pytube import YouTube
from bot_utils import make_request

from custom_exceptions import MaxDurationException


class MusicDL:
    def __init__(self, max_duration=600, download_path='./'):
        self.max_duration = max_duration
        self.download_path = download_path
        self.songs_csv_path = './songs.csv'
        self.youtube_api_key = os.environ.get('YOUTUBE_API_KEY')

    def download(self, user_input):
        url = None
        if 'https://www.youtube.com/watch?v=' in user_input:
            url = user_input
        else:
            yt_id = self.get_yt_id(user_input)
            if yt_id is None:
                return

            url = f'https://www.youtube.com/watch?v={yt_id}'

        if url is None:
            return

        yt = YouTube(url)

        if yt.length > self.max_duration:
            raise MaxDurationException

        title = yt.title.replace(',', '')
        song_reference = self.get_song_reference(title)

        if song_reference is None:

            old_title = title
            new_title = str(uuid.uuid4()).replace('-', '')
            yt.title = new_title

            streams = yt.streams.filter(only_audio=True)
            stream = streams[-1]

            print(f'Donwloading {title}...')
            stream.download()

            self.save_song_reference(old_title, new_title)

            filename = f'{new_title}.webm'
            song_reference = filename
            self.relocate_song(filename)

        return song_reference

    def get_song_reference(self, title):
        with open(self.songs_csv_path, 'r', encoding='utf-8') as songs:
            data = csv.reader(songs)
            for row in data:
                if row[0] == title:
                    return f'{row[1]}.webm'

            return None

    def save_song_reference(self, old_title, new_title):
        with open(self.songs_csv_path, 'a', encoding='utf-8') as songs:
            songs.write(f'{old_title},{new_title}\n')

    def relocate_song(self, filename):
        shutil.move(f'./{filename}', f'{self.download_path}{filename}')

    def get_song_name(self, reference):
        with open(self.songs_csv_path, 'r', encoding='utf-8') as songs:
            data = csv.reader(songs)
            for row in data:
                if row[1] == reference.replace('.webm', ''):
                    return row[0]

            return None

    def get_yt_id(self, user_input):
        request_url = f'https://www.googleapis.com/youtube/v3/search?maxResults=1&q={user_input}&type=video&key={self.youtube_api_key}'
        response = make_request(request_url)
        print(response)
        items = response['items']

        if len(items) < 1:
            return None

        yt_id = items[0]['id']['videoId']
        return yt_id
