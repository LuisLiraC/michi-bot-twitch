import csv
import shutil
import uuid

from pytube import YouTube


class MusicDL:
    def __init__(self, max_duration=600, download_path='./'):
        self.max_duration = max_duration
        self.download_path = download_path
        self.songs_csv_path = './songs.csv'

    def download(self, url):
        yt = YouTube(url)

        if yt.length > self.max_duration:
            return
        
        title = yt.title.replace(',', '')
        song_reference = self.get_song_reference(title)

        if song_reference is None:
            old_title = title
            new_title = str(uuid.uuid4()).replace('-', '')
            yt.title = new_title
            self.save_song_reference(old_title, new_title)

            streams = yt.streams.filter(only_audio=True)
            stream = streams[-1]
            stream.download()

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
                if row[1] == reference:
                    return row[0]

            return None
