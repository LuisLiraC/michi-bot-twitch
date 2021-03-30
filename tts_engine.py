import pyttsx3

class TTSEngine:
    def __init__(self):
        self.tts_engine = pyttsx3.init()
        voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', voices[3].id)

    def read(self, message):
        try:
            self.tts_engine.say(message)
            self.tts_engine.runAndWait()
        except Exception as ex:
            print(ex)
