import pyttsx3
from bot_utils import find_url


class TTSEngine:
    def __init__(self, template=''):
        self.tts_engine = pyttsx3.init()
        voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', voices[3].id)
        self.is_active = True
        self.template = template
        self.blacklist_words = set(
            ['gay', 'homosexual', 'nazi', 'porno', 'feminazi']
        )

    def read(self, message):
        try:
            if not self.is_active:
                return

            is_valid = self.validate_message(message.content.lower())

            if is_valid:
                self.tts_engine.say(self.template.format(
                    message.author.name, message.content))
                self.tts_engine.runAndWait()
        except Exception as ex:
            print(ex)

    def validate_message(self, message):
        try:
            words = set(message.split(' '))
            words_count = len(words.intersection(self.blacklist_words))
            if words_count > 0:
                return False

            has_url = find_url(message)
            if has_url:
                return False

            return True
        except Exception as ex:
            print(ex)

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False
